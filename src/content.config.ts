import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { glob } from 'astro/loaders';

const tesis = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/tesis' }),
  schema: z.object({
    titulo: z.string(),
    bajada: z.string().optional(),
    eje: z.string(),
    orden: z.number().default(99),
    // borrador: lo armó Claude, sin revisar · revision: Nacho la está mirando · aprobada: se publica
    estado: z.enum(['borrador', 'revision', 'aprobada']).default('borrador'),
    // De dónde sale cada parte del texto (control de fuente)
    fuentes: z.array(z.string()).default([]),
    // Qué se tocó respecto de la fuente
    cambios: z.array(z.string()).default([]),
    cita: z.string().optional(),
    // fundamento: lo comparte cualquiera, sin importar el bando (EPP se apoya solo en esto)
    // diagnostico: la lectura de Nacho de por qué no se cumple · propuesta: qué hacer
    nivel: z.enum(['fundamento', 'diagnostico', 'propuesta']).optional(),
    actualizado: z.coerce.date().optional(),
  }),
});

export const collections = { tesis };
