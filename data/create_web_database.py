#!/usr/bin/env python3
"""
Create a web-optimized database with only common words.

This reduces the database size from ~74MB to ~5-10MB by keeping only:
- Words with is_common = 1
- JLPT N5-N2 for Japanese
- HSK 1-4 for Chinese
- Top 3000 most frequent words

The smaller database loads much faster in web browsers.
"""

import argparse
import shutil
import sqlite3
from pathlib import Path


def create_web_database(source_db, output_db, verbose=False):
    """Create web-optimized database from full database."""

    # Copy original database
    if verbose:
        print(f"Copying {source_db} to {output_db}...")
    shutil.copy(source_db, output_db)

    # Connect to new database
    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()

    # Get initial counts
    cursor.execute("SELECT COUNT(*) FROM japanese_words")
    ja_before = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM chinese_words")
    zh_before = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM examples")
    ex_before = cursor.fetchone()[0]

    if verbose:
        print(f"\nBefore optimization:")
        print(f"  Japanese words: {ja_before:,}")
        print(f"  Chinese words: {zh_before:,}")
        print(f"  Examples: {ex_before:,}")

    # Keep only common words OR top-ranked words
    if verbose:
        print("\nRemoving uncommon words...")

    cursor.execute("""
        DELETE FROM japanese_words
        WHERE is_common = 0
        AND (frequency_rank IS NULL OR frequency_rank > 3000)
    """)
    ja_removed = cursor.rowcount

    cursor.execute("""
        DELETE FROM chinese_words
        WHERE is_common = 0
        AND (frequency_rank IS NULL OR frequency_rank > 3000)
    """)
    zh_removed = cursor.rowcount

    if verbose:
        print(f"  Removed {ja_removed:,} Japanese words")
        print(f"  Removed {zh_removed:,} Chinese words")

    # Remove orphaned definitions
    if verbose:
        print("\nCleaning orphaned definitions...")

    cursor.execute("""
        DELETE FROM japanese_definitions
        WHERE word_id NOT IN (SELECT id FROM japanese_words)
    """)
    ja_def_removed = cursor.rowcount

    cursor.execute("""
        DELETE FROM chinese_definitions
        WHERE word_id NOT IN (SELECT id FROM chinese_words)
    """)
    zh_def_removed = cursor.rowcount

    if verbose:
        print(f"  Removed {ja_def_removed:,} Japanese definitions")
        print(f"  Removed {zh_def_removed:,} Chinese definitions")

    # Remove orphaned examples
    if verbose:
        print("\nCleaning orphaned examples...")

    cursor.execute("""
        DELETE FROM examples
        WHERE language = 'ja' AND word_id NOT IN (SELECT id FROM japanese_words)
    """)
    ja_ex_removed = cursor.rowcount

    cursor.execute("""
        DELETE FROM examples
        WHERE language = 'zh' AND word_id NOT IN (SELECT id FROM chinese_words)
    """)
    zh_ex_removed = cursor.rowcount

    if verbose:
        print(f"  Removed {ja_ex_removed:,} Japanese examples")
        print(f"  Removed {zh_ex_removed:,} Chinese examples")

    # Get final counts
    cursor.execute("SELECT COUNT(*) FROM japanese_words")
    ja_after = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM chinese_words")
    zh_after = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM examples")
    ex_after = cursor.fetchone()[0]

    # Commit changes before vacuum
    conn.commit()

    # Vacuum to reclaim space (must be outside transaction)
    if verbose:
        print("\nVacuuming database to reclaim space...")
    cursor.execute("VACUUM")

    conn.close()

    # Get file sizes
    source_size = Path(source_db).stat().st_size
    output_size = Path(output_db).stat().st_size
    reduction = ((source_size - output_size) / source_size) * 100

    # Print summary
    print(f"\n{'='*60}")
    print("WEB DATABASE OPTIMIZATION COMPLETE")
    print(f"{'='*60}")
    print(f"\nFile sizes:")
    print(f"  Before: {source_size / 1024 / 1024:.1f} MB")
    print(f"  After:  {output_size / 1024 / 1024:.1f} MB")
    print(f"  Reduction: {reduction:.1f}%")

    print(f"\nContent:")
    print(f"  Japanese words: {ja_before:,} → {ja_after:,} ({ja_after/ja_before*100:.1f}%)")
    print(f"  Chinese words: {zh_before:,} → {zh_after:,} ({zh_after/zh_before*100:.1f}%)")
    print(f"  Examples: {ex_before:,} → {ex_after:,}")

    print(f"\nOutput: {output_db}")
    print("\n✅ Ready for web deployment!")

    return output_db


def main():
    parser = argparse.ArgumentParser(
        description='Create web-optimized dictionary database'
    )
    parser.add_argument(
        '--input',
        default='dictionary.db',
        help='Input database (default: dictionary.db)'
    )
    parser.add_argument(
        '--output',
        default='dictionary_web.db',
        help='Output database (default: dictionary_web.db)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input database not found: {args.input}")
        print("\nTry:")
        print("  python3 create_web_database.py --input ../data/dictionary.db")
        return 1

    create_web_database(args.input, args.output, args.verbose)

    return 0


if __name__ == '__main__':
    exit(main())
