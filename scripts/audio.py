"""Genera un MP3 por tesis con una voz neuronal (Piper, es_AR) para el lector de audio.

Se corre en GitHub Actions antes de `astro build`. Solo regenera un audio si
cambió el texto (guarda un hash al lado). Uso:
    python scripts/audio.py --voz es_AR-daniela-high --modelos .piper
"""
import argparse, hashlib, os, re, subprocess, sys, wave
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TESIS = RAIZ / 'src/content/tesis'
SALIDA = RAIZ / 'public/audio'

def frontmatter(s):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', s, re.S)
    return (m.group(1), m.group(2)) if m else ('', s)

def campo(fm, nombre):
    m = re.search(rf'^{nombre}:\s*"?(.*?)"?\s*$', fm, re.M)
    return m.group(1) if m else ''

def limpiar(cuerpo):
    lineas = []
    for l in cuerpo.splitlines():
        if l.strip().startswith('Ver también'):
            continue
        lineas.append(l)
    t = '\n'.join(lineas)
    t = re.sub(r'\[(FALTA|DUDA):[^\]]*\]', '', t)
    t = re.sub(r'\[\[[a-z0-9-]+\|([^\]]+)\]\]', r'\1', t)
    t = re.sub(r'\[\[([a-z0-9-]+)\]\]', lambda m: m.group(1).replace('-', ' '), t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'^#+\s*(.*)$', r'\1.', t, flags=re.M)
    t = re.sub(r'^\s*\d+\.\s+', '', t, flags=re.M)
    t = re.sub(r'[*_`>]', '', t)
    t = t.replace('(', ', ').replace(')', ', ')
    t = re.sub(r'\.\.+', '.', t)
    t = re.sub(r'\n{2,}', '\n\n', t)
    return t.strip()

def texto(md):
    fm, cuerpo = frontmatter(md)
    cuerpo = limpiar(cuerpo)
    bajada = campo(fm, 'bajada')
    if bajada and bajada.rstrip('.') in cuerpo:
        bajada = ''  # ya aparece en el texto, no repetirla
    partes = [campo(fm, 'titulo') + '.', bajada, cuerpo]
    return '\n\n'.join(p for p in partes if p)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--voz', default='es_AR-daniela-high')
    ap.add_argument('--modelos', default='.piper')
    a = ap.parse_args()
    modelos = Path(a.modelos); modelos.mkdir(exist_ok=True)
    onnx = modelos / f'{a.voz}.onnx'
    if not onnx.exists():
        subprocess.run([sys.executable, '-m', 'piper.download_voices', '--download-dir', str(modelos), a.voz], check=True)
    from piper import PiperVoice
    voz = PiperVoice.load(str(onnx))
    SALIDA.mkdir(parents=True, exist_ok=True)
    for md in sorted(TESIS.glob('*.md')):
        t = texto(md.read_text(encoding='utf-8'))
        h = hashlib.sha1((a.voz + t).encode()).hexdigest()
        mp3, marca = SALIDA / f'{md.stem}.mp3', SALIDA / f'{md.stem}.hash'
        if mp3.exists() and marca.exists() and marca.read_text() == h:
            print('igual', md.stem); continue
        wav = SALIDA / f'{md.stem}.wav'
        with wave.open(str(wav), 'wb') as w:
            voz.synthesize_wav(t, w)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(wav), '-ac', '1', '-b:a', '64k', str(mp3)], check=True)
        wav.unlink(); marca.write_text(h)
        print('nuevo', md.stem)

if __name__ == '__main__':
    main()
