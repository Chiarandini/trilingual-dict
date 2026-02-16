package detector

import (
	"unicode"
)

// DetectLanguage determines the input language using Unicode range analysis
func DetectLanguage(input string) string {
	if input == "" {
		return "unknown"
	}

	hasHiragana := false
	hasKatakana := false
	hasCJK := false
	hasASCII := false

	for _, r := range input {
		switch {
		case isHiragana(r):
			hasHiragana = true
		case isKatakana(r):
			hasKatakana = true
		case isCJKUnified(r):
			hasCJK = true
		case isASCII(r):
			hasASCII = true
		}
	}

	// Detection logic: kana = Japanese, ASCII-only = English
	if hasHiragana || hasKatakana {
		return "ja"
	}

	if hasASCII && !hasCJK {
		return "en"
	}

	if hasCJK {
		// CJK without kana could be Chinese or Japanese
		// For now, treat as ambiguous (will try both)
		return "ambiguous"
	}

	return "unknown"
}

// Unicode range helpers

func isHiragana(r rune) bool {
	return r >= '\u3040' && r <= '\u309F'
}

func isKatakana(r rune) bool {
	return r >= '\u30A0' && r <= '\u30FF'
}

func isCJKUnified(r rune) bool {
	return r >= '\u4E00' && r <= '\u9FFF'
}

func isASCII(r rune) bool {
	return r >= 0x20 && r <= 0x7E
}

// IsKana returns true if the rune is hiragana or katakana
func IsKana(r rune) bool {
	return isHiragana(r) || isKatakana(r)
}

// ContainsKana returns true if the string contains any kana
func ContainsKana(s string) bool {
	for _, r := range s {
		if IsKana(r) {
			return true
		}
	}
	return false
}

// IsAllASCII returns true if the string contains only ASCII characters
func IsAllASCII(s string) bool {
	for _, r := range s {
		if !unicode.IsPrint(r) && !unicode.IsSpace(r) {
			return false
		}
		if r > unicode.MaxASCII {
			return false
		}
	}
	return true
}
