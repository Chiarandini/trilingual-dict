import { Injectable } from '@angular/core';
import initSqlJs, { Database } from 'sql.js';

export interface DictionaryResponse {
  meta: {
    input_language: string;
    query: string;
  };
  outputs: LanguageOutput[];
}

export interface LanguageOutput {
  language: string;
  headword: string;
  reading?: string;
  definition: string;
  rank?: number;
  audio?: {
    type: string;
    text: string;
    locale: string;
  };
  meta?: any;
  examples?: Example[];
}

export interface Example {
  source_text: string;
  english_text: string;
}

interface JapaneseWord {
  id: number;
  headword: string;
  reading: string;
  is_common: boolean;
  frequency_rank: number | null;
  jlpt_level: string | null;
  stroke_count: number | null;
  components: string | null;
  stroke_svg: string | null;
  definitions: string[];
  examples: Example[];
}

interface ChineseWord {
  id: number;
  simplified: string;
  traditional: string;
  pinyin: string;
  is_common: boolean;
  frequency_rank: number | null;
  hsk_level: string | null;
  stroke_count: number | null;
  components: string | null;
  decomposition: string | null;
  stroke_svg: string | null;
  definitions: string[];
  examples: Example[];
}

@Injectable({
  providedIn: 'root'
})
export class DictionaryService {
  private db: Database | null = null;
  private initPromise: Promise<void> | null = null;

  async initialize(): Promise<void> {
    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = this.loadDatabase();
    return this.initPromise;
  }

  private async loadDatabase(): Promise<void> {
    try {
      // Initialize SQL.js
      const SQL = await initSqlJs({
        locateFile: (file) => `/assets/${file}`
      });

      // Load database file
      const response = await fetch('/assets/dictionary.db');
      const buffer = await response.arrayBuffer();
      this.db = new SQL.Database(new Uint8Array(buffer));

      console.log('Dictionary database loaded successfully');
    } catch (error) {
      console.error('Failed to load database:', error);
      throw error;
    }
  }

  search(query: string): DictionaryResponse | null {
    if (!this.db) {
      throw new Error('Database not initialized. Call initialize() first.');
    }

    const lang = this.detectLanguage(query);

    const response: DictionaryResponse = {
      meta: {
        input_language: lang,
        query: query
      },
      outputs: []
    };

    switch (lang) {
      case 'en':
        this.queryFromEnglish(query, response);
        break;
      case 'ja':
        this.queryFromJapanese(query, response);
        break;
      case 'zh':
        this.queryFromChinese(query, response);
        break;
      case 'ambiguous':
        this.queryAmbiguous(query, response);
        break;
    }

    return response;
  }

  private detectLanguage(input: string): string {
    let hasHiragana = false;
    let hasKatakana = false;
    let hasCJK = false;
    let hasASCII = false;

    for (const char of input) {
      const code = char.charCodeAt(0);
      if (code >= 0x3040 && code <= 0x309F) hasHiragana = true;
      if (code >= 0x30A0 && code <= 0x30FF) hasKatakana = true;
      if (code >= 0x4E00 && code <= 0x9FFF) hasCJK = true;
      if (code >= 0x20 && code <= 0x7E) hasASCII = true;
    }

    if (hasHiragana || hasKatakana) return 'ja';
    if (hasASCII && !hasCJK) return 'en';
    if (hasCJK) return 'ambiguous';
    return 'unknown';
  }

  private queryFromEnglish(query: string, response: DictionaryResponse): void {
    // Query Japanese
    const jaWords = this.queryJapaneseByEnglish(query);
    const topJa = this.rankJapanese(jaWords);
    if (topJa.length > 0) {
      response.outputs.push(this.japaneseToOutput(topJa[0]));
    }

    // Query Chinese
    const zhWords = this.queryChineseByEnglish(query);
    const topZh = this.rankChinese(zhWords);
    if (topZh.length > 0) {
      response.outputs.push(this.chineseToOutput(topZh[0]));
    }
  }

  private queryFromJapanese(query: string, response: DictionaryResponse): void {
    const jaWords = this.queryJapanese(query);
    const topJa = this.rankJapanese(jaWords);

    if (topJa.length === 0) return;

    const jaWord = topJa[0];
    response.outputs.push(this.japaneseToOutput(jaWord));

    // Pivot to Chinese
    if (jaWord.definitions.length > 0) {
      const zhWords = this.queryChineseByEnglish(jaWord.definitions[0]);
      const topZh = this.rankChinese(zhWords);
      if (topZh.length > 0) {
        response.outputs.push(this.chineseToOutput(topZh[0]));
      }
    }
  }

  private queryFromChinese(query: string, response: DictionaryResponse): void {
    const zhWords = this.queryChinese(query);
    const topZh = this.rankChinese(zhWords);

    if (topZh.length === 0) return;

    const zhWord = topZh[0];
    response.outputs.push(this.chineseToOutput(zhWord));

    // Pivot to Japanese
    if (zhWord.definitions.length > 0) {
      const jaWords = this.queryJapaneseByEnglish(zhWord.definitions[0]);
      const topJa = this.rankJapanese(jaWords);
      if (topJa.length > 0) {
        response.outputs.push(this.japaneseToOutput(topJa[0]));
      }
    }
  }

  private queryAmbiguous(query: string, response: DictionaryResponse): void {
    // Try Japanese first
    const jaWords = this.queryJapanese(query);
    if (jaWords.length > 0) {
      this.queryFromJapanese(query, response);
      return;
    }

    // Try Chinese
    const zhWords = this.queryChinese(query);
    if (zhWords.length > 0) {
      this.queryFromChinese(query, response);
    }
  }

  private queryJapanese(input: string): JapaneseWord[] {
    const stmt = this.db!.prepare(`
      SELECT id, headword, reading, is_common, frequency_rank, jlpt_level,
             stroke_count, components, stroke_svg
      FROM japanese_words
      WHERE headword = ? OR reading = ?
      ORDER BY is_common DESC, frequency_rank ASC
    `);
    stmt.bind([input, input]);

    const words: JapaneseWord[] = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      words.push({
        id: row.id as number,
        headword: row.headword as string,
        reading: row.reading as string,
        is_common: row.is_common === 1,
        frequency_rank: row.frequency_rank as number | null,
        jlpt_level: row.jlpt_level as string | null,
        stroke_count: row.stroke_count as number | null,
        components: row.components as string | null,
        stroke_svg: row.stroke_svg as string | null,
        definitions: this.getJapaneseDefinitions(row.id as number),
        examples: this.getExamples('ja', row.id as number)
      });
    }
    stmt.free();

    return words;
  }

  private queryJapaneseByEnglish(gloss: string): JapaneseWord[] {
    const stmt = this.db!.prepare(`
      SELECT DISTINCT w.id, w.headword, w.reading, w.is_common, w.frequency_rank,
             w.jlpt_level, w.stroke_count, w.components, w.stroke_svg
      FROM japanese_words w
      JOIN japanese_definitions d ON w.id = d.word_id
      WHERE d.english_gloss LIKE ?
      ORDER BY w.is_common DESC, w.frequency_rank ASC
    `);
    stmt.bind([`%${gloss.toLowerCase()}%`]);

    const words: JapaneseWord[] = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      words.push({
        id: row.id as number,
        headword: row.headword as string,
        reading: row.reading as string,
        is_common: row.is_common === 1,
        frequency_rank: row.frequency_rank as number | null,
        jlpt_level: row.jlpt_level as string | null,
        stroke_count: row.stroke_count as number | null,
        components: row.components as string | null,
        stroke_svg: row.stroke_svg as string | null,
        definitions: this.getJapaneseDefinitions(row.id as number),
        examples: this.getExamples('ja', row.id as number)
      });
    }
    stmt.free();

    return words;
  }

  private queryChinese(input: string): ChineseWord[] {
    const stmt = this.db!.prepare(`
      SELECT id, simplified, traditional, pinyin, is_common, frequency_rank,
             hsk_level, stroke_count, components, decomposition, stroke_svg
      FROM chinese_words
      WHERE simplified = ?
      ORDER BY is_common DESC, frequency_rank ASC
    `);
    stmt.bind([input]);

    const words: ChineseWord[] = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      words.push({
        id: row.id as number,
        simplified: row.simplified as string,
        traditional: row.traditional as string,
        pinyin: row.pinyin as string,
        is_common: row.is_common === 1,
        frequency_rank: row.frequency_rank as number | null,
        hsk_level: row.hsk_level as string | null,
        stroke_count: row.stroke_count as number | null,
        components: row.components as string | null,
        decomposition: row.decomposition as string | null,
        stroke_svg: row.stroke_svg as string | null,
        definitions: this.getChineseDefinitions(row.id as number),
        examples: this.getExamples('zh', row.id as number)
      });
    }
    stmt.free();

    return words;
  }

  private queryChineseByEnglish(gloss: string): ChineseWord[] {
    const stmt = this.db!.prepare(`
      SELECT DISTINCT w.id, w.simplified, w.traditional, w.pinyin, w.is_common,
             w.frequency_rank, w.hsk_level, w.stroke_count, w.components,
             w.decomposition, w.stroke_svg
      FROM chinese_words w
      JOIN chinese_definitions d ON w.id = d.word_id
      WHERE d.english_gloss LIKE ?
      ORDER BY w.is_common DESC, w.frequency_rank ASC
    `);
    stmt.bind([`%${gloss.toLowerCase()}%`]);

    const words: ChineseWord[] = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      words.push({
        id: row.id as number,
        simplified: row.simplified as string,
        traditional: row.traditional as string,
        pinyin: row.pinyin as string,
        is_common: row.is_common === 1,
        frequency_rank: row.frequency_rank as number | null,
        hsk_level: row.hsk_level as string | null,
        stroke_count: row.stroke_count as number | null,
        components: row.components as string | null,
        decomposition: row.decomposition as string | null,
        stroke_svg: row.stroke_svg as string | null,
        definitions: this.getChineseDefinitions(row.id as number),
        examples: this.getExamples('zh', row.id as number)
      });
    }
    stmt.free();

    return words;
  }

  private getJapaneseDefinitions(wordId: number): string[] {
    const stmt = this.db!.prepare(`
      SELECT english_gloss FROM japanese_definitions WHERE word_id = ?
    `);
    stmt.bind([wordId]);

    const defs: string[] = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      defs.push(row.english_gloss as string);
    }
    stmt.free();

    return defs;
  }

  private getChineseDefinitions(wordId: number): string[] {
    const stmt = this.db!.prepare(`
      SELECT english_gloss FROM chinese_definitions WHERE word_id = ?
    `);
    stmt.bind([wordId]);

    const defs: string[] = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      defs.push(row.english_gloss as string);
    }
    stmt.free();

    return defs;
  }

  private getExamples(language: string, wordId: number): Example[] {
    const stmt = this.db!.prepare(`
      SELECT source_text, english_text
      FROM examples
      WHERE language = ? AND word_id = ?
      LIMIT 5
    `);
    stmt.bind([language, wordId]);

    const examples: Example[] = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      examples.push({
        source_text: row.source_text as string,
        english_text: row.english_text as string
      });
    }
    stmt.free();

    return examples;
  }

  private rankJapanese(words: JapaneseWord[]): JapaneseWord[] {
    if (words.length === 0) return words;

    words.sort((a, b) => {
      const scoreA = this.japaneseScore(a);
      const scoreB = this.japaneseScore(b);
      return scoreB - scoreA;
    });

    return words.slice(0, 1); // Top-1
  }

  private rankChinese(words: ChineseWord[]): ChineseWord[] {
    if (words.length === 0) return words;

    words.sort((a, b) => {
      const scoreA = this.chineseScore(a);
      const scoreB = this.chineseScore(b);
      return scoreB - scoreA;
    });

    return words.slice(0, 1); // Top-1
  }

  private japaneseScore(word: JapaneseWord): number {
    let score = 0;
    if (word.is_common) score += 100;
    if (word.frequency_rank !== null) {
      score += Math.max(0, 1000 - word.frequency_rank);
    }
    score += Math.floor(100 / word.headword.length);
    return score;
  }

  private chineseScore(word: ChineseWord): number {
    let score = 0;
    if (word.is_common) score += 100;
    if (word.frequency_rank !== null) {
      score += Math.max(0, 1000 - word.frequency_rank);
    }
    score += Math.floor(100 / word.simplified.length);
    return score;
  }

  private japaneseToOutput(word: JapaneseWord): LanguageOutput {
    return {
      language: 'ja',
      headword: word.headword,
      reading: word.reading,
      definition: word.definitions.join('; '),
      rank: word.frequency_rank || undefined,
      audio: {
        type: 'tts',
        text: word.headword,
        locale: 'ja-JP'
      },
      meta: {
        jlpt_level: word.jlpt_level,
        stroke_count: word.stroke_count,
        components: word.components,
        stroke_svg: word.stroke_svg
      },
      examples: word.examples
    };
  }

  private chineseToOutput(word: ChineseWord): LanguageOutput {
    return {
      language: 'zh',
      headword: word.simplified,
      reading: word.pinyin,
      definition: word.definitions.join('; '),
      rank: word.frequency_rank || undefined,
      audio: {
        type: 'tts',
        text: word.simplified,
        locale: 'zh-CN'
      },
      meta: {
        traditional: word.traditional,
        hsk_level: word.hsk_level,
        stroke_count: word.stroke_count,
        components: word.components,
        decomposition: word.decomposition,
        stroke_svg: word.stroke_svg
      },
      examples: word.examples
    };
  }
}
