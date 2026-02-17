import Foundation
import SQLite3

// MARK: - Data Models

struct DictionaryResponse: Codable {
    let meta: MetaInfo
    let outputs: [LanguageOutput]
}

struct MetaInfo: Codable {
    let inputLanguage: String
    let query: String

    enum CodingKeys: String, CodingKey {
        case inputLanguage = "input_language"
        case query
    }
}

struct LanguageOutput: Codable {
    let language: String
    let headword: String
    let reading: String?
    let definition: String
    let rank: Int?
    let audio: AudioInfo?
    let meta: MetadataType?
    let examples: [Example]?

    enum CodingKeys: String, CodingKey {
        case language, headword, reading, definition, rank, audio, meta, examples
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        language = try container.decode(String.self, forKey: .language)
        headword = try container.decode(String.self, forKey: .headword)
        reading = try container.decodeIfPresent(String.self, forKey: .reading)
        definition = try container.decode(String.self, forKey: .definition)
        rank = try container.decodeIfPresent(Int.self, forKey: .rank)
        audio = try container.decodeIfPresent(AudioInfo.self, forKey: .audio)
        examples = try container.decodeIfPresent([Example].self, forKey: .examples)

        // Decode metadata based on language
        if language == "ja" {
            meta = try container.decodeIfPresent(KanjiMeta.self, forKey: .meta)
        } else if language == "zh" {
            meta = try container.decodeIfPresent(HanziMeta.self, forKey: .meta)
        } else {
            meta = nil
        }
    }
}

protocol MetadataType: Codable {}

struct KanjiMeta: MetadataType {
    let jlptLevel: String?
    let strokeCount: Int?
    let components: String?
    let strokeSVG: String?

    enum CodingKeys: String, CodingKey {
        case jlptLevel = "jlpt_level"
        case strokeCount = "stroke_count"
        case components
        case strokeSVG = "stroke_svg"
    }
}

struct HanziMeta: MetadataType {
    let traditional: String?
    let hskLevel: String?
    let strokeCount: Int?
    let components: String?
    let decomposition: String?
    let strokeSVG: String?

    enum CodingKeys: String, CodingKey {
        case traditional
        case hskLevel = "hsk_level"
        case strokeCount = "stroke_count"
        case components
        case decomposition
        case strokeSVG = "stroke_svg"
    }
}

struct AudioInfo: Codable {
    let type: String
    let text: String
    let locale: String
}

struct Example: Codable {
    let sourceText: String
    let englishText: String

    enum CodingKeys: String, CodingKey {
        case sourceText = "source_text"
        case englishText = "english_text"
    }
}

// MARK: - Database Manager

class DatabaseManager: ObservableObject {
    private var db: OpaquePointer?

    init() {
        openDatabase()
    }

    deinit {
        closeDatabase()
    }

    private func openDatabase() {
        // Try to find database in bundle
        guard let dbPath = Bundle.main.path(forResource: "dictionary", ofType: "db") else {
            print("Error: dictionary.db not found in bundle")
            return
        }

        if sqlite3_open(dbPath, &db) != SQLITE_OK {
            print("Error opening database")
        }
    }

    private func closeDatabase() {
        if db != nil {
            sqlite3_close(db)
            db = nil
        }
    }

    func search(query: String) -> DictionaryResponse? {
        let language = detectLanguage(query)

        var outputs: [LanguageOutput] = []

        switch language {
        case "en":
            outputs = searchFromEnglish(query)
        case "ja":
            outputs = searchFromJapanese(query)
        case "zh":
            outputs = searchFromChinese(query)
        case "ambiguous":
            outputs = searchAmbiguous(query)
        default:
            break
        }

        return DictionaryResponse(
            meta: MetaInfo(inputLanguage: language, query: query),
            outputs: outputs
        )
    }

    // MARK: - Language Detection

    private func detectLanguage(_ input: String) -> String {
        var hasHiragana = false
        var hasKatakana = false
        var hasCJK = false
        var hasASCII = false

        for scalar in input.unicodeScalars {
            switch scalar.value {
            case 0x3040...0x309F: hasHiragana = true
            case 0x30A0...0x30FF: hasKatakana = true
            case 0x4E00...0x9FFF: hasCJK = true
            case 0x20...0x7E: hasASCII = true
            default: break
            }
        }

        if hasHiragana || hasKatakana {
            return "ja"
        }
        if hasASCII && !hasCJK {
            return "en"
        }
        if hasCJK {
            return "ambiguous"
        }
        return "unknown"
    }

    // MARK: - Search Methods

    private func searchFromEnglish(_ query: String) -> [LanguageOutput] {
        var outputs: [LanguageOutput] = []

        // Search Japanese
        if let jaOutput = queryJapaneseByEnglish(query) {
            outputs.append(jaOutput)
        }

        // Search Chinese
        if let zhOutput = queryChineseByEnglish(query) {
            outputs.append(zhOutput)
        }

        return outputs
    }

    private func searchFromJapanese(_ query: String) -> [LanguageOutput] {
        var outputs: [LanguageOutput] = []

        // Direct Japanese lookup
        if let jaOutput = queryJapanese(query) {
            outputs.append(jaOutput)

            // Pivot to Chinese via English
            if let zhOutput = queryChineseByEnglish(jaOutput.definition) {
                outputs.append(zhOutput)
            }
        }

        return outputs
    }

    private func searchFromChinese(_ query: String) -> [LanguageOutput] {
        var outputs: [LanguageOutput] = []

        // Direct Chinese lookup
        if let zhOutput = queryChinese(query) {
            outputs.append(zhOutput)

            // Pivot to Japanese via English
            if let jaOutput = queryJapaneseByEnglish(zhOutput.definition) {
                outputs.append(jaOutput)
            }
        }

        return outputs
    }

    private func searchAmbiguous(_ query: String) -> [LanguageOutput] {
        // Try Japanese first, then Chinese
        let jaResults = searchFromJapanese(query)
        if !jaResults.isEmpty {
            return jaResults
        }
        return searchFromChinese(query)
    }

    // MARK: - Query Helpers

    private func queryJapanese(_ input: String) -> LanguageOutput? {
        guard let db = db else { return nil }

        let query = """
            SELECT id, headword, reading, is_common, frequency_rank, jlpt_level,
                   stroke_count, components, stroke_svg
            FROM japanese_words
            WHERE headword = ? OR reading = ?
            ORDER BY is_common DESC, frequency_rank ASC
            LIMIT 1
            """

        var statement: OpaquePointer?
        defer {
            if statement != nil {
                sqlite3_finalize(statement)
            }
        }

        guard sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK else {
            print("Error preparing Japanese query")
            return nil
        }

        sqlite3_bind_text(statement, 1, input, -1, nil)
        sqlite3_bind_text(statement, 2, input, -1, nil)

        guard sqlite3_step(statement) == SQLITE_ROW else {
            return nil
        }

        return buildJapaneseOutput(from: statement!)
    }

    private func queryJapaneseByEnglish(_ gloss: String) -> LanguageOutput? {
        guard let db = db else { return nil }

        // Strict word boundary matching - only exact matches or definitions starting with the word
        // Phase 1: Return only primary/exact matches
        let query = """
            SELECT DISTINCT w.id, w.headword, w.reading, w.is_common, w.frequency_rank,
                   w.jlpt_level, w.stroke_count, w.components, w.stroke_svg
            FROM japanese_words w
            JOIN japanese_definitions d ON w.id = d.word_id
            WHERE LOWER(d.english_gloss) = LOWER(?)
               OR LOWER(d.english_gloss) LIKE LOWER(?) || ' (%'
               OR LOWER(d.english_gloss) LIKE LOWER(?) || ';%'
               OR LOWER(d.english_gloss) LIKE '%;' || LOWER(?)
               OR LOWER(d.english_gloss) LIKE '%; ' || LOWER(?) || ';%'
            ORDER BY
               CASE
                 WHEN LOWER(d.english_gloss) = LOWER(?) THEN 0
                 WHEN LOWER(d.english_gloss) LIKE LOWER(?) || ' (%' THEN 1
                 WHEN LOWER(d.english_gloss) LIKE LOWER(?) || ';%' THEN 2
                 ELSE 3
               END,
               w.is_common DESC, w.frequency_rank ASC
            LIMIT 1
            """

        var statement: OpaquePointer?
        defer {
            if statement != nil {
                sqlite3_finalize(statement)
            }
        }

        guard sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK else {
            print("Error preparing Japanese by English query")
            return nil
        }

        // Bind the gloss to all 8 parameters
        for i in 1...8 {
            sqlite3_bind_text(statement, Int32(i), gloss, -1, nil)
        }

        guard sqlite3_step(statement) == SQLITE_ROW else {
            return nil
        }

        return buildJapaneseOutput(from: statement!)
    }

    private func queryChinese(_ input: String) -> LanguageOutput? {
        guard let db = db else { return nil }

        let query = """
            SELECT id, simplified, traditional, pinyin, is_common, frequency_rank,
                   hsk_level, stroke_count, components, decomposition, stroke_svg
            FROM chinese_words
            WHERE simplified = ?
            ORDER BY is_common DESC, frequency_rank ASC
            LIMIT 1
            """

        var statement: OpaquePointer?
        defer {
            if statement != nil {
                sqlite3_finalize(statement)
            }
        }

        guard sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK else {
            print("Error preparing Chinese query")
            return nil
        }

        sqlite3_bind_text(statement, 1, input, -1, nil)

        guard sqlite3_step(statement) == SQLITE_ROW else {
            return nil
        }

        return buildChineseOutput(from: statement!)
    }

    private func queryChineseByEnglish(_ gloss: String) -> LanguageOutput? {
        guard let db = db else { return nil }

        // Strict word boundary matching - only exact matches or definitions starting with the word
        // Phase 1: Return only primary/exact matches
        let query = """
            SELECT DISTINCT w.id, w.simplified, w.traditional, w.pinyin, w.is_common,
                   w.frequency_rank, w.hsk_level, w.stroke_count, w.components,
                   w.decomposition, w.stroke_svg
            FROM chinese_words w
            JOIN chinese_definitions d ON w.id = d.word_id
            WHERE LOWER(d.english_gloss) = LOWER(?)
               OR LOWER(d.english_gloss) LIKE LOWER(?) || ' (%'
               OR LOWER(d.english_gloss) LIKE LOWER(?) || ';%'
               OR LOWER(d.english_gloss) LIKE '%;' || LOWER(?)
               OR LOWER(d.english_gloss) LIKE '%; ' || LOWER(?) || ';%'
            ORDER BY
               CASE
                 WHEN LOWER(d.english_gloss) = LOWER(?) THEN 0
                 WHEN LOWER(d.english_gloss) LIKE LOWER(?) || ' (%' THEN 1
                 WHEN LOWER(d.english_gloss) LIKE LOWER(?) || ';%' THEN 2
                 ELSE 3
               END,
               w.is_common DESC, w.frequency_rank ASC
            LIMIT 1
            """

        var statement: OpaquePointer?
        defer {
            if statement != nil {
                sqlite3_finalize(statement)
            }
        }

        guard sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK else {
            print("Error preparing Chinese by English query")
            return nil
        }

        // Bind the gloss to all 8 parameters
        for i in 1...8 {
            sqlite3_bind_text(statement, Int32(i), gloss, -1, nil)
        }

        guard sqlite3_step(statement) == SQLITE_ROW else {
            return nil
        }

        return buildChineseOutput(from: statement!)
    }

    // MARK: - Helper Methods

    private func buildJapaneseOutput(from statement: OpaquePointer) -> LanguageOutput? {
        let id = Int(sqlite3_column_int(statement, 0))
        let headword = String(cString: sqlite3_column_text(statement, 1))
        let reading = String(cString: sqlite3_column_text(statement, 2))
        let isCommon = sqlite3_column_int(statement, 3) != 0

        var frequencyRank: Int? = nil
        if sqlite3_column_type(statement, 4) != SQLITE_NULL {
            frequencyRank = Int(sqlite3_column_int(statement, 4))
        }

        var jlptLevel: String? = nil
        if sqlite3_column_type(statement, 5) != SQLITE_NULL {
            jlptLevel = String(cString: sqlite3_column_text(statement, 5))
        }

        var strokeCount: Int? = nil
        if sqlite3_column_type(statement, 6) != SQLITE_NULL {
            strokeCount = Int(sqlite3_column_int(statement, 6))
        }

        // Get definitions
        let definitions = getJapaneseDefinitions(wordId: id)
        let definition = definitions.joined(separator: "; ")

        // Get examples
        let examples = getExamples(language: "ja", wordId: id)

        // Calculate rank (simplified - just use frequency rank or 100 if common)
        let rank = frequencyRank ?? (isCommon ? 100 : 1000)

        return LanguageOutput(
            language: "ja",
            headword: headword,
            reading: reading,
            definition: definition,
            rank: rank,
            audio: AudioInfo(type: "tts", text: headword, locale: "ja-JP"),
            meta: KanjiMeta(
                jlptLevel: jlptLevel,
                strokeCount: strokeCount,
                components: nil,
                strokeSVG: nil
            ),
            examples: examples
        )
    }

    private func buildChineseOutput(from statement: OpaquePointer) -> LanguageOutput? {
        let id = Int(sqlite3_column_int(statement, 0))
        let simplified = String(cString: sqlite3_column_text(statement, 1))
        let traditional = String(cString: sqlite3_column_text(statement, 2))
        let pinyin = String(cString: sqlite3_column_text(statement, 3))
        let isCommon = sqlite3_column_int(statement, 4) != 0

        var frequencyRank: Int? = nil
        if sqlite3_column_type(statement, 5) != SQLITE_NULL {
            frequencyRank = Int(sqlite3_column_int(statement, 5))
        }

        var hskLevel: String? = nil
        if sqlite3_column_type(statement, 6) != SQLITE_NULL {
            hskLevel = String(cString: sqlite3_column_text(statement, 6))
        }

        var strokeCount: Int? = nil
        if sqlite3_column_type(statement, 7) != SQLITE_NULL {
            strokeCount = Int(sqlite3_column_int(statement, 7))
        }

        // Get definitions
        let definitions = getChineseDefinitions(wordId: id)
        let definition = definitions.joined(separator: "; ")

        // Get examples
        let examples = getExamples(language: "zh", wordId: id)

        // Calculate rank
        let rank = frequencyRank ?? (isCommon ? 100 : 1000)

        return LanguageOutput(
            language: "zh",
            headword: simplified,
            reading: pinyin,
            definition: definition,
            rank: rank,
            audio: AudioInfo(type: "tts", text: simplified, locale: "zh-CN"),
            meta: HanziMeta(
                traditional: traditional != simplified ? traditional : nil,
                hskLevel: hskLevel,
                strokeCount: strokeCount,
                components: nil,
                decomposition: nil,
                strokeSVG: nil
            ),
            examples: examples
        )
    }

    private func getJapaneseDefinitions(wordId: Int) -> [String] {
        guard let db = db else { return [] }

        let query = "SELECT english_gloss FROM japanese_definitions WHERE word_id = ?"

        var statement: OpaquePointer?
        defer {
            if statement != nil {
                sqlite3_finalize(statement)
            }
        }

        guard sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK else {
            return []
        }

        sqlite3_bind_int(statement, 1, Int32(wordId))

        var definitions: [String] = []
        while sqlite3_step(statement) == SQLITE_ROW {
            let gloss = String(cString: sqlite3_column_text(statement, 0))
            definitions.append(gloss)
        }

        return definitions
    }

    private func getChineseDefinitions(wordId: Int) -> [String] {
        guard let db = db else { return [] }

        let query = "SELECT english_gloss FROM chinese_definitions WHERE word_id = ?"

        var statement: OpaquePointer?
        defer {
            if statement != nil {
                sqlite3_finalize(statement)
            }
        }

        guard sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK else {
            return []
        }

        sqlite3_bind_int(statement, 1, Int32(wordId))

        var definitions: [String] = []
        while sqlite3_step(statement) == SQLITE_ROW {
            let gloss = String(cString: sqlite3_column_text(statement, 0))
            definitions.append(gloss)
        }

        return definitions
    }

    private func getExamples(language: String, wordId: Int) -> [Example]? {
        guard let db = db else { return nil }

        let query = """
            SELECT source_text, english_text
            FROM examples
            WHERE language = ? AND word_id = ?
            LIMIT 5
            """

        var statement: OpaquePointer?
        defer {
            if statement != nil {
                sqlite3_finalize(statement)
            }
        }

        guard sqlite3_prepare_v2(db, query, -1, &statement, nil) == SQLITE_OK else {
            return nil
        }

        sqlite3_bind_text(statement, 1, language, -1, nil)
        sqlite3_bind_int(statement, 2, Int32(wordId))

        var examples: [Example] = []
        while sqlite3_step(statement) == SQLITE_ROW {
            let sourceText = String(cString: sqlite3_column_text(statement, 0))
            let englishText = String(cString: sqlite3_column_text(statement, 1))
            examples.append(Example(sourceText: sourceText, englishText: englishText))
        }

        return examples.isEmpty ? nil : examples
    }
}
