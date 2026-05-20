import {
  Component,
  signal,
  inject,
  AfterViewInit,
  ViewChild,
  ElementRef,
  DestroyRef,
  OnDestroy,
} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NavComponent } from '../../components/nav/nav.component';
import { FooterComponent } from '../../components/footer/footer.component';
import { PROJECTS } from '../../data/projects.data';
import { SERVICES } from '../../data/services.data';

const BOOKING_URL =
  'https://outlook.office.com/bookwithme/user/a9497d377a0445eea242b5cb788396bd@ignia.site/meetingtype/Eimuu4q_r0-V7IA3PC_42w2?anonymous&ismsaljsauthenabled&ep=mlink';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, NavComponent, FooterComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements AfterViewInit, OnDestroy {
  @ViewChild('chatContainer') chatContainer!: ElementRef<HTMLDivElement>;

  private http = inject(HttpClient);
  private destroyRef = inject(DestroyRef);
  messages = signal<ChatMessage[]>([]);
  inputText = signal<string>('');
  isLoading = signal<boolean>(false);
  heroLoaded = signal(false);
  services = SERVICES;
  projects = PROJECTS;

  private observer: IntersectionObserver | null = null;

  ngAfterViewInit(): void {
    this.messages.set([{
      role: 'assistant',
      content: '¡Hola! Soy el asistente de Ignia. ¿En qué puedo ayudarte hoy? Cuéntame sobre tu proyecto.',
    }]);

    setTimeout(() => this.heroLoaded.set(true), 80);

    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('visible');
            const el = e.target as HTMLElement;
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -30px 0px' }
    );

    setTimeout(() => {
      document
        .querySelectorAll(
          '.reveal, .reveal-left, .reveal-right, .reveal-scale, .reveal-fade, [data-anim]'
        )
        .forEach((el) => this.observer?.observe(el));
    }, 120);
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
  }

  sendMessage(): void {
    const text = this.inputText().trim();
    if (!text || this.isLoading()) return;

    // Capture history BEFORE adding the new user message
    const history = this.messages().map(m => ({ role: m.role, content: m.content }));

    this.messages.update((msgs) => [...msgs, { role: 'user', content: text }]);
    this.inputText.set('');
    this.isLoading.set(true);
    this.scrollChatToBottom();

    this.http
      .post<{ message?: string; response?: string; content?: string; action?: string }>(
        '/api/chat',
        { agent_id: 'website_agent', message: text, conversation_history: history }
      )
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          const content =
            res.message ?? res.response ?? res.content ?? '¡Gracias! Nos pondremos en contacto pronto.';
          this.messages.update((msgs) => [...msgs, { role: 'assistant', content }]);
          if (res.action === 'open_calendar') {
            window.open(BOOKING_URL, '_blank', 'noopener,noreferrer');
          }
          this.isLoading.set(false);
          this.scrollChatToBottom();
        },
        error: () => {
          this.messages.update((msgs) => [
            ...msgs,
            {
              role: 'assistant',
              content:
                'Estaré disponible cuando el servidor esté activo. Mientras tanto: admin@ignia.site',
            },
          ]);
          this.isLoading.set(false);
          this.scrollChatToBottom();
        },
      });
  }

  private scrollChatToBottom(): void {
    setTimeout(() => {
      if (this.chatContainer?.nativeElement) {
        this.chatContainer.nativeElement.scrollTop =
          this.chatContainer.nativeElement.scrollHeight;
      }
    }, 50);
  }

  trackByFn(index: number): number {
    return index;
  }
}
