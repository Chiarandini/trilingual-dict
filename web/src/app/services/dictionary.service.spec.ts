import { DictionaryService } from './dictionary.service';

describe('DictionaryService', () => {
  let service: DictionaryService;

  beforeEach(() => {
    service = new DictionaryService();
  });

  describe('Language Detection', () => {
    it('should detect English', () => {
      expect(service['detectLanguage']('cat')).toBe('en');
      expect(service['detectLanguage']('hello world')).toBe('en');
      expect(service['detectLanguage']('Hello, world!')).toBe('en');
    });

    it('should detect Japanese with hiragana', () => {
      expect(service['detectLanguage']('ねこ')).toBe('ja');
      expect(service['detectLanguage']('たべる')).toBe('ja');
      expect(service['detectLanguage']('こんにちは')).toBe('ja');
    });

    it('should detect Japanese with katakana', () => {
      expect(service['detectLanguage']('カタカナ')).toBe('ja');
      expect(service['detectLanguage']('コンピュータ')).toBe('ja');
    });

    it('should detect Japanese with kanji and kana', () => {
      expect(service['detectLanguage']('食べる')).toBe('ja');
      expect(service['detectLanguage']('猫はかわいい')).toBe('ja');
    });

    it('should detect ambiguous for Chinese/kanji only', () => {
      expect(service['detectLanguage']('猫')).toBe('ambiguous');
      expect(service['detectLanguage']('你好')).toBe('ambiguous');
      expect(service['detectLanguage']('我喜欢猫')).toBe('ambiguous');
    });

    it('should handle edge cases', () => {
      expect(service['detectLanguage']('')).toBe('en');
      expect(service['detectLanguage']('   ')).toBe('en');
      expect(service['detectLanguage']('12345')).toBe('en');
    });
  });

  describe('Unicode Range Detection', () => {
    it('should detect hiragana range correctly', () => {
      const service = new DictionaryService();

      // Hiragana: U+3040-U+309F
      expect(service['detectLanguage']('\u3040')).toBe('ja'); // Start
      expect(service['detectLanguage']('\u3070')).toBe('ja'); // Middle
      expect(service['detectLanguage']('\u309F')).toBe('ja'); // End
    });

    it('should detect katakana range correctly', () => {
      const service = new DictionaryService();

      // Katakana: U+30A0-U+30FF
      expect(service['detectLanguage']('\u30A0')).toBe('ja'); // Start
      expect(service['detectLanguage']('\u30C0')).toBe('ja'); // Middle
      expect(service['detectLanguage']('\u30FF')).toBe('ja'); // End
    });

    it('should detect CJK range correctly', () => {
      const service = new DictionaryService();

      // CJK Unified: U+4E00-U+9FFF
      expect(service['detectLanguage']('\u4E00')).toBe('ambiguous'); // Start
      expect(service['detectLanguage']('\u7530')).toBe('ambiguous'); // Middle
      expect(service['detectLanguage']('\u9FFF')).toBe('ambiguous'); // End
    });
  });

  describe('Ranking Algorithm', () => {
    it('should rank common words higher', () => {
      const words = [
        { id: 1, headword: '犬', is_common: 0, frequency_rank: null },
        { id: 2, headword: '猫', is_common: 1, frequency_rank: 100 }
      ];

      const ranked = service['rankJapaneseWords'](words as any[]);
      expect(ranked[0].headword).toBe('猫');
      expect(ranked[1].headword).toBe('犬');
    });

    it('should rank lower frequency numbers as better', () => {
      const words = [
        { id: 1, headword: '食べる', is_common: 1, frequency_rank: 200 },
        { id: 2, headword: '猫', is_common: 1, frequency_rank: 100 }
      ];

      const ranked = service['rankJapaneseWords'](words as any[]);
      expect(ranked[0].headword).toBe('猫');
    });

    it('should rank shorter words higher when equal', () => {
      const words = [
        { id: 1, headword: '食べる', is_common: 1, frequency_rank: 100 },
        { id: 2, headword: '猫', is_common: 1, frequency_rank: 100 }
      ];

      const ranked = service['rankJapaneseWords'](words as any[]);
      expect(ranked[0].headword).toBe('猫'); // Shorter
    });

    it('should handle NULL frequency ranks', () => {
      const words = [
        { id: 1, headword: '珍', is_common: 0, frequency_rank: null },
        { id: 2, headword: '猫', is_common: 1, frequency_rank: 100 }
      ];

      const ranked = service['rankJapaneseWords'](words as any[]);
      expect(ranked[0].headword).toBe('猫');
      expect(ranked[1].headword).toBe('珍');
    });
  });

  describe('Score Calculation', () => {
    it('should calculate score for common word with rank', () => {
      const score = service['calculateScore'](true, 100, 1);
      // is_common(100) + (1000-100) + (100/1) = 100 + 900 + 100 = 1100
      expect(score).toBe(1100);
    });

    it('should calculate score for common word without rank', () => {
      const score = service['calculateScore'](true, null, 1);
      // is_common(100) + 0 + (100/1) = 100 + 0 + 100 = 200
      expect(score).toBe(200);
    });

    it('should calculate score for uncommon word', () => {
      const score = service['calculateScore'](false, 500, 3);
      // 0 + (1000-500) + (100/3) = 0 + 500 + 33 = 533
      expect(score).toBe(533);
    });

    it('should penalize longer words', () => {
      const score1 = service['calculateScore'](true, 100, 1);
      const score2 = service['calculateScore'](true, 100, 10);

      expect(score1).toBeGreaterThan(score2);
    });
  });

  describe('String Length Calculation', () => {
    it('should count ASCII characters correctly', () => {
      expect(service['getStringLength']('cat')).toBe(3);
      expect(service['getStringLength']('hello')).toBe(5);
    });

    it('should count Japanese characters correctly', () => {
      expect(service['getStringLength']('猫')).toBe(1);
      expect(service['getStringLength']('ねこ')).toBe(2);
      expect(service['getStringLength']('食べる')).toBe(3);
    });

    it('should count Chinese characters correctly', () => {
      expect(service['getStringLength']('猫')).toBe(1);
      expect(service['getStringLength']('你好')).toBe(2);
      expect(service['getStringLength']('我喜欢猫')).toBe(4);
    });
  });

  describe('Metadata Construction', () => {
    it('should create KanjiMeta correctly', () => {
      const word = {
        jlpt_level: 'N3',
        stroke_count: 11,
        components: '犭田',
        stroke_svg: '<svg>...</svg>'
      };

      const meta = {
        jlpt_level: word.jlpt_level,
        stroke_count: word.stroke_count,
        components: word.components,
        stroke_svg: word.stroke_svg
      };

      expect(meta.jlpt_level).toBe('N3');
      expect(meta.stroke_count).toBe(11);
    });

    it('should create HanziMeta correctly', () => {
      const word = {
        traditional: '貓',
        simplified: '猫',
        hsk_level: '1',
        stroke_count: 11,
        components: '犭苗',
        decomposition: '⿰犭苗'
      };

      const meta = {
        traditional: word.traditional !== word.simplified ? word.traditional : undefined,
        hsk_level: word.hsk_level,
        stroke_count: word.stroke_count,
        components: word.components,
        decomposition: word.decomposition
      };

      expect(meta.traditional).toBe('貓');
      expect(meta.hsk_level).toBe('1');
    });
  });

  describe('Audio Info Generation', () => {
    it('should generate Japanese audio info', () => {
      const audio = {
        type: 'tts',
        text: '猫',
        locale: 'ja-JP'
      };

      expect(audio.type).toBe('tts');
      expect(audio.locale).toBe('ja-JP');
    });

    it('should generate Chinese audio info', () => {
      const audio = {
        type: 'tts',
        text: '猫',
        locale: 'zh-CN'
      };

      expect(audio.type).toBe('tts');
      expect(audio.locale).toBe('zh-CN');
    });
  });

  describe('Service Initialization', () => {
    it('should create service instance', () => {
      expect(service).toBeTruthy();
    });

    it('should have db property initially null', () => {
      expect(service['db']).toBeNull();
    });
  });
});
