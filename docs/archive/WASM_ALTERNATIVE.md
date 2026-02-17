# WASM Solution: SQL.js Instead of Go SQLite

## Problem

No Go SQLite library works with WebAssembly:
- `mattn/go-sqlite3`: Uses CGO (C bindings)
- `modernc.org/sqlite`: Has platform-specific libc code
- All other options: Also use CGO

## Solution: Hybrid Approach

Keep the Go WASM for business logic, use SQL.js for database access in the browser.

### Architecture

```
Web Browser
├── SQL.js (SQLite compiled to WASM)
│   └── dictionary.db → Query results
├── TypeScript/Angular
│   ├── Database queries
│   ├── Language detection (can use Go WASM)
│   ├── Result ranking (can use Go WASM)
│   └── Triangulation logic (TypeScript version)
└── Go WASM (optional)
    └── Helper functions if needed
```

## Implementation Options

### Option 1: Pure TypeScript (Recommended)

Port the core logic to TypeScript for the web version:
- Keep Go for CLI, Neovim, iOS (native)
- Implement TypeScript version for web
- Both use the same database format
- Simpler, smaller bundle size

**Pros:**
- Smaller bundle (no Go WASM)
- Native JavaScript performance
- Easier debugging in browser

**Cons:**
- Need to maintain two implementations
- But they're small (~850 lines of Go)

### Option 2: Hybrid Go WASM + SQL.js

Use SQL.js for database, Go WASM for logic:
- SQL.js loads dictionary.db
- TypeScript does database queries
- Go WASM exports helper functions (detect language, rank results)
- TypeScript implements triangulation

**Pros:**
- Reuses some Go code
- Demonstrates WASM integration

**Cons:**
- Larger bundle size
- More complex setup

### Option 3: Full JavaScript Implementation

Simplest for web - no Go WASM at all:
- Use SQL.js for database
- Port all logic to TypeScript
- Identical API/JSON output
- Keep Go for native platforms only

## Recommended: Option 1 (Pure TypeScript for Web)

Let me create a TypeScript implementation for the web version.
