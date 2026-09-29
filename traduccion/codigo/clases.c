// Clase de entrenador en femenino. El juego tiene una sola clase para chicos y chicas ("Jardinero"), así que en los
// mensajes de combate el nombre se elige por el sprite del entrenador: si la pareja (clase, sprite) está en la tabla
// de clases femeninas, se usa su nombre ("Jardinera"). Cuando chicos y chicas comparten sprite, la fila indica el
// número del entrenador. build.py escribe la tabla en CLASES_FEM a partir de data/tablas/clases_femeninas.tsv.
// Se llama desde BufferStringBattle (B_TXT_TRAINER1_CLASS, 0x080D8084).

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

struct Trainer                 // 40 bytes, como en FireRed
{
    u8 partyFlags;
    u8 trainerClass;
    u8 encounterMusic_gender;  // el bit de chica no es fiable en el hack: se usa el sprite
    u8 trainerPic;
    u8 trainerName[12];
    u16 items[4];
    u32 doubleBattle;
    u32 aiFlags;
    u32 partySize;
    const void *party;
};

struct ClaseFemenina           // 20 bytes
{
    u16 entrenador;            // 0xFFFF: cualquiera con esa clase y sprite
    u8 clase;                  // 0xFF: fin de la tabla
    u8 sprite;
    u8 nombre[16];             // texto del juego acabado en 0xFF (máx. 12 letras)
};

extern const struct Trainer gTrainers[];
extern const u8 gTrainerClassNames[][13];

#define CLASES_FEM ((const struct ClaseFemenina *)0x09F20000)

const u8 *NombreClaseEntrenador(u16 trainerId)
{
    const struct Trainer *t = &gTrainers[trainerId];
    const struct ClaseFemenina *c;

    for (c = CLASES_FEM; c->clase != 0xFF; c++)
    {
        if (c->entrenador != 0xFFFF ? c->entrenador != trainerId
                                    : c->clase != t->trainerClass || c->sprite != t->trainerPic)
            continue;
        return c->nombre;
    }
    return gTrainerClassNames[t->trainerClass];
}
