#!/usr/bin/env python3
"""Download dictionary source files."""

import argparse
import os
from pathlib import Path
import sys

try:
    import requests
except ImportError:
    print("Error: requests library not found")
    print("Install with: pip install requests")
    sys.exit(1)


SOURCES = {
    'jmdict': {
        'url': 'http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz',
        'file': 'JMdict_e.xml.gz',
        'description': 'Japanese-English dictionary',
    },
    'cedict': {
        'url': 'https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz',
        'file': 'cedict.txt.gz',
        'description': 'Chinese-English dictionary',
    },
    'kanjidic': {
        'url': 'http://www.edrdg.org/kanjidic/kanjidic2.xml.gz',
        'file': 'kanjidic2.xml.gz',
        'description': 'Kanji character dictionary',
    },
}


def download_file(url: str, dest: Path) -> bool:
    """Download a file with progress indication."""
    try:
        print(f"Downloading {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)

                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progress: {percent:.1f}%", end='')

        print(f"\n  ✓ Saved to {dest}")
        return True

    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Download dictionary sources')
    parser.add_argument('--sample', action='store_true',
                        help='Skip downloads (use sample data)')
    parser.add_argument('--output', default='sources',
                        help='Output directory (default: sources)')
    args = parser.parse_args()

    output_dir = Path(__file__).parent / args.output
    output_dir.mkdir(exist_ok=True)

    if args.sample:
        print("Sample mode: skipping downloads")
        print("Use sample data in sample/ directory")
        return 0

    print("Downloading dictionary sources...\n")

    success_count = 0
    for name, info in SOURCES.items():
        print(f"[{name}] {info['description']}")
        dest = output_dir / info['file']

        if dest.exists():
            print(f"  ⚠ Already exists: {dest}")
            print(f"  Delete it to re-download")
            success_count += 1
            continue

        if download_file(info['url'], dest):
            success_count += 1

        print()

    print(f"\nCompleted: {success_count}/{len(SOURCES)} files downloaded")

    if success_count == len(SOURCES):
        print("\nNext steps:")
        print(f"  1. Extract files: cd {output_dir} && gunzip *.gz")
        print(f"  2. Run ingestion: python3 ingest.py --input {output_dir}")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
