package query

import (
	"fmt"
	"strings"

	"github.com/Chiarandini/trilingual-dict/core/database"
	"github.com/Chiarandini/trilingual-dict/core/detector"
	"github.com/Chiarandini/trilingual-dict/core/pinyin"
	"github.com/Chiarandini/trilingual-dict/core/ranker"
	"github.com/Chiarandini/trilingual-dict/core/types"
)

// Query performs triangular translation lookup
// maxResults: maximum number of results per language (0 = unlimited, default 5)
func Query(db *database.DB, input string, maxResults int) (*types.Response, error) {
	input = strings.TrimSpace(input)
	if input == "" {
		return nil, fmt.Errorf("empty query")
	}

	// Default to 5 results if not specified
	if maxResults == 0 {
		maxResults = 5
	}

	lang := detector.DetectLanguage(input)

	response := &types.Response{
		Meta: types.MetaInfo{
			InputLanguage: lang,
			Query:         input,
		},
		Outputs: []types.LanguageOutput{},
	}

	var err error
	switch lang {
	case "en":
		err = queryFromEnglish(db, input, response, maxResults)
	case "ja":
		err = queryFromJapanese(db, input, response, maxResults)
	case "zh":
		err = queryFromChinese(db, input, response, maxResults)
	case "ambiguous":
		err = queryAmbiguous(db, input, response, maxResults)
	default:
		return nil, fmt.Errorf("unsupported language: %s", lang)
	}

	return response, err
}

// queryFromEnglish searches from English to Japanese and Chinese
func queryFromEnglish(db *database.DB, input string, response *types.Response, maxResults int) error {
	// Query Japanese
	jaWords, err := db.QueryJapaneseByEnglish(input)
	if err != nil {
		return fmt.Errorf("japanese query failed: %w", err)
	}

	jaWords = ranker.RankJapanese(jaWords, maxResults)
	for _, w := range jaWords {
		output := japaneseToOutput(w)
		response.Outputs = append(response.Outputs, output)
	}

	// Query Chinese
	zhWords, err := db.QueryChineseByEnglish(input)
	if err != nil {
		return fmt.Errorf("chinese query failed: %w", err)
	}

	zhWords = ranker.RankChinese(zhWords, maxResults)
	for _, w := range zhWords {
		output := chineseToOutput(w)
		response.Outputs = append(response.Outputs, output)
	}

	return nil
}

// queryFromJapanese searches from Japanese to English and Chinese (via English pivot)
func queryFromJapanese(db *database.DB, input string, response *types.Response, maxResults int) error {
	// Direct lookup in Japanese
	jaWords, err := db.QueryJapanese(input, input)
	if err != nil {
		return fmt.Errorf("japanese query failed: %w", err)
	}

	jaWords = ranker.RankJapanese(jaWords, maxResults)
	if len(jaWords) == 0 {
		return nil
	}

	// Add all Japanese results
	for _, jaWord := range jaWords {
		response.Outputs = append(response.Outputs, japaneseToOutput(jaWord))
	}

	// Get English glosses from top result for pivot
	var englishGlosses []string
	for _, def := range jaWords[0].Definitions {
		englishGlosses = append(englishGlosses, def.EnglishGloss)
	}

	// Use first English gloss to find Chinese
	if len(englishGlosses) > 0 {
		zhWords, err := db.QueryChineseByEnglish(englishGlosses[0])
		if err != nil {
			return fmt.Errorf("chinese pivot query failed: %w", err)
		}

		zhWords = ranker.RankChinese(zhWords, maxResults)
		for _, w := range zhWords {
			output := chineseToOutput(w)
			response.Outputs = append(response.Outputs, output)
		}
	}

	return nil
}

// queryFromChinese searches from Chinese to English and Japanese (via English pivot)
func queryFromChinese(db *database.DB, input string, response *types.Response, maxResults int) error {
	// Direct lookup in Chinese
	zhWords, err := db.QueryChinese(input)
	if err != nil {
		return fmt.Errorf("chinese query failed: %w", err)
	}

	zhWords = ranker.RankChinese(zhWords, maxResults)
	if len(zhWords) == 0 {
		return nil
	}

	// Add all Chinese results
	for _, zhWord := range zhWords {
		response.Outputs = append(response.Outputs, chineseToOutput(zhWord))
	}

	// Get English glosses from top result for pivot
	var englishGlosses []string
	for _, def := range zhWords[0].Definitions {
		englishGlosses = append(englishGlosses, def.EnglishGloss)
	}

	// Use first English gloss to find Japanese
	if len(englishGlosses) > 0 {
		jaWords, err := db.QueryJapaneseByEnglish(englishGlosses[0])
		if err != nil {
			return fmt.Errorf("japanese pivot query failed: %w", err)
		}

		jaWords = ranker.RankJapanese(jaWords, maxResults)
		for _, w := range jaWords {
			output := japaneseToOutput(w)
			response.Outputs = append(response.Outputs, output)
		}
	}

	return nil
}

// queryAmbiguous tries both Japanese and Chinese
func queryAmbiguous(db *database.DB, input string, response *types.Response, maxResults int) error {
	// Try Japanese first
	jaWords, err := db.QueryJapanese(input, input)
	if err != nil {
		return fmt.Errorf("japanese query failed: %w", err)
	}

	// Try Chinese
	zhWords, err := db.QueryChinese(input)
	if err != nil {
		return fmt.Errorf("chinese query failed: %w", err)
	}

	// If we have results from both, it's truly ambiguous
	// Process as Japanese if found
	if len(jaWords) > 0 {
		return queryFromJapanese(db, input, response, maxResults)
	}

	// Otherwise try Chinese
	if len(zhWords) > 0 {
		return queryFromChinese(db, input, response, maxResults)
	}

	return nil
}

// Helper functions to convert database types to output types

func japaneseToOutput(w types.JapaneseWord) types.LanguageOutput {
	// Combine all definitions
	var definitions []string
	for _, def := range w.Definitions {
		definitions = append(definitions, def.EnglishGloss)
	}
	definition := strings.Join(definitions, "; ")

	output := types.LanguageOutput{
		Language:   "ja",
		Headword:   w.Headword,
		Reading:    w.Reading,
		Definition: definition,
		Examples:   w.Examples,
	}

	// Add audio info
	output.Audio = &types.AudioInfo{
		Type:   "tts",
		Text:   w.Headword,
		Locale: "ja-JP",
	}

	// Add frequency rank if available
	if w.FrequencyRank != nil {
		output.Rank = *w.FrequencyRank
	}

	// Add kanji metadata
	meta := types.KanjiMeta{}
	if w.JLPTLevel != nil {
		meta.JLPTLevel = *w.JLPTLevel
	}
	if w.StrokeCount != nil {
		meta.StrokeCount = *w.StrokeCount
	}
	if w.Components != nil {
		meta.Components = *w.Components
	}
	if w.StrokeSVG != nil {
		meta.StrokeSVG = *w.StrokeSVG
	}
	output.Meta = meta

	return output
}

func chineseToOutput(w types.ChineseWord) types.LanguageOutput {
	// Combine all definitions
	var definitions []string
	for _, def := range w.Definitions {
		definitions = append(definitions, def.EnglishGloss)
	}
	definition := strings.Join(definitions, "; ")

	output := types.LanguageOutput{
		Language:   "zh",
		Headword:   w.Simplified,
		Reading:    pinyin.NumberedToTones(w.Pinyin), // Convert numbered pinyin to tone marks
		Definition: definition,
		Examples:   w.Examples,
	}

	// Add audio info
	output.Audio = &types.AudioInfo{
		Type:   "tts",
		Text:   w.Simplified,
		Locale: "zh-CN",
	}

	// Add frequency rank if available
	if w.FrequencyRank != nil {
		output.Rank = *w.FrequencyRank
	}

	// Add hanzi metadata
	meta := types.HanziMeta{
		Traditional: w.Traditional,
	}
	if w.HSKLevel != nil {
		meta.HSKLevel = *w.HSKLevel
	}
	if w.StrokeCount != nil {
		meta.StrokeCount = *w.StrokeCount
	}
	if w.Components != nil {
		meta.Components = *w.Components
	}
	if w.Decomposition != nil {
		meta.Decomposition = *w.Decomposition
	}
	if w.StrokeSVG != nil {
		meta.StrokeSVG = *w.StrokeSVG
	}
	output.Meta = meta

	return output
}
