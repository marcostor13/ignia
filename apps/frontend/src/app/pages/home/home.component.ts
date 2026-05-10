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
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements AfterViewInit, OnDestroy {
  @ViewChild('chatContainer') chatContainer!: ElementRef<HTMLDivElement>;

  private http = inject(HttpClient);
  private destroyRef = inject(DestroyRef);

  // ── Chat signals ──────────────────────────────────────────────────────────
  messages = signal<ChatMessage[]>([]);
  inputText = signal<string>('');
  isLoading = signal<boolean>(false);
  hasScrolled = signal<boolean>(false);

  // ── Lead form signals ─────────────────────────────────────────────────────
  email = signal<string>('');
  formName = signal<string>('');
  formSubmitted = signal<boolean>(false);
  formLoading = signal<boolean>(false);
  formError = signal<string>('');
  communityUrl = signal<string>('');

  private observer: IntersectionObserver | null = null;
  private scrollHandler = () => {
    this.hasScrolled.set(window.scrollY > 60);
  };

  // ── Static data ───────────────────────────────────────────────────────────
  projects = [
    {
      title: 'E-Commerce Especializado',
      category: 'Plataforma Digital',
      description:
        'Tienda online con catálogo dinámico, pagos integrados y panel de administración personalizado.',
      icon: '🛒',
      gradient: 'linear-gradient(135deg, #1a1a3e, #2d2db0)',
      tags: ['Angular', 'FastAPI', 'PostgreSQL', 'Stripe'],
    },
    {
      title: 'Dashboard Analytics',
      category: 'Herramienta Interna',
      description:
        'Panel de métricas en tiempo real para equipo de ventas con visualizaciones interactivas.',
      icon: '📊',
      gradient: 'linear-gradient(135deg, #1a1010, #FF3A5C55)',
      tags: ['React', 'Python', 'WebSockets', 'TimescaleDB'],
    },
    {
      title: 'Landing de Alto Impacto',
      category: 'Marketing',
      description:
        'Sitio de conversión con IA integrada, A/B testing y optimización de velocidad Core Web Vitals.',
      icon: '🚀',
      gradient: 'linear-gradient(135deg, #0a1a10, #FF603533)',
      tags: ['Next.js', 'Strapi', 'Vercel', 'IA'],
    },
    {
      title: 'App de Gestión',
      category: 'SaaS',
      description:
        'Plataforma multi-tenant para gestión de proyectos con notificaciones en tiempo real.',
      icon: '⚙️',
      gradient: 'linear-gradient(135deg, #1a0a2e, #6b21a855)',
      tags: ['Angular', 'Node.js', 'Firebase', 'PWA'],
    },
  ];

  pillars = [
    {
      icon: '⚡',
      title: 'Tecnologías modernas',
      description:
        'Angular, React, Next.js, Python, IA integrada. Usamos el stack correcto para cada proyecto, no el de moda.',
    },
    {
      icon: '🗺️',
      title: 'Planificación completa',
      description:
        'Desde el brief inicial hasta el wireframe aprobado. Nada entra a desarrollo sin estar bien definido.',
    },
    {
      icon: '🚀',
      title: 'Puesta en producción',
      description:
        'Deploy en AWS, GCP, Netlify o Vercel. CI/CD, monitoreo y performance desde el día uno.',
    },
    {
      icon: '🔄',
      title: 'Mejora continua',
      description:
        'Post-entrega no es el final. Acompañamiento, analytics, iteraciones y soporte cuando lo necesitas.',
    },
  ];

  process = [
    { label: 'Planificación' },
    { label: 'Diseño' },
    { label: 'Desarrollo' },
    { label: 'Producción' },
    { label: 'Mejora continua' },
  ];

  painPoints = [
    { icon: '😩', text: 'Tu web actual no genera consultas ni ventas' },
    { icon: '🔍', text: 'Tu negocio no aparece en buscadores ni redes' },
    { icon: '📱', text: 'Tu competencia ya tiene plataforma online' },
    { icon: '⏰', text: 'Perdés tiempo en tareas que podrían automatizarse' },
  ];

  benefits = [
    {
      icon: '🎨',
      title: 'Diseño único',
      desc: 'Nada de templates. Tu identidad digital, construida desde cero para diferenciarte.',
    },
    {
      icon: '⚡',
      title: 'Tecnología moderna',
      desc: 'Angular, React, Python, IA. Usamos lo que mejor resuelve tu problema, no lo de moda.',
    },
    {
      icon: '📈',
      title: 'Resultados medibles',
      desc: 'Analytics integrado desde el día uno. Sabés exactamente qué funciona y qué mejorar.',
    },
  ];

  processSteps = [
    {
      num: '01',
      icon: '🗺️',
      title: 'Planificación',
      desc: 'Definimos juntos el alcance, funcionalidades y plazos reales.',
    },
    {
      num: '02',
      icon: '🎨',
      title: 'Diseño',
      desc: 'Wireframes y prototipo aprobado antes de escribir código.',
    },
    {
      num: '03',
      icon: '⚙️',
      title: 'Desarrollo',
      desc: 'Sprints de 2 semanas. Ves avances reales, no solo reportes.',
    },
    {
      num: '04',
      icon: '🚀',
      title: 'Lanzamiento',
      desc: 'Deploy en producción con CI/CD, SSL y monitoreo incluido.',
    },
    {
      num: '05',
      icon: '🔄',
      title: 'Mejora continua',
      desc: 'Analytics, soporte y actualizaciones post-entrega.',
    },
  ];

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  ngAfterViewInit(): void {
    this.messages.set([
      {
        role: 'assistant',
        content:
          '¡Hola! Soy el asistente de Ignia 👋 ¿En qué puedo ayudarte hoy?',
      },
    ]);

    window.addEventListener('scroll', this.scrollHandler, { passive: true });

    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1 }
    );

    setTimeout(() => {
      document.querySelectorAll('.reveal').forEach((el) => {
        this.observer?.observe(el);
      });
    }, 100);
  }

  ngOnDestroy(): void {
    window.removeEventListener('scroll', this.scrollHandler);
    this.observer?.disconnect();
  }

  // ── Lead form ─────────────────────────────────────────────────────────────
  submitLead(): void {
    if (this.formLoading() || !this.email().trim()) return;

    this.formLoading.set(true);
    this.formError.set('');

    this.http
      .post<{ whatsapp_community_url?: string }>('/api/leads', {
        email: this.email(),
        name: this.formName(),
        source: 'taller',
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.formSubmitted.set(true);
          this.communityUrl.set(res.whatsapp_community_url ?? '');
          this.formLoading.set(false);
        },
        error: () => {
          this.formError.set('Hubo un error. Intentá de nuevo.');
          this.formLoading.set(false);
        },
      });
  }

  // ── Chat ──────────────────────────────────────────────────────────────────
  sendMessage(): void {
    const text = this.inputText().trim();
    if (!text || this.isLoading()) return;

    this.messages.update((msgs) => [...msgs, { role: 'user', content: text }]);
    this.inputText.set('');
    this.isLoading.set(true);
    this.scrollChatToBottom();

    this.http
      .post<{ message?: string; response?: string; content?: string }>(
        '/api/chat',
        { agent_id: 'website_agent', message: text }
      )
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          const content =
            res.message ??
            res.response ??
            res.content ??
            'Gracias por tu mensaje. ¡Nos pondremos en contacto contigo pronto!';
          this.messages.update((msgs) => [
            ...msgs,
            { role: 'assistant', content },
          ]);
          this.isLoading.set(false);
          this.scrollChatToBottom();
        },
        error: () => {
          this.messages.update((msgs) => [
            ...msgs,
            {
              role: 'assistant',
              content:
                'Estaré disponible cuando el servidor esté activo. Mientras tanto, escríbenos a hola@ignia.dev',
            },
          ]);
          this.isLoading.set(false);
          this.scrollChatToBottom();
        },
      });
  }

  scrollTo(id: string): void {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  private scrollChatToBottom(): void {
    setTimeout(() => {
      if (this.chatContainer?.nativeElement) {
        const el = this.chatContainer.nativeElement;
        el.scrollTop = el.scrollHeight;
      }
    }, 50);
  }

  trackByFn(index: number): number {
    return index;
  }
}
