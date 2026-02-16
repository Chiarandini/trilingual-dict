package types

// Response is the top-level structure returned by all query operations
type Response struct {
	Meta    MetaInfo         `json:"meta"`
	Outputs []LanguageOutput `json:"outputs"`
}

// MetaInfo contains query metadata
type MetaInfo struct {
	InputLanguage string `json:"input_language"`
	Query         string `json:"query"`
}

// LanguageOutput represents results for a single language
type LanguageOutput struct {
	Language   string      `json:"language"`
	Headword   string      `json:"headword"`
	Reading    string      `json:"reading,omitempty"`
	Definition string      `json:"definition"`
	Rank       int         `json:"rank,omitempty"`
	Audio      *AudioInfo  `json:"audio,omitempty"`
	Meta       interface{} `json:"meta,omitempty"`
	Examples   []Example   `json:"examples,omitempty"`
}

// AudioInfo provides text-to-speech information
type AudioInfo struct {
	Type   string `json:"type"` // "tts"
	Text   string `json:"text"`
	Locale string `json:"locale"`
}

// Example represents a usage example
type Example struct {
	SourceText  string `json:"source_text"`
	EnglishText string `json:"english_text"`
}

// KanjiMeta contains Japanese character metadata
type KanjiMeta struct {
	JLPTLevel   string `json:"jlpt_level,omitempty"`
	StrokeCount int    `json:"stroke_count,omitempty"`
	Components  string `json:"components,omitempty"`
	StrokeSVG   string `json:"stroke_svg,omitempty"`
}

// HanziMeta contains Chinese character metadata
type HanziMeta struct {
	Traditional   string `json:"traditional,omitempty"`
	HSKLevel      string `json:"hsk_level,omitempty"`
	StrokeCount   int    `json:"stroke_count,omitempty"`
	Components    string `json:"components,omitempty"`
	Decomposition string `json:"decomposition,omitempty"`
	StrokeSVG     string `json:"stroke_svg,omitempty"`
}

// Internal database types

// JapaneseWord represents a row from japanese_words table
type JapaneseWord struct {
	ID            int
	Headword      string
	Reading       string
	IsCommon      bool
	FrequencyRank *int
	JLPTLevel     *string
	StrokeCount   *int
	Components    *string
	StrokeSVG     *string
	Definitions   []JapaneseDefinition
	Examples      []Example
}

// JapaneseDefinition represents a row from japanese_definitions table
type JapaneseDefinition struct {
	ID           int
	WordID       int
	EnglishGloss string
	POS          *string
}

// ChineseWord represents a row from chinese_words table
type ChineseWord struct {
	ID            int
	Simplified    string
	Traditional   string
	Pinyin        string
	IsCommon      bool
	FrequencyRank *int
	HSKLevel      *string
	StrokeCount   *int
	Components    *string
	Decomposition *string
	StrokeSVG     *string
	Definitions   []ChineseDefinition
	Examples      []Example
}

// ChineseDefinition represents a row from chinese_definitions table
type ChineseDefinition struct {
	ID           int
	WordID       int
	EnglishGloss string
}
