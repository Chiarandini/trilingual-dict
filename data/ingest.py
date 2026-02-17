#!/usr/bin/env python3
"""Ingest dictionary data into SQLite database."""

import argparse
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    print("Error: lxml not found. Install with: pip install lxml")
    sys.exit(1)


# Priority tag to frequency rank mapping
# Lower rank = more common
PRIORITY_MAP = {
    'news1': 100,    # Common news vocabulary (top 12k)
    'news2': 200,    # Somewhat common news vocabulary
    'ichi1': 150,    # Common words from Ichimango
    'ichi2': 250,
    'spec1': 50,     # Specialized but common
    'spec2': 150,
    'gai1': 200,     # Common loanwords
    'gai2': 300,
}

# JLPT tag mapping
JLPT_MAP = {
    'jlpt-n5': 'N5',
    'jlpt-n4': 'N4',
    'jlpt-n3': 'N3',
    'jlpt-n2': 'N2',
    'jlpt-n1': 'N1',
}

# HSK level patterns (extracted from definitions or tags)
HSK_PATTERNS = {
    1: ['HSK 1', 'HSK1'],
    2: ['HSK 2', 'HSK2'],
    3: ['HSK 3', 'HSK3'],
    4: ['HSK 4', 'HSK4'],
    5: ['HSK 5', 'HSK5'],
    6: ['HSK 6', 'HSK6'],
}


class DatabaseBuilder:
    """Build SQLite database from parsed dictionary data."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def create_schema(self, schema_path: Path):
        """Execute schema SQL to create tables and indexes."""
        print(f"Creating database schema...")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        self.cursor.executescript(schema_sql)
        self.conn.commit()
        print(f"  ✓ Schema created")

    def insert_japanese_word(self, headword, reading, is_common, freq_rank, jlpt_level, stroke_count):
        """Insert a Japanese word and return its ID."""
        self.cursor.execute('''
            INSERT INTO japanese_words
            (headword, reading, is_common, frequency_rank, jlpt_level, stroke_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (headword, reading, is_common, freq_rank, jlpt_level, stroke_count))
        return self.cursor.lastrowid

    def insert_japanese_definition(self, word_id, gloss, pos):
        """Insert a Japanese definition."""
        self.cursor.execute('''
            INSERT INTO japanese_definitions (word_id, english_gloss, pos)
            VALUES (?, ?, ?)
        ''', (word_id, gloss, pos))

    def insert_chinese_word(self, simplified, traditional, pinyin, is_common, freq_rank, hsk_level, stroke_count):
        """Insert a Chinese word and return its ID."""
        self.cursor.execute('''
            INSERT INTO chinese_words
            (simplified, traditional, pinyin, is_common, frequency_rank, hsk_level, stroke_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (simplified, traditional, pinyin, is_common, freq_rank, hsk_level, stroke_count))
        return self.cursor.lastrowid

    def insert_chinese_definition(self, word_id, gloss):
        """Insert a Chinese definition."""
        self.cursor.execute('''
            INSERT INTO chinese_definitions (word_id, english_gloss)
            VALUES (?, ?)
        ''', (word_id, gloss))

    def insert_example(self, language, word_id, source_text, english_text):
        """Insert an example sentence."""
        self.cursor.execute('''
            INSERT INTO examples (language, word_id, source_text, english_text)
            VALUES (?, ?, ?, ?)
        ''', (language, word_id, source_text, english_text))

    def commit(self):
        """Commit transaction."""
        self.conn.commit()


def parse_jmdict(xml_path: Path, kanjidic_data: dict) -> list:
    """Parse JMdict XML file and return list of entries.

    Each entry: {
        'headword': str,
        'reading': str,
        'is_common': bool,
        'frequency_rank': int or None,
        'jlpt_level': str or None,
        'stroke_count': int or None,
        'definitions': [{'gloss': str, 'pos': str}],
    }
    """
    print(f"Parsing JMdict: {xml_path}")

    if not xml_path.exists():
        print("  ⚠ File not found")
        return []

    entries = []
    tree = etree.parse(str(xml_path))
    root = tree.getroot()

    total_entries = len(root.findall('entry'))
    print(f"  Found {total_entries} entries")

    for i, entry in enumerate(root.findall('entry'), 1):
        # Progress indicator every 10k entries
        if i % 10000 == 0:
            print(f"  Progress: {i}/{total_entries} ({i*100//total_entries}%)")

        # Extract kanji headword (k_ele)
        k_ele = entry.find('k_ele')
        if k_ele is not None:
            headword = k_ele.find('keb').text
        else:
            # Kana-only word, use reading as headword
            r_ele = entry.find('r_ele')
            if r_ele is None:
                continue
            headword = r_ele.find('reb').text

        # Extract reading (r_ele)
        r_ele = entry.find('r_ele')
        reading = r_ele.find('reb').text if r_ele is not None else headword

        # Extract priority tags for frequency ranking
        priorities = []
        for ke_pri in entry.findall('.//ke_pri'):
            priorities.append(ke_pri.text)
        for re_pri in entry.findall('.//re_pri'):
            priorities.append(re_pri.text)

        # Calculate frequency rank
        is_common = len(priorities) > 0
        freq_rank = None
        if priorities:
            # Use the best (lowest) rank from priority tags
            ranks = [PRIORITY_MAP.get(p, 1000) for p in priorities]
            freq_rank = min(ranks)

        # Extract JLPT level
        jlpt_level = None
        for pri in priorities:
            if pri in JLPT_MAP:
                jlpt_level = JLPT_MAP[pri]
                break

        # Get stroke count from KANJIDIC2
        stroke_count = kanjidic_data.get(headword, {}).get('stroke_count')

        # Extract definitions (sense elements)
        definitions = []
        for sense in entry.findall('sense'):
            # Get glosses
            glosses = [g.text for g in sense.findall('gloss') if g.text]
            if not glosses:
                continue

            # Get part of speech
            pos_elements = sense.findall('pos')
            pos = pos_elements[0].text if pos_elements else None
            if pos:
                # Simplify POS tags (e.g., "noun (common) (futsuumeishi)" -> "noun")
                pos = pos.split('(')[0].strip()

            # Combine glosses
            combined_gloss = '; '.join(glosses)
            definitions.append({'gloss': combined_gloss, 'pos': pos})

        if definitions:
            entries.append({
                'headword': headword,
                'reading': reading,
                'is_common': is_common,
                'frequency_rank': freq_rank,
                'jlpt_level': jlpt_level,
                'stroke_count': stroke_count,
                'definitions': definitions,
            })

    print(f"  ✓ Parsed {len(entries)} Japanese entries")
    return entries


def parse_cedict(txt_path: Path) -> list:
    """Parse CC-CEDICT text file and return list of entries.

    Format: 繁體 简体 [pin1 yin1] /definition 1/definition 2/

    Each entry: {
        'simplified': str,
        'traditional': str,
        'pinyin': str,
        'is_common': bool,
        'frequency_rank': int or None,
        'hsk_level': str or None,
        'stroke_count': int or None,
        'definitions': [str],
    }
    """
    print(f"Parsing CC-CEDICT: {txt_path}")

    if not txt_path.exists():
        print("  ⚠ File not found")
        return []

    entries = []
    line_pattern = re.compile(r'^(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+/(.+)/$')

    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"  Processing {total_lines} lines")

    for i, line in enumerate(lines, 1):
        # Progress indicator
        if i % 10000 == 0:
            print(f"  Progress: {i}/{total_lines} ({i*100//total_lines}%)")

        # Skip comments and empty lines
        if line.startswith('#') or not line.strip():
            continue

        match = line_pattern.match(line)
        if not match:
            continue

        traditional, simplified, pinyin, definitions_str = match.groups()

        # Split definitions
        definitions = [d.strip() for d in definitions_str.split('/') if d.strip()]
        if not definitions:
            continue

        # Check for HSK level in definitions
        hsk_level = None
        for level, patterns in HSK_PATTERNS.items():
            for pattern in patterns:
                if any(pattern in d for d in definitions):
                    hsk_level = str(level)
                    break
            if hsk_level:
                break

        # Estimate frequency based on word length (shorter = more common for basic words)
        # This is a heuristic; real frequency data would be better
        is_common = len(simplified) <= 2 or hsk_level in ['1', '2', '3']
        freq_rank = None
        if is_common:
            # Rough heuristic: shorter words are more common
            freq_rank = 100 + (len(simplified) - 1) * 50
            if hsk_level:
                # HSK level provides better frequency estimate
                freq_rank = int(hsk_level) * 200

        # Stroke count (approximate by character count * 10)
        # Real stroke data would come from a separate database
        stroke_count = len(simplified) * 10

        entries.append({
            'simplified': simplified,
            'traditional': traditional,
            'pinyin': pinyin,
            'is_common': is_common,
            'frequency_rank': freq_rank,
            'hsk_level': hsk_level,
            'stroke_count': stroke_count,
            'definitions': definitions,
        })

    print(f"  ✓ Parsed {len(entries)} Chinese entries")
    return entries


def parse_kanjidic(xml_path: Path) -> dict:
    """Parse KANJIDIC2 XML file and return kanji data.

    Returns: {kanji: {'stroke_count': int, 'grade': int, ...}}
    """
    print(f"Parsing KANJIDIC2: {xml_path}")

    if not xml_path.exists():
        print("  ⚠ File not found (optional - stroke counts will be estimated)")
        return {}

    kanji_data = {}
    tree = etree.parse(str(xml_path))
    root = tree.getroot()

    for character in root.findall('character'):
        literal = character.find('literal')
        if literal is None:
            continue

        kanji = literal.text

        # Get stroke count
        stroke_count = None
        misc = character.find('misc')
        if misc is not None:
            sc = misc.find('stroke_count')
            if sc is not None:
                stroke_count = int(sc.text)

        # Get grade (JLPT approximation)
        grade = None
        if misc is not None:
            g = misc.find('grade')
            if g is not None:
                grade = int(g.text)

        kanji_data[kanji] = {
            'stroke_count': stroke_count,
            'grade': grade,
        }

    print(f"  ✓ Parsed {len(kanji_data)} kanji characters")
    return kanji_data


def build_database(output_path: Path, japanese_entries: list, chinese_entries: list, schema_path: Path):
    """Build SQLite database from parsed entries."""
    print(f"\nBuilding database: {output_path}")

    # Remove existing database
    if output_path.exists():
        output_path.unlink()
        print(f"  Removed existing database")

    with DatabaseBuilder(output_path) as db:
        # Create schema
        db.create_schema(schema_path)

        # Insert Japanese entries
        print(f"\nInserting {len(japanese_entries)} Japanese entries...")
        for i, entry in enumerate(japanese_entries, 1):
            if i % 10000 == 0:
                print(f"  Progress: {i}/{len(japanese_entries)} ({i*100//len(japanese_entries)}%)")
                db.commit()

            word_id = db.insert_japanese_word(
                headword=entry['headword'],
                reading=entry['reading'],
                is_common=entry['is_common'],
                freq_rank=entry['frequency_rank'],
                jlpt_level=entry['jlpt_level'],
                stroke_count=entry['stroke_count']
            )

            for defn in entry['definitions']:
                db.insert_japanese_definition(
                    word_id=word_id,
                    gloss=defn['gloss'],
                    pos=defn['pos']
                )

        db.commit()
        print(f"  ✓ Inserted Japanese entries")

        # Insert Chinese entries
        print(f"\nInserting {len(chinese_entries)} Chinese entries...")
        for i, entry in enumerate(chinese_entries, 1):
            if i % 10000 == 0:
                print(f"  Progress: {i}/{len(chinese_entries)} ({i*100//len(chinese_entries)}%)")
                db.commit()

            word_id = db.insert_chinese_word(
                simplified=entry['simplified'],
                traditional=entry['traditional'],
                pinyin=entry['pinyin'],
                is_common=entry['is_common'],
                freq_rank=entry['frequency_rank'],
                hsk_level=entry['hsk_level'],
                stroke_count=entry['stroke_count']
            )

            for defn in entry['definitions']:
                db.insert_chinese_definition(
                    word_id=word_id,
                    gloss=defn
                )

        db.commit()
        print(f"  ✓ Inserted Chinese entries")

        # Optimize database
        print(f"\nOptimizing database...")
        db.cursor.execute('ANALYZE')
        db.cursor.execute('VACUUM')
        db.commit()
        print(f"  ✓ Database optimized")

    # Show database statistics
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"Database created successfully!")
    print(f"  Location: {output_path}")
    print(f"  Size: {file_size_mb:.1f} MB")
    print(f"  Japanese entries: {len(japanese_entries)}")
    print(f"  Chinese entries: {len(chinese_entries)}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='Ingest dictionary data')
    parser.add_argument('--input', default='sources',
                        help='Input directory with source files (default: sources)')
    parser.add_argument('--output', default='dictionary.db',
                        help='Output SQLite database path (default: dictionary.db)')
    parser.add_argument('--sample', action='store_true',
                        help='Use sample data only')
    args = parser.parse_args()

    # Resolve paths
    input_dir = Path(__file__).parent / args.input
    output_path = Path(__file__).parent / args.output
    schema_path = Path(__file__).parent / 'schema.sql'

    if args.sample:
        print("Sample mode: Using sample data generator")
        print("Run: cd sample && python3 generate_samples.py")
        return 0

    # Check input directory
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        print("\nPlease download source files first:")
        print(f"  python3 download.py --extract --output {input_dir.name}")
        return 1

    print("=" * 60)
    print("Trilingual Dictionary - Data Ingestion")
    print("=" * 60)
    print(f"\nInput directory: {input_dir}")
    print(f"Output database: {output_path}")
    print(f"Schema file: {schema_path}\n")

    # Find source files
    jmdict_path = input_dir / 'JMdict_e.xml'
    cedict_path = input_dir / 'cedict.txt'
    kanjidic_path = input_dir / 'kanjidic2.xml'

    # Check required files
    if not jmdict_path.exists():
        print(f"Error: JMdict file not found: {jmdict_path}")
        print("\nExtract downloaded files:")
        print(f"  cd {input_dir} && gunzip JMdict_e.xml.gz")
        return 1

    if not cedict_path.exists():
        print(f"Error: CC-CEDICT file not found: {cedict_path}")
        print("\nExtract downloaded files:")
        print(f"  cd {input_dir} && gunzip cedict.txt.gz")
        return 1

    # Parse KANJIDIC2 (optional)
    kanjidic_data = parse_kanjidic(kanjidic_path)

    # Parse dictionaries
    japanese_entries = parse_jmdict(jmdict_path, kanjidic_data)
    chinese_entries = parse_cedict(cedict_path)

    if not japanese_entries and not chinese_entries:
        print("\nError: No entries parsed from source files")
        return 1

    # Build database
    build_database(output_path, japanese_entries, chinese_entries, schema_path)

    print("\n✅ Data ingestion complete!")
    print("\nNext steps:")
    print(f"  1. Copy database: cp {output_path} ../cmd/dict/")
    print(f"  2. Test CLI: cd ../cmd/dict && ./dict cat")
    print(f"  3. Copy to other frontends:")
    print(f"     - Web: cp {output_path} ../web/src/assets/")
    print(f"     - iOS: cp {output_path} ../ios/TriDict/Resources/")

    return 0


if __name__ == '__main__':
    sys.exit(main())
