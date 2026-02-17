#!/usr/bin/env python3
"""Comprehensive test of dictionary queries across all three languages."""

import json
import random
import sqlite3
import subprocess
import sys
from pathlib import Path

# Test configuration
NUM_TESTS_PER_LANGUAGE = 30
DICT_CLI = Path(__file__).parent / "cmd/dict/dict"
DATABASE = Path(__file__).parent / "data/dictionary.db"

def get_sample_words(db_path, language, count):
    """Get sample words from the database for testing."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if language == "en":
        # Get common single-word English glosses that appear in both JA and ZH
        cursor.execute("""
            SELECT DISTINCT j.english_gloss
            FROM japanese_definitions j
            JOIN chinese_definitions c ON LOWER(j.english_gloss) = LOWER(c.english_gloss)
            WHERE j.english_gloss NOT LIKE '%(%'
            AND j.english_gloss NOT LIKE '%;%'
            AND j.english_gloss NOT LIKE '% %'
            AND LENGTH(j.english_gloss) < 15
            AND LENGTH(j.english_gloss) > 2
            ORDER BY RANDOM()
            LIMIT ?
        """, (count,))
        words = [row[0] for row in cursor.fetchall()]
    elif language == "ja":
        # Get Japanese headwords
        cursor.execute("""
            SELECT headword FROM japanese_words
            WHERE is_common = 1
            AND headword NOT LIKE '%/%'
            ORDER BY RANDOM()
            LIMIT ?
        """, (count,))
        words = [row[0] for row in cursor.fetchall()]
    elif language == "zh":
        # Get Chinese simplified words
        cursor.execute("""
            SELECT simplified FROM chinese_words
            WHERE is_common = 1
            AND simplified NOT LIKE '%/%'
            ORDER BY RANDOM()
            LIMIT ?
        """, (count,))
        words = [row[0] for row in cursor.fetchall()]

    conn.close()
    return words

def query_word(word):
    """Query a word using the CLI and return parsed JSON response."""
    try:
        result = subprocess.run(
            [str(DICT_CLI), "--json", word],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error querying '{word}': {e}")
        return None

def validate_response(word, response, expected_language):
    """Validate that a response is reasonable."""
    issues = []

    if not response:
        issues.append("No response returned")
        return issues

    # Check meta
    if 'meta' not in response:
        issues.append("Missing 'meta' field")
        return issues

    if response['meta'].get('query') != word:
        issues.append(f"Query mismatch: expected '{word}', got '{response['meta'].get('query')}'")

    detected_lang = response['meta'].get('input_language')
    if detected_lang not in ['en', 'ja', 'zh', 'ambiguous', 'unknown']:
        issues.append(f"Invalid language detection: {detected_lang}")

    # Check outputs
    if 'outputs' not in response:
        issues.append("Missing 'outputs' field")
        return issues

    outputs = response['outputs']

    if expected_language == "en":
        # English input should return at least 1 output (JA or ZH, or both)
        if len(outputs) == 0:
            issues.append(f"Expected at least 1 output for English, got 0")
        else:
            # Check all outputs have valid language codes
            languages = {o.get('language') for o in outputs}
            valid_languages = {'ja', 'zh'}
            invalid = languages - valid_languages
            if invalid:
                issues.append(f"Invalid languages in outputs: {invalid}")
    else:
        # Japanese/Chinese input should return the source + pivoted language
        if len(outputs) == 0:
            issues.append("No outputs returned")
        else:
            # Check first output has required fields
            first_output = outputs[0]
            required_fields = ['language', 'headword', 'reading', 'definition']
            for field in required_fields:
                if field not in first_output:
                    issues.append(f"Missing field '{field}' in output")

            # Check that headword is not empty
            if 'headword' in first_output and not first_output['headword']:
                issues.append("Empty headword")

            # Check that definition is not empty
            if 'definition' in first_output and not first_output['definition']:
                issues.append("Empty definition")

    return issues

def run_tests():
    """Run comprehensive tests."""
    print("=" * 70)
    print("COMPREHENSIVE DICTIONARY TEST")
    print("=" * 70)
    print(f"\nDatabase: {DATABASE}")
    print(f"CLI: {DICT_CLI}")
    print(f"Tests per language: {NUM_TESTS_PER_LANGUAGE}\n")

    if not DICT_CLI.exists():
        print(f"ERROR: CLI not found at {DICT_CLI}")
        print("Please build it first: cd cmd/dict && go build -o dict")
        return 1

    if not DATABASE.exists():
        print(f"ERROR: Database not found at {DATABASE}")
        print("Please create it first: cd data && python3 ingest.py")
        return 1

    # Get sample words
    print("Gathering sample words...")
    english_words = get_sample_words(DATABASE, "en", NUM_TESTS_PER_LANGUAGE)
    japanese_words = get_sample_words(DATABASE, "ja", NUM_TESTS_PER_LANGUAGE)
    chinese_words = get_sample_words(DATABASE, "zh", NUM_TESTS_PER_LANGUAGE)

    print(f"  English: {len(english_words)} words")
    print(f"  Japanese: {len(japanese_words)} words")
    print(f"  Chinese: {len(chinese_words)} words\n")

    # Test results tracking
    results = {
        'en': {'total': 0, 'passed': 0, 'failed': 0, 'errors': [], 'samples': []},
        'ja': {'total': 0, 'passed': 0, 'failed': 0, 'errors': [], 'samples': []},
        'zh': {'total': 0, 'passed': 0, 'failed': 0, 'errors': [], 'samples': []},
    }

    # Test English words
    print("Testing English words...")
    for i, word in enumerate(english_words, 1):
        if i % 20 == 0:
            print(f"  Progress: {i}/{len(english_words)}")

        results['en']['total'] += 1
        response = query_word(word)
        issues = validate_response(word, response, 'en')

        if issues:
            results['en']['failed'] += 1
            results['en']['errors'].append({'word': word, 'issues': issues})
        else:
            results['en']['passed'] += 1
            if len(results['en']['samples']) < 5:
                results['en']['samples'].append({'word': word, 'response': response})

    print(f"  ✓ Completed: {results['en']['passed']}/{results['en']['total']} passed\n")

    # Test Japanese words
    print("Testing Japanese words...")
    for i, word in enumerate(japanese_words, 1):
        if i % 20 == 0:
            print(f"  Progress: {i}/{len(japanese_words)}")

        results['ja']['total'] += 1
        response = query_word(word)
        issues = validate_response(word, response, 'ja')

        if issues:
            results['ja']['failed'] += 1
            results['ja']['errors'].append({'word': word, 'issues': issues})
        else:
            results['ja']['passed'] += 1
            if len(results['ja']['samples']) < 5:
                results['ja']['samples'].append({'word': word, 'response': response})

    print(f"  ✓ Completed: {results['ja']['passed']}/{results['ja']['total']} passed\n")

    # Test Chinese words
    print("Testing Chinese words...")
    for i, word in enumerate(chinese_words, 1):
        if i % 20 == 0:
            print(f"  Progress: {i}/{len(chinese_words)}")

        results['zh']['total'] += 1
        response = query_word(word)
        issues = validate_response(word, response, 'zh')

        if issues:
            results['zh']['failed'] += 1
            results['zh']['errors'].append({'word': word, 'issues': issues})
        else:
            results['zh']['passed'] += 1
            if len(results['zh']['samples']) < 5:
                results['zh']['samples'].append({'word': word, 'response': response})

    print(f"  ✓ Completed: {results['zh']['passed']}/{results['zh']['total']} passed\n")

    # Print summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    total_tests = sum(r['total'] for r in results.values())
    total_passed = sum(r['passed'] for r in results.values())
    total_failed = sum(r['failed'] for r in results.values())

    print(f"\nOverall: {total_passed}/{total_tests} passed ({total_passed*100//total_tests}%)")
    print(f"  English: {results['en']['passed']}/{results['en']['total']} passed")
    print(f"  Japanese: {results['ja']['passed']}/{results['ja']['total']} passed")
    print(f"  Chinese: {results['zh']['passed']}/{results['zh']['total']} passed")

    # Show sample successful queries
    if total_passed > 0:
        print("\n✅ Sample successful queries:\n")
        for lang, lang_name in [('en', 'English'), ('ja', 'Japanese'), ('zh', 'Chinese')]:
            if results[lang]['samples']:
                print(f"{lang_name}:")
                for sample in results[lang]['samples'][:3]:
                    word = sample['word']
                    outputs = sample['response'].get('outputs', [])
                    if outputs:
                        first = outputs[0]
                        headword = first.get('headword', '?')
                        reading = first.get('reading', '?')
                        print(f"  • '{word}' → {headword} ({reading})")
                print()

    # Report failures
    if total_failed > 0:
        print(f"\n⚠ {total_failed} failures detected")
        print("\nFirst 10 failures per language:\n")

        for lang, lang_name in [('en', 'English'), ('ja', 'Japanese'), ('zh', 'Chinese')]:
            if results[lang]['errors']:
                print(f"{lang_name} failures:")
                for error in results[lang]['errors'][:10]:
                    print(f"  • '{error['word']}': {', '.join(error['issues'])}")
                if len(results[lang]['errors']) > 10:
                    print(f"    ... and {len(results[lang]['errors']) - 10} more")
                print()
    else:
        print("\n✅ All tests passed!")

    print("=" * 70)

    return 0 if total_failed == 0 else 1

if __name__ == '__main__':
    sys.exit(run_tests())
