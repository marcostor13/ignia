import { Component, signal, inject, OnInit, AfterViewInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { SERVICES, Service } from '../../data/services.data';
import { PROJECTS } from '../../data/projects.data';
import { NavComponent } from '../../components/nav/nav.component';
import { FooterComponent } from '../../components/footer/footer.component';

@Component({
  selector: 'app-servicio',
  standalone: true,
  imports: [CommonModule, RouterLink, NavComponent, FooterComponent],
  templateUrl: './servicio.component.html',
  styleUrl: './servicio.component.scss',
})
export class ServicioComponent implements OnInit, AfterViewInit, OnDestroy {
  private route = inject(ActivatedRoute);

  service = signal<Service | null>(null);
  relatedProjects = signal<any[]>([]);

  private observer: IntersectionObserver | null = null;
  private routeSub: Subscription | null = null;

  ngOnInit(): void {
    this.routeSub = this.route.paramMap.subscribe((params) => {
      const id = params.get('id') as Service['id'];
      const svc = SERVICES.find((s) => s.id === id) ?? SERVICES[0];
      this.service.set(svc);
      this.relatedProjects.set(PROJECTS.filter((p) => svc.projectSlugs.includes(p.slug)));
      this.reobserve();
    });
  }

  ngAfterViewInit(): void {
    this.observer = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('visible'); }),
      { threshold: 0.1 }
    );
    this.reobserve();
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
    this.routeSub?.unsubscribe();
  }

  private reobserve(): void {
    setTimeout(() => {
      document.querySelectorAll('.reveal').forEach((el) => {
        el.classList.remove('visible');
        this.observer?.observe(el);
      });
    }, 50);
  }
}
