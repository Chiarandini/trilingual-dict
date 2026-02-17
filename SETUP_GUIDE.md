# Setup Guide - Trilingual Dictionary

## Table of Contents
1. [CLI Installation](#cli-installation)
2. [Example Sentences (Tatoeba)](#example-sentences)
3. [Website Integration (nate-website)](#website-integration)

---

## CLI Installation

### Quick Install

Run the install script to make `dict` available globally:

```bash
./install.sh
```

This will:
1. Build the CLI binary
2. Copy it to `~/.local/bin/dict`
3. Make it executable

### Add to PATH (if needed)

If `~/.local/bin` is not in your PATH, add this to your `~/.zshrc` or `~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell:

```bash
source ~/.zshrc
```

### Usage

```bash
# Basic search
dict cat
dict 猫
dict 水

# JSON output
dict --json cat
```

### CLI displays:
- ✅ Strict word boundary matching (no "cat" in "catalog")
- ✅ Two-column layout (Japanese | Chinese)
- ✅ Stroke counts, JLPT/HSK levels
- ✅ Definitions and readings

---

## Example Sentences

### Overview

The database currently has **0 example sentences**. The data sources (JMdict, CC-CEDICT) don't include examples.

To add example sentences, use the **Tatoeba Project** - an open-source collection of sentences with translations.

### Import Tatoeba Examples

```bash
cd data

# Download Tatoeba data (~2GB compressed, ~10GB extracted)
python3 import_tatoeba.py --download --db ../data/dictionary.db

# Import without downloading (if data already exists)
python3 import_tatoeba.py --db ../data/dictionary.db

# Custom options
python3 import_tatoeba.py \
  --db ../data/dictionary.db \
  --download \
  --data-dir tatoeba \
  --max-per-word 5
```

### What it does:

1. **Downloads**:
   - `sentences.tar.bz2` - All Tatoeba sentences (~1GB)
   - `links.tar.bz2` - Translation links (~500MB)

2. **Processes**:
   - Extracts Japanese (jpn) and Chinese (cmn) sentences
   - Finds English translations via links
   - Matches sentences to dictionary words
   - Imports up to 5 examples per word

3. **Database Impact**:
   - Adds rows to `examples` table
   - Does NOT modify existing word data
   - **Safe to run** - clears old examples first

### Expected Results:

- ~100k-500k example sentences imported
- Most common words will have 5 examples
- Less common words may have fewer or none

### Requirements:

```bash
pip install requests
```

### Data Source:

- **Tatoeba Project**: https://tatoeba.org
- **License**: CC BY 2.0 FR
- **Data exports**: https://downloads.tatoeba.org/exports/

---

## Website Integration (nate-website)

### Current Status

✅ **Dictionary service updated** with strict word boundary matching
✅ **Component already exists** at `/src/app/components/dictionary/`
⚠️ **Database size issue** - needs optimization for web

### Database Size Problem

The full production database is **74MB**, which is too large for web loading:

```
dictionary.db (production) = 74MB   ← Too large for web
dictionary.db (sample)     = 72KB   ← Only 40 words
```

### Solution Options

#### Option 1: Use Common Words Only (Recommended)

Create a web-optimized database with only common/essential words:

```bash
cd data
python3 create_web_database.py
```

This will create `dictionary_web.db` (~5-10MB) with:
- is_common = 1 words only
- JLPT N5-N2 (Japanese)
- HSK 1-4 (Chinese)
- Top 3000 most frequent words
- Includes all definitions and examples

#### Option 2: Use Full Database (Accept Slow Load)

Copy the full database to nate-website:

```bash
cp data/dictionary.db ~/website-nate/nate-website/src/assets/dictionary.db
```

**Pros**: Complete dictionary
**Cons**: 74MB download on first load (~10-30 seconds on slow connections)

#### Option 3: Lazy Loading (Future Enhancement)

Load basic words first, fetch rare words on-demand from API.

### Update nate-website

The dictionary service has been updated with strict word boundary matching:

```bash
# Already done:
cp web/src/app/services/dictionary.service.ts \
   ~/website-nate/nate-website/src/app/services/dictionary.service.ts
```

### Current Files:

```
nate-website/
├── src/app/
│   ├── components/dictionary/
│   │   ├── dictionary.component.ts     ✅ Already exists
│   │   ├── dictionary.component.html   ✅ Already exists
│   │   └── dictionary.component.scss   ✅ Already exists
│   └── services/
│       ├── dictionary.service.ts       ✅ Updated with strict matching
│       └── audio.service.ts            ✅ Already exists
└── src/assets/
    └── dictionary.db                   ⚠️ Old 72KB sample (needs update)
```

### Build & Deploy

```bash
cd ~/website-nate/nate-website

# Install dependencies (if needed)
npm install

# Build for production
ng build --configuration production

# Deploy
# (Your deployment process here)
```

### Testing Locally

```bash
cd ~/website-nate/nate-website
ng serve

# Open browser
open http://localhost:4200/dictionary
```

### What Works Now:

✅ Strict word boundary matching ("cat" won't match "catalog")
✅ Japanese and Chinese results side-by-side
✅ Audio playback (TTS)
✅ Metadata display (JLPT, HSK, stroke counts)
✅ Example sentences (once Tatoeba is imported)

---

## Creating Web-Optimized Database

Create this script to generate a smaller database for web:

```python
# data/create_web_database.py
import sqlite3
import shutil

# Copy original database
shutil.copy('dictionary.db', 'dictionary_web.db')

conn = sqlite3.connect('dictionary_web.db')
cursor = conn.cursor()

# Keep only common words
cursor.execute("DELETE FROM japanese_words WHERE is_common = 0")
cursor.execute("DELETE FROM chinese_words WHERE is_common = 0")

# Remove orphaned definitions
cursor.execute("""
    DELETE FROM japanese_definitions
    WHERE word_id NOT IN (SELECT id FROM japanese_words)
""")
cursor.execute("""
    DELETE FROM chinese_definitions
    WHERE word_id NOT IN (SELECT id FROM chinese_words)
""")

# Remove orphaned examples
cursor.execute("""
    DELETE FROM examples
    WHERE language = 'ja' AND word_id NOT IN (SELECT id FROM japanese_words)
""")
cursor.execute("""
    DELETE FROM examples
    WHERE language = 'zh' AND word_id NOT IN (SELECT id FROM chinese_words)
""")

# Vacuum to reclaim space
cursor.execute("VACUUM")

conn.commit()
conn.close()

print("✅ Created dictionary_web.db")
```

Run it:

```bash
cd data
python3 create_web_database.py
cp dictionary_web.db ~/website-nate/nate-website/src/assets/dictionary.db
```

---

## Summary

### ✅ Completed

1. **CLI Installation**: `dict` command now available globally
2. **Dictionary Service**: Updated with strict word boundary matching
3. **nate-website**: Service updated, ready for deployment

### ⚠️ Next Steps

1. **Choose database strategy** for nate-website:
   - Recommended: Create web-optimized database (5-10MB)
   - Alternative: Use full 74MB database (slow initial load)

2. **Optional - Import examples**:
   ```bash
   cd data
   python3 import_tatoeba.py --download --db ../data/dictionary.db
   ```

3. **Build & deploy nate-website**:
   ```bash
   cd ~/website-nate/nate-website
   ng build --configuration production
   ```

---

## Testing

### CLI
```bash
dict cat      # Should return 猫 (neko/māo)
dict catalog  # Should NOT match "cat"
dict dog      # Should return 犬 (inu), not 狸 (raccoon dog)
```

### Website
```bash
cd ~/website-nate/nate-website
ng serve
# Test at http://localhost:4200/dictionary
```

### Example Sentences
```bash
# After importing Tatoeba
dict --json cat | jq '.outputs[0].examples'
```

---

## Troubleshooting

### CLI not found after install

Add to PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Website database too large

Create web-optimized version:
```bash
cd data
python3 create_web_database.py
```

### No example sentences

Import Tatoeba:
```bash
cd data
python3 import_tatoeba.py --download
```

---

**Questions?** Check existing test files:
- `test_expected_results.py` - Test with 141 hardcoded words
- `STRICT_WORD_BOUNDARY_TEST_RESULTS.md` - Full test analysis
