from machine import Pin, time_pulse_us
import neopixel
import time


# ============================================================
#              CONFIGURATION DES LEDS
# ============================================================

# ------------------------------------------------------------
# 2 PREMIERS DIGITS = HEURES
# GPIO4
# ------------------------------------------------------------

PIN_HEURE = 4
NB_HEURE = 14

led_heure = neopixel.NeoPixel(
    Pin(PIN_HEURE),
    NB_HEURE
)


# ------------------------------------------------------------
# 2 DERNIERS DIGITS = MINUTES
# GPIO2
# ------------------------------------------------------------

PIN_MINUTE = 2
NB_MINUTE = 14

led_minute = neopixel.NeoPixel(
    Pin(PIN_MINUTE),
    NB_MINUTE
)


# ------------------------------------------------------------
# DOUBLE POINT
# GPIO3
# ------------------------------------------------------------

PIN_POINTS = 3
NB_POINTS = 2

led_points = neopixel.NeoPixel(
    Pin(PIN_POINTS),
    NB_POINTS
)


# ------------------------------------------------------------
# RECEPTEUR IR
# GPIO5
# ------------------------------------------------------------

PIN_IR = 5
ir = Pin(PIN_IR, Pin.IN)


# ------------------------------------------------------------
# BUZZER
# GPIO7
# ------------------------------------------------------------

PIN_BUZZER = 7

buzzer = Pin(
    PIN_BUZZER,
    Pin.OUT
)

buzzer.value(0)


# ============================================================
#              CODES TELECOMMANDE IR
# ============================================================

CODE_PLUS  = 0xB946FF00
CODE_MOINS = 0xEA15FF00
CODE_START = 0xBA45FF00
CODE_PAUSE = 0xBF40FF00
CODE_RESET = 0xB847FF00


# ============================================================
#                     COULEURS
# ============================================================

COULEUR_HEURE = (30, 30, 30)
COULEUR_MINUTE = (30, 30, 30)
COULEUR_POINTS = (30, 30, 30)

ETEINT = (0, 0, 0)


# ============================================================
#                  TABLE DES SEGMENTS
# ============================================================

# Ordre physique utilisé dans ton code :
#
# 0 = segment A
# 1 = segment B
# 2 = segment C
# 3 = segment D
# 4 = segment E
# 5 = segment F
# 6 = segment G

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
#                 AFFICHER UN CHIFFRE
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
#                 AFFICHER LES HEURES
# ============================================================

def afficher_heures(heures):

    if heures < 0:
        heures = 0

    if heures > 99:
        heures = 99

    dizaine = heures // 10
    unite = heures % 10

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
#                 AFFICHER LES MINUTES
# ============================================================

def afficher_minutes(minutes):

    if minutes < 0:
        minutes = 0

    if minutes > 59:
        minutes = 59

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
#                AFFICHAGE COMPLET HH:MM
# ============================================================

def afficher_temps(heures, minutes):

    afficher_heures(heures)
    afficher_minutes(minutes)


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
#                       BUZZER
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

    # --------------------------------------------------------
    # Début de trame NEC
    # --------------------------------------------------------

    t = time_pulse_us(
        ir,
        0,
        15000
    )

    if t < 8500 or t > 10000:
        return None


    # --------------------------------------------------------
    # 4,5 ms HIGH
    # --------------------------------------------------------

    t = time_pulse_us(
        ir,
        1,
        6000
    )

    if t < 3500 or t > 5500:
        return None


    code = 0


    # --------------------------------------------------------
    # Lecture des 32 bits
    # --------------------------------------------------------

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


        # Bit 0

        if 300 < t < 900:

            bit = 0


        # Bit 1

        elif 1200 < t < 2100:

            bit = 1


        else:

            return None


        code |= (bit << i)


    return code


# ============================================================
#                  VARIABLES DU MINUTEUR
# ============================================================

heures = 0
minutes = 0
secondes = 0

en_marche = False

etat_points = False

dernier_decompte = time.ticks_ms()


# ============================================================
#                  INITIALISATION
# ============================================================

afficher_temps(
    heures,
    minutes
)

points_off()

buzzer.value(0)


print()
print("========================================")
print("          MINUTEUR GEANT HH:MM")
print("          XIAO ESP32-S3")
print("========================================")
print()

print("GPIO4 : HEURES - 14 LEDs")
print("GPIO2 : MINUTES - 14 LEDs")
print("GPIO3 : DOUBLE POINT - 2 LEDs")
print("GPIO5 : RECEPTEUR IR")
print("GPIO7 : BUZZER")

print()

print("Format : HH:MM")
print("Plage : 00:00 a 99:59")

print()

print("Télécommande :")
print("PLUS  :", hex(CODE_PLUS))
print("MOINS :", hex(CODE_MOINS))
print("START :", hex(CODE_START))
print("PAUSE :", hex(CODE_PAUSE))
print("RESET :", hex(CODE_RESET))

print()
print("Systeme pret")
print()


# ============================================================
#                  BOUCLE PRINCIPALE
# ============================================================

while True:


    # ========================================================
    # 1. TELECOMMANDE IR
    # ========================================================

    code = lire_ir()


    if code is not None:

        print(
            "IR recu :",
            hex(code)
        )


        # ====================================================
        # PLUS : +1 MINUTE
        # ====================================================

        if code == CODE_PLUS:

            if not en_marche:

                # Conversion du temps total en minutes

                total_minutes = (heures * 60) + minutes

                # Ajouter 1 minute

                if total_minutes < (99 * 60 + 59):

                    total_minutes += 1

                # Recalculer heures et minutes

                heures = total_minutes // 60

                minutes = total_minutes % 60

                secondes = 0

                afficher_temps(
                    heures,
                    minutes
                )

                print(
                    "Temps programme : {:02d}:{:02d}".format(
                        heures,
                        minutes
                    )
                )


        # ====================================================
        # MOINS : -1 MINUTE
        # ====================================================

        elif code == CODE_MOINS:

            if not en_marche:

                # Conversion du temps total en minutes

                total_minutes = (heures * 60) + minutes

                # Retirer 1 minute

                if total_minutes > 0:

                    total_minutes -= 1

                # Recalculer heures et minutes

                heures = total_minutes // 60

                minutes = total_minutes % 60

                secondes = 0

                afficher_temps(
                    heures,
                    minutes
                )

                print(
                    "Temps programme : {:02d}:{:02d}".format(
                        heures,
                        minutes
                    )
                )


        # ====================================================
        # START
        # ====================================================

        elif code == CODE_START:

            if heures > 0 or minutes > 0 or secondes > 0:

                en_marche = True

                dernier_decompte = time.ticks_ms()

                etat_points = True

                points_on()

                print(
                    ">>> START"
                )


        # ====================================================
        # PAUSE
        # ====================================================

        elif code == CODE_PAUSE:

            en_marche = False

            points_off()

            print(
                ">>> PAUSE"
            )


        # ====================================================
        # RESET
        # ====================================================

        elif code == CODE_RESET:

            en_marche = False

            heures = 0
            minutes = 0
            secondes = 0

            afficher_temps(
                0,
                0
            )

            points_off()

            print(
                ">>> RESET"
            )


        # ----------------------------------------------------
        # Eviter une répétition immédiate de la télécommande
        # ----------------------------------------------------

        time.sleep_ms(250)


    # ========================================================
    # 2. DECOMPTE
    # ========================================================

    if en_marche:

        maintenant = time.ticks_ms()


        if time.ticks_diff(
            maintenant,
            dernier_decompte
        ) >= 1000:


            # ------------------------------------------------
            # Préparer la prochaine seconde
            # ------------------------------------------------

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

                    if heures > 0:

                        heures -= 1

                        minutes = 59

                        secondes = 59


                    else:

                        # ====================================
                        # FIN DU MINUTEUR
                        # ====================================

                        heures = 0
                        minutes = 0
                        secondes = 0

                        en_marche = False

                        points_off()

                        afficher_temps(
                            0,
                            0
                        )

                        print()
                        print("================================")
                        print("        FIN DU MINUTEUR")
                        print("================================")
                        print()

                        bip()


            # ------------------------------------------------
            # AFFICHAGE DU TEMPS RESTANT
            # ------------------------------------------------

            afficher_temps(
                heures,
                minutes
            )

            print(
                "Temps restant : {:02d}:{:02d}:{:02d}".format(
                    heures,
                    minutes,
                    secondes
                )
            )


    # ========================================================
    # PETITE PAUSE
    # ========================================================

    time.sleep_ms(10)