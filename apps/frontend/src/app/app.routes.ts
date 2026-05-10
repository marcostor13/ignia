import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/home/home.component').then((m) => m.HomeComponent),
    title: 'Ignia — Desarrollo Web a Medida',
  },
  {
    path: 'taller',
    loadComponent: () =>
      import('./pages/taller/taller.component').then((m) => m.TallerComponent),
    title: 'Taller Gratuito — De Cero a IA en 1 Día | Ignia',
  },
  { path: '**', redirectTo: '' },
];
