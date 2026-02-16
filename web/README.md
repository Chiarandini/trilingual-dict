# TriDict Web Application

Angular web application for the trilingual dictionary using WebAssembly.

## Prerequisites

- Node.js 18+ and npm
- Angular CLI: `npm install -g @angular/cli`
- Built WASM module (see `../wasm/README.md`)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Build and copy WASM files:
```bash
cd ../wasm
make install
```

3. Ensure these files exist in `src/assets/`:
   - `main.wasm` - The compiled dictionary WASM module
   - `wasm_exec.js` - Go WASM runtime
   - `dictionary.db` - SQLite database

## Development

```bash
ng serve
```

Navigate to `http://localhost:4200/`

## Build

```bash
ng build --configuration production
```

The build artifacts will be in `dist/`.

## Deployment

### Static Hosting

The app can be deployed to any static hosting service:

- **Netlify**: Drop the `dist/` folder
- **Vercel**: Connect your Git repository
- **GitHub Pages**: Use `angular-cli-ghpages`
- **AWS S3**: Upload to S3 bucket with static hosting

### Important Notes

1. **WASM MIME Type**: Ensure your server serves `.wasm` files with `application/wasm` MIME type

2. **File Size**: The WASM bundle is large (~10MB). Consider:
   - Enabling gzip/brotli compression
   - Using a CDN
   - Implementing lazy loading

3. **CORS**: If hosting WASM files separately, configure CORS headers

## Integration as a Module

To use this dictionary in your existing Angular app:

1. Copy the `src/app/services` and `src/app/dictionary` folders to your project

2. Copy WASM assets to your `src/assets/` folder

3. Import the component:

```typescript
import { DictionaryComponent } from './dictionary/dictionary.component';

@Component({
  imports: [DictionaryComponent],
  // ...
})
```

4. Use in template:

```html
<app-dictionary></app-dictionary>
```

## API

### WasmLoaderService

```typescript
const wasmLoader = inject(WasmLoaderService);

// Initialize (call once on app start)
await wasmLoader.initialize();

// Search
const result = wasmLoader.search('cat');
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

## Standalone Component

The dictionary component is standalone and can be used without NgModule:

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { DictionaryComponent } from './app/dictionary/dictionary.component';

bootstrapApplication(DictionaryComponent);
```

## Browser Support

- Chrome 57+
- Firefox 52+
- Safari 11+
- Edge 79+

WebAssembly and Web Speech API support required.

## Troubleshooting

### WASM fails to load
- Check browser console for errors
- Verify `main.wasm` and `wasm_exec.js` are in `assets/`
- Check network tab for 404 errors

### Database not found
- Ensure `dictionary.db` is in `assets/`
- Check file size (should be > 0 bytes)

### Audio doesn't work
- Web Speech API requires HTTPS (except localhost)
- Some browsers may need user interaction before playing audio
- Check browser compatibility

## License

MIT
