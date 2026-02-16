# TriDict Web Application

Angular web application for the trilingual dictionary using **SQL.js** (SQLite compiled to WebAssembly).

## Why SQL.js Instead of Go WASM?

No Go SQLite library supports WebAssembly because they all use either CGO or platform-specific code. Instead, we use:
- **SQL.js**: SQLite compiled directly to WASM (official, well-maintained)
- **TypeScript**: Port of the Go core logic (detector, ranker, triangulation)
- Same database format and API as other platforms

This results in a smaller bundle and better browser integration.

## Prerequisites

- Node.js 18+ and npm
- Angular CLI: `npm install -g @angular/cli`

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy database and SQL.js files:
```bash
# Copy database
cp ../dictionary.db src/assets/

# Copy SQL.js WASM file (automatically done by npm install)
# It will be in node_modules/sql.js/dist/
```

3. Ensure these files exist in `src/assets/`:
   - `dictionary.db` - SQLite database
   - `sql-wasm.wasm` - SQL.js WebAssembly module (auto-copied)

## Development

```bash
npm start
# or
ng serve
```

Navigate to `http://localhost:4200/`

## Build

```bash
ng build --configuration production
```

The build artifacts will be in `dist/`.

## Architecture

```
Angular App
├── DictionaryService (TypeScript)
│   ├── Language detection
│   ├── Result ranking
│   ├── Triangulation logic
│   └── SQL.js database queries
├── AudioService
│   └── Web Speech API
└── Components
    ├── DictionaryComponent
    ├── Result display
    └── Audio playback
```

## Deployment

### Static Hosting

The app can be deployed to any static hosting service:

- **Netlify**: Drop the `dist/` folder or connect Git repo
- **Vercel**: Connect your Git repository
- **GitHub Pages**: Use `angular-cli-ghpages`
- **AWS S3**: Upload to S3 bucket with static hosting
- **Cloudflare Pages**: Connect repository

### Important Notes

1. **WASM MIME Type**: Ensure your server serves `.wasm` files with `application/wasm` MIME type

2. **File Sizes**:
   - Database: ~73KB (sample), ~30MB (full)
   - SQL.js: ~800KB gzipped
   - Total bundle: ~2-3MB for sample data

3. **CORS**: If hosting database separately, configure CORS headers

4. **Service Worker**: Consider adding for offline support

## Integration as a Module

To use this dictionary in your existing Angular app:

1. Install SQL.js:
```bash
npm install sql.js @types/sql.js
```

2. Copy services and components:
```bash
cp -r src/app/services/dictionary.service.ts your-app/src/app/services/
cp -r src/app/services/audio.service.ts your-app/src/app/services/
cp -r src/app/dictionary your-app/src/app/
```

3. Copy assets:
```bash
cp src/assets/dictionary.db your-app/src/assets/
```

4. Import and use:

```typescript
import { DictionaryComponent } from './dictionary/dictionary.component';

@Component({
  imports: [DictionaryComponent],
  // ...
})
```

## API

### DictionaryService

```typescript
const dictService = inject(DictionaryService);

// Initialize (call once on app start)
await dictService.initialize();

// Search
const result = dictService.search('cat');
console.log(result.outputs);
```

### AudioService

```typescript
const audioService = inject(AudioService);

// Play text-to-speech
audioService.speak('猫', 'ja-JP');
audioService.speak('māo', 'zh-CN');

// Stop audio
audioService.stop();
```

## SQL.js Configuration

SQL.js is configured to load the WASM file from `/assets/`:

```typescript
const SQL = await initSqlJs({
  locateFile: (file) => `/assets/${file}`
});
```

Make sure `sql-wasm.wasm` is in your `src/assets/` folder. This is typically copied from `node_modules/sql.js/dist/` during build.

## Browser Support

- Chrome 57+ ✅
- Firefox 52+ ✅
- Safari 11+ ✅
- Edge 79+ ✅

Requires:
- WebAssembly support
- Web Speech API (for TTS)
- Modern JavaScript (ES2015+)

## Troubleshooting

### Database fails to load
- Check browser console for errors
- Verify `dictionary.db` is in `src/assets/`
- Check network tab for 404 errors
- Ensure file size is > 0 bytes

### SQL.js WASM not found
- Ensure `sql-wasm.wasm` is in `src/assets/`
- Check Angular asset configuration in `angular.json`
- Verify MIME type is `application/wasm`

### Audio doesn't work
- Web Speech API requires HTTPS (except localhost)
- Some browsers need user interaction before playing
- Check browser compatibility
- Try different voices in browser settings

### Build errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Angular cache
rm -rf .angular/
```

## Performance

- **First load**: ~2-3s (includes WASM + database)
- **Query time**: < 50ms (sample data)
- **Bundle size**: ~2-3MB total (production build, gzipped)

## Comparison: TypeScript vs Go WASM

| Feature | TypeScript + SQL.js | Go WASM |
|---------|-------------------|---------|
| Bundle size | ~2-3MB | ~35MB+ |
| Load time | Fast | Slow |
| Maintenance | Same logic in TS | Shared with CLI |
| Debugging | Easy in browser | Harder |
| Performance | Excellent | Good |

## Future Enhancements

- [ ] Service Worker for offline mode
- [ ] IndexedDB caching
- [ ] Progressive database loading
- [ ] Web Workers for queries
- [ ] Virtual scrolling for results

## License

MIT
