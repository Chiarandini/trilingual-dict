#!/usr/bin/env python3
"""Generate sample dictionary data for development and testing."""

import sqlite3
import sys
from pathlib import Path

# Sample data: (english, japanese_headword, japanese_reading, chinese_simplified, chinese_traditional, pinyin)
SAMPLE_WORDS = [
    ("cat", "猫", "ねこ", "猫", "貓", "māo", "N3", "1", 11),
    ("dog", "犬", "いぬ", "狗", "狗", "gǒu", "N3", "2", 8),
    ("eat", "食べる", "たべる", "吃", "吃", "chī", "N4", "1", 6),
    ("drink", "飲む", "のむ", "喝", "喝", "hē", "N4", "1", 12),
    ("book", "本", "ほん", "书", "書", "shū", "N5", "1", 4),
    ("water", "水", "みず", "水", "水", "shuǐ", "N5", "1", 4),
    ("fire", "火", "ひ", "火", "火", "huǒ", "N5", "1", 4),
    ("tree", "木", "き", "树", "樹", "shù", "N5", "1", 4),
    ("person", "人", "ひと", "人", "人", "rén", "N5", "1", 2),
    ("big", "大きい", "おおきい", "大", "大", "dà", "N5", "1", 3),
    ("small", "小さい", "ちいさい", "小", "小", "xiǎo", "N5", "1", 3),
    ("good", "良い", "よい", "好", "好", "hǎo", "N4", "1", 6),
    ("bad", "悪い", "わるい", "坏", "壞", "huài", "N4", "2", 7),
    ("house", "家", "いえ", "家", "家", "jiā", "N5", "1", 10),
    ("school", "学校", "がっこう", "学校", "學校", "xuéxiào", "N5", "1", 10),
    ("friend", "友達", "ともだち", "朋友", "朋友", "péngyǒu", "N4", "1", 8),
    ("time", "時間", "じかん", "时间", "時間", "shíjiān", "N4", "1", 10),
    ("year", "年", "とし", "年", "年", "nián", "N5", "1", 6),
    ("day", "日", "ひ", "天", "天", "tiān", "N5", "1", 4),
    ("hand", "手", "て", "手", "手", "shǒu", "N5", "1", 4),
]

# Example sentences
JAPANESE_EXAMPLES = [
    (1, "猫が好きです。", "I like cats."),
    (2, "犬を飼っています。", "I have a dog."),
    (3, "ご飯を食べます。", "I eat rice."),
    (4, "水を飲みます。", "I drink water."),
    (5, "本を読みます。", "I read books."),
]

CHINESE_EXAMPLES = [
    (1, "我喜欢猫。", "I like cats."),
    (2, "我有一只狗。", "I have a dog."),
    (3, "我吃饭。", "I eat rice."),
    (4, "我喝水。", "I drink water."),
    (5, "我看书。", "I read books."),
]

def generate_db(output_path: Path):
    """Generate sample database."""
    # Read schema
    schema_path = Path(__file__).parent.parent / "schema.sql"
    schema = schema_path.read_text()

    # Create database
    conn = sqlite3.connect(output_path)
    cursor = conn.cursor()

    # Execute schema
    cursor.executescript(schema)

    # Insert sample data
    for idx, (english, ja_head, ja_read, zh_simp, zh_trad, pinyin, jlpt, hsk, strokes) in enumerate(SAMPLE_WORDS, 1):
        # Insert Japanese word
        cursor.execute("""
            INSERT INTO japanese_words (headword, reading, is_common, frequency_rank, jlpt_level, stroke_count)
            VALUES (?, ?, 1, ?, ?, ?)
        """, (ja_head, ja_read, idx, jlpt, strokes))
        ja_word_id = cursor.lastrowid

        # Insert Japanese definition
        cursor.execute("""
            INSERT INTO japanese_definitions (word_id, english_gloss, pos)
            VALUES (?, ?, 'noun')
        """, (ja_word_id, english))

        # Insert Chinese word
        cursor.execute("""
            INSERT INTO chinese_words (simplified, traditional, pinyin, is_common, frequency_rank, hsk_level, stroke_count)
            VALUES (?, ?, ?, 1, ?, ?, ?)
        """, (zh_simp, zh_trad, pinyin, idx, hsk, strokes))
        zh_word_id = cursor.lastrowid

        # Insert Chinese definition
        cursor.execute("""
            INSERT INTO chinese_definitions (word_id, english_gloss)
            VALUES (?, ?)
        """, (zh_word_id, english))

    # Insert examples
    for word_id, source, english in JAPANESE_EXAMPLES:
        cursor.execute("""
            INSERT INTO examples (language, word_id, source_text, english_text)
            VALUES ('ja', ?, ?, ?)
        """, (word_id, source, english))

    for word_id, source, english in CHINESE_EXAMPLES:
        cursor.execute("""
            INSERT INTO examples (language, word_id, source_text, english_text)
            VALUES ('zh', ?, ?, ?)
        """, (word_id, source, english))

    conn.commit()
    conn.close()

    print(f"✓ Generated sample database: {output_path}")
    print(f"  - {len(SAMPLE_WORDS)} word pairs")
    print(f"  - {len(JAPANESE_EXAMPLES)} Japanese examples")
    print(f"  - {len(CHINESE_EXAMPLES)} Chinese examples")

if __name__ == "__main__":
    output = Path(__file__).parent.parent.parent / "dictionary.db"
    if len(sys.argv) > 1:
        output = Path(sys.argv[1])

    generate_db(output)
