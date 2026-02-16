import SwiftUI

struct ResultCard: View {
    let output: LanguageOutput
    @StateObject private var audioManager = AudioManager()

    var languageTitle: String {
        switch output.language {
        case "ja": return "Japanese"
        case "zh": return "Chinese"
        default: return output.language
        }
    }

    var languageColor: Color {
        switch output.language {
        case "ja": return .blue
        case "zh": return .red
        default: return .gray
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                Text(languageTitle)
                    .font(.headline)
                    .foregroundColor(languageColor)

                Spacer()

                if let audio = output.audio {
                    Button(action: {
                        audioManager.speak(text: audio.text, locale: audio.locale)
                    }) {
                        Image(systemName: "speaker.wave.2.fill")
                            .foregroundColor(languageColor)
                    }
                }
            }

            // Headword and reading
            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Text(output.headword)
                    .font(.title)
                    .fontWeight(.bold)

                if let reading = output.reading, !reading.isEmpty {
                    Text("(\(reading))")
                        .font(.title3)
                        .foregroundColor(.secondary)
                        .italic()
                }
            }

            // Definition
            Text(output.definition)
                .font(.body)
                .foregroundColor(.primary)

            // Metadata
            if !metadata.isEmpty {
                HStack {
                    ForEach(metadata, id: \.self) { item in
                        Text(item)
                            .font(.caption)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color(.systemGray5))
                            .cornerRadius(8)
                    }
                }
            }

            // Example (first one only)
            if let example = output.examples?.first {
                VStack(alignment: .leading, spacing: 4) {
                    Text(example.sourceText)
                        .font(.callout)
                        .foregroundColor(.secondary)
                    Text(example.englishText)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .italic()
                }
                .padding(.top, 4)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 4, x: 0, y: 2)
    }

    private var metadata: [String] {
        var items: [String] = []

        if let kanjiMeta = output.meta as? KanjiMeta {
            if let jlpt = kanjiMeta.jlptLevel {
                items.append("JLPT: \(jlpt)")
            }
            if let strokes = kanjiMeta.strokeCount {
                items.append("\(strokes) strokes")
            }
        } else if let hanziMeta = output.meta as? HanziMeta {
            if let hsk = hanziMeta.hskLevel {
                items.append("HSK: \(hsk)")
            }
            if let strokes = hanziMeta.strokeCount {
                items.append("\(strokes) strokes")
            }
        }

        return items
    }
}
