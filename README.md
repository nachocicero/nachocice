# nachocice

Ensayos enlazados de Nacho Cicero. El libro *El lento proceso retrodemocratizador del poder* escrito como una red de tesis, y el fundamento de [El Pueblo Propone](https://elpueblopropone.org).

## Cómo funciona

- Cada tesis es un archivo en `src/content/tesis/`. Para enlazar otra tesis se escribe `[[slug]]` o `[[slug|texto del enlace]]`.
- `[FALTA: ...]` y `[DUDA: ...]` quedan resaltados en la página: son huecos que tiene que completar el autor.
- Las partes del libro están en `src/lib/ejes.ts`.
- En el sitio público solo aparecen las tesis con `estado: aprobada`. Las que están en `borrador` o `revision` se ven en local.

## Comandos

```
npm install
npm run dev        # http://localhost:4321, muestra también los borradores
npm run build      # lo mismo que se publica
```

Cada push a `main` se publica solo en GitHub Pages: https://nachocicero.github.io/nachocice/

## Reglas editoriales

Ver `CLAUDE.md` y `editorial/protocolo-estilo.md`.
