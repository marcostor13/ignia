import { Component, signal, inject, OnInit, AfterViewInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PROJECTS, Project } from '../../data/projects.data';
import { NavComponent } from '../../components/nav/nav.component';
import { FooterComponent } from '../../components/footer/footer.component';

@Component({
  selector: 'app-proyecto-detalle',
  standalone: true,
  imports: [CommonModule, RouterLink, NavComponent, FooterComponent],
  templateUrl: './proyecto-detalle.component.html',
  styleUrl: './proyecto-detalle.component.scss',
})
export class ProyectoDetalleComponent implements OnInit, AfterViewInit, OnDestroy {
  private route = inject(ActivatedRoute);

  project = signal<Project | null>(null);
  otherProjects = signal<Project[]>([]);

  private observer: IntersectionObserver | null = null;

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug');
    const p = PROJECTS.find((pr) => pr.slug === slug) ?? PROJECTS[0];
    this.project.set(p);
    this.otherProjects.set(PROJECTS.filter((pr) => pr.slug !== p.slug).slice(0, 2));
  }

  ngAfterViewInit(): void {
    this.observer = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('visible'); }),
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );
    setTimeout(() => {
      const els = document.querySelectorAll('.reveal');
      els.forEach((el) => this.observer?.observe(el));
      // fallback: ensure nothing stays invisible after 1.5s
      setTimeout(() => els.forEach((el) => el.classList.add('visible')), 1500);
    }, 100);
  }

  ngOnDestroy(): void { this.observer?.disconnect(); }
}
