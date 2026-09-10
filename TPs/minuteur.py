Un projet de minuteur géant sur ESP32 en MicroPython est très accessible. Pour piloter un affichage géant, la solution la plus simple et robuste consiste à utiliser des bandeaux LED RGB adressables (type **WS2812B / Neopixel**) pour former chaque segment des chiffres, contrôlés par un seul pin de l'ESP32.

---

### 1. Matériel requis

* **Microcontrôleur :** ESP32 (ex. ESP32 DevKit V1)
* **Affichage :** Bandeau LED WS2812B 5V (30 ou 60 LED/m)
* **Réception IR :** Récepteur infrarouge **TSOP38238** (ou module IR standard 38kHz)
* **Télécommande :** Télécommande infrarouge standard (type télécommande MP3/Arduino ou vieille télécommande TV)
* **Alimentation :** Bloc secteur 5V (5A à 10A selon le nombre de LED)
* **Composants passifs :** Condensateur $1000\,\mu\text{F}$ (sur le 5V), résistance de $330\,\Omega$ (sur le signal LED)

---

### 2. Schéma de câblage

* **Récepteur IR (TSOP38238) :**
* `VCC` $\rightarrow$ 3.3V (ou 5V selon le module)
* `GND` $\rightarrow$ GND
* `OUT` $\rightarrow$ GPIO 15 de l'ESP32


* **Bandeau LED WS2812B :**
* `+5V` $\rightarrow$ Alimentation 5V externe
* `GND` $\rightarrow$ GND externe **(relié au GND de l'ESP32)**
* `DIN` $\rightarrow$ GPIO 4 de l'ESP32 (avec une résistance de $330\,\Omega$ en série)



---

### 3. Fabrication de l'affichage à 7 segments

Un affichage à 4 chiffres (MM:SS) nécessite **28 segments** (7 par chiffre).

1. Découpez des sections égales de bandeau LED (par exemple **3 LED par segment**).
2. Cablez tous les segments en série les uns après les autres (A, B, C, D, E, F, G pour chaque chiffre).
3. Connectez la sortie de la dernière LED du Chiffre 1 à l'entrée du Chiffre 2, et ainsi de suite.

```
       A
    ┌─────┐
  F │     │ B
    ├─────┤ <--- G
  E │     │ C
    └─────┘
       D

```

---

### 4. Code MicroPython (`main.py`)

Ce code gère la matrice 7 segments, le décompte du temps et la lecture des signaux Infrarouges.

```python
import machine
import neopixel
import utime
from machine import Pin

# Configuration
NUM_DIGITS = 4
LEDS_PER_SEG = 5  # Nombre de LED par segment
LEDS_PER_DIGIT = LEDS_PER_SEG * 7
TOTAL_LEDS = LEDS_PER_DIGIT * NUM_DIGITS

np = neopixel.NeoPixel(Pin(4), TOTAL_LEDS)
ir_pin = Pin(15, Pin.IN)

# Mapping des segments A, B, C, D, E, F, G pour former les chiffres 0-9
SEGMENTS = [
    [1, 1, 1, 1, 1, 1, 0], # 0
    [0, 1, 1, 0, 0, 0, 0], # 1
    [1, 1, 0, 1, 1, 0, 1], # 2
    [1, 1, 1, 1, 0, 0, 1], # 3
    [0, 1, 1, 0, 0, 1, 1], # 4
    [1, 0, 1, 1, 0, 1, 1], # 5
    [1, 0, 1, 1, 1, 1, 1], # 6
    [1, 1, 1, 0, 0, 0, 0], # 7
    [1, 1, 1, 1, 1, 1, 1], # 8
    [1, 1, 1, 1, 0, 1, 1]  # 9
]

COLOR = (255, 0, 0) # Rouge
OFF = (0, 0, 0)

def set_digit(digit_idx, val):
    """ Allume un chiffre à une position donnée """
    start_led = digit_idx * LEDS_PER_DIGIT
    pattern = SEGMENTS[val]
    
    for seg_idx, is_on in enumerate(pattern):
        color = COLOR if is_on else OFF
        for l in range(LEDS_PER_SEG):
            np[start_led + seg_idx * LEDS_PER_SEG + l] = color

def display_time(seconds):
    """ Affiche le temps au format MM:SS """
    m = seconds // 60
    s = seconds % 60
    
    digits = [m // 10, m % 10, s // 10, s % 10]
    for idx, d in enumerate(digits):
        set_digit(idx, d)
    np.write()

# Decodeur IR simplifié (NEC protocol)
def read_ir():
    if ir_pin.value() == 0:
        count = 0
        while ir_pin.value() == 0:
            count += 1
            utime.sleep_us(10)
        return count
    return None

# Boucle Principale
time_left = 300 # 5 minutes par défaut
running = False
last_tick = utime.ticks_ms()

display_time(time_left)

while True:
    # Gestion du décompte
    if running and utime.ticks_diff(utime.ticks_ms(), last_tick) >= 1000:
        last_tick = utime.ticks_ms()
        if time_left > 0:
            time_left -= 1
            display_time(time_left)
        else:
            running = False # Fin du décompte

    # Lecture IR basique (A adapter selon les codes de votre télécommande)
    ir_val = read_ir()
    if ir_val:
        # Action selon le signal reçu
        # Exemple : Toggle Play/Pause, +60s, -60s, Reset
        utime.sleep_ms(200) # Anti-rebond

```

---

### 5. Gestion de la télécommande IR

Pour décoder précisément votre télécommande :

1. Utilisez la bibliothèque MicroPython **`necir`** ou **`uremote`** pour lire les codes hexagonaux des touches de votre télécommande (Marche, Pause, +1 min, -1 min, Reset).
2. Attribuez chaque code IR à une fonction dans le code :
* **Bouton Play/Pause :** Inverse la variable `running`.
* **Boutons + / - :** Ajoute ou retire 60 secondes à `time_left`.
* **Bouton Reset :** Remet `time_left` à la valeur initiale.

#=========================================================================================================================
#  FABLAB_MEN_EX2 ---> Fablab@2026
#================================================================================================================================

Voici la solution complète utilisant une classe légère et réactive pour décoder le protocole **IR NEC** (le standard le plus courant pour les télécommandes IR) de façon non-bloquante via des interruptions hardware (`IRQ`).

---

### 1. Fichier du décodeur IR NEC (`ir_rx.py`)

Créez un fichier nommé **`ir_rx.py`** sur votre ESP32 (via Thonny, uPyCraft ou ampy) et collez-y ce code. Il se charge de lire les signaux sans bloquer l'exécution du reste du programme.

```python
# ir_rx.py - Décodeur IR NEC non-bloquant pour MicroPython
import utime
from machine import Pin

class NEC_RX:
    def __init__(self, pin, callback):
        self.pin = pin
        self.callback = callback
        self.pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._cb)
        self.edge_ticks = []
        
    def _cb(self, pin):
        self.edge_ticks.append(utime.ticks_us())
        if len(self.edge_ticks) >= 67:
            # Traitement du signal une fois le paquet complet
            ticks = self.edge_ticks
            self.edge_ticks = []
            self._decode(ticks)

    def _decode(self, ticks):
        durations = [utime.ticks_diff(ticks[i+1], ticks[i]) for i in range(len(ticks)-1)]
        
        # Vérification de la trame de tête NEC (9ms LOW + 4.5ms HIGH)
        if not (8000 < durations[0] < 10000 and 4000 < durations[1] < 5000):
            return

        data = 0
        for i in range(3, 67, 2):
            data <<= 1
            if durations[i] > 1000: # Intervalle long (~1.68ms) = bit 1
                data |= 1

        # Extraction de l'adresse et de la commande (8-bit)
        cmd = (data >> 8) & 0xFF
        addr = (data >> 24) & 0xFF
        
        # Appel de la fonction utilisateur avec le code reçu
        self.callback(cmd, addr)

```

---

### 2. Code principal du Minuteur (`main.py`)

Ce code importe la classe `NEC_RX`, gère les segments LED (WS2812B/Neopixel) et associe chaque bouton de la télécommande à une fonction (Start/Pause, +1min, -1min, Reset).

```python
import utime
import neopixel
from machine import Pin
from ir_rx import NEC_RX

# --- CONFIGURATION MATÉRIELLE ---
GPIO_NEOPIXEL = 4
GPIO_IR = 15

NUM_DIGITS = 4
LEDS_PER_SEG = 3  # Ajustez selon la taille de vos segments
LEDS_PER_DIGIT = LEDS_PER_SEG * 7
TOTAL_LEDS = LEDS_PER_DIGIT * NUM_DIGITS

np = neopixel.NeoPixel(Pin(GPIO_NEOPIXEL), TOTAL_LEDS)

# Mapping des segments 7 segments (0-9)
SEGMENTS = [
    [1, 1, 1, 1, 1, 1, 0], # 0
    [0, 1, 1, 0, 0, 0, 0], # 1
    [1, 1, 0, 1, 1, 0, 1], # 2
    [1, 1, 1, 1, 0, 0, 1], # 3
    [0, 1, 1, 0, 0, 1, 1], # 4
    [1, 0, 1, 1, 0, 1, 1], # 5
    [1, 0, 1, 1, 1, 1, 1], # 6
    [1, 1, 1, 0, 0, 0, 0], # 7
    [1, 1, 1, 1, 1, 1, 1], # 8
    [1, 1, 1, 1, 0, 1, 1]  # 9
]

COLOR = (255, 0, 0) # Couleur des chiffres (Rouge)
OFF = (0, 0, 0)

# --- VARIABLES D'ÉTAT DU MINUTEUR ---
time_left = 300  # Temps par défaut : 5 minutes (en secondes)
running = False
last_tick = utime.ticks_ms()

# --- FONCTIONS D'AFFICHAGE ---
def set_digit(digit_idx, val):
    start_led = digit_idx * LEDS_PER_DIGIT
    pattern = SEGMENTS[val]
    for seg_idx, is_on in enumerate(pattern):
        color = COLOR if is_on else OFF
        for l in range(LEDS_PER_SEG):
            np[start_led + seg_idx * LEDS_PER_SEG + l] = color

def display_time(seconds):
    m = seconds // 60
    s = seconds % 60
    digits = [m // 10, m % 10, s // 10, s % 10]
    for idx, d in enumerate(digits):
        set_digit(idx, d)
    np.write()

# --- CODES TÉLÉCOMMANDE (À ADAPTER) ---
# Astuce : Lancez le code et appuyez sur vos touches pour voir les codes s'afficher
CMD_PLAY_PAUSE = 0x45  # Exemple : Touche CH-
CMD_PLUS_1MIN  = 0x09  # Exemple : Touche +
CMD_MINUS_1MIN = 0x15  # Exemple : Touche -
CMD_RESET      = 0x43  # Exemple : Touche EQ

# --- TRAITEMENT DES COMMANDES IR ---
def on_ir_receive(cmd, addr):
    global time_left, running
    print(f"Code IR reçu : 0x{cmd:02X} (Adresse: 0x{addr:02X})")
    
    if cmd == CMD_PLAY_PAUSE:
        running = not running
        print("Etat :", "En cours" if running else "En pause")
        
    elif cmd == CMD_PLUS_1MIN:
        time_left += 60
        display_time(time_left)
        
    elif cmd == CMD_MINUS_1MIN:
        if time_left >= 60:
            time_left -= 60
        else:
            time_left = 0
        display_time(time_left)
        
    elif cmd == CMD_RESET:
        running = False
        time_left = 300 # Remet à 5 min
        display_time(time_left)

# Configuration du récepteur IR
ir_sensor = NEC_RX(Pin(GPIO_IR, Pin.IN), callback=on_ir_receive)

# Premier affichage
display_time(time_left)

# --- BOUCLE PRINCIPALE ---
while True:
    if running and utime.ticks_diff(utime.ticks_ms(), last_tick) >= 1000:
        last_tick = utime.ticks_ms()
        if time_left > 0:
            time_left -= 1
            display_time(time_left)
        else:
            running = False  # Arrivé à zéro
            # Clignotement de fin (optionnel)
            for _ in range(3):
                np.fill(OFF)
                np.write()
                utime.sleep_ms(300)
                display_time(0)
                utime.sleep_ms(300)

    utime.sleep_ms(20) # Petite pause pour libérer le CPU

```

---

### 3. Comment identifier les codes de votre télécommande ?

1. Téléversez les fichiers `ir_rx.py` et `main.py` sur votre ESP32.
2. Ouvrez la **console / REPL** (dans Thonny par exemple).
3. Appuyez sur les touches de votre télécommande en pointant vers le récepteur IR.
4. La console affichera des lignes comme :
`Code IR reçu : 0x18 (Adresse: 0x00)`
5. Notez les valeurs (ex: `0x18`) correspondant à chaque touche, puis mettez à jour la section **`CODES TÉLÉCOMMANDE`** dans `main.py`.


#============================================================================================


Le dimensionnement et le câblage de l'alimentation sont les étapes les plus critiques pour un affichage géant à LED WS2812B. Si l'alimentation est insuffisante ou mal câblée, vous observerez une chute de tension (changement de couleur vers le rouge en fin de ruban) voire un risque d'échauffement des câbles.

---

### 1. Dimensionnement de l'alimentation (Puissance)

Chaque LED WS2812B intègre 3 puces (Rouge, Vert, Bleu) et consomme environ **20 mA par couleur à pleine intensité**, soit un maximum de **60 mA (0,06 A) par LED** lorsqu'elle affiche du blanc pur.

#### Calcul du courant maximal

Pour un affichage 4 chiffres à 7 segments avec par exemple 3 LED par segment :

* $4 \text{ chiffres} \times 7 \text{ segments} = 28 \text{ segments}$
* $28 \text{ segments} \times 3 \text{ LED} = 84 \text{ LED}$
* **Courant max théorique :** $84 \text{ LED} \times 0,06\,\text{A} = 5,04\,\text{A}$

#### Marge de sécurité

Appliquez toujours une **marge de sécurité de 20 %** pour éviter de faire chauffer le bloc d'alimentation en continu :


$$I_{\text{alim}} = I_{\text{max}} \times 1,2$$

| Nombre total de LED | Courant Max (Blanc pur) | Courant Moyen (Affichage Rouge/Vert) | Alimentation recommandée |
| --- | --- | --- | --- |
| **84 LED** (3 LED/seg) | 5,0 A | ~1,7 A | **5V / 6A** |
| **140 LED** (5 LED/seg) | 8,4 A | ~2,8 A | **5V / 10A** |
| **280 LED** (10 LED/seg) | 16,8 A | ~5,6 A | **5V / 20A** |

> **Note :** Si vous n'affichez vos chiffres qu'en **Rouge** (1 seule couleur active sur 3), la consommation réelle chute à environ **20 mA par LED**, ce qui réduit fortement les besoins réels. Mais il faut toujours dimensionner l'alimentation pour le cas où tout s'allumerait en blanc.

---

### 2. Le phénomène de chute de tension (Power Injection)

Les pistes de cuivre internes des rubans LED sont très fines. Au-delà de **50 à 100 LED en série**, la résistance du ruban provoque une chute de tension : les LED en fin de chaîne reçoivent moins de 5V et deviennent plus faibles ou tirent vers le rouge.

#### La solution : Réinjection d'alimentation

Ne comptez pas sur le ruban pour faire circuler tout le courant d'un bout à autre.

* **Données (`DIN`) :** Les données circulent impérativement en série, de la sortie d'un segment vers l'entrée du suivant.
* **Alimentation (`5V` / `GND`) :** L'alimentation doit être distribuée en parallèle via un câble de forte section (bus d'alimentation) qui vient se repiquer à plusieurs endroits du ruban.

```
       [ Bloc Alimentation 5V / 10A ]
             │              │
      +5V ───┼──────────────┼──────────────┐
             │              │              │
      GND ───┼──────────────┼──────────────┘
             │              │
             ▼              ▼
       [Chiffre 1] ───> [Chiffre 2] ───> [Chiffre 3] ... (Données DIN en série)
         (Repiquage      (Repiquage
          5V/GND)         5V/GND)

```

Pour un minuteur à 4 chiffres :

1. Amenez un câble $5\text{V}$ et $GND$ principal jusqu'à l'arrière du panneau.
2. Connectez le $5\text{V}$ et le $GND$ au **début du Chiffre 1**, entre le **Chiffre 2 et 3**, et à la **fin du Chiffre 4**.

---

### 3. Choix de la section des câbles

Pour transporter des courants forts en 5V sans perte ni échauffement, respectez la section minimale des fils (AWG) :

* **Bus d'alimentation principal (Sortie d'alim $\rightarrow$ Panneau) :** 1,5 $\text{mm}^2$ à 2,5 $\text{mm}^2$ (14 à 16 AWG).
* **Repiquages individuels vers les chiffres :** 0,5 $\text{mm}^2$ à 0,75 $\text{mm}^2$ (20 à 22 AWG).
* **Ligne de signal (`DIN`) :** Un petit fil de 0,2 $\text{mm}^2$ (24 AWG) suffit amplement.

---

### 4. Schéma de protection du circuit

Pour protéger l'ESP32 et les LED contre les pics de tension et les perturbations :

```
                  ┌──────────────┐
  [ Alim 5V ] ──┬─┤ +5V   WS2812 ├─┐
                │ └──────────────┘ │
                │   [ Condensateur ] (1000 µF / 10V ou 16V)
                │ ┌──────────────┐ │
                └─┤ GND   WS2812 ├─┴──────────────────┐
                  └──────────────┘                    │
                         ▲                            │ (Masse Commune)
                         │ DATA                       │
                      [ R 330Ω ]                      │
                         │                            │
                  ┌──────────────┐                    │
  [ ESP32 ] ──────┤ GPIO 4   GND ├────────────────────┘
                  └──────────────┘

```

1. **Masse commune (GND) :** Le $GND$ de l'ESP32 et le $GND$ du bloc $5\text{V}$ doivent **impérativement être reliés ensemble**. Sans cela, le signal de données sera parasite.
2. **Condensateur de filtrage :** Placez un condensateur électrolytique de $1000\,\mu\text{F}$ (10V ou 16V) aux bornes $5\text{V}$ et $GND$ au plus près de l'entrée du premier ruban LED. Il absorbe les pics de courant lors de l'allumage.
3. **Résistance sur la ligne de données :** Ajoutez une résistance de $330\,\Omega$ à $470\,\Omega$ sur la ligne entre le GPIO 4 de l'ESP32 et le `DIN` de la première LED pour amortir les réflexions de signal.
4. **Niveau logique 3.3V vs 5V :** L'ESP32 sort un signal de 3.3V sur ses GPIO. En général, les WS2812B acceptent le 3.3V si le premier segment n'est pas trop éloigné de l'ESP32 (moins de 30 cm de fil). Si l'affichage clignote, ajoutez un adaptateur de niveau logique (Logic Level Shifter type 74AHCT125 ou module bidirectionnel) pour monter le signal data à 5V.


#==================================================================================================================


