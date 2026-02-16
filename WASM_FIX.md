# WASM SQLite Compatibility Fix

## Problem

`github.com/mattn/go-sqlite3` uses CGO (C bindings) which doesn't work with WebAssembly. When compiling to WASM, you get an error about missing go.sum entries.

## Solution

Use build tags to conditionally import different SQLite drivers:
- **Native builds** (CLI, tests): `github.com/mattn/go-sqlite3` (faster, uses C)
- **WASM builds**: `modernc.org/sqlite` (pure Go, WASM-compatible)

## Changes Made

### 1. Created Build-Specific Files

**core/database/db_native.go** (used for CLI, tests)
```go
//go:build !js && !wasm

package database

import (
	_ "github.com/mattn/go-sqlite3"
)

const driverName = "sqlite3"
```

**core/database/db_wasm.go** (used for WASM)
```go
//go:build js && wasm

package database

import (
	_ "modernc.org/sqlite"
)

const driverName = "sqlite"
```

### 2. Updated db.go

Changed `sql.Open("sqlite3", path)` to `sql.Open(driverName, path)` where `driverName` is set by build tags.

### 3. Updated go.mod Files

Added `modernc.org/sqlite v1.28.0` to dependencies.

## Disk Space Issue

**ERROR:** Your system ran out of disk space while downloading dependencies.

### Before Continuing

1. **Check disk space:**
   ```bash
   df -h
   ```

2. **Free up space** (choose what's appropriate):
   ```bash
   # Clean Go module cache
   go clean -modcache

   # Clean Homebrew cache
   brew cleanup

   # Clean Docker (if installed)
   docker system prune -a

   # Clean npm cache (if you have web projects)
   npm cache clean --force

   # Find large files
   du -sh ~/Downloads/* | sort -h
   ```

3. **Retry after freeing space:**
   ```bash
   cd core
   go mod tidy

   cd ../wasm
   go mod tidy

   # Try building WASM
   make build
   ```

## Testing After Fix

Once you have disk space:

### Test Native CLI (should still work)
```bash
cd cmd/dict
go build -o dict
./dict cat
```

### Test WASM Build
```bash
cd wasm
make build
# Should create main.wasm without errors
```

## How It Works

The Go compiler uses build tags to include only the appropriate file:

- When building normally: `db_native.go` is included → uses mattn/go-sqlite3
- When building with GOOS=js GOARCH=wasm: `db_wasm.go` is included → uses modernc.org/sqlite

Both drivers implement the same `database/sql` interface, so the rest of the code doesn't change.

## WASM Database Loading

Note: In WASM, you'll need to handle the database file loading differently. The WASM main.go currently uses:

```go
db, err = database.Open("/dictionary.db")
```

This expects the database to be available in the WASM virtual filesystem. You may need to:

1. Embed the database in the WASM binary (increases size)
2. Download it separately and load into virtual FS
3. Use IndexedDB in the browser

For now, the simplest approach is to load the database into the virtual FS from JavaScript before calling WASM functions.

## Alternative: SQL.js

If the bundle size is too large with modernc.org/sqlite, consider using [SQL.js](https://github.com/sql-js/sql.js/) (SQLite compiled to WASM directly) and rewriting the database layer in JavaScript/TypeScript. This would require more changes but results in a smaller bundle.
