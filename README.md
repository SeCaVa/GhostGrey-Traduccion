# Pokémon Ghost Grey — Traducción al castellano

**English speakers:** [read this README in English](#english).

Traducción no oficial al castellano (España) de **Pokémon Ghost Grey**, el hack de terror de Pokémon Rojo Fuego
creado por **Joey Zeed**. Kanto, año 2049: una catástrofe ha arrasado la región, todos los Pokémon salvajes son de
tipo Fantasma y cada entrenador sobrevive como puede.

La traducción está hecha sobre la **versión 04** del hack (la última publicada por su autor).

> Este repositorio solo contiene el parche de la traducción.
> **No incluye ninguna ROM.** Necesitas tu propia copia de Pokémon FireRed (USA).

Hilo del proyecto en Whack a Hack!: **[Pokémon Ghost Grey — Traducción al castellano](https://whackahack.com/foro/threads/pokemon-ghost-grey-traduccion-al-castellano.69363/)**.
Ahí puedes comentar, dar sugerencias o avisar de errores.

---

## Cómo jugar

1. Consigue una ROM de **Pokémon - FireRed Version (USA)**, revisión 1.0.
   - CRC32: `DD88761C`
   - La revisión 1.1 no sirve: si al encender sale «Presents» bajo el logo de GAME FREAK, es la 1.1 y el juego
     se quedará en blanco o se colgará. Rom Patcher JS enseña el CRC32 de tu ROM antes de parchear.
2. Aplica el parche [`GhostGrey_ES.bps`](https://github.com/SeCaVa/GhostGrey-Traduccion/releases/latest) con
   [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) (desde el navegador) o con Floating IPS (Flips).
3. El resultado es una ROM de 32 MB con **CRC32 `BFBB84CC`**. Juega con cualquier emulador de GBA (mGBA
   recomendado).

Versión actual: **v0.95**. SHA-256 del parche: `89789b5f1e9373adf33e049cd3b991d1480c491a8ee15f5049e7321fb0a09ef8`.

El parche se aplica **directamente a FireRed USA**: no hace falta parchear antes el hack en inglés, porque ya
lo incluye.

### Novedades de la v0.95

- El Gloomeon de Azulona ya no sale como Poltchagst al enviarlo al PC ni al ponerle mote (fallo del hack original).
- Entrada de la Pokédex de Tyranitar con su texto oficial del Rojo Fuego español.

### Novedades de la v0.94

- «Poké Balls» bien escrito en los 18 textos donde salía «Poké BallS».
- La pantalla para poner mote dice «¿Mote de Litwick?», como en el Rojo Fuego español.
- 18 textos del Rojo Fuego original con su versión oficial en castellano (descripciones de la Pokédex, Sala Unión
  y opciones).

### Novedades de la v0.93

- Ocho gritos que seguían en inglés, traducidos («¡Socorro!», «¡Fuera de combate!», «¡Toc, toc!»…).
- Unos 80 mensajes de entrenadores que salían en inglés al volver a hablarles o al ganarles: ahora dicen
  «¡Charla tras el combate!» y «¡Has ganado!».

### Novedades de la v0.92

- Tres diálogos que salían con basura (un entrenador y el cartel «Chof, chof… ¡Túnel Sureste!») vuelven a verse bien.
- Devueltos a su sitio unos pocos bytes de código de combate, gráficos y sonido que la traducción había pisado sin querer.
- Unos 50 textos que seguían en inglés, traducidos: mensajes de la Sala Unión con su versión oficial del Rojo Fuego,
  la descripción de la Master Ball, el pirata de la cerveza, la hija de Koga, Tina y textos de revancha.
- Cuatro nombres de lugar más cortos para que quepan en el cartel: Corazón Oscuro, Base Lunar Edén, Casa de Títeres
  y Cabaña Costera.
- El parche ocupa menos (11,5 MB).

### Novedades de la v0.91

- Arreglado el cuelgue tras la tormenta del Calabazar y los segundos de espera antes de algunos combates salvajes (la traducción había estropeado sin querer 4 bytes del código que crea los Pokémon).

### Novedades de la v0.9

- El cavernícola de la cueva dice «primer hijo» o «primera hija» según el protagonista que elijas.

### Novedades de la v0.8

- Ficha de Entrenador arreglada: «MEDALLAS» sale entero (antes «MEDALL» con basura) y «ENTRENADOR:» ya no pisa el nombre.
- Dos mensajes muy largos (la placa de las Guerras psíquicas y una charla del Prof. Oak) acortados para que no
  desborden la memoria del juego.
- La medalla de Erika dice «Ciudad Azulona», como en el Rojo Fuego español.
- Cuatro frases cortas que seguían en inglés, traducidas, y «Prof. Oak» y «Sr. Fuji» bien escritos en el Buscafamas.

### Novedades de la v0.7

- Las palabras del Easy Chat, ahora con las del Rojo Fuego español y su orden alfabético en castellano.
- Unos 500 textos que seguían en inglés, traducidos: textos del Rojo Fuego original con su versión oficial,
  decoraciones, Club Unión y unos 30 diálogos del hack (entre ellos, la escena de la base lunar).
- El título al poner mote ya no sale como «Litwick¿Mote de ?».
- «FIN» de los créditos y pantalla del Regalo Misterioso en castellano.
- Cuadros mejor repartidos: ninguna línea acaba en «el», «la» o «un» y no quedan palabras sueltas al final.
- Nombres de lugar más cortos donde no cabían (Calabazar, Palacio Desértico…), signos ¡! ¿? y siglas revisados.

### Novedades de la v0.6

- Nombres de entrenador oficiales del Rojo Fuego español donde coinciden, y clase «Entrenadora» para las chicas.
- Plurales correctos de las bayas («Bayas Aranja») y descripciones de objeto oficiales.
- Unos 100 textos que seguían en inglés, ya traducidos.
- Orden natural en castellano: «¿Mote de X?», «Ficha de Entrenador de X» y «Pokémon Semilla» en la Pokédex.
- «Nv» y «PS» como en el Rojo Fuego español, y Pokédex revisada (marco de la entrada e índice).
- La Condesa de «Fauce Roja», menos palabras sueltas al final de los cuadros y siglas bien escritas.

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
- **Clases de entrenador en femenino**: el hack usa la misma clase para chicos y chicas, así que en combate el
  nombre se elige por el sprite del entrenador ("Jardinera Jaida", "Científica Takako", "Bruja Micah"…).
- Pokédex con **altura en metros y peso en kilos**: el hack mostraba pies y libras y se ha cambiado el código.
- **Teclado de nombres con tildes y ñ** en la página de símbolos (á é í ó ú ñ y sus mayúsculas), que ni el Rojo Fuego español tenía.
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
Si encuentras algo en inglés, un texto que se sale del cuadro o una errata, rellena el [formulario de fallos](https://github.com/SeCaVa/GhostGrey-Traduccion/issues/new?template=fallo.yml).
Pide versión, emulador, zona y captura, y así puedo arreglarlo sin preguntarte nada más.

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

☕ Si quieres apoyar mi trabajo como traductor, puedes hacerlo en [Ko-fi](https://ko-fi.com/secava),
[Patreon](https://www.patreon.com/secava) o [GitHub Sponsors](https://github.com/sponsors/SeCaVa). Es totalmente voluntario: la traducción es y seguirá siendo
gratis. Y si te gusta el juego, apoya también a Joey Zeed, su autor.

### Aviso
Proyecto de fans sin ánimo de lucro, no afiliado a Nintendo, The Pokémon Company, Creatures ni GAME FREAK.
Pokémon es una marca registrada de Nintendo, Creatures Inc. y GAME FREAK inc. No se distribuye ninguna ROM:
usa solo copias de juegos que poseas legalmente.

---

## English

Unofficial **Spanish (Spain) translation** of **Pokémon Ghost Grey**, the horror hack of Pokémon FireRed made by
**Joey Zeed**. Kanto, year 2049: a catastrophe has devastated the region, every wild Pokémon is Ghost-type and every
Trainer survives however they can.

The translation is based on **version 04** of the hack (the latest one released by its author).

> This repository only contains the translation patch.
> **It does not include any ROM.** You need your own copy of Pokémon FireRed (USA).

Project thread on Whack a Hack! (in Spanish): **[Pokémon Ghost Grey — Traducción al castellano](https://whackahack.com/foro/threads/pokemon-ghost-grey-traduccion-al-castellano.69363/)**.
Feel free to leave comments, suggestions or bug reports there.

### How to play

1. Get a ROM of **Pokémon - FireRed Version (USA)**, revision 1.0.
   - CRC32: `DD88761C`
   - Revision 1.1 won't work: if "Presents" shows under the GAME FREAK logo when you boot it, it's 1.1 and the
     game will show a white screen or crash. Rom Patcher JS shows your ROM's CRC32 before patching.
2. Apply the patch [`GhostGrey_ES.bps`](https://github.com/SeCaVa/GhostGrey-Traduccion/releases/latest) with
   [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) (in the browser) or with Floating IPS (Flips).
3. The result is a 32 MB ROM with **CRC32 `BFBB84CC`**. Play it on any GBA emulator (mGBA recommended).

Current version: **v0.95**. Patch SHA-256: `89789b5f1e9373adf33e049cd3b991d1480c491a8ee15f5049e7321fb0a09ef8`.

The patch applies **directly to FireRed USA**: you don't need to patch the English hack first, it's already included.

### What is translated

**Text**
- **All the dialogue**: main story, secrets, postgame, credits and epilogue.
- **Menus and battles**: battle messages, menus, PC, Pokédex, Trainer Card, shop, Game Corner…
- **Names**: moves, abilities, items, types, Trainer classes and names, natures and places.
- Official names are used wherever they exist: those of **the Spanish FireRed** (TM/HM, Elite Four, Indigo League,
  Gym Leader, Saffron, Cerulean…) and the current official Spanish names for everything the hack adds.
- The hack's own characters **keep their names**: Summer, Theodora, Voltage, Cap'n Steve…
- **Boy or girl protagonist**: Spanish is gendered, so the engine was modified to make the dialogue agree with the
  chosen character ("cansado/cansada", "el Campeón/la Campeona"…).
- **Female Trainer classes**: the hack uses one class for both men and women, so in battle the class name is chosen
  from the Trainer's sprite ("Jardinera Jaida", "Científica Takako", "Bruja Micah"…).
- Pokédex with **height in metres and weight in kilograms** instead of feet and pounds (the code was changed).
- **Naming keyboard with Spanish letters** on the symbols page (á é í ó ú ñ and their capitals), which not even the Spanish FireRed had.
- Stat change messages worded like in the Spanish games ("¡El Ataque de X subió mucho!").

**Graphics with text**

The ~1,500 graphics the hack adds or modifies were reviewed. The criteria:

- **What the hack copies from the Game Boy Red version** is left as in the **Spanish Game Boy Red** ("POKé",
  "SHOP", "GIM" signs).
- **The hack's own graphics** are translated, imitating their lettering.
- **Brands** are not translated: BrunoCorp ("BC"), SNACK SNEASEL, LEVEL+ and the candy and can logos.

Among others: the title screen ("Versión Ghost Grey", "PULSA START SI TE ATREVES"), the Pokémon summary, type
(including FAIRY) and status icons, Trainer Card, PC, the slot machines, the Pewter City billboards, the Saffron City
signs and police poster, the Diglett's Cave entrance screen, the painted cave signs, the letters on the control room
floor, the "memes" and photos the characters send you, the letters (mail paper) and the battle backgrounds with text.

**Bug reports**

If you find something still in English, text overflowing its box or a typo, please fill in the [bug report form](https://github.com/SeCaVa/GhostGrey-Traduccion/issues/new?template=fallo.yml).
It asks for the version, emulator, location and a screenshot.

### Credits

**Pokémon Ghost Grey** (original hack) is the work of **Joey Zeed**.
[Official thread on PokéCommunity](https://www.pokecommunity.com/threads/pok%C3%A9mon-ghost-grey-version.543491/).
All the credit for the game goes to him and the people who helped him; this translation only changes the language.

Credits shown in the game itself:

| Role | People |
|---|---|
| Hack author: direction, game design, art direction, Pokémon designs, programming, story, maps, sprites | **Joey Zeed** |
| Original music (composition and sequencing) | **Whale (Amn)** |
| Sequencing | Magma |
| Music arrangement and insertion | Joey Zeed |
| Story consultant | Nathaniel Lee |
| Character design and battle graphics | Joey Zeed, Game Freak |
| Overworld sprites, character voices, portraits, promotional art, dialogue writing, back sprites | Joey Zeed, BunnyVA, Whale (Amn), Nathaniel Lee, Ghosty, Nate |
| Pokédex entries | Joey Zeed, Ghosty, Nathaniel Lee |
| Pokémon cries | Game Freak, Joey Zeed |
| Wario ambassador | Nate |
| Scripting help | DontJoelMe, Invis, YeahPotato, BroTacos, Adriccustoms |
| Bug testers | Whale (Amn), Ghosty, Rhyuuhime, Storm, Adriccustoms, Jeff, Yanchop, Nigel (Arachnocturne), vilevermin, Magma, Jake from Real Life |
| Tools | HexManiacAdvance, Microsoft Paint, AnvilStudio, CryEditor, BeepBox |
| Dedicated to | Eugenie |

Joey Zeed also thanks "the Nate group" (Whale, Magma, Ghosty, Nate, Ryuuhime, Seiko, Sunny, 5th Nate, Servbot,
Bret and Teddy) and the people of reddit, YouTube, Discord and PokéCommunity for their support. The credits song is
*"Oh Sheila"* by Ready for the World.

The hack uses **Complete FireRed Upgrade (CFRU)** and **Dynamic Pokémon Expansion (DPE)**, by Skeli789 and
contributors.

**Spanish translation**
- Translation, graphics adaptation and tools: **SeCaVa**.
- Official names and texts from the Spanish Pokémon FireRed and Pokémon Red: © Nintendo / Creatures Inc. /
  GAME FREAK inc.

☕ If you'd like to support my work as a translator, you can do so on [Ko-fi](https://ko-fi.com/secava),
[Patreon](https://www.patreon.com/secava) or [GitHub Sponsors](https://github.com/sponsors/SeCaVa). It's completely optional: the translation is and will always
be free. And if you enjoy the game, please support Joey Zeed, its author, too.

**Disclaimer**

Non-profit fan project, not affiliated with Nintendo, The Pokémon Company, Creatures or GAME FREAK. Pokémon is a
registered trademark of Nintendo, Creatures Inc. and GAME FREAK inc. No ROM is distributed: only use copies of games
you legally own.
