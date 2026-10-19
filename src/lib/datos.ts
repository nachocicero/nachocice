import { getCollection, type CollectionEntry } from 'astro:content';
import { ejes } from './ejes';

export type Tesis = CollectionEntry<'tesis'>;

// En producción solo salen las aprobadas. Para revisar borradores:
// PUBLIC_BORRADORES=1 npm run build   (o npm run dev, que los muestra siempre)
const verBorradores = import.meta.env.DEV || import.meta.env.PUBLIC_BORRADORES === '1';

export async function tesisVisibles(): Promise<Tesis[]> {
  const todas = await getCollection('tesis', t => verBorradores || t.data.estado === 'aprobada');
  const ordenEje = (id: string) => { const i = ejes.findIndex(e => e.id === id); return i < 0 ? 99 : i; };
  return todas.sort((a, b) => ordenEje(a.data.eje) - ordenEje(b.data.eje) || a.data.orden - b.data.orden);
}

const RE = /\[\[([a-z0-9-]+)(?:\|[^\]]+)?\]\]/g;

export function enlacesDe(t: Tesis): string[] {
  return [...new Set([...(t.body ?? '').matchAll(RE)].map(m => m[1]))].filter(s => s !== t.id);
}

export async function grafo() {
  const lista = await tesisVisibles();
  const ids = new Set(lista.map(t => t.id));
  const salientes = new Map(lista.map(t => [t.id, enlacesDe(t).filter(s => ids.has(s))]));
  const entrantes = new Map(lista.map(t => [t.id, [] as string[]]));
  for (const [de, hacia] of salientes) for (const h of hacia) entrantes.get(h)!.push(de);
  return { lista, salientes, entrantes };
}

export function minutos(t: Tesis) {
  const palabras = (t.body ?? '').split(/\s+/).length;
  return Math.max(1, Math.round(palabras / 220));
}
