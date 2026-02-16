# Design Doc: Trilingual Dictionary (English / Japanese / Chinese)

## 1. Overview
A portable, high-reliability dictionary application designed for **Triangular Translation**.
*   **Core Philosophy:** The tool accepts input in **Language A** and strictly returns detailed results in **Languages B and C**.
*   **Input Supported:** English, Japanese (Kanji/Kana), Chinese (Traditional/Simplified).
*   **Output Standard:**
    *   Chinese output is always **Simplified**.
    *   Japanese output includes Kanji/Kana.
    *   English output is standard definitions.
    *   **One-to-One Mapping (Phase 1):** The system intelligently selects the single "Best Match" (most common) word for the output languages to keep the UI clean, but the architecture supports returning multiple candidates for Phase 2.

## 2. Architecture: The "Portable Core"
To ensure reliability across 4 different platforms (CLI, iOS, Neovim, Web), the backend is designed as a **Single Portable Library** written in **Go (Golang)** that bundles a **SQLite database**.

### A. Data Strategy (The Database)
The SQLite database aggregates data from multiple open-source projects.
1.  **JMdict (Japanese):** Definitions, Readings, Priority Tags (`nf01`, `news1`).
2.  **CC-CEDICT (Chinese):** Definitions, Pinyin, Simplified/Traditional mappings.
3.  **Tatoeba (Examples):** Sentence pairs (linked by ID).
4.  **KANJIDIC2 & MakeMeAHanzi (Metadata):** Stroke order SVGs, decomposition, JLPT levels.

### B. Logic & Input Detection
The backend employs a **Heuristic Waterfall** to determine the input language:
1.  **Is ASCII?** -> Treat as **English**.
2.  **Contains Kana (Hiragana/Katakana)?** -> Treat as **Japanese**.
3.  **Contains Simplified-only Hanzi?** -> Treat as **Chinese**.
4.  **Ambiguous (Shared Hanzi/Kanji only, e.g., "骨" or "大学"):**
    *   *Strategy:* If the input consists entirely of characters shared by both languages (Han Unification), the backend must query **BOTH** the Japanese and Chinese tables.
    *   *Result:* The JSON output will contain a `results` object with populated fields for both languages if matches are found in both.

### C. The "Triangulation" Logic (The Pivot)
Since we lack a direct Japanese-to-Chinese dictionary, we use **English as the Pivot**.

**The "Best Candidate" Algorithm (Handling One-to-Many)**
*Problem:* Input "Eat" maps to multiple Japanese words (*Taberu*, *Kuu*, *Meshiagaru*).
*   **Phase 1 Strategy:** The backend performs the query but filters the result to return **only the highest-ranked entry**.
    *   **Ranking Logic:**
        1.  Check **Frequency Tags** (e.g., JMdict `nfxx` tags).
        2.  Check **Common Flag** (is marked as a common word?).
        3.  Check **Length** (shorter matches often preferred for core vocab).
*   **Phase 2 Readiness:** The JSON response `output` field is an *array*. In Phase 1, this array size is limited to `1`. In Phase 2, we simply increase the limit to `5` or `10` without breaking the front-ends.

**Triangulation Flows:**
1.  **Input: English** -> Query JPN (Rank by Freq) + Query CHN (Rank by Freq).
2.  **Input: Japanese** -> Lookup JPN word -> Get English Defs -> Search CHN using English Defs -> Rank CHN results.
3.  **Input: Chinese** -> Normalize to Simplified -> Lookup CHN word -> Get English Defs -> Search JPN using English Defs -> Rank JPN results.

### D. Audio Strategy
The backend does **not** store audio files (to save space) but returns an `audio` object:
1.  **Direct Link:** If a URL exists in the DB (e.g., from Tatoeba), provide it.
2.  **TTS Fallback:** Provide a `tts_string` and `locale` (e.g., `zh-CN`) so the Front-End can use the system's native speech engine (Web Speech API, iOS AVSpeech, `espeak`).

## 3. Data Structure (Rich JSON Output)
The backend returns a comprehensive JSON object with the following schema:
*   **Meta:** Source language, query string, and phase (1 or 2).
*   **Outputs (Object):** Contains keys for the target languages (e.g., `japanese`, `chinese`).
    *   **Headword:** The canonical form (Kanji/Hanzi).
    *   **Reading:** Kana (JP) or Pinyin (CN).
    *   **Definitions:** English glosses.
    *   **Rank:** The "Best Match" score (based on frequency).
    *   **Audio:** Object containing TTS parameters or direct audio link.
    *   **Meta (Rich Data):** Stroke count, JLPT/HSK level, decomposition.
    *   **Examples:** Array of sentence pairs (Source + English).

**Example Output (English Input "Cat"):**
```json
{
  "meta": {
    "source_lang": "English",
    "query": "cat",
    "phase": 1
  },
  "outputs": {
    "japanese": [
      {
        "headword": "猫",
        "reading": "ねこ (neko)",
        "rank": 1,
        "is_common": true,
        "tags": ["jlpt-n3"],
        "definition": "cat; feline",
        "audio": { "type": "tts", "text": "ねこ", "locale": "ja-JP" },
        "kanji_meta": {
          "strokes": 11,
          "components": ["犭", "苗"],
          "stroke_svg": "M10,20 L..."
        },
        "examples": [
          { "ja": "猫がベッドにいる。", "en": "The cat is on the bed." }
        ]
      }
    ],
    "chinese": [
      {
        "headword": "猫",
        "pinyin": "māo",
        "rank": 1,
        "definition": "cat; feline",
        "audio": { "type": "tts", "text": "猫", "locale": "zh-CN" },
        "hanzi_meta": {
          "strokes": 11,
          "components": ["犭", "苗"],
          "decomposition": "⿰犭苗",
          "stroke_svg": "M..."
        },
        "examples": [
           { "cn": "猫在床上。", "en": "The cat is on the bed." }
        ]
      }
    ]
  }
}
```

## 4. Front-End Specifications

### A. CLI (Terminal)
*   **Stack:** Go (Golang).
*   **Mode:** `dict <word>`
*   **Display:**
    *   Detects input language automatically.
    *   Displays 2 columns (one for each target language).
    *   **Rich Data:** Shows Stroke Count and JLPT/HSK levels in dim text.
    *   **Audio:** `--play` flag uses system command (`say` / `espeak`).

### B. iOS Application
*   **Target:** iPhone 17 (iOS 19+).
*   **Stack:** Swift (SwiftUI) + `SQLite.swift`.
*   **Offline Capability:** The `.sqlite` database file is bundled **inside the App Bundle**. No internet required.
*   **Distribution Strategy (AltStore + GitHub Pages):**
    *   **Method:** Sideloading via **AltStore**.
    *   **Website Integration:** The user's website (`nathanaelsrawley.com/apps/tridict/`) serves as the "AltStore Source."
        1.  **Host the IPA:** Upload the compiled app binary (`tridict.ipa`) to this path.
        2.  **Host the Metadata:** Upload a JSON file (`altstore.json`) pointing to the IPA and listing the version number.
    *   **User Flow:** The user adds the website URL to the AltStore app on their iPhone. AltStore then automatically detects updates when a new IPA is pushed to GitHub Pages.
*   **Audio Strategy:**
    *   Uses the native **AVSpeechSynthesizer** framework.
    *   The app reads the `locale` field from the backend JSON (e.g., `zh-CN`) and speaks the headword using the system's high-quality voices.
*   **UI Layout:**
    *   **Top:** Search Bar (Auto-detects language, with manual override toggle).
    *   **Body:** A vertical stack of **Two Cards** (representing the two target languages).
        *   *Card 1:* Target Language A (Headword + Definition).
        *   *Card 2:* Target Language B (Headword + Definition).
    *   **Detail View:** Tapping a card opens a full-screen view showing:
        *   **Stroke Order Animation:** Renders the SVG data from the backend.
        *   **Examples:** A list of sentence pairs.

### C. Neovim Plugin
*   **Stack:** Lua + `nui.nvim`.
*   **Filetype Name:** `tridict` (allows binding `q` to close).
*   **Layout:**
    *   **Floating Window:** Split Vertically.
    *   **Left Pane:** Target Language A.
    *   **Right Pane:** Target Language B.
*   **Input Handling:**
    *   The command `:Dict <word>` triggers the lookup.
    *   If the input is Japanese/Chinese, the plugin must support IME input or paste.
*   **Rich Data:**
    *   Uses **Virtual Text** (neovim annotation feature) to show JLPT/HSK levels next to the headword.
    *   Examples are folded by default (expand with `<Tab>`).

### D. Web Frontend (Angular on GitHub Pages)
**Integration Scope:**
This front-end is **not** a standalone application but a feature module to be integrated into an existing Angular website (`nathanaelsrawley.com`) hosted on GitHub Pages. The project scope is strictly limited to generating the necessary **Angular Components** (UI), **Routes** (e.g., `/dictionary`), and **Static Assets** (WASM binary + Database file). It does not involve rebuilding the host website.
*   **Note on APIs:** Since the host is a static GitHub Pages environment, there are no server-side API endpoints. The "Backend" is delivered as a WebAssembly (WASM) module that mimics an API client-side, allowing the Angular components to query the database locally within the user's browser.

*   **Architecture: WebAssembly (WASM)**
    *   The "Portable Core" (Go) is compiled to **WASM** (`main.wasm`).
    *   The SQLite Database is optimized (indexes stripped) and placed in `assets/dictionary.db`.
*   **Data Flow:**
    1.  User opens `nathanaelsrawley.com/dictionary`.
    2.  Angular loads `main.wasm` and downloads `dictionary.db` (cached in browser).
    3.  **Search:** Angular calls a function exposed by WASM (e.g., `TriDictSearch("cat")`).
    4.  **Result:** WASM queries the in-memory SQLite DB and returns the JSON string.
*   **UI:**
    *   Material Design Cards.
    *   **Audio:** Uses browser `window.speechSynthesis.speak()` using the `locale` provided in the JSON.
    *   **Stroke Order:** Renders the SVG paths provided in the JSON data.

## 5. Implementation Roadmap
1.  **Data Ingestion (Python Script):** Parse JMdict/CEDICT/Tatoeba -> Generate `master.db` (SQLite).
2.  **Core Library (Go):** Implement the "Best Match" logic and SQLite query wrappers.
3.  **CLI:** Wrap Core Library in a CLI interface.
4.  **WASM Adapter:** Compile Core Library to WASM for Angular.
5.  **Neovim/iOS:** Build UI wrappers around the Logic.
