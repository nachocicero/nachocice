// Convierte [[slug]] y [[slug|texto]] en enlaces a /tesis/slug/.
// Si el slug no existe todavía, queda marcado como "por escribir".
import { visit } from 'unist-util-visit';
import fs from 'node:fs';
import path from 'node:path';

const DIR = path.resolve('src/content/tesis');
const RE = /\[\[([a-z0-9-]+)(?:\|([^\]]+))?\]\]/g;

function existentes() {
  try {
    return new Set(fs.readdirSync(DIR).filter(f => f.endsWith('.md')).map(f => f.slice(0, -3)));
  } catch { return new Set(); }
}

const FALTA = /\[(FALTA|DUDA):\s*([^\]]+)\]/g;

export default function wikilinks() {
  return (tree) => {
    const slugs = existentes();
    // [FALTA: ...] y [DUDA: ...] quedan visibles y resaltados para que Nacho los complete.
    visit(tree, 'text', (node, index, parent) => {
      if (!parent || !FALTA.test(node.value)) return;
      FALTA.lastIndex = 0;
      const out = []; let last = 0, m;
      while ((m = FALTA.exec(node.value))) {
        if (m.index > last) out.push({ type: 'text', value: node.value.slice(last, m.index) });
        out.push({ type: 'emphasis', data: { hName: 'mark', hProperties: { className: ['falta'] } },
                   children: [{ type: 'text', value: `${m[1]}: ${m[2]}` }] });
        last = m.index + m[0].length;
      }
      if (last < node.value.length) out.push({ type: 'text', value: node.value.slice(last) });
      parent.children.splice(index, 1, ...out);
      return index + out.length;
    });
    visit(tree, 'text', (node, index, parent) => {
      if (!parent || !RE.test(node.value)) return;
      RE.lastIndex = 0;
      const out = [];
      let last = 0, m;
      while ((m = RE.exec(node.value))) {
        if (m.index > last) out.push({ type: 'text', value: node.value.slice(last, m.index) });
        const [, slug, texto] = m;
        const label = texto ?? slug.replace(/-/g, ' ');
        if (slugs.has(slug)) {
          out.push({ type: 'link', url: `/tesis/${slug}/`, data: { hProperties: { className: ['wl'] } },
                     children: [{ type: 'text', value: label }] });
        } else {
          out.push({ type: 'emphasis', data: { hName: 'span', hProperties: { className: ['wl-falta'], title: 'Tesis por escribir' } },
                     children: [{ type: 'text', value: label }] });
        }
        last = m.index + m[0].length;
      }
      if (last < node.value.length) out.push({ type: 'text', value: node.value.slice(last) });
      parent.children.splice(index, 1, ...out);
      return index + out.length;
    });
  };
}
