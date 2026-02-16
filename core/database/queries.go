package database

import (
	"database/sql"
	"fmt"
	"strings"

	"github.com/trilingual-dict/core/types"
)

// QueryJapanese searches for Japanese words by headword or reading
func (db *DB) QueryJapanese(headword, reading string) ([]types.JapaneseWord, error) {
	query := `
		SELECT id, headword, reading, is_common, frequency_rank, jlpt_level,
		       stroke_count, components, stroke_svg
		FROM japanese_words
		WHERE headword = ? OR reading = ?
		ORDER BY is_common DESC, frequency_rank ASC
	`

	rows, err := db.conn.Query(query, headword, reading)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return db.scanJapaneseWords(rows)
}

// QueryJapaneseByEnglish searches for Japanese words by English gloss
func (db *DB) QueryJapaneseByEnglish(gloss string) ([]types.JapaneseWord, error) {
	query := `
		SELECT DISTINCT w.id, w.headword, w.reading, w.is_common, w.frequency_rank,
		       w.jlpt_level, w.stroke_count, w.components, w.stroke_svg
		FROM japanese_words w
		JOIN japanese_definitions d ON w.id = d.word_id
		WHERE d.english_gloss LIKE ?
		ORDER BY w.is_common DESC, w.frequency_rank ASC
	`

	searchTerm := "%" + strings.ToLower(gloss) + "%"
	rows, err := db.conn.Query(query, searchTerm)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return db.scanJapaneseWords(rows)
}

// QueryChinese searches for Chinese words by simplified form
func (db *DB) QueryChinese(simplified string) ([]types.ChineseWord, error) {
	query := `
		SELECT id, simplified, traditional, pinyin, is_common, frequency_rank,
		       hsk_level, stroke_count, components, decomposition, stroke_svg
		FROM chinese_words
		WHERE simplified = ?
		ORDER BY is_common DESC, frequency_rank ASC
	`

	rows, err := db.conn.Query(query, simplified)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return db.scanChineseWords(rows)
}

// QueryChineseByEnglish searches for Chinese words by English gloss
func (db *DB) QueryChineseByEnglish(gloss string) ([]types.ChineseWord, error) {
	query := `
		SELECT DISTINCT w.id, w.simplified, w.traditional, w.pinyin, w.is_common,
		       w.frequency_rank, w.hsk_level, w.stroke_count, w.components,
		       w.decomposition, w.stroke_svg
		FROM chinese_words w
		JOIN chinese_definitions d ON w.id = d.word_id
		WHERE d.english_gloss LIKE ?
		ORDER BY w.is_common DESC, w.frequency_rank ASC
	`

	searchTerm := "%" + strings.ToLower(gloss) + "%"
	rows, err := db.conn.Query(query, searchTerm)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return db.scanChineseWords(rows)
}

// GetJapaneseDefinitions retrieves all definitions for a Japanese word
func (db *DB) GetJapaneseDefinitions(wordID int) ([]types.JapaneseDefinition, error) {
	query := `
		SELECT id, word_id, english_gloss, pos
		FROM japanese_definitions
		WHERE word_id = ?
	`

	rows, err := db.conn.Query(query, wordID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var defs []types.JapaneseDefinition
	for rows.Next() {
		var def types.JapaneseDefinition
		var pos sql.NullString
		err := rows.Scan(&def.ID, &def.WordID, &def.EnglishGloss, &pos)
		if err != nil {
			return nil, err
		}
		if pos.Valid {
			def.POS = &pos.String
		}
		defs = append(defs, def)
	}

	return defs, rows.Err()
}

// GetChineseDefinitions retrieves all definitions for a Chinese word
func (db *DB) GetChineseDefinitions(wordID int) ([]types.ChineseDefinition, error) {
	query := `
		SELECT id, word_id, english_gloss
		FROM chinese_definitions
		WHERE word_id = ?
	`

	rows, err := db.conn.Query(query, wordID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var defs []types.ChineseDefinition
	for rows.Next() {
		var def types.ChineseDefinition
		err := rows.Scan(&def.ID, &def.WordID, &def.EnglishGloss)
		if err != nil {
			return nil, err
		}
		defs = append(defs, def)
	}

	return defs, rows.Err()
}

// GetExamples retrieves examples for a word
func (db *DB) GetExamples(language string, wordID int) ([]types.Example, error) {
	query := `
		SELECT source_text, english_text
		FROM examples
		WHERE language = ? AND word_id = ?
		LIMIT 5
	`

	rows, err := db.conn.Query(query, language, wordID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var examples []types.Example
	for rows.Next() {
		var ex types.Example
		err := rows.Scan(&ex.SourceText, &ex.EnglishText)
		if err != nil {
			return nil, err
		}
		examples = append(examples, ex)
	}

	return examples, rows.Err()
}

// Helper functions

func (db *DB) scanJapaneseWords(rows *sql.Rows) ([]types.JapaneseWord, error) {
	var words []types.JapaneseWord

	for rows.Next() {
		var w types.JapaneseWord
		var freqRank, strokeCount sql.NullInt64
		var jlptLevel, components, strokeSVG sql.NullString

		err := rows.Scan(
			&w.ID, &w.Headword, &w.Reading, &w.IsCommon,
			&freqRank, &jlptLevel, &strokeCount, &components, &strokeSVG,
		)
		if err != nil {
			return nil, err
		}

		if freqRank.Valid {
			rank := int(freqRank.Int64)
			w.FrequencyRank = &rank
		}
		if jlptLevel.Valid {
			w.JLPTLevel = &jlptLevel.String
		}
		if strokeCount.Valid {
			count := int(strokeCount.Int64)
			w.StrokeCount = &count
		}
		if components.Valid {
			w.Components = &components.String
		}
		if strokeSVG.Valid {
			w.StrokeSVG = &strokeSVG.String
		}

		// Load definitions
		defs, err := db.GetJapaneseDefinitions(w.ID)
		if err != nil {
			return nil, fmt.Errorf("failed to load definitions for word %d: %w", w.ID, err)
		}
		w.Definitions = defs

		// Load examples
		examples, err := db.GetExamples("ja", w.ID)
		if err != nil {
			return nil, fmt.Errorf("failed to load examples for word %d: %w", w.ID, err)
		}
		w.Examples = examples

		words = append(words, w)
	}

	return words, rows.Err()
}

func (db *DB) scanChineseWords(rows *sql.Rows) ([]types.ChineseWord, error) {
	var words []types.ChineseWord

	for rows.Next() {
		var w types.ChineseWord
		var freqRank, strokeCount sql.NullInt64
		var hskLevel, components, decomposition, strokeSVG sql.NullString

		err := rows.Scan(
			&w.ID, &w.Simplified, &w.Traditional, &w.Pinyin, &w.IsCommon,
			&freqRank, &hskLevel, &strokeCount, &components, &decomposition, &strokeSVG,
		)
		if err != nil {
			return nil, err
		}

		if freqRank.Valid {
			rank := int(freqRank.Int64)
			w.FrequencyRank = &rank
		}
		if hskLevel.Valid {
			w.HSKLevel = &hskLevel.String
		}
		if strokeCount.Valid {
			count := int(strokeCount.Int64)
			w.StrokeCount = &count
		}
		if components.Valid {
			w.Components = &components.String
		}
		if decomposition.Valid {
			w.Decomposition = &decomposition.String
		}
		if strokeSVG.Valid {
			w.StrokeSVG = &strokeSVG.String
		}

		// Load definitions
		defs, err := db.GetChineseDefinitions(w.ID)
		if err != nil {
			return nil, fmt.Errorf("failed to load definitions for word %d: %w", w.ID, err)
		}
		w.Definitions = defs

		// Load examples
		examples, err := db.GetExamples("zh", w.ID)
		if err != nil {
			return nil, fmt.Errorf("failed to load examples for word %d: %w", w.ID, err)
		}
		w.Examples = examples

		words = append(words, w)
	}

	return words, rows.Err()
}
