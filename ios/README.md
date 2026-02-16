# TriDict iOS Application

SwiftUI-based iOS app for the trilingual dictionary.

## Requirements

- Xcode 15.0+
- iOS 17.0+
- Swift 6.0+

## Setup

1. Open Xcode project:
```bash
open TriDict.xcodeproj
```

2. Add `dictionary.db` to Resources:
   - Drag `../../dictionary.db` into `Resources/` folder
   - Ensure "Copy items if needed" is checked
   - Add to target: TriDict

3. Build and run on simulator or device

## Project Structure

```
TriDict/
├── TridictApp.swift           # App entry point
├── ContentView.swift          # Main search view
├── ResultCard.swift           # Result card component
├── DetailView.swift           # Detailed word view
├── DatabaseManager.swift      # SQLite interface
├── AudioManager.swift         # Text-to-speech
└── Resources/
    └── dictionary.db          # Bundled database
```

## Features

### Implemented
- ✅ Search by English, Japanese, or Chinese
- ✅ Automatic language detection
- ✅ Triangular translation via English pivot
- ✅ Text-to-speech for pronunciations
- ✅ Material-style UI cards
- ✅ Detailed view with examples and metadata

### Future Enhancements
- [ ] Stroke order animation
- [ ] Favorites/bookmarks
- [ ] Search history
- [ ] Offline first design
- [ ] Widget support
- [ ] Handwriting input
- [ ] Kanji/Hanzi drawing practice

## Database Integration

The app bundles the SQLite database directly. For updates:

1. Regenerate database: `cd data/sample && python3 generate_samples.py`
2. Copy to iOS project: `cp dictionary.db ios/TriDict/Resources/`
3. Clean build in Xcode

## Text-to-Speech

Uses `AVSpeechSynthesizer` with system voices:
- Japanese: `ja-JP`
- Chinese: `zh-CN`
- English: `en-US`

Download additional voices in Settings → Accessibility → Spoken Content → Voices.

## Performance

- Database queries run on background thread
- UI updates on main thread
- Lazy loading for large result sets
- Image caching for stroke SVGs

## Testing

### Unit Tests
- Language detection
- Database queries
- Result ranking

### UI Tests
- Search flow
- Navigation
- Audio playback

## Deployment

1. Update version/build number
2. Archive build (Product → Archive)
3. Distribute to App Store or TestFlight

## Known Issues

1. **DatabaseManager SQL queries**: Currently simplified placeholders. Need full implementation of:
   - `queryJapanese()`
   - `queryJapaneseByEnglish()`
   - `queryChinese()`
   - `queryChineseByEnglish()`

2. **Stroke order**: SVG rendering not implemented. Consider using:
   - Core Graphics path rendering
   - Third-party SVG libraries
   - Animated stroke-by-stroke drawing

3. **Bundle size**: Including full dictionary increases app size. Consider:
   - Downloading database on first launch
   - Differential updates
   - Core data migration

## License

MIT
