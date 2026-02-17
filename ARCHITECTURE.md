# Architecture Documentation

## System Overview

The trilingual dictionary is designed as a **single-core, multi-frontend** architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     Frontends                           │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│   CLI    │  Neovim  │   Web    │   iOS    │   Future    │
│  (Go)    │  (Lua)   │ (WASM)   │ (Swift)  │   (...)     │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
           │          │          │          │
           └──────────┴─────┬────┴──────────┘
                            │
                   ┌────────▼────────┐
                   │   Core Library  │
                   │      (Go)       │
                   ├─────────────────┤
                   │  - Detector     │
                   │  - Ranker       │
                   │  - Query        │
                   │  - Database     │
                   └────────┬────────┘
                            │
                   ┌────────▼────────┐
                   │  SQLite DB      │
                   │  dictionary.db  │
                   └─────────────────┘
```

## Core Library (Go)

### Package Structure

```
core/
├── types/         # Data structures and JSON response types
├── database/      # SQLite connection and queries
├── detector/      # Language detection heuristics
├── ranker/        # Result ranking algorithms
└── query/         # Triangulation logic
```

### Key Components

#### 1. Language Detector (`detector/detect.go`)

**Algorithm:**
```go
if containsKana(input) → Japanese
if is ASCII(input)      → English
if hasCJK(input)       → Ambiguous (try both JA/ZH)
```

**Unicode Ranges:**
- Hiragana: U+3040-309F
- Katakana: U+30A0-30FF
- CJK Unified: U+4E00-9FFF

#### 2. Result Ranker (`ranker/rank.go`)

**Scoring Function:**
```go
score = (is_common ? 100 : 0) +
        max(0, 1000 - frequency_rank) +
        (100 / character_length)
```

Returns top-1 result (easily expandable to top-N).

#### 3. Query Engine (`query/triangulate.go`)

**Triangulation Logic:**

```
English Input:
  ├─ Query japanese_definitions WHERE gloss LIKE %input%
  ├─ Query chinese_definitions WHERE gloss LIKE %input%
  └─ Return both results

Japanese Input:
  ├─ Direct lookup in japanese_words
  ├─ Extract English glosses
  ├─ Use glosses to query chinese_definitions (pivot)
  └─ Return Japanese + Chinese

Chinese Input:
  ├─ Direct lookup in chinese_words
  ├─ Extract English glosses
  ├─ Use glosses to query japanese_definitions (pivot)
  └─ Return Chinese + Japanese

Ambiguous Input:
  ├─ Try Japanese first
  └─ Fallback to Chinese if no results
```

## Database Schema

### Entity-Relationship Diagram

```
japanese_words ──┬─< japanese_definitions
                 │
                 └─< examples (language='ja')

chinese_words ──┬─< chinese_definitions
                │
                └─< examples (language='zh')
```

### Tables

**japanese_words**
- Core Japanese word metadata
- Indexed on: headword, reading, (is_common, frequency_rank)

**japanese_definitions**
- English glosses for Japanese words
- Many-to-one relationship
- Indexed on: word_id, english_gloss

**chinese_words**
- Core Chinese word metadata
- Indexed on: simplified, traditional, (is_common, frequency_rank)

**chinese_definitions**
- English glosses for Chinese words
- Indexed on: word_id, english_gloss

**examples**
- Usage examples with translations
- Polymorphic: language='ja' or 'zh'
- Indexed on: (language, word_id)

### Query Patterns

1. **Direct Lookup**
   ```sql
   SELECT * FROM japanese_words WHERE headword = ? OR reading = ?
   ```

2. **English Pivot**
   ```sql
   SELECT w.* FROM chinese_words w
   JOIN chinese_definitions d ON w.id = d.word_id
   WHERE d.english_gloss LIKE ?
   ORDER BY w.is_common DESC, w.frequency_rank ASC
   ```

## Data Flow

### Example: Searching "cat"

```
User Input: "cat"
     │
     ▼
┌─────────────┐
│  Detector   │ → Language: "en"
└─────┬───────┘
      │
      ▼
┌─────────────┐
│ Query Engine│
└─────┬───────┘
      │
      ├─► Japanese Query:
      │   SELECT * FROM japanese_words w
      │   JOIN japanese_definitions d ON w.id = d.word_id
      │   WHERE d.english_gloss LIKE '%cat%'
      │   → Result: {headword: "猫", reading: "ねこ", ...}
      │
      ├─► Chinese Query:
      │   SELECT * FROM chinese_words w
      │   JOIN chinese_definitions d ON w.id = d.word_id
      │   WHERE d.english_gloss LIKE '%cat%'
      │   → Result: {simplified: "猫", pinyin: "māo", ...}
      │
      ▼
┌─────────────┐
│   Ranker    │ → Top-1 for each language
└─────┬───────┘
      │
      ▼
JSON Response:
{
  "outputs": [
    {"language": "ja", "headword": "猫", ...},
    {"language": "zh", "headword": "猫", ...}
  ]
}
```

## Frontend Architectures

### CLI (Go Native)

```
main.go
  ├─ Parse arguments
  ├─ Call query.Query()
  ├─ Format output with lipgloss
  └─ Print to stdout
```

### Neovim Plugin (Lua)

```
:Dict command
  ├─ init.lua: Call CLI with --json flag
  ├─ Parse JSON response
  ├─ ui.lua: Create floating windows
  └─ Display side-by-side results
```

### Web (WebAssembly)

```
Angular Component
  ├─ wasm-loader.service: Initialize Go WASM
  ├─ Call window.TriDictSearch(query)
  ├─ Parse JSON response
  └─ Render Material cards
```

### iOS (SwiftUI + SQLite)

```
ContentView
  ├─ DatabaseManager: Direct SQLite queries
  ├─ Replicate query.Query() logic in Swift
  ├─ ResultCard: Display results
  └─ AudioManager: AVSpeechSynthesizer for TTS
```

## Design Decisions

### 1. English as Pivot Language

**Rationale:**
- Most comprehensive JA-EN and ZH-EN dictionaries available
- No need for separate JA-ZH dictionary
- Simplifies maintenance and updates

**Trade-offs:**
- Slight loss of precision vs. direct JA-ZH translation
- Requires two lookups for non-English queries
- Mitigated by caching and indexing

### 2. SQLite for All Platforms

**Rationale:**
- Universal compatibility (Go, Swift, Web via WASM)
- Single-file portability
- Excellent query performance with proper indexes
- No server required

**Trade-offs:**
- WASM bundle size (~10MB with database)
- Write operations not needed (read-only)
- Perfect for dictionary use case

### 3. Top-1 Results (Phase 1)

**Rationale:**
- Simplifies UX for initial release
- Most users need primary translation only
- Reduces response size and render time

**Future:** Easily expandable to top-N with pagination

### 4. Unicode-Based Language Detection

**Rationale:**
- Fast (no ML model needed)
- Works offline
- Accurate for most inputs

**Limitations:**
- Ambiguous for pure Kanji/Hanzi (handled by trying both)
- Could add user override option

## Performance Characteristics

### Query Performance

- **Direct lookup**: O(log n) via B-tree index
- **English pivot**: O(log n) + O(m) where m = matching definitions
- **Ranking**: O(k log k) where k = candidates (typically < 10)

### Database Size

- **Sample**: ~70KB (20 word pairs)
- **Full JMdict**: ~15MB (180k entries)
- **Full CC-CEDICT**: ~5MB (120k entries)
- **Total estimated**: ~25-30MB

### WASM Bundle Size

- **Go runtime**: ~2MB
- **Core logic**: ~1MB
- **Database**: ~25-30MB
- **Total**: ~30-35MB (compresses to ~10MB gzip)

## Scalability Considerations

### Current Limitations (Phase 1)

1. Top-1 results only
2. Exact + substring matching (no fuzzy search)
3. No full-text search
4. Limited metadata (stroke order SVGs not included)

### Scaling Strategies

1. **More Results**
   - Change ranker to return top-N
   - Add pagination in UI

2. **Fuzzy Matching**
   - Add trigram indexes
   - Implement Levenshtein distance
   - Use FTS5 extension

3. **Full Metadata**
   - Add stroke order SVG paths
   - Include audio file references
   - Grammar notes and usage patterns

4. **Performance**
   - Add in-memory LRU cache
   - Preload common queries
   - Index optimization for common patterns

## Security Considerations

1. **SQL Injection**: All queries use prepared statements
2. **XSS**: JSON responses are properly escaped
3. **CORS**: Web app uses same-origin policy
4. **File Access**: Database is read-only, no write operations

## Testing Strategy

### Unit Tests
- Language detection edge cases
- Ranking algorithm correctness
- Query triangulation logic

### Integration Tests
- End-to-end CLI queries
- JSON response validation
- Cross-platform compatibility

### Performance Tests
- Query latency benchmarks
- Database index effectiveness
- WASM load time

## Future Architecture

### Planned Enhancements

1. **API Server Mode**
   ```
   Go HTTP server
     ├─ REST API endpoints
     ├─ WebSocket for real-time
     └─ Multiple concurrent users
   ```

2. **Offline-First PWA**
   ```
   Service Worker
     ├─ Cache WASM + database
     ├─ Background sync
     └─ Update notifications
   ```

3. **User Accounts**
   ```
   Additional tables:
     ├─ users
     ├─ favorites
     ├─ search_history
     └─ study_progress
   ```

## References

- [JMdict Documentation](http://www.edrdg.org/jmdict/j_jmdict.html)
- [CC-CEDICT Format](https://cc-cedict.org/wiki/format:syntax)
- [Go SQLite Driver](https://github.com/mattn/go-sqlite3)
- [WebAssembly Go Guide](https://github.com/golang/go/wiki/WebAssembly)
