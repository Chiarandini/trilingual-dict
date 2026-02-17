package ranker

import (
	"sort"

	"github.com/Chiarandini/trilingual-dict/core/types"
)

// RankJapanese sorts Japanese words by priority and returns the top results
// maxResults: maximum number of results to return (0 = unlimited)
func RankJapanese(words []types.JapaneseWord, maxResults int) []types.JapaneseWord {
	if len(words) == 0 {
		return words
	}

	// Sort by priority
	sort.Slice(words, func(i, j int) bool {
		return japaneseScore(words[i]) > japaneseScore(words[j])
	})

	// Return top N results
	if maxResults <= 0 || maxResults >= len(words) {
		return words
	}
	return words[:maxResults]
}

// RankChinese sorts Chinese words by priority and returns the top results
// maxResults: maximum number of results to return (0 = unlimited)
func RankChinese(words []types.ChineseWord, maxResults int) []types.ChineseWord {
	if len(words) == 0 {
		return words
	}

	// Sort by priority
	sort.Slice(words, func(i, j int) bool {
		return chineseScore(words[i]) > chineseScore(words[j])
	})

	// Return top N results
	if maxResults <= 0 || maxResults >= len(words) {
		return words
	}
	return words[:maxResults]
}

// japaneseScore calculates priority score for a Japanese word
// Higher score = better match
func japaneseScore(w types.JapaneseWord) int {
	score := 0

	// Common words get priority
	if w.IsCommon {
		score += 100
	}

	// Frequency rank (lower rank = more common = higher score)
	if w.FrequencyRank != nil {
		// Invert rank: rank 1 = 1000 points, rank 1000 = 1 point
		score += max(0, 1000-*w.FrequencyRank)
	}

	// Shorter words are often more basic
	headwordLen := len([]rune(w.Headword))
	if headwordLen > 0 {
		score += 100 / headwordLen
	}

	return score
}

// chineseScore calculates priority score for a Chinese word
func chineseScore(w types.ChineseWord) int {
	score := 0

	// Common words get priority
	if w.IsCommon {
		score += 100
	}

	// Frequency rank
	if w.FrequencyRank != nil {
		score += max(0, 1000-*w.FrequencyRank)
	}

	// Shorter words are often more basic
	charLen := len([]rune(w.Simplified))
	if charLen > 0 {
		score += 100 / charLen
	}

	return score
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}
