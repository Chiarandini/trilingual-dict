package detector

import (
	"testing"
)

func TestDetectLanguage(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		// ASCII/English
		{"English word", "cat", "en"},
		{"English phrase", "hello world", "en"},
		{"English with punctuation", "Hello, world!", "en"},
		{"Numbers only", "12345", "en"},
		{"Empty string", "", "unknown"},
		{"Whitespace only", "   ", "en"},

		// Japanese - Hiragana
		{"Hiragana only", "ねこ", "ja"},
		{"Hiragana word", "たべる", "ja"},
		{"Hiragana with kanji", "食べる", "ja"},

		// Japanese - Katakana
		{"Katakana only", "カタカナ", "ja"},
		{"Katakana word", "コンピュータ", "ja"},

		// Japanese - Mixed
		{"Mixed kana and kanji", "猫はかわいい", "ja"},
		{"Kanji with hiragana okurigana", "飲む", "ja"},

		// Chinese
		{"Chinese simplified", "猫", "ambiguous"}, // Could be Japanese or Chinese
		{"Chinese word", "吃", "ambiguous"},
		{"Chinese phrase", "你好", "ambiguous"},
		{"Chinese sentence", "我喜欢猫", "ambiguous"},

		// Ambiguous cases
		{"Single kanji/hanzi", "日", "ambiguous"},
		{"Common CJK character", "学", "ambiguous"},

		// Edge cases
		{"Mixed English and hiragana", "hello ねこ", "ja"}, // Has kana, so Japanese
		{"Mixed English and CJK", "hello 猫", "ambiguous"},
		{"Japanese reading", "いぬ", "ja"},
		{"Katakana loanword", "テスト", "ja"},

		// Special characters
		{"Japanese with space", "猫 です", "ja"},
		{"Chinese with numbers", "第1课", "ambiguous"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := DetectLanguage(tt.input)
			if result != tt.expected {
				t.Errorf("DetectLanguage(%q) = %q, want %q", tt.input, result, tt.expected)
			}
		})
	}
}

func TestDetectLanguageBoundaries(t *testing.T) {
	// Test exact Unicode range boundaries
	tests := []struct {
		name     string
		char     rune
		expected string
	}{
		// Hiragana boundaries
		{"Hiragana start", '\u3040', "ja"},
		{"Hiragana middle", '\u3070', "ja"},
		{"Hiragana end", '\u309F', "ja"},

		// Katakana boundaries
		{"Katakana start", '\u30A0', "ja"},
		{"Katakana middle", '\u30C0', "ja"},
		{"Katakana end", '\u30FF', "ja"},

		// CJK Unified boundaries
		{"CJK start", '\u4E00', "ambiguous"},
		{"CJK middle", '\u7530', "ambiguous"},
		{"CJK end", '\u9FFF', "ambiguous"},

		// ASCII boundaries
		{"ASCII space", '\u0020', "en"},
		{"ASCII letter", '\u0041', "en"},
		{"ASCII tilde", '\u007E', "en"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := DetectLanguage(string(tt.char))
			if result != tt.expected {
				t.Errorf("DetectLanguage(%q) = %q, want %q", string(tt.char), result, tt.expected)
			}
		})
	}
}

func TestDetectLanguageConsistency(t *testing.T) {
	// Same input should always return same result
	inputs := []string{"cat", "猫", "ねこ", "你好", "hello world"}

	for _, input := range inputs {
		result1 := DetectLanguage(input)
		result2 := DetectLanguage(input)

		if result1 != result2 {
			t.Errorf("DetectLanguage(%q) not consistent: got %q and %q", input, result1, result2)
		}
	}
}
