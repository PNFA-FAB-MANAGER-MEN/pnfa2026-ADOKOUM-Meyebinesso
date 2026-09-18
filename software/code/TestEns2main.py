from machine import Pin, RTC, time_pulse_us
import neopixel
import time


# =========================================================
# CONFIGURATION DES BROCHES
# =========================================================

PIN_HEURES = 4       # 14 WS2811
PIN_MINUTES = 2      # 14 WS2811
PIN_COLON = 3        # 2 WS2811
PIN_IR = 5           # HW-477 V02 : S
PIN_BUZZER = 7       # Buzzer


# =========================================================
# CONFIGURATION WS2811
# =========================================================

LED_H = neopixel.NeoPixel(Pin(PIN_HEURES), 14)
LED_M = neopixel.NeoPixel(Pin(PIN_MINUTES), 14)
LED_COLON = neopixel.NeoPixel(Pin(PIN_COLON), 2)


# Luminosité simple
BRIGHTNESS = 0.20


def couleur(r, g, b):
    return (
        int(r * BRIGHTNESS),
        int(g * BRIGHTNESS),
        int(b * BRIGHTNESS)
    )


BLANC = couleur(255, 255, 255)
ROUGE = couleur(255, 0, 0)
VERT = couleur(0, 255, 0)
NOIR = (0, 0, 0)


# =========================================================
# TABLE DES SEGMENTS
# =========================================================
# Ordre : A B C D E F G
#
# Cette table est exactement celle fournie.
# =========================================================

SEGMENTS = {
    0: [1, 1, 1, 1, 1, 1, 0],
    1: [0, 0, 1, 1, 0, 0, 0],
    2: [0, 1, 1, 0, 1, 1, 1],
    3: [0, 1, 1, 1, 1, 0, 1],
    4: [1, 0, 1, 1, 0, 0, 1],
    5: [1, 1, 0, 1, 1, 0, 1],
    6: [1, 1, 0, 1, 1, 1, 1],
    7: [0, 1, 1, 1, 0, 0, 0],
    8: [1, 1, 1, 1, 1, 1, 1],
    9: [1, 1, 1, 1, 1, 0, 1]
}


# =========================================================
# CODES TELECOMMANDE
# =========================================================

IR_PLUS = 0xB946FF00
IR_MINUS = 0xEA15FF00

IR_START = 0xBA45FF00
IR_PAUSE = 0xBF40FF00
IR_RESET = 0xB847FF00

IR_SEL = 0xE619FF00
IR_LEFT = 0xBB44FF00
IR_RIGHT = 0xBC43FF00


# Pavé numérique
IR_0 = 0xE916FF00
IR_1 = 0xF30CFF00
IR_2 = 0xE718FF00
IR_3 = 0xA15EFF00
IR_4 = 0xF708FF00
IR_5 = 0xE31CFF00
IR_6 = 0xA55AFF00
IR_7 = 0xBD42FF00
IR_8 = 0xAD52FF00
IR_9 = 0xB54AFF00


IR_NUM = {
    IR_0: 0,
    IR_1: 1,
    IR_2: 2,
    IR_3: 3,
    IR_4: 4,
    IR_5: 5,
    IR_6: 6,
    IR_7: 7,
    IR_8: 8,
    IR_9: 9
}


# =========================================================
# RTC
# =========================================================

rtc = RTC()

# Année, mois, jour, jour_semaine,
# heure, minute, seconde, microseconde
rtc.datetime((
    2026,
    9,
    16,
    2,
    15,
    30,
    0,
    0
))


# =========================================================
# VARIABLES
# =========================================================

# Valeurs affichées HH:MM
digits = [1, 2, 0, 0]

# Position sélectionnée
# 0 = dizaine heure
# 1 = unité heure
# 2 = dizaine minute
# 3 = unité minute
selection = 0

# Etat du minuteur
countdown_running = False

# Temps restant en secondes
countdown_seconds = 0

# Gestion du clignotement
blink_state = True
last_blink = time.ticks_ms()

# Dernière seconde
last_second = time.ticks_ms()


# =========================================================
# AFFICHAGE D'UN DIGIT
# =========================================================

def afficher_digit(leds, position, chiffre, couleur_led):
    debut = position * 7

    segments = SEGMENTS[chiffre]

    for i in range(7):
        if segments[i]:
            leds[debut + i] = couleur_led
        else:
            leds[debut + i] = NOIR


# =========================================================
# EFFACER LES AFFICHEURS
# =========================================================

def effacer():
    for i in range(14):
        LED_H[i] = NOIR
        LED_M[i] = NOIR

    for i in range(2):
        LED_COLON[i] = NOIR

    LED_H.write()
    LED_M.write()
    LED_COLON.write()


# =========================================================
# AFFICHAGE COMPLET
# =========================================================

def afficher():

    # -----------------------------
    # HEURES
    # -----------------------------

    for pos in range(2):

        chiffre = digits[pos]

        # Digit sélectionné
        if pos == selection and not blink_state:
            couleur_digit = NOIR
        else:
            couleur_digit = BLANC

        afficher_digit(
            LED_H,
            pos,
            chiffre,
            couleur_digit
        )


    # -----------------------------
    # MINUTES
    # -----------------------------

    for pos in range(2):

        chiffre = digits[pos + 2]

        # Digit sélectionné
        if pos + 2 == selection and not blink_state:
            couleur_digit = NOIR
        else:
            couleur_digit = BLANC

        afficher_digit(
            LED_M,
            pos,
            chiffre,
            couleur_digit
        )


    # -----------------------------
    # COLON
    # -----------------------------

    if countdown_running:

        if blink_state:
            LED_COLON[0] = BLANC
            LED_COLON[1] = BLANC
        else:
            LED_COLON[0] = NOIR
            LED_COLON[1] = NOIR

    else:

        LED_COLON[0] = BLANC
        LED_COLON[1] = BLANC


    LED_H.write()
    LED_M.write()
    LED_COLON.write()


# =========================================================
# AFFICHER L'HEURE RTC
# =========================================================

def mettre_heure_rtc():

    global digits

    t = rtc.datetime()

    heure = t[4]
    minute = t[5]

    digits[0] = heure // 10
    digits[1] = heure % 10

    # Les minutes restent celles du minuteur
    # et ne sont pas remplacées par RTC.


# =========================================================
# METTRE LE COMPTE À REBOURS
# =========================================================

def mettre_countdown_dans_digits():

    global digits

    minutes = countdown_seconds // 60

    if minutes > 99:
        minutes = 99

    digits[2] = minutes // 10
    digits[3] = minutes % 10


# =========================================================
# BUZZER
# =========================================================

buzzer = Pin(PIN_BUZZER, Pin.OUT)
buzzer.value(0)


def alarme():

    for i in range(5):

        buzzer.value(1)
        time.sleep_ms(250)

        buzzer.value(0)
        time.sleep_ms(250)


# =========================================================
# DECODAGE IR NEC
# =========================================================

def lire_ir():

    try:

        # Attendre début NEC
        pulse = time_pulse_us(
            Pin(PIN_IR),
            0,
            15000
        )

        if pulse < 8500 or pulse > 9500:
            return None

        pulse = time_pulse_us(
            Pin(PIN_IR),
            1,
            6000
        )

        if pulse < 4000 or pulse > 5000:
            return None

        data = 0

        for i in range(32):

            pulse = time_pulse_us(
                Pin(PIN_IR),
                0,
                2000
            )

            if pulse < 300 or pulse > 800:
                return None

            pulse = time_pulse_us(
                Pin(PIN_IR),
                1,
                2500
            )

            if pulse > 1000:
                data |= (1 << i)

        return data

    except:
        return None


# =========================================================
# MODIFICATION D'UN DIGIT
# =========================================================

def modifier_digit(chiffre):

    global digits

    # --------------------------------
    # DIGITS DES HEURES
    # --------------------------------

    if selection == 0:
        # dizaine des heures
        if chiffre <= 2:
            digits[0] = chiffre

    elif selection == 1:
        # unité des heures
        # vérification 00-23
        if digits[0] == 2:
            if chiffre <= 3:
                digits[1] = chiffre
        else:
            digits[1] = chiffre

    # --------------------------------
    # DIGITS DES MINUTES
    # --------------------------------

    elif selection == 2:
        # dizaine minutes : 0-5
        if chiffre <= 5:
            digits[2] = chiffre

    elif selection == 3:
        # unité minutes : 0-9
        digits[3] = chiffre


# =========================================================
# CONVERSION HH:MM EN SECONDES
# =========================================================

def digits_vers_secondes():

    heures = digits[0] * 10 + digits[1]
    minutes = digits[2] * 10 + digits[3]

    return heures * 3600 + minutes * 60


# =========================================================
# TRAITEMENT DES TOUCHES
# =========================================================

def traiter_touche(code):

    global selection
    global countdown_seconds
    global countdown_running

    # --------------------------------
    # SEL
    # --------------------------------

    if code == IR_SEL:

        selection += 1

        if selection > 3:
            selection = 0


    # --------------------------------
    # LEFT
    # --------------------------------

    elif code == IR_LEFT:

        selection -= 1

        if selection < 0:
            selection = 3


    # --------------------------------
    # RIGHT
    # --------------------------------

    elif code == IR_RIGHT:

        selection += 1

        if selection > 3:
            selection = 0


    # --------------------------------
    # CHIFFRES
    # --------------------------------

    elif code in IR_NUM:

        chiffre = IR_NUM[code]

        modifier_digit(chiffre)

        # Si on modifie les minutes,
        # actualiser le compte à rebours
        if selection == 2 or selection == 3:

            minutes = digits[2] * 10 + digits[3]

            countdown_seconds = minutes * 60


    # --------------------------------
    # PLUS
    # --------------------------------

    elif code == IR_PLUS:

        countdown_seconds += 60

        if countdown_seconds > 99 * 60:
            countdown_seconds = 99 * 60

        mettre_countdown_dans_digits()


    # --------------------------------
    # MOINS
    # --------------------------------

    elif code == IR_MINUS:

        countdown_seconds -= 60

        if countdown_seconds < 0:
            countdown_seconds = 0

        mettre_countdown_dans_digits()


    # --------------------------------
    # START
    # --------------------------------

    elif code == IR_START:

        # Utiliser les minutes affichées
        countdown_seconds = (
            (digits[2] * 10 + digits[3]) * 60
        )

        if countdown_seconds > 0:
            countdown_running = True


    # --------------------------------
    # PAUSE
    # --------------------------------

    elif code == IR_PAUSE:

        countdown_running = False


    # --------------------------------
    # RESET
    # --------------------------------

    elif code == IR_RESET:

        countdown_running = False
        countdown_seconds = 0

        digits[2] = 0
        digits[3] = 0


# =========================================================
# INITIALISATION
# =========================================================

mettre_heure_rtc()

digits[2] = 0
digits[3] = 0

afficher()


# =========================================================
# BOUCLE PRINCIPALE
# =========================================================

while True:

    maintenant = time.ticks_ms()


    # =====================================================
    # CLIGNOTEMENT
    # =====================================================

    if time.ticks_diff(maintenant, last_blink) >= 500:

        last_blink = maintenant
        blink_state = not blink_state

        afficher()


    # =====================================================
    # LECTURE TELECOMMANDE
    # =====================================================

    code = lire_ir()

    if code is not None:

        traiter_touche(code)

        afficher()

        # Petite pause pour éviter les doubles lectures
        time.sleep_ms(150)


    # =====================================================
    # COMPTE À REBOURS
    # =====================================================

    if countdown_running:

        if time.ticks_diff(maintenant, last_second) >= 1000:

            last_second += 1000

            if countdown_seconds > 0:

                countdown_seconds -= 1

                mettre_countdown_dans_digits()

                afficher()


            # ---------------------------------------------
            # FIN DU COMPTE À REBOURS
            # ---------------------------------------------

            if countdown_seconds <= 0:

                countdown_seconds = 0

                digits[2] = 0
                digits[3] = 0

                countdown_running = False

                afficher()

                alarme()


    else:

        last_second = maintenant


    # =====================================================
    # ACTUALISATION DE L'HEURE
    # =====================================================

    # On récupère l'heure RTC toutes les secondes
    # sans modifier les minutes du compte à rebours.

    if not countdown_running:

        t = rtc.datetime()

        heure = t[4]

        digits[0] = heure // 10
        digits[1] = heure % 10

        afficher()


    time.sleep_ms(10)
    