from machine import Pin, time_pulse_us
import neopixel
import time

# ============================================================
# CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# Bandeau principal : 14 LEDs
# GPIO2 -> DATA
# 7 LEDs = chiffre gauche
# 7 LEDs = chiffre droit
# ------------------------------------------------------------

PIN_DIGITS = 2
NB_DIGITS_LEDS = 14

digits = neopixel.NeoPixel(
    Pin(PIN_DIGITS),
    NB_DIGITS_LEDS
)

# ------------------------------------------------------------
# Double point : 2 LEDs
# GPIO3 -> DATA
# ------------------------------------------------------------

PIN_POINTS = 3
NB_POINTS_LEDS = 2

points = neopixel.NeoPixel(
    Pin(PIN_POINTS),
    NB_POINTS_LEDS
)

# ------------------------------------------------------------
# Récepteur infrarouge HW-477
# S -> GPIO4
# ------------------------------------------------------------

PIN_IR = 4
ir = Pin(PIN_IR, Pin.IN)


# ============================================================
# CODES DE LA TELECOMMANDE
# ============================================================

CODE_PLUS  = 0xB946FF00
CODE_MOINS = 0xEA15FF00
CODE_START = 0xBA45FF00
CODE_PAUSE = 0xBF40FF00
CODE_RESET = 0xB847FF00


# ============================================================
# COULEURS
# ============================================================

# Commencer avec une intensité modérée
COULEUR = (40, 40, 40)

COULEUR_POINTS = (40, 40, 40)

ETEINT = (0, 0, 0)


# ============================================================
# CONFIGURATION DES SEGMENTS
# ============================================================

# Chaque chiffre possède 7 segments :
#
#             A
#           -----
#        F |     | B
#           --G--
#        E |     | C
#           -----
#             D
#
# Pour chaque chiffre :
#
# [A, B, C, D, E, F, G]
#
# 1 = LED allumée
# 0 = LED éteinte

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


# ============================================================
# ETEINDRE LES 14 LEDs
# ============================================================

def eteindre_digits():

    for i in range(14):
        digits[i] = ETEINT

    digits.write()


# ============================================================
# AFFICHER UN CHIFFRE
# ============================================================

def afficher_chiffre(chiffre, position):

    schema = SEGMENTS[chiffre]

    # Chiffre gauche = LEDs 0 à 6
    # Chiffre droit  = LEDs 7 à 13

    if position == 0:
        debut = 0
    else:
        debut = 7

    for segment in range(7):

        if schema[segment] == 1:
            digits[debut + segment] = COULEUR
        else:
            digits[debut + segment] = ETEINT


# ============================================================
# AFFICHER LES MINUTES
# ============================================================

def afficher_minutes(minutes):

    if minutes < 0:
        minutes = 0

    if minutes > 99:
        minutes = 99

    dizaines = minutes // 10
    unites = minutes % 10

    afficher_chiffre(dizaines, 0)
    afficher_chiffre(unites, 1)

    digits.write()


# ============================================================
# DOUBLE POINT
# GPIO3
# ============================================================

def points_on():

    points[0] = COULEUR_POINTS
    points[1] = COULEUR_POINTS

    points.write()


def points_off():

    points[0] = ETEINT
    points[1] = ETEINT

    points.write()


# ============================================================
# LECTURE INFRAROUGE NEC
# ============================================================

def lire_ir():

    # Début de trame NEC
    t = time_pulse_us(ir, 0, 15000)

    if t < 8500 or t > 10000:
        return None

    # Impulsion HIGH de ~4,5 ms
    t = time_pulse_us(ir, 1, 6000)

    if t < 3500 or t > 5500:
        return None

    code = 0

    # Lecture des 32 bits
    for i in range(32):

        # LOW ~560 us
        t = time_pulse_us(ir, 0, 2000)

        if t < 300 or t > 900:
            return None

        # HIGH :
        # ~560 us  = 0
        # ~1690 us = 1

        t = time_pulse_us(ir, 1, 2500)

        if 300 < t < 900:

            bit = 0

        elif 1200 < t < 2100:

            bit = 1

        else:

            return None

        code |= (bit << i)

    return code


# ============================================================
# VARIABLES DU MINUTEUR
# ============================================================

minutes = 0
secondes = 0

en_marche = False

dernier_temps = time.ticks_ms()

etat_points = False


# ============================================================
# INITIALISATION
# ============================================================

afficher_minutes(0)
points_off()

print()
print("====================================")
print("       MINUTEUR WS2811")
print("       XIAO ESP32-S3")
print("====================================")
print("GPIO2 : 14 LEDs chiffres")
print("GPIO3 : 2 LEDs double point")
print("GPIO4 : récepteur IR HW-477")
print("------------------------------------")
print("PLUS  :", hex(CODE_PLUS))
print("MOINS :", hex(CODE_MOINS))
print("START :", hex(CODE_START))
print("PAUSE :", hex(CODE_PAUSE))
print("RESET :", hex(CODE_RESET))
print("------------------------------------")
print("Minuteur prêt")
print()


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

while True:

    # ========================================================
    # TELECOMMANDE
    # ========================================================

    code = lire_ir()

    if code is not None:

        print("IR :", hex(code))

        # ----------------------------------------------------
        # PLUS
        # ----------------------------------------------------

        if code == CODE_PLUS:

            # Modification seulement lorsque le minuteur
            # est arrêté ou en pause

            if not en_marche:

                if minutes < 99:
                    minutes += 1

                secondes = 0

                afficher_minutes(minutes)

                print(
                    "Temps programmé :",
                    "{:02d}:00".format(minutes)
                )


        # ----------------------------------------------------
        # MOINS
        # ----------------------------------------------------

        elif code == CODE_MOINS:

            if not en_marche:

                if minutes > 0:
                    minutes -= 1

                secondes = 0

                afficher_minutes(minutes)

                print(
                    "Temps programmé :",
                    "{:02d}:00".format(minutes)
                )


        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        elif code == CODE_START:

            if minutes > 0 or secondes > 0:

                en_marche = True

                dernier_temps = time.ticks_ms()

                print(">>> START")


        # ----------------------------------------------------
        # PAUSE
        # ----------------------------------------------------

        elif code == CODE_PAUSE:

            en_marche = False

            points_off()

            print(">>> PAUSE")


        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

        elif code == CODE_RESET:

            en_marche = False

            minutes = 0
            secondes = 0

            afficher_minutes(0)

            points_off()

            print(">>> RESET")


        # éviter les doubles lectures
        time.sleep_ms(250)


    # ========================================================
    # DECOMPTE
    # ========================================================

    if en_marche:

        maintenant = time.ticks_ms()

        if time.ticks_diff(
                maintenant,
                dernier_temps
        ) >= 1000:

            dernier_temps = time.ticks_add(
                dernier_temps,
                1000
            )

            # ------------------------------------------------
            # CLIGNOTEMENT DES DEUX POINTS
            # ------------------------------------------------

            etat_points = not etat_points

            if etat_points:
                points_on()
            else:
                points_off()


            # ------------------------------------------------
            # DECOMPTE
            # ------------------------------------------------

            if secondes > 0:

                secondes -= 1

            else:

                if minutes > 0:

                    minutes -= 1
                    secondes = 59

                else:

                    # Arrivée à 00:00

                    minutes = 0
                    secondes = 0

                    en_marche = False

                    points_off()

                    print(">>> FIN DU MINUTEUR")


            # ------------------------------------------------
            # AFFICHAGE
            # ------------------------------------------------

            afficher_minutes(minutes)

            print(
                "Temps restant : {:02d}:{:02d}".format(
                    minutes,
                    secondes
                )
            )


    time.sleep_ms(5)