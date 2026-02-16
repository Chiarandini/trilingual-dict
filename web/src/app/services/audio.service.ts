import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AudioService {
  private synth: SpeechSynthesis;

  constructor() {
    this.synth = window.speechSynthesis;
  }

  speak(text: string, locale: string): void {
    // Cancel any ongoing speech
    this.synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = locale;
    utterance.rate = 0.9;

    // Try to find a native voice for the locale
    const voices = this.synth.getVoices();
    const voice = voices.find(v => v.lang.startsWith(locale.split('-')[0]));
    if (voice) {
      utterance.voice = voice;
    }

    this.synth.speak(utterance);
  }

  stop(): void {
    this.synth.cancel();
  }

  getVoices(locale?: string): SpeechSynthesisVoice[] {
    const voices = this.synth.getVoices();
    if (locale) {
      return voices.filter(v => v.lang.startsWith(locale));
    }
    return voices;
  }
}
