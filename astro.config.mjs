import { defineConfig } from 'astro/config';
import wikilinks from './src/lib/wikilinks.mjs';

export default defineConfig({
  site: 'https://nachocicero.github.io',
  trailingSlash: 'always',
  markdown: {
    remarkPlugins: [wikilinks],
    smartypants: true,
  },
});
