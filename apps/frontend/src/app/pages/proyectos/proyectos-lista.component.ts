import { Component, signal, AfterViewInit, OnDestroy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PROJECTS } from '../../data/projects.data';
import { NavComponent } from '../../components/nav/nav.component';
import { FooterComponent } from '../../components/footer/footer.component';

@Component({
  selector: 'app-proyectos-lista',
  standalone: true,
  imports: [CommonModule, RouterLink, NavComponent, FooterComponent],
  templateUrl: './proyectos-lista.component.html',
  styleUrl: './proyectos-lista.component.scss',
})
export class ProyectosListaComponent implements AfterViewInit, OnDestroy {
  projects = PROJECTS;
  private observer: IntersectionObserver | null = null;

  ngAfterViewInit(): void {
    this.observer = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('visible'); }),
      { threshold: 0.1 }
    );
    setTimeout(() => document.querySelectorAll('.reveal').forEach((el) => this.observer?.observe(el)), 100);
  }

  ngOnDestroy(): void { this.observer?.disconnect(); }
}
