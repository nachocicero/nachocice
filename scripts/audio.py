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
    libro(lambda t, w: voz.synthesize_wav(t, w))

NUMEROS = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez']

def orden_de_lectura():
    """Devuelve [(titulo_de_parte, [slugs])] en el orden del índice."""
    ejes = re.findall(r"id: '([\w-]+)', titulo: '([^']*)'", (RAIZ / 'src/lib/ejes.ts').read_text(encoding='utf-8'))
    tesis = {}
    for md in TESIS.glob('*.md'):
        fm, _ = frontmatter(md.read_text(encoding='utf-8'))
        orden = campo(fm, 'orden')
        tesis.setdefault(campo(fm, 'eje'), []).append((float(orden or 99), md.stem))
    salida, n = [], 0
    for id_, titulo in ejes:
        if id_ not in tesis:
            continue
        if id_ == 'base':
            intro = f'Antes de empezar. {titulo}.'
        elif id_ == 'anexo':
            intro = f'{titulo}.'
        else:
            n += 1
            intro = f'Parte {NUMEROS[n - 1] if n <= len(NUMEROS) else n}. {titulo}.'
        salida.append((intro, [s for _, s in sorted(tesis[id_])]))
    return salida

def libro(sintetizar):
    """Une todos los audios en un solo MP3, en orden de lectura, con el título de cada parte."""
    partes = orden_de_lectura()
    clave = hashlib.sha1(repr([(i, [(s, (SALIDA / f'{s}.hash').read_text() if (SALIDA / f'{s}.hash').exists() else '') for s in ss]) for i, ss in partes]).encode()).hexdigest()
    mp3, marca = SALIDA / 'libro-completo.mp3', SALIDA / 'libro-completo.hash'
    if mp3.exists() and marca.exists() and marca.read_text() == clave:
        print('igual', 'libro-completo'); return
    tmp = SALIDA / '_libro'; tmp.mkdir(exist_ok=True)
    piezas = []
    pausa = tmp / 'pausa.wav'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono', '-t', '1.5', str(pausa)], check=True)
    intro = tmp / 'intro.wav'
    with wave.open(str(intro), 'wb') as w:
        sintetizar('El lento proceso retrodemocratizador del poder. De Nacho Cicero.', w)
    piezas += [intro, pausa]
    for k, (titulo, slugs) in enumerate(partes):
        wav = tmp / f'parte-{k}.wav'
        with wave.open(str(wav), 'wb') as w:
            sintetizar(titulo, w)
        piezas += [pausa, wav, pausa]
        for s in slugs:
            if (SALIDA / f'{s}.mp3').exists():
                piezas += [SALIDA / f'{s}.mp3', pausa]
    # Todo a WAV con el mismo formato, así el concat no mezcla códecs.
    uniformes = []
    for j, p in enumerate(piezas):
        u = tmp / f'u{j:04d}.wav'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(p), '-ac', '1', '-ar', '22050', '-sample_fmt', 's16', str(u)], check=True)
        uniformes.append(u)
    lista = tmp / 'lista.txt'
    lista.write_text(''.join(f"file '{p.resolve()}'\n" for p in uniformes))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(lista),
                    '-ac', '1', '-ar', '22050', '-b:a', '32k', str(mp3)], check=True)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    marca.write_text(clave)
    print('nuevo', 'libro-completo')

if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        tb = traceback.format_exc().strip().replace('\n', ' | ')
        print(f'::error title=audio::{tb[-900:]}')
        sys.exit(1)
