// Antepone la base del sitio (/nachocice/) a una ruta interna.
export const B = import.meta.env.BASE_URL.replace(/\/$/, '');
export const url = (ruta: string) => `${B}${ruta}`;
