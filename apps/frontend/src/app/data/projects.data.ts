export interface Project {
  slug: string;
  title: string;
  category: string;
  service: 'plataformas-web' | 'consultoria-ti' | 'automatizacion';
  client: string;
  tagline: string;
  description: string;
  challenge: string;
  solution: string;
  results: { label: string; value: string }[];
  technologies: string[];
  accent: string;
  accentLight: string;
  tags: string[];
  year: string;
  image?: string;
}

export const PROJECTS: Project[] = [
  {
    slug: 'asisteya',
    title: 'AsisteYa',
    category: 'ERP de Recursos Humanos',
    service: 'plataformas-web',
    client: 'AsisteYa!',
    tagline: 'ERP de RRHH con biometría facial, huella digital y cálculo de planilla completo.',
    description:
      'Desarrollamos una plataforma ERP completa para la gestión de recursos humanos: control de asistencia con reconocimiento facial y huella digital, fotocheck digital, cálculo automático de planilla y reportes en tiempo real para múltiples sedes.',
    challenge:
      'Las empresas clientes gestionaban la asistencia y planilla de forma manual, con errores frecuentes en los cálculos, dificultad para controlar asistencia en múltiples sedes y procesos de pago lentos que generaban conflictos laborales.',
    solution:
      'Construimos un ERP modular con Angular en el frontend y NestJS en el backend, integrado con dispositivos biométricos (facial y huella) y generación de fotocheck. El motor de planilla calcula automáticamente horas extras, descuentos, bonos y retenciones según la normativa vigente.',
    results: [
      { label: 'Reducción en errores de planilla', value: '95%' },
      { label: 'Tiempo de cierre de planilla', value: '2 hs vs 2 días' },
      { label: 'Sedes controladas en tiempo real', value: 'Multi-sede' },
      { label: 'Métodos biométricos integrados', value: '3' },
    ],
    technologies: ['Angular', 'NestJS', 'MongoDB Atlas', 'AWS', 'Biometría Facial', 'Huella Digital'],
    accent: '#1E1B4B',
    accentLight: '#3730A3',
    tags: ['RRHH', 'ERP', 'Biometría', 'Angular'],
    year: '2026',
    image: '/jobs/asisteya.png',
  },
  {
    slug: 'viatika',
    title: 'Viatika',
    category: 'Plataforma Web',
    service: 'plataformas-web',
    client: 'Viatika',
    tagline: 'Administración de viáticos, anticipos y contabilidad de gastos por proyecto.',
    description:
      'Plataforma web para la gestión integral de viáticos corporativos: solicitud de anticipos, aprobación por niveles jerárquicos, liquidación de gastos y reportes contables por proyecto, área y colaborador.',
    challenge:
      'La gestión de viáticos se realizaba por correo y hojas de cálculo, generando demoras en aprobaciones, falta de trazabilidad en los anticipos y reportes contables que tardaban días en consolidarse.',
    solution:
      'Desarrollamos una plataforma con flujos de aprobación configurables por niveles, módulo de anticipos con seguimiento de estado, liquidación de gastos con comprobantes digitales y exportación automática a contabilidad por centro de costo y proyecto.',
    results: [
      { label: 'Tiempo de aprobación de anticipos', value: '-80%' },
      { label: 'Trazabilidad de gastos', value: '100%' },
      { label: 'Reportes contables automáticos', value: 'En tiempo real' },
      { label: 'Eliminación de procesos manuales', value: 'Total' },
    ],
    technologies: ['Angular', 'NestJS', 'MongoDB Atlas', 'AWS'],
    accent: '#7F1D1D',
    accentLight: '#DC2626',
    tags: ['Finanzas', 'Viáticos', 'Angular', 'NestJS'],
    year: '2026',
    image: '/jobs/viatika.png',
  },
  {
    slug: 'tecmeing',
    title: 'ERP Tecmeing',
    category: 'Consultoría & ERP a medida',
    service: 'consultoria-ti',
    client: 'Tecmeing',
    tagline: 'Consultoría de procesos y ERP a medida para empresa de estructuras metálicas para minería.',
    description:
      'Realizamos una consultoría integral de procesos para Tecmeing, empresa especializada en estructuras metálicas para el sector minero. Identificamos y mapeamos más de 20 procesos de distintas áreas y construimos un ERP a medida para automatizarlos.',
    challenge:
      'Tecmeing operaba con procesos completamente manuales y desconectados entre áreas: cotización, producción, logística, compras y administración no compartían información, generando retrasos, errores y duplicación de trabajo.',
    solution:
      'Ejecutamos un diagnóstico completo de los 20+ procesos identificados, definimos la arquitectura del ERP y lo construimos módulo por módulo: cotizaciones, órdenes de trabajo, control de inventario, compras, producción y reportes gerenciales unificados.',
    results: [
      { label: 'Procesos identificados y mapeados', value: '20+' },
      { label: 'Áreas integradas en el ERP', value: '6' },
      { label: 'Reducción de tiempo en cotizaciones', value: '-70%' },
      { label: 'Visibilidad de operaciones', value: 'Tiempo real' },
    ],
    technologies: ['Angular', 'NestJS', 'PostgreSQL', 'AWS', 'Consultoría de Procesos'],
    accent: '#0F172A',
    accentLight: '#334155',
    tags: ['Minería', 'ERP', 'Consultoría', 'Automatización'],
    year: '2025',
    image: 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=1200&q=85',
  },
  {
    slug: 'redline',
    title: 'Redline Installers',
    category: 'Plataforma Web + Generación de Leads',
    service: 'plataformas-web',
    client: 'Redline Installers (USA)',
    tagline: 'Plataforma de cotización y captación de leads para empresa especialista en almacenes en USA.',
    description:
      'Redline Installers, con 34+ años instalando sistemas de almacenamiento y estanterías para pallets en Illinois y todo USA, necesitaba digitalizar su proceso comercial completo. Desarrollamos una plataforma web para captar leads, gestionar cotizaciones y optimizar su funnel de ventas.',
    challenge:
      'Todo el proceso de cotización y obtención de leads se realizaba manualmente por teléfono y correo. Esto limitaba el alcance comercial, generaba tiempos de respuesta lentos y no permitía escalar el negocio sin aumentar el equipo de ventas.',
    solution:
      'Diseñamos y desarrollamos una plataforma web con formularios inteligentes de cotización (servicio, proyecto, presupuesto, contacto), integración de leads al CRM, panel administrativo para seguimiento y automatización de respuestas iniciales al cliente.',
    results: [
      { label: 'Leads digitales capturados', value: '+300%' },
      { label: 'Tiempo de respuesta a prospects', value: '-85%' },
      { label: 'Cotizaciones automatizadas', value: '100%' },
      { label: 'Cobertura geográfica expandida', value: 'Nacional USA' },
    ],
    technologies: ['Angular', 'NestJS', 'MongoDB Atlas', 'AWS', 'CRM Integration'],
    accent: '#111827',
    accentLight: '#DC2626',
    tags: ['USA', 'Leads', 'Cotizaciones', 'Angular'],
    year: '2026',
    image: '/jobs/redline.png',
  },
  {
    slug: 'ba-kitchen',
    title: 'BA Kitchen & Bath',
    category: 'Plataforma Web + App iOS + IA',
    service: 'automatizacion',
    client: 'BA Kitchen & Bath Design (USA)',
    tagline: 'Cotización con IA, plataforma multi-rol e integración con Stripe para empresa de remodelación en USA.',
    description:
      'BA Kitchen & Bath Design, empresa de remodelación de interiores en USA, necesitaba automatizar completamente su proceso de cotización. Desarrollamos una plataforma web multi-rol (cliente, estimador y administrador), app móvil para iOS y automatización de cotizaciones con inteligencia artificial.',
    challenge:
      'El proceso de cotización era completamente manual: un estimador tardaba horas en calcular materiales, mano de obra y márgenes para cada proyecto de cocina o baño. Además, la gestión de clientes, proyectos e invoices se hacía con herramientas desconectadas.',
    solution:
      'Implementamos un motor de cotización con IA que calcula automáticamente materiales, costos y márgenes basándose en las dimensiones y especificaciones del proyecto. Desarrollamos tres plataformas integradas: portal de cliente, herramienta de estimador y panel de administrador, con generación de invoices y cobros vía Stripe.',
    results: [
      { label: 'Tiempo de cotización', value: '3 hs → 8 min' },
      { label: 'Plataformas desarrolladas', value: '3 roles' },
      { label: 'Integración de pagos', value: 'Stripe' },
      { label: 'App iOS disponible', value: 'App Store' },
    ],
    technologies: ['Angular', 'iOS (Swift)', 'NestJS', 'MongoDB Atlas', 'OpenAI', 'Stripe', 'AWS'],
    accent: '#1C1917',
    accentLight: '#78716C',
    tags: ['USA', 'IA', 'iOS', 'Stripe'],
    year: '2025',
    image: '/jobs/ba-kitchen.png',
  },
];
