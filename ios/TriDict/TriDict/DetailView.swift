import SwiftUI

struct DetailView: View {
    let output: LanguageOutput
    @StateObject private var audioManager = AudioManager()

    var languageTitle: String {
        switch output.language {
        case "ja": return "Japanese"
        case "zh": return "Chinese"
        default: return output.language
        }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Headword section
                VStack(alignment: .leading, spacing: 8) {
                    HStack(alignment: .firstTextBaseline) {
                        Text(output.headword)
                            .font(.system(size: 48, weight: .bold))

                        if let audio = output.audio {
                            Button(action: {
                                audioManager.speak(text: audio.text, locale: audio.locale)
                            }) {
                                Image(systemName: "speaker.wave.2.fill")
                                    .font(.title2)
                            }
                        }
                    }

                    if let reading = output.reading, !reading.isEmpty {
                        Text(reading)
                            .font(.title2)
                            .foregroundColor(.secondary)
                            .italic()
                    }
                }

                Divider()

                // Definition
                VStack(alignment: .leading, spacing: 8) {
                    Text("Definition")
                        .font(.headline)
                        .foregroundColor(.secondary)

                    Text(output.definition)
                        .font(.title3)
                }

                // Metadata
                if let metadataView = renderMetadata() {
                    Divider()
                    metadataView
                }

                // Examples
                if let examples = output.examples, !examples.isEmpty {
                    Divider()

                    VStack(alignment: .leading, spacing: 12) {
                        Text("Examples")
                            .font(.headline)
                            .foregroundColor(.secondary)

                        ForEach(Array(examples.enumerated()), id: \.offset) { index, example in
                            VStack(alignment: .leading, spacing: 4) {
                                Text("\(index + 1). \(example.sourceText)")
                                    .font(.body)

                                Text(example.englishText)
                                    .font(.callout)
                                    .foregroundColor(.secondary)
                                    .italic()
                                    .padding(.leading, 16)
                            }
                        }
                    }
                }

                // Stroke order (if available)
                if let strokeSVG = getStrokeSVG() {
                    Divider()

                    VStack(alignment: .leading, spacing: 8) {
                        Text("Stroke Order")
                            .font(.headline)
                            .foregroundColor(.secondary)

                        Text("Stroke order visualization coming soon")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding()
        }
        .navigationTitle(languageTitle)
        .navigationBarTitleDisplayMode(.inline)
    }

    private func renderMetadata() -> AnyView? {
        if let kanjiMeta = output.meta as? KanjiMeta {
            return AnyView(
                VStack(alignment: .leading, spacing: 8) {
                    Text("Metadata")
                        .font(.headline)
                        .foregroundColor(.secondary)

                    if let jlpt = kanjiMeta.jlptLevel {
                        MetadataRow(label: "JLPT Level", value: jlpt)
                    }
                    if let strokes = kanjiMeta.strokeCount {
                        MetadataRow(label: "Stroke Count", value: "\(strokes)")
                    }
                    if let components = kanjiMeta.components {
                        MetadataRow(label: "Components", value: components)
                    }
                }
            )
        } else if let hanziMeta = output.meta as? HanziMeta {
            return AnyView(
                VStack(alignment: .leading, spacing: 8) {
                    Text("Metadata")
                        .font(.headline)
                        .foregroundColor(.secondary)

                    if let traditional = hanziMeta.traditional {
                        MetadataRow(label: "Traditional", value: traditional)
                    }
                    if let hsk = hanziMeta.hskLevel {
                        MetadataRow(label: "HSK Level", value: hsk)
                    }
                    if let strokes = hanziMeta.strokeCount {
                        MetadataRow(label: "Stroke Count", value: "\(strokes)")
                    }
                    if let decomp = hanziMeta.decomposition {
                        MetadataRow(label: "Decomposition", value: decomp)
                    }
                }
            )
        }
        return nil
    }

    private func getStrokeSVG() -> String? {
        if let kanjiMeta = output.meta as? KanjiMeta {
            return kanjiMeta.strokeSVG
        } else if let hanziMeta = output.meta as? HanziMeta {
            return hanziMeta.strokeSVG
        }
        return nil
    }
}

struct MetadataRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .fontWeight(.medium)
            Spacer()
            Text(value)
                .foregroundColor(.secondary)
        }
    }
}
