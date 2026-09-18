from machine import Pin, RTC, time_pulse_us
import neopixel
import time


# ============================================================
#                    CONFIGURATION
# ============================================================

# -------------------------
# LEDs HEURE
# GPIO4
# -------------------------
PIN_HEURE = 4
NB_HEURE = 14

led_heure = neopixel.NeoPixel(
    Pin(PIN_HEURE),
    NB_HEURE
)


# -------------------------
# LEDs MINUTEUR
# GPIO2
# -------------------------
PIN_MINUTE = 2
NB_MINUTE = 14

led_minute = neopixel.NeoPixel(
    Pin(PIN_MINUTE),
    NB_MINUTE
)


# -------------------------
# DOUBLE POINT
# GPIO3
# -------------------------
PIN_POINTS = 3
NB_POINTS = 2

led_points = neopixel.NeoPixel(
    Pin(PIN_POINTS),
    NB_POINTS
)


# -------------------------
# RECEPTEUR IR
# GPIO5
# -------------------------
PIN_IR = 5

ir = Pin(PIN_IR, Pin.IN)


# -------------------------
# BUZZER
# GPIO7
# -------------------------
PIN_BUZZER = 7

buzzer = Pin(
    PIN_BUZZER,
    Pin.OUT
)

buzzer.value(0)


# -------------------------
# HORLOGE RTC
# -------------------------
rtc = RTC()


# ============================================================
#                CODES TELECOMMANDE
# ============================================================

CODE_PLUS  = 0xB946FF00
CODE_MOINS = 0xEA15FF00
CODE_START = 0xBA45FF00
CODE_PAUSE = 0xBF40FF00
CODE_RESET = 0xB847FF00


# ============================================================
#                     COULEURS
# ============================================================

# Commencer avec une luminosité raisonnable
COULEUR_HEURE = (30, 30, 30)

COULEUR_MINUTE = (30, 30, 30)

COULEUR_POINTS = (30, 30, 30)

ETEINT = (0, 0, 0)


# ============================================================
#                 TABLE DES SEGMENTS
# ============================================================

# Ordre supposé des LEDs :
#
# LED 0 = A
# LED 1 = B
# LED 2 = C
# LED 3 = D
# LED 4 = E
# LED 5 = F
# LED 6 = G
#
# puis deuxième chiffre :
#
# LED 7  = A
# LED 8  = B
# LED 9  = C
# LED 10 = D
# LED 11 = E
# LED 12 = F
# LED 13 = G

'''
SEGMENTS = {

    0: [1, 1, 1, 1, 1, 1, 0],

    1: [0, 1, 1, 0, 0, 0, 0],

    2: [1, 1, 0, 1, 1, 0, 1],

    3: [1, 1, 1, 1, 0, 0, 1],

    4: [0, 1, 1, 0, 0, 1, 1],

    5: [1, 0, 1, 1, 0, 1, 1],

    6: [1, 0, 1, 1, 1, 1, 1],

    7: [1, 1, 1, 0, 0, 0, 0],

    8: [1, 1, 1, 1, 1, 1, 1],

    9: [1, 1, 1, 1, 0, 1, 1]
}
'''

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
#              AFFICHER UN CHIFFRE
# ============================================================

def afficher_chiffre(bandeau, chiffre, position, couleur):

    schema = SEGMENTS[chiffre]

    if position == 0:
        debut = 0
    else:
        debut = 7

    for segment in range(7):

        if schema[segment] == 1:
            bandeau[debut + segment] = couleur

        else:
            bandeau[debut + segment] = ETEINT


# ============================================================
#                  AFFICHER HEURE
# ============================================================

def afficher_heure(heure):

    dizaine = heure // 10
    unite = heure % 10

    afficher_chiffre(
        led_heure,
        dizaine,
        0,
        COULEUR_HEURE
    )

    afficher_chiffre(
        led_heure,
        unite,
        1,
        COULEUR_HEURE
    )

    led_heure.write()


# ============================================================
#               AFFICHER MINUTEUR
# ============================================================

def afficher_minuteur(minutes):

    if minutes < 0:
        minutes = 0

    if minutes > 99:
        minutes = 99

    dizaine = minutes // 10
    unite = minutes % 10

    afficher_chiffre(
        led_minute,
        dizaine,
        0,
        COULEUR_MINUTE
    )

    afficher_chiffre(
        led_minute,
        unite,
        1,
        COULEUR_MINUTE
    )

    led_minute.write()


# ============================================================
#                  DOUBLE POINT
# ============================================================

def points_on():

    led_points[0] = COULEUR_POINTS
    led_points[1] = COULEUR_POINTS

    led_points.write()


def points_off():

    led_points[0] = ETEINT
    led_points[1] = ETEINT

    led_points.write()


# ============================================================
#                      BUZZER
# ============================================================

def bip():

    # 5 bips
    for i in range(5):

        buzzer.value(1)
        time.sleep_ms(250)

        buzzer.value(0)
        time.sleep_ms(250)


# ============================================================
#                  LECTURE IR NEC
# ============================================================

def lire_ir():

    # Début de trame NEC
    t = time_pulse_us(
        ir,
        0,
        15000
    )

    if t < 8500 or t > 10000:
        return None


    # 4,5 ms HIGH
    t = time_pulse_us(
        ir,
        1,
        6000
    )

    if t < 3500 or t > 5500:
        return None


    code = 0


    # 32 bits
    for i in range(32):

        # LOW ~560 us
        t = time_pulse_us(
            ir,
            0,
            2000
        )

        if t < 300 or t > 900:
            return None


        # HIGH
        t = time_pulse_us(
            ir,
            1,
            2500
        )


        # bit 0
        if 300 < t < 900:

            bit = 0


        # bit 1
        elif 1200 < t < 2100:

            bit = 1


        else:

            return None


        code |= (bit << i)


    return code


# ============================================================
#             CONFIGURATION DE L'HORLOGE
# ============================================================

# Format RTC :
#
# (année, mois, jour, jour_semaine,
#  heure, minute, seconde, sous-seconde)
#
# IMPORTANT :
# MODIFIEZ CES VALEURS POUR REGLER L'HEURE
#
# Exemple : 16 septembre 2026 à 15h30

rtc.datetime((
    2026,     # année
    9,        # mois
    16,       # jour
    2,        # jour de la semaine
    15,       # heure
    30,       # minute
    0,        # seconde
    0
))


# ============================================================
#              VARIABLES DU MINUTEUR
# ============================================================

minutes = 0
secondes = 0

en_marche = False

etat_points = False

dernier_decompte = time.ticks_ms()


# ============================================================
#                  INITIALISATION
# ============================================================

afficher_heure(
    rtc.datetime()[4]
)

afficher_minuteur(0)

points_off()

buzzer.value(0)


print()
print("========================================")
print("       MINUTEUR + HORLOGE WS2811")
print("       XIAO ESP32-S3")
print("========================================")
print()
print("GPIO4 : HEURE - 14 LEDs")
print("GPIO2 : MINUTEUR - 14 LEDs")
print("GPIO3 : DOUBLE POINT - 2 LEDs")
print("GPIO5 : RECEPTEUR IR")
print("GPIO7 : BUZZER")
print()
print("Télécommande :")
print("PLUS  :", hex(CODE_PLUS))
print("MOINS :", hex(CODE_MOINS))
print("START :", hex(CODE_START))
print("PAUSE :", hex(CODE_PAUSE))
print("RESET :", hex(CODE_RESET))
print()
print("Système prêt")
print()


# ============================================================
#                  BOUCLE PRINCIPALE
# ============================================================

while True:

    # ========================================================
    # 1. MISE A JOUR DE L'HEURE
    # ========================================================

    maintenant_rtc = rtc.datetime()

    heure_actuelle = maintenant_rtc[4]

    # Afficher l'heure
    afficher_heure(
        heure_actuelle
    )


    # ========================================================
    # 2. TELECOMMANDE IR
    # ========================================================

    code = lire_ir()


    if code is not None:

        print(
            "IR reçu :",
            hex(code)
        )


        # ----------------------------------------------------
        # PLUS
        # ----------------------------------------------------

        if code == CODE_PLUS:

            if not en_marche:

                if minutes < 99:

                    minutes += 1

                secondes = 0

                afficher_minuteur(
                    minutes
                )

                print(
                    "Temps programmé : {:02d}:00".format(
                        minutes
                    )
                )


        # ----------------------------------------------------
        # MOINS
        # ----------------------------------------------------

        elif code == CODE_MOINS:

            if not en_marche:

                if minutes > 0:

                    minutes -= 1

                secondes = 0

                afficher_minuteur(
                    minutes
                )

                print(
                    "Temps programmé : {:02d}:00".format(
                        minutes
                    )
                )


        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        elif code == CODE_START:

            if minutes > 0 or secondes > 0:

                en_marche = True

                dernier_decompte = time.ticks_ms()

                etat_points = True

                points_on()

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

            afficher_minuteur(0)

            points_off()

            print(">>> RESET")


        # Eviter une répétition immédiate
        time.sleep_ms(250)


    # ========================================================
    # 3. DECOMPTE DES MINUTES
    # ========================================================

    if en_marche:

        maintenant = time.ticks_ms()


        if time.ticks_diff(
                maintenant,
                dernier_decompte
        ) >= 1000:


            dernier_decompte = time.ticks_add(
                dernier_decompte,
                1000
            )


            # ------------------------------------------------
            # CLIGNOTEMENT DU DOUBLE POINT
            # ------------------------------------------------

            etat_points = not etat_points


            if etat_points:

                points_on()

            else:

                points_off()


            # ------------------------------------------------
            # DECREMENTATION
            # ------------------------------------------------

            if secondes > 0:

                secondes -= 1


            else:

                if minutes > 0:

                    minutes -= 1

                    secondes = 59


                else:

                    # ========================================
                    # FIN DU MINUTEUR
                    # ========================================

                    minutes = 0
                    secondes = 0

                    en_marche = False

                    points_off()

                    afficher_minuteur(0)

                    print()
                    print("================================")
                    print("       FIN DU MINUTEUR")
                    print("================================")
                    print()

                    bip()


            # Affichage du temps restant
            afficher_minuteur(
                minutes
            )

            print(
                "Temps restant : {:02d}:{:02d}".format(
                    minutes,
                    secondes
                )
            )


    # ========================================================
    # PETITE PAUSE
    # ========================================================

    time.sleep_ms(10)
    