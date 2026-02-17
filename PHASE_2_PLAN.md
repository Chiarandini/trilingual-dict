# Phase 2: Multiple Word Results

## Overview

**Phase 1**: Single best match (strict word boundaries)
**Phase 2**: Multiple results with ranked ordering

### Goals

1. Return top N results instead of just the best match
2. Include compound phrases (e.g., "raccoon dog" when searching "dog")
3. Show related words and variations
4. Maintain ranking quality (best results first)

---

## Design Decisions

### 1. How Many Results?

**Recommendation**: Return top 5 results by default, configurable

**Rationale**:
- 5 results covers most use cases
- Prevents overwhelming users
- Fast to render
- Can expand to 10 with "show more" button

### 2. Ranking Strategy

Keep current prioritization but return multiple:

```
Priority Order:
1. Exact match type (0 = exact, 1 = starts-with, 2 = semicolon)
2. Word count (shorter = simpler = better)
3. is_common flag (common words first)
4. Frequency rank (lower = more common)
```

**Example for "dog"**:
1. 犬 (いぬ) - "dog" - exact, common, rank 100
2. 狗 (gǒu) - "dog" - exact, common, rank 120
3. 狸 (たぬき) - "raccoon dog" - compound, common, rank 50
4. 小犬 (こいぬ) - "puppy; small dog" - compound
5. 番犬 (ばんけん) - "watchdog; guard dog" - compound

### 3. UI Display Strategy

#### CLI (Terminal)
**Option A**: Numbered list (recommended)
```
Japanese:
  1. 犬 (いぬ) - dog (Canis familiaris)
  2. 狗 (gǒu) - dog
  3. 狸 (たぬき) - raccoon dog; tanuki
  [4-5 more...]

Chinese:
  1. 狗 (gǒu) - dog
  2. 犬 (quǎn) - dog; canine
  [3-5 more...]
```

**Option B**: Expandable detail
```
╭─ Japanese (5 results) ──────╮  ╭─ Chinese (5 results) ────────╮
│ 1. 犬 (いぬ)                │  │ 1. 狗 (gǒu)                  │
│    dog (Canis familiaris)   │  │    dog; CL:隻|只             │
│    ★ Common | JLPT N3       │  │    ★ Common | HSK 2          │
│                             │  │                              │
│ 2. 狸 (たぬき)              │  │ 2. 犬 (quǎn)                 │
│    raccoon dog              │  │    dog; canine               │
│    [Press ↓ for more]       │  │    [Press ↓ for more]        │
╰─────────────────────────────╯  ╰──────────────────────────────╯
```

#### Web (Angular)
```
┌──────────────────────────┐  ┌──────────────────────────┐
│ Japanese                 │  │ Chinese                  │
├──────────────────────────┤  ├──────────────────────────┤
│ [Card 1] 犬 (いぬ)       │  │ [Card 1] 狗 (gǒu)        │
│   dog                    │  │   dog                    │
│   ★ Common | JLPT N3     │  │   ★ Common | HSK 2       │
│   [🔊 Play]              │  │   [🔊 Play]              │
├──────────────────────────┤  ├──────────────────────────┤
│ [Card 2] 狸 (たぬき)     │  │ [Card 2] 犬 (quǎn)       │
│   raccoon dog            │  │   dog; canine            │
│   ★ Common | Rank: 50    │  │   [🔊 Play]              │
├──────────────────────────┤  ├──────────────────────────┤
│ ... 3 more results       │  │ ... 3 more results       │
│ [Show All]               │  │ [Show All]               │
└──────────────────────────┘  └──────────────────────────┘
```

#### iOS (SwiftUI)
- Scrollable list of cards
- Top result highlighted/larger
- "Show more" button at bottom
- Tap card to expand details

---

## Implementation Plan

### Step 1: Update Ranker (Go)

**File**: `core/ranker/rank.go`

**Current**:
```go
// Phase 1: Return only top result
return words[:1]
```

**Phase 2**:
```go
// Phase 2: Return top 5 results (configurable)
maxResults := 5
if len(words) <= maxResults {
    return words
}
return words[:maxResults]
```

**Enhanced**: Add configuration
```go
type RankConfig struct {
    MaxResults int
    IncludeCompounds bool
    MinFrequencyRank int  // Filter out very rare words
}

func RankJapaneseWithConfig(words []types.JapaneseWord, cfg RankConfig) []types.JapaneseWord {
    // Sort by priority
    sort.Slice(words, func(i, j int) bool {
        return japaneseScore(words[i]) > japaneseScore(words[j])
    })

    // Filter if needed
    filtered := words
    if cfg.MinFrequencyRank > 0 {
        filtered = filterByFrequency(words, cfg.MinFrequencyRank)
    }

    // Return top N
    if len(filtered) <= cfg.MaxResults {
        return filtered
    }
    return filtered[:cfg.MaxResults]
}
```

### Step 2: Update Query Functions (Go)

**File**: `core/query/triangulate.go`

**Current**: Ranker already returns limited results, just used once

**Phase 2**: No changes needed if ranker handles limiting

**Enhancement**: Add result count to response metadata
```go
response.Meta.ResultCount = map[string]int{
    "ja": len(jaWords),
    "zh": len(zhWords),
}
```

### Step 3: Update CLI Display

**File**: `cmd/dict/main.go`

**New flag**: Add `--limit` or `-n` flag
```go
var maxResults = flag.Int("n", 5, "Number of results to show")
```

**Update display function**:
```go
func outputPretty(result *types.Response) {
    jaOutputs := filterByLanguage(result.Outputs, "ja")
    zhOutputs := filterByLanguage(result.Outputs, "zh")

    fmt.Println("\nJapanese:")
    for i, output := range jaOutputs {
        fmt.Printf("  %d. %s (%s)\n", i+1, output.Headword, output.Reading)
        fmt.Printf("     %s\n", truncate(output.Definition, 60))
        if output.Meta != nil {
            fmt.Printf("     %s\n", formatMeta(output.Meta))
        }
        fmt.Println()
    }

    fmt.Println("Chinese:")
    for i, output := range zhOutputs {
        fmt.Printf("  %d. %s (%s)\n", i+1, output.Headword, output.Reading)
        fmt.Printf("     %s\n", truncate(output.Definition, 60))
        if output.Meta != nil {
            fmt.Printf("     %s\n", formatMeta(output.Meta))
        }
        fmt.Println()
    }
}
```

### Step 4: Update Web Service (TypeScript)

**File**: `web/src/app/services/dictionary.service.ts`

**Changes**:
1. Update ranker to return top N (similar to Go)
2. Update component to display multiple cards

**Component changes**:
```typescript
// dictionary.component.ts
japaneseOutputs: LanguageOutput[] = [];
chineseOutputs: LanguageOutput[] = [];
showAllJapanese = false;
showAllChinese = false;

search() {
  const result = this.dictionaryService.search(this.searchQuery);

  this.japaneseOutputs = result.outputs.filter(o => o.language === 'ja');
  this.chineseOutputs = result.outputs.filter(o => o.language === 'zh');
}

getVisibleOutputs(outputs: LanguageOutput[], showAll: boolean): LanguageOutput[] {
  return showAll ? outputs : outputs.slice(0, 3);
}
```

**Template changes**:
```html
<!-- dictionary.component.html -->
<div class="results-container">
  <div class="japanese-results">
    <h3>Japanese ({{ japaneseOutputs.length }} results)</h3>

    <div class="result-card" *ngFor="let output of getVisibleOutputs(japaneseOutputs, showAllJapanese); let i = index">
      <div class="result-number">{{ i + 1 }}</div>
      <div class="headword">{{ output.headword }} ({{ output.reading }})</div>
      <div class="definition">{{ output.definition }}</div>
      <div class="metadata">{{ getMetadata(output).join(' | ') }}</div>
      <button (click)="playAudio(output)">🔊</button>
    </div>

    <button *ngIf="japaneseOutputs.length > 3 && !showAllJapanese"
            (click)="showAllJapanese = true">
      Show {{ japaneseOutputs.length - 3 }} more
    </button>
  </div>

  <div class="chinese-results">
    <!-- Similar structure -->
  </div>
</div>
```

### Step 5: Update iOS (Swift)

**File**: `ios/TriDict/TriDict/DatabaseManager.swift`

**Changes**:
1. Update query limit from 1 to 5
2. Return array of results instead of single result

**Component changes**:
```swift
// SearchView.swift
struct ResultsListView: View {
    let outputs: [LanguageOutput]

    var body: some View {
        ScrollView {
            VStack(spacing: 12) {
                ForEach(Array(outputs.enumerated()), id: \.element.headword) { index, output in
                    ResultCardView(output: output, index: index + 1)
                }
            }
        }
    }
}

struct ResultCardView: View {
    let output: LanguageOutput
    let index: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("\(index).")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Text("\(output.headword) (\(output.reading))")
                    .font(.headline)
            }

            Text(output.definition)
                .font(.body)
                .foregroundColor(.secondary)

            if let meta = output.meta {
                Text(formatMeta(meta))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
}
```

---

## Configuration Options

### CLI Flags
```bash
dict cat              # Default: 5 results
dict cat -n 10        # Show 10 results
dict cat -n 1         # Phase 1 behavior (single result)
dict cat --all        # Show all results (unlimited)
```

### Environment Variables
```bash
export TRIDICT_MAX_RESULTS=10
dict cat
```

### Config File (Future)
```yaml
# ~/.tridict/config.yml
max_results: 10
include_compounds: true
min_frequency_rank: 5000
```

---

## Testing Strategy

### Test Cases

1. **Single exact match**
   - Query: "cat"
   - Expect: Multiple variations (猫 as pet vs wildcat)

2. **Compound phrases**
   - Query: "dog"
   - Expect: 犬 (dog), 狸 (raccoon dog), 小犬 (puppy)

3. **Rare words**
   - Query: "dog" with min_rank=100
   - Expect: Only common words, no obscure variants

4. **No results**
   - Query: "zzzzz"
   - Expect: Empty results, no crash

5. **Many results**
   - Query: "water"
   - Expect: Top 5, with indicator of more available

### Performance Testing

- Ensure returning 5 results doesn't significantly slow queries
- Database queries should still be <20ms
- Ranking algorithm should handle 50+ candidates efficiently

---

## Migration Path

### Backward Compatibility

**JSON API**: Add version field
```json
{
  "version": "2.0",
  "meta": {
    "query": "dog",
    "result_count": {"ja": 5, "zh": 5}
  },
  "outputs": [...]
}
```

**CLI**: Preserve old behavior with flag
```bash
dict cat --phase1   # Single result (old behavior)
dict cat            # Multiple results (new default)
```

---

## Rollout Plan

### Phase 2.1: Core Changes (Week 1)
1. ✅ Update ranker to return top 5
2. ✅ Update CLI display for multiple results
3. ✅ Add tests for ranking with multiple results
4. ✅ Update documentation

### Phase 2.2: Web Integration (Week 1-2)
1. ✅ Update TypeScript service
2. ✅ Update Angular component UI
3. ✅ Add "show more" functionality
4. ✅ Test with web-optimized database

### Phase 2.3: iOS Integration (Week 2)
1. ✅ Update Swift database manager
2. ✅ Update SwiftUI views
3. ✅ Add scrolling/pagination
4. ✅ Test on device

### Phase 2.4: Refinement (Week 3)
1. ✅ User feedback collection
2. ✅ Adjust ranking algorithm based on feedback
3. ✅ Performance optimization
4. ✅ Edge case handling

---

## Open Questions

1. **Result limit**: 5 or 10 default?
   - Recommendation: 5 (show more button for rest)

2. **Compound phrase filtering**: Separate section or mixed?
   - Recommendation: Mixed with ranking indicator

3. **Audio for all results**: Play all or just top?
   - Recommendation: Individual play buttons per result

4. **Mobile UX**: Scrolling or pagination?
   - Recommendation: Scrolling (more natural on mobile)

5. **Result grouping**: Group by match type?
   - Recommendation: No grouping, trust ranking

---

## Success Metrics

### Quantitative
- Query time remains <20ms
- User sees relevant results in top 3
- 80% of queries satisfied without "show more"

### Qualitative
- Users discover related words naturally
- Compound phrases provide context
- Ranking feels intuitive

---

## Next Steps

Ready to implement? Here's the order:

1. **Start with ranker** (easiest, affects all platforms)
2. **Update CLI** (fastest feedback loop)
3. **Update web** (most users)
4. **Update iOS** (can test later)

Each step can be tested independently before moving to the next.

Would you like me to start with Step 1 (updating the ranker)?
