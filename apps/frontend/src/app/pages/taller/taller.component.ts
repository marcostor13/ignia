import {
  Component,
  signal,
  inject,
  AfterViewInit,
  OnDestroy,
  DestroyRef,
  NgZone,
} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

// Replace with your Google Cloud Console OAuth 2.0 Client ID
const GOOGLE_CLIENT_ID = '1037282001930-3fc8v51lg0tcu2fth75cbb9e8egcc5pr.apps.googleusercontent.com';

@Component({
  selector: 'app-taller',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './taller.component.html',
  styleUrl: './taller.component.scss',
})
export class TallerComponent implements AfterViewInit, OnDestroy {
  private http = inject(HttpClient);
  private destroyRef = inject(DestroyRef);
  private ngZone = inject(NgZone);

  hasScrolled = signal(false);

  formName = signal('');
  formPhone = signal('');
  formEmail = signal('');
  formSubmitted = signal(false);
  formLoading = signal(false);
  formError = signal('');
  communityUrl = signal('');

  googleReady = signal(false);

  private scrollHandler = () => this.hasScrolled.set(window.scrollY > 60);
  private observer: IntersectionObserver | null = null;

  modules = [
    {
      num: '01', icon: '🤖',
      title: 'Domina los LLMs como un profesional',
      desc: 'Qué son ChatGPT, Claude y Gemini, cuándo usar cada uno, y los 10 prompts que todo emprendedor debería tener guardados.',
      value: '$97',
    },
    {
      num: '02', icon: '📚',
      title: 'Tu asistente de investigación con NotebookLM',
      desc: 'Convierte documentos, PDFs y webs en una base de conocimiento consultable. RAG explicado simple, sin código.',
      value: '$147',
    },
    {
      num: '03', icon: '🌐',
      title: 'Publica tu web profesional HOY',
      desc: 'Crea y sube a internet una web funcional usando IA. Te vas del taller con la URL en la mano.',
      value: '$297',
    },
    {
      num: '04', icon: '🎨',
      title: 'Branding y contenido con IA',
      desc: 'Genera la identidad visual de tu marca (logo, paleta, estilo) y produce contenido para redes — una habilidad que aplicarás siempre que quieras.',
      value: '$197',
    },
    {
      num: '05', icon: '⚙️',
      title: 'Ecosistema IA: agentes, n8n y automatizaciones',
      desc: 'Las herramientas que están reemplazando equipos enteros. Saldrás con el panorama claro para saber qué explorar según tu negocio.',
      value: '$147',
    },
  ];

  outcomes = [
    'Tu primera web publicada en internet — con URL real y funcionando',
    'Un sistema de investigación con IA para tu empresa (NotebookLM)',
    'El know-how para crear branding y contenido con IA cuando quieras',
    'Claridad sobre agentes IA, n8n y automatizaciones — sin jerga técnica',
    'Acceso de por vida a la comunidad privada de WhatsApp',
  ];

  forWho = [
    { icon: '🏪', text: 'Emprendedores que quieren modernizar su negocio' },
    { icon: '💼', text: 'Freelancers que quieren multiplicar su productividad' },
    { icon: '🏢', text: 'Dueños de PyMEs que sienten que se están quedando atrás' },
    { icon: '🙋', text: 'Curiosos por la IA pero abrumados por dónde empezar' },
  ];

  notForWho = [
    'Si buscas un curso técnico de programación',
    'Si esperas resultados sin ningún esfuerzo',
  ];

  faqs = [
    { q: '¿Necesito saber programar?', a: 'No. El taller está diseñado para personas sin conocimientos técnicos. Si sabes usar una computadora, estás listo.' },
    { q: '¿Qué necesito llevar?', a: 'Una laptop con conexión a internet y una cuenta de Google activa. Nada más.' },
    { q: '¿Se va a grabar?', a: 'No. Para garantizar atención personalizada y aprovechar al máximo la sesión, es solo para asistentes en vivo.' },
    { q: '¿Tiene algún costo?', a: 'Cero. El taller es completamente gratuito. Solo limitamos los cupos a 30 personas para garantizar la calidad.' },
  ];

  openFaq = signal<number | null>(null);
  toggleFaq(i: number): void { this.openFaq.set(this.openFaq() === i ? null : i); }

  ngAfterViewInit(): void {
    window.addEventListener('scroll', this.scrollHandler, { passive: true });

    this.observer = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('visible'); }),
      { threshold: 0.08 }
    );
    setTimeout(() => {
      document.querySelectorAll('.reveal').forEach((el) => this.observer?.observe(el));
    }, 100);

    this.initGoogle();
  }

  ngOnDestroy(): void {
    window.removeEventListener('scroll', this.scrollHandler);
    this.observer?.disconnect();
  }

  private initGoogle(): void {
    const tryInit = (attempts = 0) => {
      const g = (window as any).google;
      if (!g && attempts < 20) {
        setTimeout(() => tryInit(attempts + 1), 300);
        return;
      }
      if (!g) return;

      g.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: (res: any) => this.ngZone.run(() => this.handleGoogleCredential(res)),
        auto_select: false,
      });

      const btn = document.getElementById('google-btn');
      if (btn) {
        g.accounts.id.renderButton(btn, {
          theme: 'outline',
          size: 'large',
          width: btn.parentElement?.offsetWidth ?? 340,
          text: 'signup_with',
          locale: 'es_419',
          shape: 'pill',
        });
      }

      this.googleReady.set(true);
    };

    setTimeout(() => tryInit(), 500);
  }

  private handleGoogleCredential(response: any): void {
    try {
      const raw = response.credential.split('.')[1];
      const padded = raw + '=='.slice((raw.length % 4) || 4);
      const payload = JSON.parse(atob(padded));
      this.formName.set(payload.name ?? '');
      this.formEmail.set(payload.email ?? '');
      this.submitLead();
    } catch {
      this.formError.set('Error con Google. Completá el formulario manualmente.');
    }
  }

  submitLead(): void {
    if (this.formLoading() || !this.formEmail().trim()) return;
    this.formLoading.set(true);
    this.formError.set('');

    this.http
      .post<{ whatsapp_community_url?: string }>('/api/leads', {
        email: this.formEmail().trim(),
        name: this.formName().trim() || null,
        phone: this.formPhone().trim() || null,
        source: 'taller_ia',
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.formSubmitted.set(true);
          this.communityUrl.set(res.whatsapp_community_url ?? '');
          this.formLoading.set(false);
        },
        error: () => {
          this.formError.set('Hubo un error al registrarte. Intentá de nuevo.');
          this.formLoading.set(false);
        },
      });
  }

  scrollTo(id: string): void {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}
