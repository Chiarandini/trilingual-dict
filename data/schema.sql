-- Trilingual Dictionary Schema
-- Optimized for triangular translation with English as pivot

CREATE TABLE IF NOT EXISTS japanese_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    headword TEXT NOT NULL,
    reading TEXT NOT NULL,
    is_common BOOLEAN DEFAULT 0,
    frequency_rank INTEGER,
    jlpt_level TEXT,
    stroke_count INTEGER,
    components TEXT,
    stroke_svg TEXT
);

CREATE TABLE IF NOT EXISTS japanese_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    english_gloss TEXT NOT NULL,
    pos TEXT,
    FOREIGN KEY (word_id) REFERENCES japanese_words(id)
);

CREATE TABLE IF NOT EXISTS chinese_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simplified TEXT NOT NULL,
    traditional TEXT NOT NULL,
    pinyin TEXT NOT NULL,
    is_common BOOLEAN DEFAULT 0,
    frequency_rank INTEGER,
    hsk_level TEXT,
    stroke_count INTEGER,
    components TEXT,
    decomposition TEXT,
    stroke_svg TEXT
);

CREATE TABLE IF NOT EXISTS chinese_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    english_gloss TEXT NOT NULL,
    FOREIGN KEY (word_id) REFERENCES chinese_words(id)
);

CREATE TABLE IF NOT EXISTS examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language TEXT NOT NULL CHECK(language IN ('ja', 'zh')),
    word_id INTEGER NOT NULL,
    source_text TEXT NOT NULL,
    english_text TEXT NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_japanese_headword ON japanese_words(headword);
CREATE INDEX IF NOT EXISTS idx_japanese_reading ON japanese_words(reading);
CREATE INDEX IF NOT EXISTS idx_japanese_common_freq ON japanese_words(is_common, frequency_rank);
CREATE INDEX IF NOT EXISTS idx_japanese_def_word ON japanese_definitions(word_id);
CREATE INDEX IF NOT EXISTS idx_japanese_def_gloss ON japanese_definitions(english_gloss);

CREATE INDEX IF NOT EXISTS idx_chinese_simplified ON chinese_words(simplified);
CREATE INDEX IF NOT EXISTS idx_chinese_traditional ON chinese_words(traditional);
CREATE INDEX IF NOT EXISTS idx_chinese_common_freq ON chinese_words(is_common, frequency_rank);
CREATE INDEX IF NOT EXISTS idx_chinese_def_word ON chinese_definitions(word_id);
CREATE INDEX IF NOT EXISTS idx_chinese_def_gloss ON chinese_definitions(english_gloss);

CREATE INDEX IF NOT EXISTS idx_examples_lang_word ON examples(language, word_id);
