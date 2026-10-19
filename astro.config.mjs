import { defineConfig } from 'astro/config';
import wikilinks from './src/lib/wikilinks.mjs';

export default defineConfig({
  site: 'https://nachocicero.github.io',
  // El repo se llama nachocice, así que el sitio vive en /nachocice/
  base: '/nachocice',
  trailingSlash: 'always',
  markdown: {
    remarkPlugins: [wikilinks],
    smartypants: true,
  },
});
