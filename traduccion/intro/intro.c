// Pantallas de crédito de la traducción, entre la escena del logo del creador del hack (IntroCB_GF_RevealLogo) y la
// del combate (IntroCB_Scene1). Como en la traducción de Emerald Rogue: 5 golpes del jingle con el logo de SeCaVa y
// otros 5 con 'Traducido por SeCaVa'. B se las salta; A/START/SELECT las gestiona el juego (salta toda la intro).
// Compilar: python tools/intro_traduccion.py (direcciones de FireRed USA 1.0 en intro.ld).

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

struct IntroSequenceData
{
    void (*callback)(struct IntroSequenceData *);
    u8 state;
    u8 taskId;
    u8 gengarAttackLanded;
    u16 data[5];             // el juego no los lee: [0] salto con B, [1] DISPCNT y [2] BG0CNT guardados
    u16 timer;
};

extern void SetIntroCB(struct IntroSequenceData *ptr, void (*cb)(struct IntroSequenceData *));
extern void IntroCB_Scene1(struct IntroSequenceData *ptr);
extern void SetGpuReg(u8 regOffset, u16 value);
extern u16 GetGpuReg(u8 regOffset);
extern void LoadPalette(const void *src, u16 offset, u16 size);
extern void BlendPalettes(u32 selectedPalettes, u8 coeff, u16 color);
extern u8 BeginNormalPaletteFade(u32 selectedPalettes, signed char delay, u8 startY, u8 targetY, u16 blendColor);
extern void CpuSet(const void *src, void *dest, u32 control);
extern void MPlayStart(void *mplayInfo, const void *songHeader);
extern void FadeOutBGM(u8 speed);
extern void m4aSoundMode(u32 mode);
extern void Task_CallIntroCallback(u8 taskId);
extern void (*volatile gTasks_func[])(u8);   // gTasks[i].func; cada tarea ocupa 0x28 bytes
extern u8 gMPlayInfo_BGM[];
extern volatile u8 gPaletteFade[];
extern volatile u16 gMain_newKeys;

extern const u8 mus_traduccion[];

#define REG_OFFSET_DISPCNT 0x00
#define REG_OFFSET_BG0CNT  0x08
#define REG_OFFSET_BG0HOFS 0x10
#define REG_OFFSET_BG0VOFS 0x12
#define DISPCNT_BGS        0x0F00
#define DISPCNT_WINDOWS    0xE000  // la escena del logo deja WIN0 activa: recortaría la pantalla
#define DISPCNT_BG0_ON     0x0100
#define PALETTES_ALL       0xFFFFFFFF
#define RGB_BLACK          0
#define B_BUTTON           2
#define SKIP_INTRO_KEYS    (1 | 4 | 8)   // A, SELECT y START: Task_CallIntroCallback salta al título
#define TASK_WORDS         (0x28 / 4)
#define VRAM               0x06000000

// Mezclador de sonido: Emerald Rogue usa 18157 Hz y 12 canales; FireRed (y Ghost Grey), 13379 Hz y 5, que cortan
// los acordes del jingle. Se cambia solo mientras suena y luego se vuelve al del juego (m4aSoundInit de FireRed).
#define SOUND_MODE_JINGLE  (0x00900000 | 0x00060000 | (12 << 12) | (12 << 8))
#define SOUND_MODE_JUEGO   (0x00900000 | 0x00040000 | (12 << 12) | (5 << 8))

#define SWAP_FRAME 270       // mientras se apaga el 5.º golpe, antes de la 2.ª frase (90 BPM = 40 fotogramas por tiempo)
#define END_FRAME  560       // el jingle acaba hacia el fotograma 580

// graficos.s
extern const u32 sPantalla1_Gfx[], sPantalla1_Gfx_End[], sPantalla1_Pal[], sPantalla1_Map[];
extern const u32 sPantalla2_Gfx[], sPantalla2_Gfx_End[], sPantalla2_Pal[], sPantalla2_Map[];

static int FadeActive(void)
{
    return gPaletteFade[7] & 0x80;
}

static void CargarPantalla(const u32 *gfx, const u32 *gfxEnd, const u32 *pal, const u32 *map)
{
    CpuSet(gfx, (void *)(VRAM + 0x8000), (u32)(gfxEnd - gfx) | (1 << 26));
    CpuSet(map, (void *)(VRAM + 0x3800), (0x800 / 4) | (1 << 26));
    LoadPalette(pal, 0, 32);
    BlendPalettes(PALETTES_ALL, 16, RGB_BLACK);
    SetGpuReg(REG_OFFSET_BG0CNT, (2 << 2) | (7 << 8));    // prioridad 0, teselas en 0x8000, mapa en 0x3800
    SetGpuReg(REG_OFFSET_BG0HOFS, 0);
    SetGpuReg(REG_OFFSET_BG0VOFS, 0);
}

// Mientras suenan las pantallas, la tarea de la intro pasa por aquí: si el juego va a saltar al título, el sonido
// vuelve antes a su configuración, porque IntroCB_Traduccion ya no se llamará.
static void Task_IntroTraduccion(u8 taskId)
{
    if (gMain_newKeys & SKIP_INTRO_KEYS)
        m4aSoundMode(SOUND_MODE_JUEGO);
    Task_CallIntroCallback(taskId);
}

__attribute__((section(".text.entry")))
void IntroCB_Traduccion(struct IntroSequenceData *this)
{
    if (this->state >= 2 && this->state <= 4)
    {
        this->timer++;
        if (!this->data[0] && (gMain_newKeys & B_BUTTON))
        {
            FadeOutBGM(4);
            this->data[0] = 1;
        }
    }
    switch (this->state)
    {
    case 0: // se apaga lo que quede de la escena del logo
        if (FadeActive())
            break;
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
        this->state++;
        break;
    case 1:
        if (FadeActive())
            break;
        this->data[1] = GetGpuReg(REG_OFFSET_DISPCNT);
        this->data[2] = GetGpuReg(REG_OFFSET_BG0CNT);
        CargarPantalla(sPantalla1_Gfx, sPantalla1_Gfx_End, sPantalla1_Pal, sPantalla1_Map);
        SetGpuReg(REG_OFFSET_DISPCNT, (this->data[1] & ~(DISPCNT_BGS | DISPCNT_WINDOWS)) | DISPCNT_BG0_ON);
        m4aSoundMode(SOUND_MODE_JINGLE);
        gTasks_func[this->taskId * TASK_WORDS] = Task_IntroTraduccion;
        MPlayStart(gMPlayInfo_BGM, mus_traduccion);
        BeginNormalPaletteFade(PALETTES_ALL, 1, 16, 0, RGB_BLACK);
        this->data[0] = 0;
        this->timer = 0;
        this->state++;
        break;
    case 2: // logo de SeCaVa
    case 3: // fundido a negro entre las dos pantallas
    case 4: // 'Traducido por SeCaVa'
        if (FadeActive())
            break;
        if (this->data[0] || (this->state == 4 && this->timer >= END_FRAME))
        {
            BeginNormalPaletteFade(PALETTES_ALL, 1, 0, 16, RGB_BLACK);
            this->state = 5;
        }
        else if (this->state == 2 && this->timer >= SWAP_FRAME)
        {
            BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
            this->state = 3;
        }
        else if (this->state == 3)
        {
            CargarPantalla(sPantalla2_Gfx, sPantalla2_Gfx_End, sPantalla2_Pal, sPantalla2_Map);
            BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
            this->state = 4;
        }
        break;
    case 5:
        if (FadeActive())
            break;
        SetGpuReg(REG_OFFSET_BG0CNT, this->data[2]);
        SetGpuReg(REG_OFFSET_DISPCNT, this->data[1]);
        m4aSoundMode(SOUND_MODE_JUEGO);
        gTasks_func[this->taskId * TASK_WORDS] = Task_CallIntroCallback;
        SetIntroCB(this, IntroCB_Scene1);
        break;
    }
}
