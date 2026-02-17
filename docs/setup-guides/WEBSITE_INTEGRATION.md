# Integrating Dictionary into Your Website

## Your Website Architecture

- **Framework**: Angular 15
- **Style**: NgModule (traditional, not standalone components)
- **Location**: `/Users/nathanaelchwojko-srawkey/website-nate/nate-website`
- **Components**: `src/app/components/`
- **Routing**: Configured in `app-routing.module.ts`

## Integration Steps

### Option 1: Automated Script (Recommended)

```bash
cd /Users/nathanaelchwojko-srawkey/trilingual-dict

# Run the integration script
./integrate-to-website.sh
```

This will:
1. ✅ Copy services to `src/app/services/`
2. ✅ Copy dictionary component to `src/app/components/dictionary/`
3. ✅ Copy `dictionary.db` to `src/assets/`

### Option 2: Manual Copy

```bash
WEBSITE_DIR="/Users/nathanaelchwojko-srawkey/website-nate/nate-website"
DICT_DIR="/Users/nathanaelchwojko-srawkey/trilingual-dict"

# Create directories
mkdir -p "$WEBSITE_DIR/src/app/services"
mkdir -p "$WEBSITE_DIR/src/app/components/dictionary"

# Copy services
cp "$DICT_DIR/web/src/app/services/dictionary.service.ts" "$WEBSITE_DIR/src/app/services/"
cp "$DICT_DIR/web/src/app/services/audio.service.ts" "$WEBSITE_DIR/src/app/services/"

# Copy component
cp "$DICT_DIR/web/src/app/dictionary/dictionary.component.ts" "$WEBSITE_DIR/src/app/components/dictionary/"
cp "$DICT_DIR/web/src/app/dictionary/dictionary.component.html" "$WEBSITE_DIR/src/app/components/dictionary/"
cp "$DICT_DIR/web/src/app/dictionary/dictionary.component.scss" "$WEBSITE_DIR/src/app/components/dictionary/"

# Copy database
cp "$DICT_DIR/dictionary.db" "$WEBSITE_DIR/src/assets/"
```

## After Copying Files

### 1. Install SQL.js

```bash
cd /Users/nathanaelchwojko-srawkey/website-nate/nate-website
npm install sql.js @types/sql.js
```

### 2. Copy SQL.js WASM file

```bash
cp node_modules/sql.js/dist/sql-wasm.wasm src/assets/
```

### 3. Update Dictionary Component for Angular 15

Edit `src/app/components/dictionary/dictionary.component.ts`:

**Remove these lines:**
```typescript
standalone: true,
imports: [CommonModule, FormsModule],
```

**Change from:**
```typescript
@Component({
  selector: 'app-dictionary',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dictionary.component.html',
  styleUrls: ['./dictionary.component.scss']
})
```

**To:**
```typescript
@Component({
  selector: 'app-dictionary',
  templateUrl: './dictionary.component.html',
  styleUrls: ['./dictionary.component.scss']
})
```

### 4. Add to app.module.ts

Edit `src/app/app.module.ts`:

**Add imports at the top:**
```typescript
import { DictionaryComponent } from './components/dictionary/dictionary.component';
import { DictionaryService } from './services/dictionary.service';
import { AudioService } from './services/audio.service';
```

**Add to declarations array:**
```typescript
@NgModule({
  declarations: [
    // ... existing components
    DictionaryComponent
  ],
  providers: [
    DictionaryService,
    AudioService
  ],
  // ...
})
```

### 5. Add Route

Edit `src/app/app-routing.module.ts`:

**Add import:**
```typescript
import { DictionaryComponent } from './components/dictionary/dictionary.component';
```

**Add route to routes array:**
```typescript
const routes: Routes = [
  // ... existing routes
  {path: 'dictionary', component: DictionaryComponent},
  {path: "**", component: NotFoundComponent}  // Keep this last
];
```

### 6. Add to Navigation (Optional)

If you have a navigation menu in your header component, add:

```html
<a routerLink="/dictionary">Dictionary</a>
```

## File Structure After Integration

```
nate-website/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── about/
│   │   │   ├── blog/
│   │   │   ├── dictionary/              ← NEW
│   │   │   │   ├── dictionary.component.ts
│   │   │   │   ├── dictionary.component.html
│   │   │   │   └── dictionary.component.scss
│   │   │   └── ...
│   │   ├── services/                    ← NEW (or existing)
│   │   │   ├── dictionary.service.ts    ← NEW
│   │   │   └── audio.service.ts         ← NEW
│   │   ├── app.module.ts                ← MODIFIED
│   │   └── app-routing.module.ts        ← MODIFIED
│   └── assets/
│       ├── dictionary.db                ← NEW
│       ├── sql-wasm.wasm               ← NEW
│       └── ...
└── package.json                         ← MODIFIED (new dependencies)
```

## Testing

1. **Start development server:**
   ```bash
   cd /Users/nathanaelchwojko-srawkey/website-nate/nate-website
   npm start
   ```

2. **Navigate to dictionary:**
   ```
   http://localhost:4200/dictionary
   ```

3. **Test searches:**
   - cat
   - 猫
   - ねこ
   - dog
   - 吃

## Troubleshooting

### Error: "Can't resolve 'sql.js'"
```bash
npm install sql.js @types/sql.js
```

### Error: "Database not found"
```bash
# Check if database exists
ls -lh src/assets/dictionary.db

# If missing, copy it
cp /Users/nathanaelchwojko-srawkey/trilingual-dict/dictionary.db src/assets/
```

### Error: "sql-wasm.wasm 404"
```bash
# Copy WASM file
cp node_modules/sql.js/dist/sql-wasm.wasm src/assets/
```

### Error: Component not declared
- Make sure you added `DictionaryComponent` to declarations in `app.module.ts`
- Make sure you removed `standalone: true` from the component

### Styling looks off
- The component uses its own SCSS
- May need to adjust styles to match your website theme
- Check `dictionary.component.scss` and modify as needed

## Customization

### Match Your Website Theme

Edit `src/app/components/dictionary/dictionary.component.scss` to match your website's color scheme:

```scss
// Example: Use your website's primary color
.search-button {
  background: var(--your-primary-color);
}

.result-card h2 {
  color: var(--your-accent-color);
}
```

### Add to Main Navigation

Edit your header component to add a dictionary link:

```html
<nav>
  <a routerLink="/about">About</a>
  <a routerLink="/books">Books</a>
  <a routerLink="/dictionary">Dictionary</a>  <!-- NEW -->
  <!-- other links -->
</nav>
```

## Summary

✅ **Copy files** with script or manually
✅ **Install dependencies**: `sql.js` and `@types/sql.js`
✅ **Remove standalone** from component
✅ **Add to module** declarations and providers
✅ **Add route** to routing module
✅ **Copy WASM file** to assets
✅ **Test** at `/dictionary` route

The dictionary will integrate seamlessly with your existing Angular 15 website!
