# Trilingual Dictionary

A comprehensive dictionary system supporting English, Japanese, and Chinese with triangular translation using English as a pivot language.

## Features

- **Triangular Translation**: Translate between any pair of languages (EN/JA/ZH) using English as the intermediate language
- **Automatic Language Detection**: Smart detection based on Unicode ranges
- **Multiple Frontends**: CLI, Neovim plugin, Web app, and iOS app (in progress)
- **Rich Metadata**: JLPT/HSK levels, stroke counts, example sentences
- **Text-to-Speech**: Pronunciation support across all platforms
- **Offline-First**: No server required for any frontend

## Quick Start

### 1. Generate Sample Database

```bash
cd data/sample
python3 generate_samples.py
```

This creates `dictionary.db` with 20 word pairs for testing.

### 2. Build and Test CLI

```bash
cd cmd/dict
go build -o dict
./dict cat
```

Expected output:
```
╭─ Japanese ────────────╮  ╭─ Chinese ──────────────╮
│ 猫 (ねこ)             │  │ 猫 (māo)               │
│ cat                   │  │ cat                    │
│ JLPT: N3 | 11 strokes │  │ HSK: 1 | 11 strokes    │
╰───────────────────────╯  ╰────────────────────────╯
```

### 3. Try Other Frontends

**Neovim:**
```bash
ln -s ~/trilingual-dict/nvim ~/.config/nvim/pack/plugins/start/tridict
nvim
:Dict cat
```

**Web:**
```bash
cd web
./setup.sh
npm start
# Navigate to http://localhost:4200
```

## Platform Status

| Platform | Status | Technology |
|----------|--------|-----------|
| **CLI** | ✅ Production Ready | Go + SQLite |
| **Neovim** | ✅ Production Ready | Lua + Go CLI |
| **Web** | ✅ Production Ready | TypeScript + SQL.js |
| **iOS** | ⚠️ In Progress | Swift + SQLite |

## Project Structure

```
trilingual-dict/
├── cmd/dict/              # CLI application
├── core/                  # Go core library
│   ├── types/             # Data structures
│   ├── database/          # SQLite interface
│   ├── detector/          # Language detection
│   ├── ranker/            # Result ranking
│   └── query/             # Triangulation logic
├── data/                  # Data acquisition
│   ├── schema.sql         # Database schema
│   └── sample/            # Sample data generator
├── nvim/                  # Neovim plugin
├── web/                   # Angular web app
├── ios/                   # iOS application
└── docs/                  # Documentation
```

## Architecture

### Triangular Translation

The system uses English as a pivot language:

```
Japanese ←→ English ←→ Chinese
```

**Example: Japanese → Chinese**
1. Look up Japanese word → get English definition
2. Use English definition → find Chinese equivalent

**Example: English → Both**
1. Search Japanese definitions for English term
2. Search Chinese definitions for English term
3. Return both results

### Database Schema

- **japanese_words** + **japanese_definitions**
- **chinese_words** + **chinese_definitions**
- **examples** (usage examples)

All connected via English glosses for triangular translation.

## Building

### CLI

```bash
cd cmd/dict
go build -o dict
./dict cat              # English input
./dict 猫               # Japanese/Chinese input
./dict --json ねこ      # JSON output
```

### Web Application

```bash
cd web
npm install
npm start
```

### Cross-Platform

```bash
# Linux
GOOS=linux GOARCH=amd64 go build -o dict-linux

# Windows
GOOS=windows GOARCH=amd64 go build -o dict.exe

# macOS ARM
GOOS=darwin GOARCH=arm64 go build -o dict-macos
```

## Development

### Sample Data

The project includes sample data (20 words) for development:

```bash
cd data/sample
python3 generate_samples.py
```

### Full Data (In Progress)

For production use with full dictionaries:

```bash
cd data
python3 download.py          # Download JMdict, CC-CEDICT, KANJIDIC2
python3 ingest.py --input sources
```

*Note: Full data ingestion is being implemented*

## Usage Examples

### CLI

```bash
# English → Japanese + Chinese
./dict cat

# Japanese → English + Chinese
./dict 猫

# Japanese reading → English + Chinese
./dict ねこ

# Chinese → English + Japanese
./dict 吃

# JSON output
./dict --json cat
```

### Neovim

```vim
:Dict cat              " Look up English word
:Dict 猫               " Look up Japanese/Chinese
:DictWord              " Look up word under cursor
```

### Web

Visit `http://localhost:4200` after running `npm start` in the `web/` directory.

## Testing

```bash
# Build CLI
make build-cli

# Run with sample data
./cmd/dict/dict cat

# Test different inputs
./cmd/dict/dict dog
./cmd/dict/dict 犬
./cmd/dict/dict いぬ
```

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and technical details
- **[STATUS.md](STATUS.md)** - Current project status and roadmap
- **[docs/](docs/)** - Additional documentation
  - `setup-guides/` - Integration guides
  - `archive/` - Implementation notes

## API / JSON Output

All frontends use a common JSON response format:

```json
{
  "meta": {
    "input_language": "en",
    "query": "cat"
  },
  "outputs": [
    {
      "language": "ja",
      "headword": "猫",
      "reading": "ねこ",
      "definition": "cat",
      "rank": 1,
      "audio": {
        "type": "tts",
        "text": "猫",
        "locale": "ja-JP"
      },
      "meta": {
        "jlpt_level": "N3",
        "stroke_count": 11
      },
      "examples": [...]
    },
    {
      "language": "zh",
      ...
    }
  ]
}
```

## Next Steps

- [ ] **Full Data Ingestion** - Implement JMdict/CC-CEDICT parsing
- [ ] **iOS Database Queries** - Complete DatabaseManager implementation
- [ ] **Unit Tests** - Add test coverage for all modules
- [ ] **Fuzzy Search** - Add approximate matching
- [ ] **Top-N Results** - Return multiple results instead of just top-1

See [STATUS.md](STATUS.md) for detailed roadmap.

## Data Sources

- **JMdict**: Japanese-English dictionary (CC BY-SA 3.0)
- **CC-CEDICT**: Chinese-English dictionary (CC BY-SA 4.0)
- **KANJIDIC2**: Kanji character database (CC BY-SA 3.0)

## Repository

https://github.com/Chiarandini/trilingual-dict

## License

MIT License - see LICENSE file for details

## Credits

- Dictionary data: JMdict, CC-CEDICT, KANJIDIC2
- Go libraries: mattn/go-sqlite3, charmbracelet/lipgloss
- Web: SQL.js, Angular
- iOS: AVFoundation

---

Built for language learners 🌏
