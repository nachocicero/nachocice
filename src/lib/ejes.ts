// Las "partes" del libro. El orden de este arreglo es el orden de lectura.
// Títulos provisorios, tomados del inventario de tesis. Los define Nacho.
export const ejes = [
  { id: 'libertad', titulo: 'Libertad es no ser dominado', bajada: '' },
  { id: 'poder', titulo: 'Dónde está el poder', bajada: '' },
  { id: 'obligacion', titulo: 'De la atención a la obligación', bajada: '' },
  { id: 'quien-paga', titulo: 'Quién paga y quién se corre', bajada: '' },
  { id: 'trabajo', titulo: 'El trabajo de quién', bajada: '' },
  { id: 'longevidad', titulo: 'Vivir más, ¿quiénes?', bajada: '' },
  { id: 'global', titulo: 'Lo global ya existe', bajada: '' },
] as const;

export function eje(id: string) {
  return ejes.find(e => e.id === id) ?? { id, titulo: id, bajada: '' };
}
