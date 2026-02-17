#!/usr/bin/env python3
"""
Import example sentences from Tatoeba Project.

Tatoeba (tatoeba.org) is an open-source collection of sentences and translations.
This script downloads Japanese and Chinese sentences with English translations
and links them to dictionary words.

Data files:
- sentences.tar.bz2: All sentences with IDs and text
- links.tar.bz2: Links between sentences (e.g., Japanese sentence #123 → English #456)

License: CC BY 2.0 FR
"""

import argparse
import bz2
import csv
import os
import re
import sqlite3
import tarfile
from collections import defaultdict
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not found")
    print("Install with: pip install requests")
    exit(1)

# Tatoeba download URLs
SENTENCES_URL = "https://downloads.tatoeba.org/exports/sentences.tar.bz2"
LINKS_URL = "https://downloads.tatoeba.org/exports/links.tar.bz2"

def download_file(url, dest_path):
    """Download a file with progress indication."""
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0

    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                print(f"\rProgress: {percent:.1f}%", end='')
    print("\n✓ Download complete")

def extract_tar_bz2(archive_path, extract_to):
    """Extract .tar.bz2 file."""
    print(f"Extracting {archive_path.name}...")
    with tarfile.open(archive_path, 'r:bz2') as tar:
        tar.extractall(extract_to)
    print("✓ Extraction complete")

def load_sentences(sentences_file, languages):
    """Load sentences for specified languages."""
    print(f"Loading sentences for languages: {', '.join(languages)}...")
    sentences = {}

    with open(sentences_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 3:
                continue

            sentence_id, lang, text = row[0], row[1], row[2]

            if lang in languages:
                sentences[sentence_id] = {'lang': lang, 'text': text}

    print(f"✓ Loaded {len(sentences)} sentences")
    return sentences

def load_links(links_file):
    """Load translation links between sentences."""
    print("Loading translation links...")
    links = defaultdict(list)

    with open(links_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 2:
                continue

            source_id, target_id = row[0], row[1]
            links[source_id].append(target_id)

    print(f"✓ Loaded {len(links)} translation links")
    return links

def find_matching_words(db_conn, text, language):
    """Find words in the database that appear in the sentence."""
    cursor = db_conn.cursor()
    matched_words = []

    if language == 'jpn':
        # Japanese: search by headword or reading
        cursor.execute("""
            SELECT id, headword, reading
            FROM japanese_words
            WHERE is_common = 1
            ORDER BY LENGTH(headword) DESC
            LIMIT 5000
        """)

        for word_id, headword, reading in cursor.fetchall():
            if headword in text or reading in text:
                matched_words.append(('ja', word_id))

    elif language == 'cmn':
        # Chinese: search by simplified form
        cursor.execute("""
            SELECT id, simplified
            FROM chinese_words
            WHERE is_common = 1
            ORDER BY LENGTH(simplified) DESC
            LIMIT 5000
        """)

        for word_id, simplified in cursor.fetchall():
            if simplified in text:
                matched_words.append(('zh', word_id))

    return matched_words

def import_examples(db_path, sentences, links, max_per_word=5):
    """Import examples into the database."""
    print("\nImporting examples into database...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing examples
    cursor.execute("DELETE FROM examples")

    # Track examples per word to avoid duplicates
    examples_per_word = defaultdict(int)
    total_imported = 0

    # Process Japanese sentences
    ja_count = 0
    for sent_id, sent_data in sentences.items():
        if sent_data['lang'] != 'jpn':
            continue

        # Find English translation
        english_text = None
        for linked_id in links.get(sent_id, []):
            if linked_id in sentences and sentences[linked_id]['lang'] == 'eng':
                english_text = sentences[linked_id]['text']
                break

        if not english_text:
            continue

        # Find matching words
        matched_words = find_matching_words(conn, sent_data['text'], 'jpn')

        for lang, word_id in matched_words:
            key = (lang, word_id)
            if examples_per_word[key] >= max_per_word:
                continue

            cursor.execute("""
                INSERT INTO examples (language, word_id, source_text, english_text)
                VALUES (?, ?, ?, ?)
            """, (lang, word_id, sent_data['text'], english_text))

            examples_per_word[key] += 1
            total_imported += 1

        ja_count += 1
        if ja_count % 1000 == 0:
            print(f"\rProcessed {ja_count} Japanese sentences, imported {total_imported} examples", end='')

    print(f"\n✓ Japanese: {ja_count} sentences processed")

    # Process Chinese sentences
    zh_count = 0
    for sent_id, sent_data in sentences.items():
        if sent_data['lang'] != 'cmn':
            continue

        # Find English translation
        english_text = None
        for linked_id in links.get(sent_id, []):
            if linked_id in sentences and sentences[linked_id]['lang'] == 'eng':
                english_text = sentences[linked_id]['text']
                break

        if not english_text:
            continue

        # Find matching words
        matched_words = find_matching_words(conn, sent_data['text'], 'cmn')

        for lang, word_id in matched_words:
            key = (lang, word_id)
            if examples_per_word[key] >= max_per_word:
                continue

            cursor.execute("""
                INSERT INTO examples (language, word_id, source_text, english_text)
                VALUES (?, ?, ?, ?)
            """, (lang, word_id, sent_data['text'], english_text))

            examples_per_word[key] += 1
            total_imported += 1

        zh_count += 1
        if zh_count % 1000 == 0:
            print(f"\rProcessed {zh_count} Chinese sentences, imported {total_imported} examples", end='')

    print(f"\n✓ Chinese: {zh_count} sentences processed")

    conn.commit()
    conn.close()

    print(f"\n✅ Imported {total_imported} examples")
    print(f"   Words with examples: {len(examples_per_word)}")

def main():
    parser = argparse.ArgumentParser(description='Import Tatoeba example sentences')
    parser.add_argument('--db', default='../dictionary.db', help='Path to dictionary database')
    parser.add_argument('--download', action='store_true', help='Download Tatoeba data')
    parser.add_argument('--data-dir', default='tatoeba', help='Directory for Tatoeba data')
    parser.add_argument('--max-per-word', type=int, default=5, help='Max examples per word')

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    data_dir.mkdir(exist_ok=True)

    sentences_archive = data_dir / 'sentences.tar.bz2'
    links_archive = data_dir / 'links.tar.bz2'
    sentences_file = data_dir / 'sentences.csv'
    links_file = data_dir / 'links.csv'

    # Download if requested
    if args.download:
        if not sentences_archive.exists():
            download_file(SENTENCES_URL, sentences_archive)
        else:
            print(f"✓ {sentences_archive} already exists")

        if not links_archive.exists():
            download_file(LINKS_URL, links_archive)
        else:
            print(f"✓ {links_archive} already exists")

        # Extract archives
        if not sentences_file.exists():
            extract_tar_bz2(sentences_archive, data_dir)
        else:
            print(f"✓ {sentences_file} already exists")

        if not links_file.exists():
            extract_tar_bz2(links_archive, data_dir)
        else:
            print(f"✓ {links_file} already exists")

    # Check if files exist
    if not sentences_file.exists():
        print(f"Error: {sentences_file} not found")
        print("Run with --download to download Tatoeba data")
        return 1

    if not links_file.exists():
        print(f"Error: {links_file} not found")
        print("Run with --download to download Tatoeba data")
        return 1

    # Load data
    sentences = load_sentences(sentences_file, ['jpn', 'cmn', 'eng'])
    links = load_links(links_file)

    # Import into database
    import_examples(args.db, sentences, links, args.max_per_word)

    print("\n✅ Done!")
    return 0

if __name__ == '__main__':
    exit(main())
