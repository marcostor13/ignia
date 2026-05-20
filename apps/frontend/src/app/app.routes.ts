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
  {
    path: 'servicios/:id',
    loadComponent: () =>
      import('./pages/servicios/servicio.component').then((m) => m.ServicioComponent),
    title: 'Servicios | Ignia',
  },
  {
    path: 'proyectos',
    loadComponent: () =>
      import('./pages/proyectos/proyectos-lista.component').then((m) => m.ProyectosListaComponent),
    title: 'Proyectos — Casos de Éxito | Ignia',
  },
  {
    path: 'proyectos/:slug',
    loadComponent: () =>
      import('./pages/proyectos/proyecto-detalle.component').then((m) => m.ProyectoDetalleComponent),
    title: 'Proyecto | Ignia',
  },
  { path: '**', redirectTo: '' },
];
