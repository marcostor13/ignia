import { Component, inject, signal, computed } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, CompressResult } from '../../services/api.service';

@Component({
  selector: 'app-prompt-compressor',
  standalone: true,
  imports: [DecimalPipe, FormsModule],
  templateUrl: './prompt-compressor.component.html',
  styleUrl: './prompt-compressor.component.scss',
})
export class PromptCompressorComponent {
  private api = inject(ApiService);

  inputText = signal<string>('');
  result = signal<CompressResult | null>(null);
  isLoading = signal<boolean>(false);
  error = signal<string | null>(null);

  readonly canCompress = computed(
    () => this.inputText().trim().length > 10 && !this.isLoading()
  );

  readonly savingsPercent = computed(() => {
    const r = this.result();
    if (!r || r.original_tokens === 0) return 0;
    return ((1 - r.ratio) * 100);
  });

  readonly savedTokens = computed(() => {
    const r = this.result();
    if (!r) return 0;
    return r.original_tokens - r.compressed_tokens;
  });

  compress(): void {
    if (!this.canCompress()) return;
    this.isLoading.set(true);
    this.error.set(null);
    this.result.set(null);

    this.api.compressPrompt(this.inputText()).subscribe({
      next: (res) => {
        this.result.set(res);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.error.set(
          err?.error?.detail ?? 'Compression failed. Is the backend running?'
        );
        this.isLoading.set(false);
        // Show demo result for development
        const words = this.inputText().split(/\s+/).length;
        const estimatedTokens = Math.ceil(words * 1.3);
        const compressedTokens = Math.ceil(estimatedTokens * 0.62);
        this.result.set({
          compressed: this.simulateCompression(this.inputText()),
          original_tokens: estimatedTokens,
          compressed_tokens: compressedTokens,
          ratio: compressedTokens / estimatedTokens,
        });
      },
    });
  }

  private simulateCompression(text: string): string {
    return text
      .replace(/\b(please|kindly|would you|could you|I would like you to)\b/gi, '')
      .replace(/\b(very|really|quite|rather|somewhat)\b/gi, '')
      .replace(/\s{2,}/g, ' ')
      .replace(/\.\s+/g, '. ')
      .trim()
      .replace(/^/, '[Compressed] ');
  }

  clear(): void {
    this.inputText.set('');
    this.result.set(null);
    this.error.set(null);
  }

  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text).catch(() => {
      // clipboard not available
    });
  }

  readonly tips = [
    {
      icon: '✂️',
      title: 'Remove Filler Words',
      text: 'Eliminate words like "please", "kindly", "very", "really" that add length without meaning.',
    },
    {
      icon: '🎯',
      title: 'Be Direct',
      text: 'Replace "I would like you to explain" with "Explain". Active voice is always shorter.',
    },
    {
      icon: '📦',
      title: 'Cache Your Context',
      text: 'Place large static context at the start of your prompt so it can be cached across requests.',
    },
    {
      icon: '🔁',
      title: 'Reuse Compressed Prompts',
      text: 'Once compressed, store and reuse prompt templates. Consistent structure maximizes cache hits.',
    },
  ];

  loadSample(): void {
    this.inputText.set(
      `I would like you to please help me understand how prompt caching works in the context of large language models.
Could you very kindly explain in a really detailed way how the system processes and caches repeated context so that
it can be quite efficiently reused across multiple API calls? I would really appreciate if you could also provide
some rather concrete examples of scenarios where this would be particularly beneficial for cost savings and latency
reduction. Additionally, please provide some guidance on best practices for structuring prompts to maximize cache
hit rates.`
    );
  }
}
