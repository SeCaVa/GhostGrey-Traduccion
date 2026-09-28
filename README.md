# Pokémon Ghost Grey — Traducción al castellano

Traducción no oficial al castellano (España) de **Pokémon Ghost Grey**, el hack de terror de Pokémon Rojo Fuego
creado por **Joey Zeed**. Kanto, año 2049: una catástrofe ha arrasado la región, todos los Pokémon salvajes son de
tipo Fantasma y cada entrenador sobrevive como puede.

> Este repositorio solo contiene el parche de la traducción y las herramientas y textos con los que se genera.
> **No incluye ninguna ROM.** Necesitas tu propia copia de Pokémon FireRed (USA).

---

## Cómo jugar

1. Consigue una ROM de **Pokémon - FireRed Version (USA)**, revisión 1.0.
   - CRC32: `DD88761C`
2. Aplica el parche [`GhostGrey_ES.bps`](GhostGrey_ES.bps) con
   [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) (desde el navegador) o con Floating IPS (Flips).
3. El resultado es una ROM de 32 MB con **CRC32 `D3902751`**. Juega con cualquier emulador de GBA (mGBA
   recomendado).

El parche se aplica **directamente a FireRed USA**: no hace falta parchear antes el hack en inglés, porque ya
lo incluye.

---

## Qué está traducido

### Textos
- **Todos los diálogos** del juego: historia principal, secretos, postgame, créditos y epílogo.
- **Menús y combate**: mensajes de combate, menús, PC, Pokédex, ficha de entrenador, tienda, casino…
- **Nombres**: movimientos, habilidades, objetos, tipos, clases y nombres de entrenador, naturalezas y lugares.
- Donde existe un nombre oficial, se usa el de **Pokémon Rojo Fuego en español**. Ejemplos: MT/MO, Alto Mando,
  Liga Añil, Líder de Gimnasio, Azafrán, Celeste…
- Los personajes propios del hack **conservan su nombre**: Summer, Theodora, Voltage, Cap'n Steve…
- **Protagonista chico o chica**: el motor se ha modificado para que los diálogos concuerden en género con el
  personaje elegido ("cansado/cansada", "el Campeón/la Campeona"…).
- Pokédex con **altura en metros y peso en kilos**: el hack mostraba pies y libras y se ha cambiado el código.
- Mensajes de subida y bajada de estadísticas como en el juego español ("¡El Ataque de X subió mucho!").

### Gráficos con texto
Se han revisado los unos 1.500 gráficos que el hack añade o modifica. El criterio ha sido:

- **Lo que el hack copia del Rojo de Game Boy** se deja como en la **edición española de Game Boy**
  (carteles "POKé", "SHOP", "GIM").
- **Lo propio del hack** se traduce, imitando su letra.
- **Las marcas** no se traducen: BrunoCorp ("BC"), SNACK SNEASEL, LEVEL+ y los logotipos de chucherías y latas.

Entre otros, se han traducido:

- **Pantallas y menús:**
  - Pantalla de título ("Versión Ghost Grey", "PULSA START SI TE ATREVES") y resumen del Pokémon.
  - Iconos de tipo (incluido HADA) e iconos de estado (ENV, DOR, PAR…).
  - Ficha de entrenador (NAC., MEDALLAS), PC (MENÚ).
- **Casino y ciudades:**
  - Tragaperras (PON MÁS / GANA MÁS, la pantalla de ayuda de Aston).
  - Vallas de Ciudad Plateada (JUEGA / BEBE).
  - Carteles de Ciudad Azafrán (POLICÍA ▪ AZAFRÁN, ESTADIO ▪ AZAFRÁN) y póster de la policía.
  - Otros carteles: SIN CAMBIOS, FAMILIA LUNA, GUAY, botón Cancelar.
- **Lugares y mazmorras:**
  - Pantalla de entrada de la Cueva Diglett (FORASTERO FUERA).
  - Carteles pintados de la gruta: SERÁS DEVORADO, TEME LA GRUTA.
  - Pintada SOY.
  - Las letras que aparecen en el suelo de la sala de control al reunir las passkeys.
- **Imágenes y fondos:**
  - "Memes" y fotos que envían los personajes.
  - Cartas (papel de carta) con dibujos propios.
  - Fondos de combate con texto (MUERE en BATALLA, Hay cosas peores…).

### Errores
Si encuentras algo en inglés, un texto que se sale del cuadro o una errata, abre una *issue* con una captura y
el lugar del juego.

---

## Créditos

### Pokémon Ghost Grey (hack original)
**Pokémon Ghost Grey** es obra de **Joey Zeed**.
[Hilo oficial en PokéCommunity](https://www.pokecommunity.com/threads/pok%C3%A9mon-ghost-grey-version.543491/).
Todo el mérito del juego es suyo y de quienes le ayudaron. Esta traducción solo cambia el idioma.

Créditos que aparecen en el propio juego:

| Papel | Personas |
|---|---|
| Autor del hack: dirección, diseño del juego, dirección artística, diseños de Pokémon, programación, historia, mapas, sprites | **Joey Zeed** |
| Música original (composición y secuenciación) | **Whale (Amn)** |
| Secuenciación | Magma |
| Arreglos e inserción de la música | Joey Zeed |
| Asesor de la historia | Nathaniel Lee |
| Diseño de personajes y gráficos de combate | Joey Zeed, Game Freak |
| Sprites del mapa, voces de personajes, retratos, arte promocional, guiones, sprites traseros | Joey Zeed, BunnyVA, Whale (Amn), Nathaniel Lee, Ghosty, Nate |
| Entradas de la Pokédex | Joey Zeed, Ghosty, Nathaniel Lee |
| Gritos de los Pokémon | Game Freak, Joey Zeed |
| Embajador de Wario | Nate |
| Ayuda con los scripts | DontJoelMe, Invis, YeahPotato, BroTacos, Adriccustoms |
| Equipo de pruebas | Whale (Amn), Ghosty, Rhyuuhime, Storm, Adriccustoms, Jeff, Yanchop, Nigel (Arachnocturne), vilevermin, Magma, Jake from Real Life |
| Herramientas | HexManiacAdvance, Microsoft Paint, AnvilStudio, CryEditor, BeepBox |
| Dedicado a | Eugenie |

Joey Zeed también agradece la ayuda del "grupo de Nate" (Whale, Magma, Ghosty, Nate, Ryuuhime, Seiko, Sunny,
5th Nate, Servbot, Bret y Teddy) y el apoyo de la gente de reddit, YouTube, Discord y PokéCommunity. La canción
de los créditos es *"Oh Sheila"*, de Ready for the World.

El hack usa **Complete FireRed Upgrade (CFRU)** y **Dynamic Pokémon Expansion (DPE)**, de Skeli789 y sus
colaboradores.

### Traducción al castellano
- Traducción, adaptación de gráficos y herramientas: **SeCaVa**.
- Nombres y textos oficiales de Pokémon Rojo Fuego y Pokémon Edición Roja en español: © Nintendo / Creatures
  Inc. / GAME FREAK inc.

### Aviso
Proyecto de fans sin ánimo de lucro, no afiliado a Nintendo, The Pokémon Company, Creatures ni GAME FREAK.
Pokémon es una marca registrada de Nintendo, Creatures Inc. y GAME FREAK inc. No se distribuye ninguna ROM:
usa solo copias de juegos que poseas legalmente.

---

## Para desarrolladores: cómo se genera el parche

### Requisitos
- Python 3.11 con `numpy` y `Pillow` (`pip install -r requirements.txt`).
- `keystone-engine`, solo si quieres regenerar los parches de código (`tools/parches_asm.py`).
- `arm-none-eabi-gcc` en WSL, solo si quieres recompilar las pantallas de la traducción (`tools/intro_traduccion.py`).
- En la **carpeta raíz del repositorio**, las ROMs y el parche original (no se incluyen):

| Archivo | CRC32 | Para qué |
|---|---|---|
| `Pokemon - FireRed Version (USA).gba` | `DD88761C` | base del parche |
| `Pokemon - Edicion Rojo Fuego (Spain).gba` | `9F08064E` | textos y gráficos oficiales en español |
| `GhostGrey.bps` | destino `DCAC3F32` | parche original del hack (en inglés) |
| `Pokemon - Edicion Roja (Spain) (SGB Enhanced).gb` | `D8507D8A` | solo para regenerar el collage de Game Boy |

### Compilar
```
python traduccion/tools/compilar.py
```
Este comando:
1. Aplica `GhostGrey.bps` a FireRed USA y deja `traduccion/build/ghostgrey_en.gba`, el hack en inglés.
2. Empareja los textos de FireRed USA con los del Rojo Fuego español y hace el inventario de todos los textos
   del hack. Los volcados que genera (`data/inventory.json`, `data/vanilla_pairs*.json`) no se suben al
   repositorio porque contienen el texto de los juegos; se regeneran solos. Usa `--rehacer` para forzarlo.
3. Escribe la traducción (`tools/build.py`) y genera `traduccion/build/GhostGrey_ES.bps`.
4. Copia el parche a la raíz y lo aplica: queda `GhostGrey_ES.gba` (CRC32 `D3902751`).

### Estructura
```
GhostGrey_ES.bps            parche final (FireRed USA -> Ghost Grey en castellano)
traduccion/
  data/
    trad/*.txt, *.json      traducciones de los diálogos y textos, por lotes
    tablas/*.tsv            nombres de longitud fija: movimientos, objetos, habilidades, entrenadores…
    glosario.md             criterios y términos de la traducción
    gfx/*.bin + gfx_bin.json    gráficos editados y dónde van
    parches_codigo.json     cambios de código (Pokédex en m/kg…), generados por tools/parches_asm.py
    parches_datos.json      cambios de datos (orden de carteles, letras del suelo…), de tools/edit_carteles.py
    pares_ajustes.json      correcciones a los emparejamientos automáticos USA/ES
    extra_inv.json          textos que el inventario automático no detecta
    intro.bin, intro.json   pantallas de la traducción ya compiladas, y dónde se enganchan
  intro/                    código C, gráficos y jingle de las pantallas de la traducción
  tools/
    compilar.py             todo el proceso en un paso
    build.py                escribe textos, nombres, gráficos y parches, y genera el .bps
    inventory.py, pair_*.py inventario de textos del hack y emparejado con los textos oficiales
    lote.py                 exporta lotes de textos pendientes para traducir
    check.py                comprueba el ancho de una línea con la fuente del hack
    edit_*.py, gotica.py    generan los gráficos traducidos (data/gfx)
    intro_traduccion.py     extrae y compila las pantallas de la traducción (intro/ -> data/intro.bin)
    mapinfo.py, ver_*.py    utilidades para inspeccionar mapas y gráficos
```

### Formato de las traducciones (`data/trad/*.txt`)
Cada texto empieza con `### ID`, que es la dirección del texto en la ROM del hack en inglés.

- **Saltos de línea**: se ajustan solos al ancho del cuadro. `\p` empieza un cuadro nuevo y `\n` fuerza un
  salto de línea.
- **Códigos del juego**: `{B01}` es el nombre del jugador. Otros van en crudo (`{C…}`, `{X…}`).
- **Género del protagonista**: `{o}`, `{a}`, `{el}`, `{on}`, `{ON}`, `{e}`, `{él}` se sustituyen según sea
  chico o chica. Por ejemplo, `cansad{o}` sale "cansado" o "cansada". Se explica en `data/glosario.md`.
- **Anchos y huecos**: `#! ancho N` fija el ancho de las líneas del archivo, `{sp}` es un espacio explícito y
  `<vacío>` deja el texto vacío.

Los textos originales de FireRed que el hack no cambia toman automáticamente la traducción oficial española.
