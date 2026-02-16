import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { WasmLoaderService, DictionaryResponse, LanguageOutput } from '../services/wasm-loader.service';
import { AudioService } from '../services/audio.service';

@Component({
  selector: 'app-dictionary',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dictionary.component.html',
  styleUrls: ['./dictionary.component.scss']
})
export class DictionaryComponent implements OnInit {
  searchQuery = '';
  loading = false;
  result: DictionaryResponse | null = null;
  error: string | null = null;

  japaneseOutput: LanguageOutput | null = null;
  chineseOutput: LanguageOutput | null = null;

  constructor(
    private wasmLoader: WasmLoaderService,
    private audioService: AudioService
  ) {}

  async ngOnInit() {
    this.loading = true;
    try {
      await this.wasmLoader.initialize();
    } catch (err) {
      this.error = 'Failed to load dictionary module';
      console.error(err);
    } finally {
      this.loading = false;
    }
  }

  search() {
    if (!this.searchQuery.trim()) {
      return;
    }

    this.loading = true;
    this.error = null;
    this.japaneseOutput = null;
    this.chineseOutput = null;

    try {
      this.result = this.wasmLoader.search(this.searchQuery);

      if (this.result) {
        // Separate outputs by language
        for (const output of this.result.outputs) {
          if (output.language === 'ja') {
            this.japaneseOutput = output;
          } else if (output.language === 'zh') {
            this.chineseOutput = output;
          }
        }
      }
    } catch (err) {
      this.error = 'Search failed';
      console.error(err);
    } finally {
      this.loading = false;
    }
  }

  playAudio(output: LanguageOutput) {
    if (output.audio) {
      this.audioService.speak(output.audio.text, output.audio.locale);
    }
  }

  getMetadata(output: LanguageOutput): string[] {
    const meta = output.meta;
    if (!meta) return [];

    const items: string[] = [];

    if (meta.jlpt_level) {
      items.push(`JLPT: ${meta.jlpt_level}`);
    }
    if (meta.hsk_level) {
      items.push(`HSK: ${meta.hsk_level}`);
    }
    if (meta.stroke_count) {
      items.push(`${meta.stroke_count} strokes`);
    }
    if (meta.traditional) {
      items.push(`Traditional: ${meta.traditional}`);
    }

    return items;
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      this.search();
    }
  }
}
