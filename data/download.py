#!/usr/bin/env python3
"""Download dictionary source files."""

import argparse
import gzip
import os
from pathlib import Path
import shutil
import sys

try:
    import requests
except ImportError:
    print("Error: requests library not found")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)


SOURCES = {
    'jmdict': {
        'url': 'http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz',
        'file': 'JMdict_e.xml.gz',
        'extracted': 'JMdict_e.xml',
        'description': 'Japanese-English dictionary (~180k entries)',
    },
    'cedict': {
        'url': 'https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz',
        'file': 'cedict.txt.gz',
        'extracted': 'cedict.txt',
        'description': 'Chinese-English dictionary (~120k entries)',
    },
    'kanjidic': {
        'url': 'http://www.edrdg.org/kanjidic/kanjidic2.xml.gz',
        'file': 'kanjidic2.xml.gz',
        'extracted': 'kanjidic2.xml',
        'description': 'Kanji character dictionary (optional)',
    },
}


def download_file(url: str, dest: Path, description: str) -> bool:
    """Download a file with progress indication."""
    try:
        print(f"\nDownloading {description}...")
        print(f"  URL: {url}")

        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)

                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    print(f"\r  Progress: {percent:.1f}% ({mb:.1f}/{total_mb:.1f} MB)", end='', flush=True)

        print(f"\n  ✓ Saved to {dest}")
        return True

    except requests.exceptions.Timeout:
        print(f"\n  ✗ Error: Download timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n  ✗ Error: {e}")
        return False
    except Exception as e:
        print(f"\n  ✗ Unexpected error: {e}")
        return False


def extract_gz(gz_path: Path, output_path: Path) -> bool:
    """Extract a .gz file."""
    try:
        print(f"  Extracting {gz_path.name}...")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"  ✓ Extracted to {output_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Extraction failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Download dictionary sources')
    parser.add_argument('--sample', action='store_true',
                        help='Skip downloads (use sample data)')
    parser.add_argument('--output', default='sources',
                        help='Output directory (default: sources)')
    parser.add_argument('--skip', nargs='+', choices=['jmdict', 'cedict', 'kanjidic'],
                        help='Skip downloading specific sources')
    parser.add_argument('--extract', action='store_true',
                        help='Extract .gz files after downloading')
    args = parser.parse_args()

    output_dir = Path(__file__).parent / args.output
    output_dir.mkdir(exist_ok=True)

    if args.sample:
        print("Sample mode: skipping downloads")
        print("Use sample data generator: cd sample && python3 generate_samples.py")
        return 0

    skip_list = args.skip or []

    print("=" * 60)
    print("Trilingual Dictionary - Data Download")
    print("=" * 60)
    print(f"\nOutput directory: {output_dir}")
    print(f"Skip list: {skip_list if skip_list else 'None'}")
    print("\nNote: These files are large (total ~50MB compressed)")
    print("Downloading may take several minutes depending on connection.")
    print()

    success_count = 0
    extracted_count = 0

    for name, info in SOURCES.items():
        if name in skip_list:
            print(f"\n[{name}] Skipped")
            continue

        print(f"\n[{name}] {info['description']}")
        dest = output_dir / info['file']
        extracted_dest = output_dir / info['extracted']

        # Check if already exists
        if extracted_dest.exists():
            print(f"  ✓ Already extracted: {extracted_dest}")
            success_count += 1
            extracted_count += 1
            continue
        elif dest.exists():
            print(f"  ⚠ Already downloaded: {dest}")
            success_count += 1

            if args.extract:
                if extract_gz(dest, extracted_dest):
                    extracted_count += 1
            continue

        # Download
        if download_file(info['url'], dest, info['description']):
            success_count += 1

            # Extract if requested
            if args.extract:
                if extract_gz(dest, extracted_dest):
                    extracted_count += 1

    print()
    print("=" * 60)
    print(f"Download Summary:")
    print(f"  Downloaded: {success_count}/{len(SOURCES) - len(skip_list)} files")
    if args.extract:
        print(f"  Extracted: {extracted_count}/{success_count} files")
    print("=" * 60)

    if success_count == len(SOURCES) - len(skip_list):
        print("\n✅ All downloads complete!")

        if args.extract:
            print("\nNext steps:")
            print(f"  python3 ingest.py --input {output_dir}")
        else:
            print("\nTo extract files:")
            print(f"  python3 download.py --extract")
            print("\nOr manually:")
            print(f"  cd {output_dir} && gunzip *.gz")

        return 0
    else:
        print("\n⚠️  Some downloads failed. Check errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
