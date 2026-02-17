#!/usr/bin/env python3
"""Test dictionary with expected results for common words."""

import json
import subprocess
import sys
from pathlib import Path

DICT_CLI = Path(__file__).parent / "cmd/dict/dict"

# Test cases: English input with expected Japanese and Chinese outputs
ENGLISH_TESTS = [
    # Animals
    {"input": "cat", "ja": "猫", "ja_reading": "ねこ", "zh": "猫", "zh_reading": "māo"},
    {"input": "dog", "ja": "犬", "ja_reading": "いぬ", "zh": "狗", "zh_reading": "gǒu"},
    {"input": "bird", "ja": "鳥", "ja_reading": "とり", "zh": "鸟", "zh_reading": "niǎo"},
    {"input": "fish", "ja": "魚", "ja_reading": "さかな", "zh": "鱼", "zh_reading": "yú"},
    {"input": "horse", "ja": "馬", "ja_reading": "うま", "zh": "马", "zh_reading": "mǎ"},
    {"input": "cow", "ja": "牛", "ja_reading": "うし", "zh": "牛", "zh_reading": "niú"},
    {"input": "pig", "ja": "豚", "ja_reading": "ぶた", "zh": "猪", "zh_reading": "zhū"},
    {"input": "chicken", "ja": "鶏", "ja_reading": "にわとり", "zh": "鸡", "zh_reading": "jī"},
    {"input": "sheep", "ja": "羊", "ja_reading": "ひつじ", "zh": "羊", "zh_reading": "yáng"},
    {"input": "tiger", "ja": "虎", "ja_reading": "とら", "zh": "虎", "zh_reading": "hǔ"},

    # Body parts
    {"input": "hand", "ja": "手", "ja_reading": "て", "zh": "手", "zh_reading": "shǒu"},
    {"input": "foot", "ja": "足", "ja_reading": "あし", "zh": "脚", "zh_reading": "jiǎo"},
    {"input": "head", "ja": "頭", "ja_reading": "あたま", "zh": "头", "zh_reading": "tóu"},
    {"input": "eye", "ja": "目", "ja_reading": "め", "zh": "眼", "zh_reading": "yǎn"},
    {"input": "ear", "ja": "耳", "ja_reading": "みみ", "zh": "耳", "zh_reading": "ěr"},
    {"input": "mouth", "ja": "口", "ja_reading": "くち", "zh": "口", "zh_reading": "kǒu"},
    {"input": "nose", "ja": "鼻", "ja_reading": "はな", "zh": "鼻", "zh_reading": "bí"},
    {"input": "tooth", "ja": "歯", "ja_reading": "は", "zh": "牙", "zh_reading": "yá"},
    {"input": "heart", "ja": "心", "ja_reading": "こころ", "zh": "心", "zh_reading": "xīn"},
    {"input": "blood", "ja": "血", "ja_reading": "ち", "zh": "血", "zh_reading": "xuè"},

    # Nature
    {"input": "water", "ja": "水", "ja_reading": "みず", "zh": "水", "zh_reading": "shuǐ"},
    {"input": "fire", "ja": "火", "ja_reading": "ひ", "zh": "火", "zh_reading": "huǒ"},
    {"input": "tree", "ja": "木", "ja_reading": "き", "zh": "树", "zh_reading": "shù"},
    {"input": "mountain", "ja": "山", "ja_reading": "やま", "zh": "山", "zh_reading": "shān"},
    {"input": "river", "ja": "川", "ja_reading": "かわ", "zh": "河", "zh_reading": "hé"},
    {"input": "sun", "ja": "日", "ja_reading": "ひ", "zh": "太阳", "zh_reading": "tài yáng"},
    {"input": "moon", "ja": "月", "ja_reading": "つき", "zh": "月", "zh_reading": "yuè"},
    {"input": "star", "ja": "星", "ja_reading": "ほし", "zh": "星", "zh_reading": "xīng"},
    {"input": "rain", "ja": "雨", "ja_reading": "あめ", "zh": "雨", "zh_reading": "yǔ"},
    {"input": "wind", "ja": "風", "ja_reading": "かぜ", "zh": "风", "zh_reading": "fēng"},

    # Food & Drink
    {"input": "rice", "ja": "米", "ja_reading": "こめ", "zh": "米", "zh_reading": "mǐ"},
    {"input": "bread", "ja": "パン", "ja_reading": "パン", "zh": "面包", "zh_reading": "miàn bāo"},
    {"input": "meat", "ja": "肉", "ja_reading": "にく", "zh": "肉", "zh_reading": "ròu"},
    {"input": "egg", "ja": "卵", "ja_reading": "たまご", "zh": "蛋", "zh_reading": "dàn"},
    {"input": "milk", "ja": "乳", "ja_reading": "ちち", "zh": "奶", "zh_reading": "nǎi"},
    {"input": "tea", "ja": "茶", "ja_reading": "ちゃ", "zh": "茶", "zh_reading": "chá"},
    {"input": "wine", "ja": "酒", "ja_reading": "さけ", "zh": "酒", "zh_reading": "jiǔ"},
    {"input": "salt", "ja": "塩", "ja_reading": "しお", "zh": "盐", "zh_reading": "yán"},
    {"input": "sugar", "ja": "砂糖", "ja_reading": "さとう", "zh": "糖", "zh_reading": "táng"},
    {"input": "oil", "ja": "油", "ja_reading": "あぶら", "zh": "油", "zh_reading": "yóu"},

    # Verbs
    {"input": "eat", "ja": "食べる", "ja_reading": "たべる", "zh": "吃", "zh_reading": "chī"},
    {"input": "drink", "ja": "飲む", "ja_reading": "のむ", "zh": "喝", "zh_reading": "hē"},
    {"input": "sleep", "ja": "寝る", "ja_reading": "ねる", "zh": "睡", "zh_reading": "shuì"},
    {"input": "walk", "ja": "歩く", "ja_reading": "あるく", "zh": "走", "zh_reading": "zǒu"},
    {"input": "run", "ja": "走る", "ja_reading": "はしる", "zh": "跑", "zh_reading": "pǎo"},
    {"input": "see", "ja": "見る", "ja_reading": "みる", "zh": "看", "zh_reading": "kàn"},
    {"input": "hear", "ja": "聞く", "ja_reading": "きく", "zh": "听", "zh_reading": "tīng"},
    {"input": "speak", "ja": "話す", "ja_reading": "はなす", "zh": "说", "zh_reading": "shuō"},
    {"input": "read", "ja": "読む", "ja_reading": "よむ", "zh": "读", "zh_reading": "dú"},
    {"input": "write", "ja": "書く", "ja_reading": "かく", "zh": "写", "zh_reading": "xiě"},

    # Common objects
    {"input": "book", "ja": "本", "ja_reading": "ほん", "zh": "书", "zh_reading": "shū"},
    {"input": "door", "ja": "戸", "ja_reading": "と", "zh": "门", "zh_reading": "mén"},
    {"input": "window", "ja": "窓", "ja_reading": "まど", "zh": "窗", "zh_reading": "chuāng"},
    {"input": "table", "ja": "卓", "ja_reading": "たく", "zh": "桌", "zh_reading": "zhuō"},
    {"input": "chair", "ja": "椅子", "ja_reading": "いす", "zh": "椅子", "zh_reading": "yǐ zi"},
    {"input": "bed", "ja": "床", "ja_reading": "とこ", "zh": "床", "zh_reading": "chuáng"},
    {"input": "house", "ja": "家", "ja_reading": "いえ", "zh": "家", "zh_reading": "jiā"},
    {"input": "car", "ja": "車", "ja_reading": "くるま", "zh": "车", "zh_reading": "chē"},
    {"input": "road", "ja": "道", "ja_reading": "みち", "zh": "路", "zh_reading": "lù"},
    {"input": "bridge", "ja": "橋", "ja_reading": "はし", "zh": "桥", "zh_reading": "qiáo"},

    # People & Family
    {"input": "person", "ja": "人", "ja_reading": "ひと", "zh": "人", "zh_reading": "rén"},
    {"input": "man", "ja": "男", "ja_reading": "おとこ", "zh": "男", "zh_reading": "nán"},
    {"input": "woman", "ja": "女", "ja_reading": "おんな", "zh": "女", "zh_reading": "nǚ"},
    {"input": "child", "ja": "子", "ja_reading": "こ", "zh": "孩子", "zh_reading": "hái zi"},
    {"input": "father", "ja": "父", "ja_reading": "ちち", "zh": "父", "zh_reading": "fù"},
    {"input": "mother", "ja": "母", "ja_reading": "はは", "zh": "母", "zh_reading": "mǔ"},
    {"input": "brother", "ja": "兄弟", "ja_reading": "きょうだい", "zh": "兄弟", "zh_reading": "xiōng dì"},
    {"input": "sister", "ja": "姉妹", "ja_reading": "しまい", "zh": "姐妹", "zh_reading": "jiě mèi"},
    {"input": "friend", "ja": "友", "ja_reading": "とも", "zh": "友", "zh_reading": "yǒu"},
    {"input": "teacher", "ja": "先生", "ja_reading": "せんせい", "zh": "老师", "zh_reading": "lǎo shī"},

    # Numbers
    {"input": "one", "ja": "一", "ja_reading": "いち", "zh": "一", "zh_reading": "yī"},
    {"input": "two", "ja": "二", "ja_reading": "に", "zh": "二", "zh_reading": "èr"},
    {"input": "three", "ja": "三", "ja_reading": "さん", "zh": "三", "zh_reading": "sān"},
    {"input": "four", "ja": "四", "ja_reading": "よん", "zh": "四", "zh_reading": "sì"},
    {"input": "five", "ja": "五", "ja_reading": "ご", "zh": "五", "zh_reading": "wǔ"},
    {"input": "six", "ja": "六", "ja_reading": "ろく", "zh": "六", "zh_reading": "liù"},
    {"input": "seven", "ja": "七", "ja_reading": "しち", "zh": "七", "zh_reading": "qī"},
    {"input": "eight", "ja": "八", "ja_reading": "はち", "zh": "八", "zh_reading": "bā"},
    {"input": "nine", "ja": "九", "ja_reading": "きゅう", "zh": "九", "zh_reading": "jiǔ"},
    {"input": "ten", "ja": "十", "ja_reading": "じゅう", "zh": "十", "zh_reading": "shí"},

    # Colors
    {"input": "red", "ja": "赤", "ja_reading": "あか", "zh": "红", "zh_reading": "hóng"},
    {"input": "blue", "ja": "青", "ja_reading": "あお", "zh": "蓝", "zh_reading": "lán"},
    {"input": "white", "ja": "白", "ja_reading": "しろ", "zh": "白", "zh_reading": "bái"},
    {"input": "black", "ja": "黒", "ja_reading": "くろ", "zh": "黑", "zh_reading": "hēi"},
    {"input": "yellow", "ja": "黄", "ja_reading": "き", "zh": "黄", "zh_reading": "huáng"},
    {"input": "green", "ja": "緑", "ja_reading": "みどり", "zh": "绿", "zh_reading": "lǜ"},

    # Time
    {"input": "day", "ja": "日", "ja_reading": "ひ", "zh": "天", "zh_reading": "tiān"},
    {"input": "night", "ja": "夜", "ja_reading": "よる", "zh": "夜", "zh_reading": "yè"},
    {"input": "morning", "ja": "朝", "ja_reading": "あさ", "zh": "早晨", "zh_reading": "zǎo chén"},
    {"input": "year", "ja": "年", "ja_reading": "とし", "zh": "年", "zh_reading": "nián"},
    {"input": "month", "ja": "月", "ja_reading": "つき", "zh": "月", "zh_reading": "yuè"},
    {"input": "week", "ja": "週", "ja_reading": "しゅう", "zh": "周", "zh_reading": "zhōu"},
    {"input": "today", "ja": "今日", "ja_reading": "きょう", "zh": "今天", "zh_reading": "jīn tiān"},
    {"input": "tomorrow", "ja": "明日", "ja_reading": "あした", "zh": "明天", "zh_reading": "míng tiān"},
    {"input": "yesterday", "ja": "昨日", "ja_reading": "きのう", "zh": "昨天", "zh_reading": "zuó tiān"},

    # Adjectives
    {"input": "big", "ja": "大きい", "ja_reading": "おおきい", "zh": "大", "zh_reading": "dà"},
    {"input": "small", "ja": "小さい", "ja_reading": "ちいさい", "zh": "小", "zh_reading": "xiǎo"},
    {"input": "good", "ja": "良い", "ja_reading": "よい", "zh": "好", "zh_reading": "hǎo"},
    {"input": "bad", "ja": "悪い", "ja_reading": "わるい", "zh": "坏", "zh_reading": "huài"},
    {"input": "new", "ja": "新しい", "ja_reading": "あたらしい", "zh": "新", "zh_reading": "xīn"},
    {"input": "old", "ja": "古い", "ja_reading": "ふるい", "zh": "旧", "zh_reading": "jiù"},
]

# Japanese input tests (common kanji/words)
JAPANESE_TESTS = [
    {"input": "猫", "expected_reading": "ねこ", "expected_en": "cat"},
    {"input": "犬", "expected_reading": "いぬ", "expected_en": "dog"},
    {"input": "水", "expected_reading": "みず", "expected_en": "water"},
    {"input": "火", "expected_reading": "ひ", "expected_en": "fire"},
    {"input": "人", "expected_reading": "ひと", "expected_en": "person"},
    {"input": "日", "expected_reading": "ひ", "expected_en": "sun|day"},
    {"input": "月", "expected_reading": "つき", "expected_en": "moon|month"},
    {"input": "木", "expected_reading": "き", "expected_en": "tree|wood"},
    {"input": "金", "expected_reading": "かね", "expected_en": "money|gold"},
    {"input": "土", "expected_reading": "つち", "expected_en": "soil|earth"},
    {"input": "本", "expected_reading": "ほん", "expected_en": "book"},
    {"input": "車", "expected_reading": "くるま", "expected_en": "car"},
    {"input": "山", "expected_reading": "やま", "expected_en": "mountain"},
    {"input": "川", "expected_reading": "かわ", "expected_en": "river"},
    {"input": "学校", "expected_reading": "がっこう", "expected_en": "school"},
    {"input": "先生", "expected_reading": "せんせい", "expected_en": "teacher"},
    {"input": "学生", "expected_reading": "がくせい", "expected_en": "student"},
    {"input": "友達", "expected_reading": "ともだち", "expected_en": "friend"},
    {"input": "家", "expected_reading": "いえ", "expected_en": "house|home"},
    {"input": "国", "expected_reading": "くに", "expected_en": "country"},
]

# Chinese input tests (common characters/words)
CHINESE_TESTS = [
    {"input": "猫", "expected_pinyin": "māo", "expected_en": "cat"},
    {"input": "狗", "expected_pinyin": "gǒu", "expected_en": "dog"},
    {"input": "水", "expected_pinyin": "shuǐ", "expected_en": "water"},
    {"input": "火", "expected_pinyin": "huǒ", "expected_en": "fire"},
    {"input": "人", "expected_pinyin": "rén", "expected_en": "person"},
    {"input": "天", "expected_pinyin": "tiān", "expected_en": "day|sky"},
    {"input": "地", "expected_pinyin": "dì", "expected_en": "earth|ground"},
    {"input": "山", "expected_pinyin": "shān", "expected_en": "mountain"},
    {"input": "河", "expected_pinyin": "hé", "expected_en": "river"},
    {"input": "书", "expected_pinyin": "shū", "expected_en": "book"},
    {"input": "车", "expected_pinyin": "chē", "expected_en": "car|vehicle"},
    {"input": "家", "expected_pinyin": "jiā", "expected_en": "home|family"},
    {"input": "国", "expected_pinyin": "guó", "expected_en": "country"},
    {"input": "学校", "expected_pinyin": "xué xiào", "expected_en": "school"},
    {"input": "老师", "expected_pinyin": "lǎo shī", "expected_en": "teacher"},
    {"input": "学生", "expected_pinyin": "xué shēng", "expected_en": "student"},
    {"input": "朋友", "expected_pinyin": "péng you", "expected_en": "friend"},
    {"input": "今天", "expected_pinyin": "jīn tiān", "expected_en": "today"},
    {"input": "明天", "expected_pinyin": "míng tiān", "expected_en": "tomorrow"},
    {"input": "昨天", "expected_pinyin": "zuó tiān", "expected_en": "yesterday"},
]

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
        return None

def normalize_reading(reading):
    """Normalize reading by removing spaces and converting to lowercase."""
    if not reading:
        return ""
    return reading.replace(" ", "").lower()

def test_english_words():
    """Test English → Japanese/Chinese translations."""
    print("\n" + "=" * 70)
    print("TESTING ENGLISH WORDS")
    print("=" * 70)

    passed = 0
    failed = 0
    errors = []

    for i, test in enumerate(ENGLISH_TESTS, 1):
        word = test["input"]
        response = query_word(word)

        if not response or 'outputs' not in response:
            failed += 1
            errors.append({"word": word, "error": "No response"})
            continue

        outputs = response['outputs']

        # Find Japanese and Chinese outputs
        ja_output = next((o for o in outputs if o.get('language') == 'ja'), None)
        zh_output = next((o for o in outputs if o.get('language') == 'zh'), None)

        test_passed = True
        issues = []

        # Check Japanese
        if ja_output:
            if ja_output.get('headword') != test.get('ja'):
                issues.append(f"JA headword: expected '{test.get('ja')}', got '{ja_output.get('headword')}'")
                test_passed = False
            if normalize_reading(ja_output.get('reading')) != normalize_reading(test.get('ja_reading')):
                issues.append(f"JA reading: expected '{test.get('ja_reading')}', got '{ja_output.get('reading')}'")
                test_passed = False
        else:
            issues.append("Missing Japanese output")
            test_passed = False

        # Check Chinese
        if zh_output:
            if zh_output.get('headword') != test.get('zh'):
                issues.append(f"ZH headword: expected '{test.get('zh')}', got '{zh_output.get('headword')}'")
                test_passed = False
            if normalize_reading(zh_output.get('reading')) != normalize_reading(test.get('zh_reading')):
                issues.append(f"ZH reading: expected '{test.get('zh_reading')}', got '{zh_output.get('reading')}'")
                test_passed = False
        else:
            issues.append("Missing Chinese output")
            test_passed = False

        if test_passed:
            passed += 1
            if passed <= 10:  # Show first 10 successes
                print(f"  ✓ {word} → {test['ja']} ({test['ja_reading']}) / {test['zh']} ({test['zh_reading']})")
        else:
            failed += 1
            errors.append({"word": word, "issues": issues})

    print(f"\nResult: {passed}/{len(ENGLISH_TESTS)} passed")

    if errors and len(errors) <= 20:
        print(f"\nFailures:")
        for error in errors:
            print(f"  ✗ {error['word']}: {'; '.join(error.get('issues', [error.get('error', 'Unknown error')]))}")
    elif errors:
        print(f"\nFirst 20 failures:")
        for error in errors[:20]:
            print(f"  ✗ {error['word']}: {'; '.join(error.get('issues', [error.get('error', 'Unknown error')]))}")
        print(f"  ... and {len(errors) - 20} more failures")

    return passed, failed

def test_japanese_words():
    """Test Japanese → English translations."""
    print("\n" + "=" * 70)
    print("TESTING JAPANESE WORDS")
    print("=" * 70)

    passed = 0
    failed = 0
    errors = []

    for test in JAPANESE_TESTS:
        word = test["input"]
        response = query_word(word)

        if not response or 'outputs' not in response or len(response['outputs']) == 0:
            failed += 1
            errors.append({"word": word, "error": "No response"})
            continue

        # Get first output (should be Japanese since it's the input language)
        output = response['outputs'][0]

        test_passed = True
        issues = []

        # Check reading
        if normalize_reading(output.get('reading')) != normalize_reading(test['expected_reading']):
            issues.append(f"Reading: expected '{test['expected_reading']}', got '{output.get('reading')}'")
            test_passed = False

        # Check definition contains expected English
        definition = output.get('definition', '').lower()
        expected_options = test['expected_en'].split('|')
        if not any(opt.lower() in definition for opt in expected_options):
            issues.append(f"Definition doesn't contain expected terms: {test['expected_en']}")
            test_passed = False

        if test_passed:
            passed += 1
            if passed <= 10:
                print(f"  ✓ {word} ({output.get('reading')}) → {output.get('definition')[:40]}...")
        else:
            failed += 1
            errors.append({"word": word, "issues": issues})

    print(f"\nResult: {passed}/{len(JAPANESE_TESTS)} passed")

    if errors:
        print(f"\nFailures:")
        for error in errors[:10]:
            print(f"  ✗ {error['word']}: {'; '.join(error.get('issues', [error.get('error', 'Unknown error')]))}")

    return passed, failed

def test_chinese_words():
    """Test Chinese → English translations."""
    print("\n" + "=" * 70)
    print("TESTING CHINESE WORDS")
    print("=" * 70)

    passed = 0
    failed = 0
    errors = []

    for test in CHINESE_TESTS:
        word = test["input"]
        response = query_word(word)

        if not response or 'outputs' not in response or len(response['outputs']) == 0:
            failed += 1
            errors.append({"word": word, "error": "No response"})
            continue

        # Get first output (should be Chinese since it's the input language)
        output = response['outputs'][0]

        test_passed = True
        issues = []

        # Check pinyin
        if normalize_reading(output.get('reading')) != normalize_reading(test['expected_pinyin']):
            issues.append(f"Pinyin: expected '{test['expected_pinyin']}', got '{output.get('reading')}'")
            test_passed = False

        # Check definition contains expected English
        definition = output.get('definition', '').lower()
        expected_options = test['expected_en'].split('|')
        if not any(opt.lower() in definition for opt in expected_options):
            issues.append(f"Definition doesn't contain expected terms: {test['expected_en']}")
            test_passed = False

        if test_passed:
            passed += 1
            if passed <= 10:
                print(f"  ✓ {word} ({output.get('reading')}) → {output.get('definition')[:40]}...")
        else:
            failed += 1
            errors.append({"word": word, "issues": issues})

    print(f"\nResult: {passed}/{len(CHINESE_TESTS)} passed")

    if errors:
        print(f"\nFailures:")
        for error in errors[:10]:
            print(f"  ✗ {error['word']}: {'; '.join(error.get('issues', [error.get('error', 'Unknown error')]))}")

    return passed, failed

def main():
    print("=" * 70)
    print("DICTIONARY EXPECTED RESULTS TEST")
    print("=" * 70)
    print(f"\nCLI: {DICT_CLI}")
    print(f"English tests: {len(ENGLISH_TESTS)}")
    print(f"Japanese tests: {len(JAPANESE_TESTS)}")
    print(f"Chinese tests: {len(CHINESE_TESTS)}")

    if not DICT_CLI.exists():
        print(f"\nERROR: CLI not found at {DICT_CLI}")
        print("Please build it first: cd cmd/dict && go build -o dict")
        return 1

    # Run tests
    en_passed, en_failed = test_english_words()
    ja_passed, ja_failed = test_japanese_words()
    zh_passed, zh_failed = test_chinese_words()

    # Summary
    total_passed = en_passed + ja_passed + zh_passed
    total_tests = len(ENGLISH_TESTS) + len(JAPANESE_TESTS) + len(CHINESE_TESTS)
    total_failed = en_failed + ja_failed + zh_failed

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"\nTotal: {total_passed}/{total_tests} passed ({total_passed*100//total_tests if total_tests > 0 else 0}%)")
    print(f"  English: {en_passed}/{len(ENGLISH_TESTS)} passed")
    print(f"  Japanese: {ja_passed}/{len(JAPANESE_TESTS)} passed")
    print(f"  Chinese: {zh_passed}/{len(CHINESE_TESTS)} passed")

    if total_failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total_failed} tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
