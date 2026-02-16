# TriDict WebAssembly Module

Compile the trilingual dictionary to WebAssembly for use in web browsers.

## Building

```bash
make build        # Compile to WASM
make install      # Copy to web/src/assets/
make clean        # Remove build artifacts
```

## Usage in JavaScript

```javascript
// Load WASM module
const go = new Go();
const result = await WebAssembly.instantiateStreaming(
    fetch('main.wasm'),
    go.importObject
);
go.run(result.instance);

// Wait for ready
while (!window.TriDictReady) {
    await new Promise(resolve => setTimeout(resolve, 100));
}

// Search
const resultJSON = TriDictSearch("cat");
const data = JSON.parse(resultJSON);
console.log(data);
```

## File Size Optimization

The WASM binary includes SQLite. To reduce size:

1. Compress with gzip (browsers support this natively)
2. Use `tinygo` instead of standard Go compiler (experimental)
3. Strip unused features from SQLite

## Database Loading

The database file must be accessible at `/dictionary.db` in the WASM filesystem. The web application should:

1. Fetch `dictionary.db`
2. Write to virtual filesystem before calling WASM functions
3. Or use SQL.js for pure JavaScript SQLite

## Integration with Angular

See `../web/README.md` for Angular integration instructions.
