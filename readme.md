# Trilingual Dictionary

A comprehensive dictionary system supporting English, Japanese, and Chinese with triangular translation using English as a pivot language.

## Features

- **Triangular Translation**: Translate between any pair of languages (EN/JA/ZH) using English as the intermediate language
- **Multiple Results**: Returns top 5 results per language (configurable) instead of just one
- **Automatic Language Detection**: Smart detection based on Unicode ranges
- **Multiple Frontends**: CLI, Neovim plugin, Web app, and iOS app (in progress)
- **Rich Metadata**: JLPT/HSK levels, stroke counts, example sentences, rank indicators
- **Text-to-Speech**: Pronunciation support across all platforms
- **Offline-First**: No server required for any frontend
- **Progressive Disclosure**: Web UI shows top 3 results with "Show more" to expand

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
./dict cat              # Returns 5 results per language
./dict cat -n 1         # Returns single best match
./dict cat -n 10        # Returns 10 results per language
```

Expected output (default 5 results, showing first 2):
```
╭─ Japanese (5 results) ────────────────╮
│ 1.                                    │
│ 猫 (ねこ)                             │
│ cat                                   │
│ ★ Common | JLPT: N3 | 11 strokes     │
│                                       │
│ ───────────────────────               │
│                                       │
│ 2.                                    │
│ キャット (キャット)                   │
│ cat                                   │
╰───────────────────────────────────────╯
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
# English → Japanese + Chinese (default: 5 results each)
./dict cat

# Custom result limit
./dict cat -n 10        # 10 results per language
./dict cat --limit 1    # Single best match (Phase 1 behavior)

# Japanese → English + Chinese
./dict 猫

# Japanese reading → English + Chinese
./dict ねこ

# Chinese → English + Japanese
./dict 吃

# JSON output (includes all results)
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

## Recent Updates

✅ **Phase 2 Complete** (Feb 17, 2026):
- Multiple word results (default: 5 per language, configurable)
- Fancy CLI boxes with numbered results and rank indicators
- Web UI with "Show more" progressive disclosure
- Consistent API across CLI and Web platforms

See [PHASE_2.md](PHASE_2.md) for full details.

## Next Steps

- [ ] **iOS Phase 2** - Implement multiple results for iOS app
- [ ] **Full Data Ingestion** - Use JMdict/CC-CEDICT parsers to build production database
- [ ] **Deployment** - Deploy web app and CLI to production
- [ ] **Fuzzy Search** - Add approximate matching for typos
- [ ] **Advanced Filtering** - Filter by JLPT/HSK level, commonality

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
