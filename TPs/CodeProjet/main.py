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
