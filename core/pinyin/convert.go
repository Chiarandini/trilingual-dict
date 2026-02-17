package pinyin

import (
	"regexp"
	"strings"
)

// Tone mark mappings for each vowel
var toneMark = map[rune][]rune{
	'a': {'ā', 'á', 'ǎ', 'à', 'a'},
	'e': {'ē', 'é', 'ě', 'è', 'e'},
	'i': {'ī', 'í', 'ǐ', 'ì', 'i'},
	'o': {'ō', 'ó', 'ǒ', 'ò', 'o'},
	'u': {'ū', 'ú', 'ǔ', 'ù', 'u'},
	'ü': {'ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü'},
	'A': {'Ā', 'Á', 'Ǎ', 'À', 'A'},
	'E': {'Ē', 'É', 'Ě', 'È', 'E'},
	'I': {'Ī', 'Í', 'Ǐ', 'Ì', 'I'},
	'O': {'Ō', 'Ó', 'Ǒ', 'Ò', 'O'},
	'U': {'Ū', 'Ú', 'Ǔ', 'Ù', 'U'},
	'Ü': {'Ǖ', 'Ǘ', 'Ǚ', 'Ǜ', 'Ü'},
}

// NumberedToTones converts numbered pinyin (e.g., "ni3 hao3") to tone-marked pinyin (e.g., "nǐ hǎo")
func NumberedToTones(numbered string) string {
	// Pattern matches syllables with tone numbers: word characters followed by 1-5
	re := regexp.MustCompile(`([a-züÜ]+)([1-5])`)

	result := re.ReplaceAllStringFunc(numbered, func(match string) string {
		// Extract the syllable and tone number
		parts := re.FindStringSubmatch(match)
		if len(parts) != 3 {
			return match
		}

		syllable := parts[1]
		toneNum := parts[2][0] - '0' // Convert ASCII digit to int (1-5)

		// Apply tone to the appropriate vowel
		return applyTone(syllable, int(toneNum))
	})

	return result
}

// applyTone applies the tone mark to the correct vowel in a syllable
// Rules for tone placement:
// 1. If 'a' or 'e' is present, it takes the tone
// 2. If 'ou' is present, 'o' takes the tone
// 3. Otherwise, the last vowel takes the tone
func applyTone(syllable string, tone int) string {
	if tone < 1 || tone > 5 {
		return syllable
	}

	runes := []rune(syllable)
	toneIndex := -1

	// Find the vowel that should receive the tone mark
	for i, r := range runes {
		lower := strings.ToLower(string(r))

		// Rule 1: 'a' or 'e' always gets the tone
		if lower == "a" || lower == "e" {
			toneIndex = i
			break
		}

		// Rule 2: in 'ou', 'o' gets the tone
		if lower == "o" && i+1 < len(runes) && strings.ToLower(string(runes[i+1])) == "u" {
			toneIndex = i
			break
		}
	}

	// Rule 3: If no 'a', 'e', or 'ou', find the last vowel
	if toneIndex == -1 {
		for i := len(runes) - 1; i >= 0; i-- {
			r := runes[i]
			if isVowel(r) {
				toneIndex = i
				break
			}
		}
	}

	// Apply the tone mark
	if toneIndex != -1 && toneIndex < len(runes) {
		vowel := runes[toneIndex]
		if marks, ok := toneMark[vowel]; ok && tone-1 < len(marks) {
			runes[toneIndex] = marks[tone-1]
		}
	}

	return string(runes)
}

// isVowel checks if a rune is a vowel (including ü)
func isVowel(r rune) bool {
	lower := strings.ToLower(string(r))
	return lower == "a" || lower == "e" || lower == "i" ||
	       lower == "o" || lower == "u" || lower == "ü"
}
