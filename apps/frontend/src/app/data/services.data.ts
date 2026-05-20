export interface Service {
  id: 'plataformas-web' | 'consultoria-ti' | 'automatizacion';
  title: string;
  shortTitle: string;
  tagline: string;
  description: string;
  image: string;
  accent: string;
  features: { title: string; desc: string }[];
  process: { num: string; title: string; desc: string }[];
  outcomes: string[];
  tech: string[];
  projectSlugs: string[];
}

export const SERVICES: Service[] = [
  {
    id: 'plataformas-web',
    title: 'Desarrollo de Plataformas Web',
    shortTitle: 'Plataformas Web',
    tagline: 'Aplicaciones web a medida que convierten y escalan.',
    description:
      'Construimos desde landing pages de alta conversión hasta plataformas SaaS complejas. Sin templates genéricos: cada proyecto es diseñado y desarrollado desde cero para resolver el problema específico de tu negocio.',
    image: 'https://images.unsplash.com/photo-1547658719-da2b51169166?auto=format&fit=crop&w=1200&q=85',
    accent: '#E5322A',
    features: [
      {
        title: 'Landing pages de alta conversión',
        desc: 'Diseño orientado a objetivos de negocio con A/B testing integrado y analytics desde el día uno.',
      },
      {
        title: 'Portales y plataformas empresariales',
        desc: 'Intranets, portales de clientes, sistemas de gestión: soluciones robustas para equipos y organizaciones.',
      },
      {
        title: 'E-commerce y tiendas digitales',
        desc: 'Catálogos dinámicos, carrito de compras, pagos integrados (Stripe, MercadoPago) y panel de administración.',
      },
      {
        title: 'Dashboards y herramientas internas',
        desc: 'Paneles de control en tiempo real, reportes automatizados y visualizaciones de datos para tu equipo.',
      },
      {
        title: 'Aplicaciones web progresivas (PWA)',
        desc: 'Apps que funcionan offline, se instalan en el móvil y ofrecen experiencia nativa sin app store.',
      },
      {
        title: 'APIs y backends a medida',
        desc: 'Arquitecturas REST y GraphQL escalables, autenticación segura, integraciones con sistemas externos.',
      },
    ],
    process: [
      { num: '01', title: 'Discovery', desc: 'Entendemos tu negocio, tus usuarios y tus objetivos antes de escribir una línea de código.' },
      { num: '02', title: 'Diseño UX/UI', desc: 'Wireframes, prototipos y diseño visual aprobado antes de entrar a desarrollo.' },
      { num: '03', title: 'Desarrollo', desc: 'Sprints de 2 semanas con demos. Ves avances reales, no solo reportes de estado.' },
      { num: '04', title: 'QA & Deploy', desc: 'Testing exhaustivo, deploy en producción con CI/CD, SSL y monitoreo incluido.' },
      { num: '05', title: 'Mejora continua', desc: 'Analytics, soporte post-entrega e iteraciones basadas en datos reales de uso.' },
    ],
    outcomes: [
      'Más conversiones y ventas desde el día del lanzamiento',
      'Reducción de costos operativos con automatización de procesos',
      'Experiencia de usuario superior que retiene y fideliza',
      'Escalabilidad para acompañar el crecimiento del negocio',
      'Visibilidad completa del comportamiento de tus usuarios',
    ],
    tech: ['Angular 21', 'React', 'Next.js', 'Python', 'FastAPI', 'PostgreSQL', 'AWS', 'Vercel'],
    projectSlugs: ['asisteya', 'viatika', 'redline'],
  },
  {
    id: 'consultoria-ti',
    title: 'Consultoría de TI, IA y Automatización',
    shortTitle: 'Consultoría & IA',
    tagline: 'Estrategia tecnológica e inteligencia artificial para crecer más rápido.',
    description:
      'Ayudamos a empresas a adoptar tecnología de forma estratégica. Desde la auditoría de tu stack actual hasta la implementación de IA en tus procesos críticos: te acompañamos en cada paso de la transformación digital.',
    image: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=85',
    accent: '#0D0D0D',
    features: [
      {
        title: 'Auditoría tecnológica',
        desc: 'Evaluamos tu infraestructura, stack, procesos y equipo. Identificamos cuellos de botella, riesgos y oportunidades.',
      },
      {
        title: 'Hoja de ruta digital',
        desc: 'Plan estratégico priorizado: qué tecnología adoptar, en qué orden y con qué presupuesto para maximizar el ROI.',
      },
      {
        title: 'Implementación de IA generativa',
        desc: 'Integramos LLMs (ChatGPT, Claude, Gemini) en tus flujos de trabajo: atención al cliente, generación de contenido, análisis de datos.',
      },
      {
        title: 'Integración de sistemas',
        desc: 'Conectamos tus herramientas existentes (CRM, ERP, ecommerce) en un ecosistema cohesivo con APIs y webhooks.',
      },
      {
        title: 'IA predictiva y análisis de datos',
        desc: 'Modelos de machine learning para predicción de demanda, detección de fraude, clasificación de clientes y más.',
      },
      {
        title: 'Capacitación y transferencia',
        desc: 'Tu equipo aprende a operar y evolucionar las soluciones implementadas. Documentación, talleres y soporte incluido.',
      },
    ],
    process: [
      { num: '01', title: 'Diagnóstico', desc: 'Auditamos tu estado tecnológico actual: herramientas, procesos, datos y equipo.' },
      { num: '02', title: 'Estrategia', desc: 'Definimos la hoja de ruta priorizada con objetivos medibles y plazos realistas.' },
      { num: '03', title: 'Prototipo', desc: 'Validamos la solución propuesta con un MVP o prototipo funcional antes de escalar.' },
      { num: '04', title: 'Implementación', desc: 'Desplegamos la solución con acompañamiento full-time del equipo Ignia.' },
      { num: '05', title: 'Transferencia', desc: 'Documentación completa, capacitación al equipo y soporte continuo post-implementación.' },
    ],
    outcomes: [
      'Decisiones más rápidas con datos en tiempo real',
      'Adopción de IA que automatiza tareas repetitivas de alto valor',
      'Stack tecnológico moderno, seguro y escalable',
      'Equipo interno capacitado para operar y evolucionar las soluciones',
      'ROI claro y medible desde el primer trimestre',
    ],
    tech: ['OpenAI', 'Claude API', 'Python', 'LangChain', 'FastAPI', 'BigQuery', 'dbt', 'GCP'],
    projectSlugs: ['tecmeing'],
  },
  {
    id: 'automatizacion',
    title: 'Automatización de Procesos para Empresas',
    shortTitle: 'Automatización',
    tagline: 'Elimina el trabajo manual que frena a tu empresa.',
    description:
      'Automatizamos los procesos operativos que consumen tiempo de tu equipo: desde tareas administrativas repetitivas hasta workflows complejos entre múltiples sistemas. El resultado: más eficiencia, menos errores y equipos enfocados en lo que importa.',
    image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=85',
    accent: '#B45309',
    features: [
      {
        title: 'Automatización de procesos robóticos (RPA)',
        desc: 'Bots que ejecutan tareas repetitivas en sistemas existentes sin necesidad de integración técnica: formularios, reportes, reconciliaciones.',
      },
      {
        title: 'Workflows y flujos de aprobación',
        desc: 'Procesos de aprobación multinivel, notificaciones automáticas y seguimiento en tiempo real de cada etapa.',
      },
      {
        title: 'Integraciones entre sistemas',
        desc: 'Conectamos tu ERP, CRM, sistema contable y más: los datos fluyen automáticamente sin trabajo manual de conciliación.',
      },
      {
        title: 'Automatización de reportes',
        desc: 'Reportes que se generan y distribuyen automáticamente en los plazos y formatos que necesita cada área.',
      },
      {
        title: 'Notificaciones y alertas inteligentes',
        desc: 'Tu equipo recibe alertas en WhatsApp, email o Slack cuando ocurren eventos críticos, sin que nadie tenga que monitorear manualmente.',
      },
      {
        title: 'Procesamiento de documentos con IA',
        desc: 'Extracción automática de datos de facturas, contratos y formularios. Clasificación y archivo sin intervención humana.',
      },
    ],
    process: [
      { num: '01', title: 'Mapeo de procesos', desc: 'Documentamos en detalle los procesos actuales: pasos, tiempos, responsables y volúmenes.' },
      { num: '02', title: 'Análisis y priorización', desc: 'Identificamos qué automatizar primero para maximizar el impacto con el menor esfuerzo.' },
      { num: '03', title: 'Diseño de solución', desc: 'Diseñamos la automatización: flujo, reglas de negocio, integraciones y manejo de excepciones.' },
      { num: '04', title: 'Implementación', desc: 'Desarrollo, testing con datos reales y puesta en producción con rollout gradual.' },
      { num: '05', title: 'Monitoreo y mejora', desc: 'Dashboard de rendimiento, alertas de fallo y mejoras iterativas basadas en datos reales.' },
    ],
    outcomes: [
      'Reducción del 60-80% en horas dedicadas a tareas manuales',
      'ROI recuperado en 3-6 meses',
      'Errores humanos eliminados en procesos críticos',
      'Equipo enfocado en trabajo de alto valor e impacto',
      'Procesos que escalan sin aumentar la plantilla',
    ],
    tech: ['Python', 'Power Automate', 'Zapier', 'FastAPI', 'PostgreSQL', 'RPA', 'n8n', 'Webhooks'],
    projectSlugs: ['ba-kitchen'],
  },
];
