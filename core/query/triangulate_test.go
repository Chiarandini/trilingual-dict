package query

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/Chiarandini/trilingual-dict/core/database"
	"github.com/Chiarandini/trilingual-dict/core/types"
)

func TestQuery(t *testing.T) {
	// Find sample database
	dbPath := findSampleDatabase(t)
	if dbPath == "" {
		t.Skip("Sample database not found - run: cd data/sample && python3 generate_samples.py")
	}

	db, err := database.Open(dbPath)
	if err != nil {
		t.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	tests := []struct {
		name           string
		input          string
		wantLang       string
		wantOutputs    int
		checkJapanese  bool
		checkChinese   bool
		checkEnglish   bool
	}{
		{
			name:          "English to both",
			input:         "cat",
			wantLang:      "en",
			wantOutputs:   2,
			checkJapanese: true,
			checkChinese:  true,
		},
		{
			name:          "Japanese to English and Chinese",
			input:         "猫",
			wantLang:      "ambiguous",
			wantOutputs:   2,
			checkJapanese: true,
			checkChinese:  true,
		},
		{
			name:          "Japanese reading",
			input:         "ねこ",
			wantLang:      "ja",
			wantOutputs:   2,
			checkJapanese: true,
			checkChinese:  true,
		},
		{
			name:         "English word not in database",
			input:        "xylophone",
			wantLang:     "en",
			wantOutputs:  0,
		},
		{
			name:        "Empty query",
			input:       "",
			wantLang:    "",
			wantOutputs: -1, // Error case
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := Query(db, tt.input)

			if tt.wantOutputs == -1 {
				// Expect error
				if err == nil {
					t.Errorf("Expected error for input %q, got none", tt.input)
				}
				return
			}

			if err != nil {
				t.Fatalf("Query(%q) returned error: %v", tt.input, err)
			}

			// Check metadata
			if result.Meta.InputLanguage != tt.wantLang {
				t.Errorf("Language = %q, want %q", result.Meta.InputLanguage, tt.wantLang)
			}

			if result.Meta.Query != tt.input {
				t.Errorf("Query = %q, want %q", result.Meta.Query, tt.input)
			}

			// Check outputs
			if len(result.Outputs) != tt.wantOutputs {
				t.Errorf("Got %d outputs, want %d", len(result.Outputs), tt.wantOutputs)
			}

			// Check output languages
			if tt.checkJapanese {
				hasJapanese := false
				for _, output := range result.Outputs {
					if output.Language == "ja" {
						hasJapanese = true
						validateJapaneseOutput(t, output)
					}
				}
				if !hasJapanese {
					t.Errorf("Expected Japanese output, got none")
				}
			}

			if tt.checkChinese {
				hasChinese := false
				for _, output := range result.Outputs {
					if output.Language == "zh" {
						hasChinese = true
						validateChineseOutput(t, output)
					}
				}
				if !hasChinese {
					t.Errorf("Expected Chinese output, got none")
				}
			}
		})
	}
}

func TestQueryFromEnglish(t *testing.T) {
	dbPath := findSampleDatabase(t)
	if dbPath == "" {
		t.Skip("Sample database not found")
	}

	db, err := database.Open(dbPath)
	if err != nil {
		t.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	response := &types.Response{
		Meta:    types.MetaInfo{},
		Outputs: []types.LanguageOutput{},
	}

	err = queryFromEnglish(db, "cat", response)
	if err != nil {
		t.Fatalf("queryFromEnglish failed: %v", err)
	}

	if len(response.Outputs) == 0 {
		t.Error("Expected outputs, got none")
	}

	// Should have both Japanese and Chinese
	hasJA := false
	hasZH := false
	for _, output := range response.Outputs {
		if output.Language == "ja" {
			hasJA = true
		}
		if output.Language == "zh" {
			hasZH = true
		}
	}

	if !hasJA {
		t.Error("Missing Japanese output")
	}
	if !hasZH {
		t.Error("Missing Chinese output")
	}
}

func TestQueryFromJapanese(t *testing.T) {
	dbPath := findSampleDatabase(t)
	if dbPath == "" {
		t.Skip("Sample database not found")
	}

	db, err := database.Open(dbPath)
	if err != nil {
		t.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	response := &types.Response{
		Meta:    types.MetaInfo{},
		Outputs: []types.LanguageOutput{},
	}

	err = queryFromJapanese(db, "ねこ", response)
	if err != nil {
		t.Fatalf("queryFromJapanese failed: %v", err)
	}

	if len(response.Outputs) == 0 {
		t.Error("Expected outputs, got none")
	}

	// First output should be Japanese (direct match)
	if response.Outputs[0].Language != "ja" {
		t.Errorf("First output should be Japanese, got %q", response.Outputs[0].Language)
	}

	// Should also have Chinese (via pivot)
	hasZH := false
	for _, output := range response.Outputs {
		if output.Language == "zh" {
			hasZH = true
		}
	}
	if !hasZH {
		t.Error("Missing Chinese output (triangulation failed)")
	}
}

func TestQueryFromChinese(t *testing.T) {
	dbPath := findSampleDatabase(t)
	if dbPath == "" {
		t.Skip("Sample database not found")
	}

	db, err := database.Open(dbPath)
	if err != nil {
		t.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	response := &types.Response{
		Meta:    types.MetaInfo{},
		Outputs: []types.LanguageOutput{},
	}

	err = queryFromChinese(db, "猫", response)
	if err != nil {
		t.Fatalf("queryFromChinese failed: %v", err)
	}

	if len(response.Outputs) == 0 {
		t.Error("Expected outputs, got none")
	}

	// First output should be Chinese (direct match)
	if response.Outputs[0].Language != "zh" {
		t.Errorf("First output should be Chinese, got %q", response.Outputs[0].Language)
	}
}

// Helper functions

func findSampleDatabase(t *testing.T) string {
	// Try multiple possible locations
	candidates := []string{
		"../../data/dictionary.db",
		"../../data/sample/dictionary.db",
		"../../../data/dictionary.db",
		"../../../data/sample/dictionary.db",
	}

	for _, path := range candidates {
		absPath, _ := filepath.Abs(path)
		if _, err := os.Stat(absPath); err == nil {
			return absPath
		}
	}

	return ""
}

func validateJapaneseOutput(t *testing.T, output types.LanguageOutput) {
	if output.Headword == "" {
		t.Error("Japanese output missing headword")
	}
	if output.Reading == "" {
		t.Error("Japanese output missing reading")
	}
	if output.Definition == "" {
		t.Error("Japanese output missing definition")
	}
	if output.Audio == nil {
		t.Error("Japanese output missing audio info")
	} else {
		if output.Audio.Locale != "ja-JP" {
			t.Errorf("Japanese audio locale = %q, want ja-JP", output.Audio.Locale)
		}
	}
}

func validateChineseOutput(t *testing.T, output types.LanguageOutput) {
	if output.Headword == "" {
		t.Error("Chinese output missing headword (simplified)")
	}
	if output.Reading == "" {
		t.Error("Chinese output missing reading (pinyin)")
	}
	if output.Definition == "" {
		t.Error("Chinese output missing definition")
	}
	if output.Audio == nil {
		t.Error("Chinese output missing audio info")
	} else {
		if output.Audio.Locale != "zh-CN" {
			t.Errorf("Chinese audio locale = %q, want zh-CN", output.Audio.Locale)
		}
	}
}
