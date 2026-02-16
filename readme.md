# Trilingual Dictionary

A comprehensive dictionary system supporting English, Japanese, and Chinese with triangular translation using English as a pivot language.

## Features

- **Triangular Translation**: Translate between any pair of languages (EN/JA/ZH) using English as the intermediate language
- **Automatic Language Detection**: Smart detection based on Unicode ranges
- **Multiple Frontends**: CLI, Neovim plugin, Web (WASM), and iOS app
- **Rich Metadata**: JLPT/HSK levels, stroke counts, example sentences
- **Text-to-Speech**: Pronunciation support across all platforms
- **Sample Data**: Development-ready with 20 word pairs

## Quick Start

### 1. Generate Sample Database

```bash
cd data/sample
python3 generate_samples.py
```

### 2. Build and Test CLI

```bash
cd cmd/dict
go build -o dict
./dict cat
```

## Project Structure

See full README for detailed architecture documentation.

## License

MIT
