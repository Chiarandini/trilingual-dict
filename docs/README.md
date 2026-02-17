# Documentation Directory

## Main Documentation

- **[../README.md](../README.md)** - Main project README with quick start
- **[../ARCHITECTURE.md](../ARCHITECTURE.md)** - Technical architecture and design decisions
- **[../STATUS.md](../STATUS.md)** - Current project status and roadmap

## Setup Guides

Located in `setup-guides/`:
- **[WEB_APP_SETUP.md](setup-guides/WEB_APP_SETUP.md)** - Setting up the web application
- **[WEBSITE_INTEGRATION.md](setup-guides/WEBSITE_INTEGRATION.md)** - Integrating into your website

## Component Documentation

Each component has its own README:
- `cmd/dict/` - CLI application (see main README)
- `nvim/README.md` - Neovim plugin setup
- `web/README.md` - Angular web application
- `ios/README.md` - iOS application
- `wasm/README.md` - WebAssembly notes

## Archive

Located in `archive/`:

Implementation notes and historical documentation:
- **IMPLEMENTATION_COMPLETE.md** - Initial implementation completion
- **MODULE_PATHS_UPDATED.md** - Go module path updates
- **WASM_FIX.md** - WASM compatibility investigation
- **WASM_ALTERNATIVE.md** - Alternative WASM approaches
- **WASM_SOLUTION.md** - Final WASM solution (TypeScript)
- **INTEGRATION_COMPLETE.md** - Website integration completion
- **FIXES_APPLIED.md** - TypeScript and webpack fixes

These files document the development journey but are not needed for using the project.

## Organization

```
docs/
├── README.md (this file)
├── setup-guides/          # How-to guides
│   ├── WEB_APP_SETUP.md
│   └── WEBSITE_INTEGRATION.md
└── archive/              # Historical notes
    ├── IMPLEMENTATION_COMPLETE.md
    ├── MODULE_PATHS_UPDATED.md
    ├── WASM_FIX.md
    ├── WASM_ALTERNATIVE.md
    ├── WASM_SOLUTION.md
    ├── INTEGRATION_COMPLETE.md
    └── FIXES_APPLIED.md
```

## Quick Links

**Getting Started**:
1. [Main README](../README.md) - Start here
2. [Architecture](../ARCHITECTURE.md) - Understand the design
3. [Status](../STATUS.md) - See what's working

**Setup**:
- [Web App](setup-guides/WEB_APP_SETUP.md)
- [Website Integration](setup-guides/WEBSITE_INTEGRATION.md)
- [Neovim](../nvim/README.md)

**Reference**:
- [Go Core Library](../core/) - Source code
- [Data Schema](../data/schema.sql) - Database structure
