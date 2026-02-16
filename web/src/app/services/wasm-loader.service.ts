import { Injectable } from '@angular/core';

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

declare global {
  interface Window {
    TriDictSearch: (query: string) => string;
    TriDictReady: boolean;
    Go: any;
  }
}

@Injectable({
  providedIn: 'root'
})
export class WasmLoaderService {
  private wasmReady = false;
  private loadingPromise: Promise<void> | null = null;

  constructor() {}

  async initialize(): Promise<void> {
    if (this.wasmReady) {
      return;
    }

    if (this.loadingPromise) {
      return this.loadingPromise;
    }

    this.loadingPromise = this.loadWasm();
    return this.loadingPromise;
  }

  private async loadWasm(): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      // Load wasm_exec.js
      const script = document.createElement('script');
      script.src = '/assets/wasm_exec.js';
      script.onload = async () => {
        try {
          // Instantiate WASM
          const go = new window.Go();
          const result = await WebAssembly.instantiateStreaming(
            fetch('/assets/main.wasm'),
            go.importObject
          );

          // Run the WASM module
          go.run(result.instance);

          // Wait for ready signal
          const checkReady = () => {
            if (window.TriDictReady) {
              this.wasmReady = true;
              resolve();
            } else {
              setTimeout(checkReady, 100);
            }
          };
          checkReady();
        } catch (error) {
          reject(error);
        }
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  search(query: string): DictionaryResponse | null {
    if (!this.wasmReady) {
      throw new Error('WASM module not loaded. Call initialize() first.');
    }

    try {
      const resultJSON = window.TriDictSearch(query);
      return JSON.parse(resultJSON) as DictionaryResponse;
    } catch (error) {
      console.error('Search failed:', error);
      return null;
    }
  }

  isReady(): boolean {
    return this.wasmReady;
  }
}
