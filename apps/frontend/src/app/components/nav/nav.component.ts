import { Component, signal, HostListener, Input } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-nav',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './nav.component.html',
  styleUrl: './nav.component.scss',
})
export class NavComponent {
  @Input() theme: 'light' | 'dark' = 'light';

  hasScrolled = signal(false);
  menuOpen = signal(false);
  serviciosOpen = signal(false);

  @HostListener('window:scroll', [])
  onScroll() {
    this.hasScrolled.set(window.scrollY > 40);
  }

  toggleMenu() {
    this.menuOpen.update((v) => !v);
  }

  toggleServicios(e: Event) {
    e.stopPropagation();
    this.serviciosOpen.update((v) => !v);
  }

  @HostListener('document:click')
  closeDropdowns() {
    this.serviciosOpen.set(false);
  }
}
