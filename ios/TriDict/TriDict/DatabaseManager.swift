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

    // MARK: - Query Helpers (Simplified - would need full SQL implementation)

    private func queryJapanese(_ input: String) -> LanguageOutput? {
        // Simplified - would need actual SQLite queries
        return nil
    }

    private func queryJapaneseByEnglish(_ gloss: String) -> LanguageOutput? {
        // Simplified - would need actual SQLite queries
        return nil
    }

    private func queryChinese(_ input: String) -> LanguageOutput? {
        // Simplified - would need actual SQLite queries
        return nil
    }

    private func queryChineseByEnglish(_ gloss: String) -> LanguageOutput? {
        // Simplified - would need actual SQLite queries
        return nil
    }
}
