import {
  Component,
  inject,
  signal,
  computed,
  OnInit,
  DestroyRef,
} from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval } from 'rxjs';
import { switchMap, startWith } from 'rxjs/operators';
import { ApiService, TokenStats } from '../../services/api.service';

interface BarEntry {
  label: string;
  value: number;
  color: string;
  percent: number;
}

@Component({
  selector: 'app-token-stats',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './token-stats.component.html',
  styleUrl: './token-stats.component.scss',
})
export class TokenStatsComponent implements OnInit {
  private api = inject(ApiService);
  private destroyRef = inject(DestroyRef);

  stats = signal<TokenStats | null>(null);
  isLoading = signal<boolean>(true);
  error = signal<string | null>(null);
  lastUpdated = signal<Date | null>(null);

  readonly barEntries = computed<BarEntry[]>(() => {
    const s = this.stats();
    if (!s) return [];
    const maxVal = Math.max(
      s.total_input_tokens,
      s.total_output_tokens,
      s.total_cached_tokens,
      1
    );
    return [
      {
        label: 'Input',
        value: s.total_input_tokens,
        color: '#7c3aed',
        percent: (s.total_input_tokens / maxVal) * 100,
      },
      {
        label: 'Output',
        value: s.total_output_tokens,
        color: '#a78bfa',
        percent: (s.total_output_tokens / maxVal) * 100,
      },
      {
        label: 'Cached',
        value: s.total_cached_tokens,
        color: '#22c55e',
        percent: (s.total_cached_tokens / maxVal) * 100,
      },
      {
        label: 'Saved',
        value: s.total_tokens_saved,
        color: '#4ade80',
        percent: (s.total_tokens_saved / maxVal) * 100,
      },
    ];
  });

  readonly savingsPercent = computed(() => {
    const s = this.stats();
    if (!s) return 0;
    return Math.min(100, Math.max(0, s.savings_percentage));
  });

  readonly formattedCost = computed(() => {
    const s = this.stats();
    if (!s) return '$0.0000';
    return `$${s.total_cost_usd.toFixed(4)}`;
  });

  ngOnInit(): void {
    interval(10_000)
      .pipe(
        startWith(0),
        switchMap(() => {
          this.isLoading.set(true);
          return this.api.getTokenStats();
        }),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe({
        next: (stats) => {
          this.stats.set(stats);
          this.isLoading.set(false);
          this.error.set(null);
          this.lastUpdated.set(new Date());
        },
        error: (err) => {
          this.error.set('Could not load token stats.');
          this.isLoading.set(false);
          // Use demo data when backend unavailable
          if (!this.stats()) {
            this.stats.set({
              total_input_tokens: 24580,
              total_output_tokens: 8120,
              total_cached_tokens: 18200,
              total_tokens_saved: 15340,
              total_cost_usd: 0.0183,
              savings_percentage: 62.5,
              records: [],
            });
          }
        },
      });
  }

  formatNumber(n: number): string {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return n.toString();
  }

  formatTime(date: Date | null): string {
    if (!date) return '—';
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
}
