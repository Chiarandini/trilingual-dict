package ranker

import (
	"testing"

	"github.com/Chiarandini/trilingual-dict/core/types"
)

func TestRankJapanese(t *testing.T) {
	tests := []struct {
		name         string
		words        []types.JapaneseWord
		expectedTop  string // Expected top result headword
		expectEmpty  bool
	}{
		{
			name: "Common words ranked higher",
			words: []types.JapaneseWord{
				{ID: 1, Headword: "犬", IsCommon: false, FrequencyRank: nil},
				{ID: 2, Headword: "猫", IsCommon: true, FrequencyRank: intPtr(100)},
			},
			expectedTop: "猫",
		},
		{
			name: "Lower frequency rank is better",
			words: []types.JapaneseWord{
				{ID: 1, Headword: "食べる", IsCommon: true, FrequencyRank: intPtr(200)},
				{ID: 2, Headword: "猫", IsCommon: true, FrequencyRank: intPtr(100)},
			},
			expectedTop: "猫",
		},
		{
			name: "Common beats non-common even with worse frequency",
			words: []types.JapaneseWord{
				{ID: 1, Headword: "珍しい", IsCommon: false, FrequencyRank: intPtr(50)},
				{ID: 2, Headword: "猫", IsCommon: true, FrequencyRank: intPtr(100)},
			},
			expectedTop: "猫",
		},
		{
			name: "Shorter words ranked higher when equal frequency",
			words: []types.JapaneseWord{
				{ID: 1, Headword: "食べる", IsCommon: true, FrequencyRank: intPtr(100)},
				{ID: 2, Headword: "猫", IsCommon: true, FrequencyRank: intPtr(100)},
			},
			expectedTop: "猫",
		},
		{
			name: "NULL frequency ranked lower",
			words: []types.JapaneseWord{
				{ID: 1, Headword: "珍", IsCommon: false, FrequencyRank: nil},
				{ID: 2, Headword: "猫", IsCommon: true, FrequencyRank: intPtr(100)},
				{ID: 3, Headword: "犬", IsCommon: false, FrequencyRank: intPtr(150)},
			},
			expectedTop: "猫",
		},
		{
			name: "Empty list",
			words: []types.JapaneseWord{},
			expectEmpty: true,
		},
		{
			name: "Single word",
			words: []types.JapaneseWord{
				{ID: 1, Headword: "猫", IsCommon: true, FrequencyRank: intPtr(100)},
			},
			expectedTop: "猫",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := RankJapanese(tt.words)

			if tt.expectEmpty {
				if len(result) != 0 {
					t.Errorf("Expected empty result, got %d items", len(result))
				}
				return
			}

			if len(result) != 1 {
				t.Fatalf("Expected 1 result (top-ranked), got %d", len(result))
			}

			if result[0].Headword != tt.expectedTop {
				t.Errorf("Expected top result %q, got %q", tt.expectedTop, result[0].Headword)
			}
		})
	}
}

func TestRankChinese(t *testing.T) {
	tests := []struct {
		name        string
		words       []types.ChineseWord
		expectedTop string // Expected top result simplified
	}{
		{
			name: "Common words ranked higher",
			words: []types.ChineseWord{
				{ID: 1, Simplified: "狗", IsCommon: false, FrequencyRank: nil},
				{ID: 2, Simplified: "猫", IsCommon: true, FrequencyRank: intPtr(100)},
			},
			expectedTop: "猫",
		},
		{
			name: "Lower frequency rank is better",
			words: []types.ChineseWord{
				{ID: 1, Simplified: "吃", IsCommon: true, FrequencyRank: intPtr(200)},
				{ID: 2, Simplified: "猫", IsCommon: true, FrequencyRank: intPtr(100)},
			},
			expectedTop: "猫",
		},
		{
			name: "Shorter words ranked higher when equal",
			words: []types.ChineseWord{
				{ID: 1, Simplified: "喜欢", IsCommon: true, FrequencyRank: intPtr(100)},
				{ID: 2, Simplified: "猫", IsCommon: true, FrequencyRank: intPtr(100)},
			},
			expectedTop: "猫",
		},
		{
			name: "HSK 1 ranked higher than HSK 6",
			words: []types.ChineseWord{
				{ID: 1, Simplified: "挑战", IsCommon: true, FrequencyRank: intPtr(600), HSKLevel: strPtr("6")},
				{ID: 2, Simplified: "猫", IsCommon: true, FrequencyRank: intPtr(200), HSKLevel: strPtr("1")},
			},
			expectedTop: "猫",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := RankChinese(tt.words)

			if len(result) != 1 {
				t.Fatalf("Expected 1 result (top-ranked), got %d", len(result))
			}

			if result[0].Simplified != tt.expectedTop {
				t.Errorf("Expected top result %q, got %q", tt.expectedTop, result[0].Simplified)
			}
		})
	}
}

// Helper functions
func intPtr(i int) *int {
	return &i
}

func strPtr(s string) *string {
	return &s
}
