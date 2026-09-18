from machine import Pin, time_pulse_us
import neopixel
import time


# ============================================================
# CONFIGURATION DES BROCHES
# ============================================================

PIN_HEURE = 4       # Bandeau des 2 premiers digits : HH
PIN_MINUTE = 2      # Bandeau des 2 derniers digits : MM
PIN_POINTS = 3      # Double point :
PIN_IR = 5          # Récepteur infrarouge
PIN_BUZZER = 7      # Buzzer

NB_LED_HEURE = 14
NB_LED_MINUTE = 14
NB_LED_POINTS = 2


# ============================================================
# INITIALISATION
# ============================================================

bandeau_heure = neopixel.NeoPixel(
    Pin(PIN_HEURE, Pin.OUT),
    NB_LED_HEURE
)

bandeau_minute = neopixel.NeoPixel(
    Pin(PIN_MINUTE, Pin.OUT),
    NB_LED_MINUTE
)

bandeau_points = neopixel.NeoPixel(
    Pin(PIN_POINTS, Pin.OUT),
    NB_LED_POINTS
)

ir = Pin(PIN_IR, Pin.IN)
buzzer = Pin(PIN_BUZZER, Pin.OUT)


# ============================================================
# COULEURS
# ============================================================

COULEUR_HEURE = (30, 30, 30)
COULEUR_MINUTE = (30, 30, 30)
COULEUR_POINTS = (30, 30, 30)

ETEINT = (0, 0, 0)


# ============================================================
# CODES INFRAROUGES
# ============================================================

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


CODES_NUMERIQUES = {
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


# ============================================================
# SEGMENTS
# ============================================================

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
# AFFICHAGE D'UN DIGIT
# ============================================================

def afficher_chiffre(bandeau, chiffre, position, couleur):

    segments = SEGMENTS[chiffre]

    debut = position * 7

    for i in range(7):
        if segments[i]:
            bandeau[debut + i] = couleur
        else:
            bandeau[debut + i] = ETEINT


# ============================================================
# AFFICHAGE DES HEURES
# ============================================================

def afficher_heures(heures):

    dizaines = heures // 10
    unites = heures % 10

    afficher_chiffre(
        bandeau_heure,
        dizaines,
        0,
        COULEUR_HEURE
    )

    afficher_chiffre(
        bandeau_heure,
        unites,
        1,
        COULEUR_HEURE
    )

    bandeau_heure.write()


# ============================================================
# AFFICHAGE DES MINUTES
# ============================================================

def afficher_minutes(minutes):

    dizaines = minutes // 10
    unites = minutes % 10

    afficher_chiffre(
        bandeau_minute,
        dizaines,
        0,
        COULEUR_MINUTE
    )

    afficher_chiffre(
        bandeau_minute,
        unites,
        1,
        COULEUR_MINUTE
    )

    bandeau_minute.write()


# ============================================================
# AFFICHAGE COMPLET HH:MM
# ============================================================

def afficher_temps():

    afficher_heures(heures)
    afficher_minutes(minutes)


# ============================================================
# DOUBLE POINT
# ============================================================

def afficher_points(etat):

    if etat:
        bandeau_points[0] = COULEUR_POINTS
        bandeau_points[1] = COULEUR_POINTS
    else:
        bandeau_points[0] = ETEINT
        bandeau_points[1] = ETEINT

    bandeau_points.write()


# ============================================================
# BUZZER
# ============================================================

def bip():

    for i in range(5):

        buzzer.value(1)
        time.sleep_ms(250)

        buzzer.value(0)
        time.sleep_ms(250)


# ============================================================
# VARIABLES DU MINUTEUR
# ============================================================

heures = 0
minutes = 0
secondes = 0

en_marche = False

etat_points = False

dernier_decompte = time.ticks_ms()


# ============================================================
# GESTION DE LA SELECTION DES DIGITS
# ============================================================

# Position :
#
# 0 = dizaine des heures
# 1 = unité des heures
# 2 = dizaine des minutes
# 3 = unité des minutes

digit_selectionne = 0


# ============================================================
# OBTENIR LES 4 DIGITS
# ============================================================

def obtenir_digits():

    return [
        heures // 10,
        heures % 10,
        minutes // 10,
        minutes % 10
    ]


# ============================================================
# RECONSTRUIRE HH ET MM AVEC LES 4 DIGITS
# ============================================================

def appliquer_digits(digits):

    global heures, minutes

    nouvelle_heure = digits[0] * 10 + digits[1]
    nouvelle_minute = digits[2] * 10 + digits[3]

    # Limite des minutes : 00 à 59
    if nouvelle_minute > 59:
        return False

    # Limite des heures : 00 à 99
    if nouvelle_heure > 99:
        return False

    heures = nouvelle_heure
    minutes = nouvelle_minute

    return True


# ============================================================
# MODIFICATION D'UN DIGIT
# ============================================================

def modifier_digit(valeur):

    global heures, minutes

    digits = obtenir_digits()

    # --------------------------------------------------------
    # Digit 0 : dizaine des heures
    # --------------------------------------------------------

    if digit_selectionne == 0:

        digits[0] = valeur

        # Exemple : 99 maximum
        if digits[0] <= 9:
            appliquer_digits(digits)


    # --------------------------------------------------------
    # Digit 1 : unité des heures
    # --------------------------------------------------------

    elif digit_selectionne == 1:

        digits[1] = valeur

        appliquer_digits(digits)


    # --------------------------------------------------------
    # Digit 2 : dizaine des minutes
    # --------------------------------------------------------

    elif digit_selectionne == 2:

        # Les dizaines de minutes vont de 0 à 5
        if valeur <= 5:

            digits[2] = valeur
            appliquer_digits(digits)

        else:
            print("Erreur : dizaine des minutes = 0 à 5")


    # --------------------------------------------------------
    # Digit 3 : unité des minutes
    # --------------------------------------------------------

    elif digit_selectionne == 3:

        digits[3] = valeur
        appliquer_digits(digits)


    afficher_temps()

    print(
        "Digit sélectionné:",
        digit_selectionne,
        "Valeur:",
        valeur
    )

    print(
        "Temps:",
        "{:02d}:{:02d}".format(heures, minutes)
    )


# ============================================================
# SELECTION DU DIGIT
# ============================================================

def selectionner_digit():

    global digit_selectionne

    digit_selectionne += 1

    if digit_selectionne > 3:
        digit_selectionne = 0

    print(
        "Digit sélectionné:",
        digit_selectionne
    )


# ============================================================
# DEPLACEMENT GAUCHE
# ============================================================

def aller_gauche():

    global digit_selectionne

    digit_selectionne -= 1

    if digit_selectionne < 0:
        digit_selectionne = 3

    print(
        "Digit sélectionné:",
        digit_selectionne
    )


# ============================================================
# DEPLACEMENT DROITE
# ============================================================

def aller_droite():

    global digit_selectionne

    digit_selectionne += 1

    if digit_selectionne > 3:
        digit_selectionne = 0

    print(
        "Digit sélectionné:",
        digit_selectionne
    )


# ============================================================
# AJOUTER UNE MINUTE
# ============================================================

def ajouter_minute():

    global heures, minutes

    total = heures * 60 + minutes

    total += 1

    # Maximum 99:59
    if total > (99 * 60 + 59):
        total = 99 * 60 + 59

    heures = total // 60
    minutes = total % 60

    afficher_temps()

    print(
        "Temps:",
        "{:02d}:{:02d}".format(heures, minutes)
    )


# ============================================================
# RETIRER UNE MINUTE
# ============================================================

def retirer_minute():

    global heures, minutes

    total = heures * 60 + minutes

    if total > 0:
        total -= 1

    heures = total // 60
    minutes = total % 60

    afficher_temps()

    print(
        "Temps:",
        "{:02d}:{:02d}".format(heures, minutes)
    )


# ============================================================
# DECODAGE IR NEC
# ============================================================

def lire_ir():

    try:

        # Attendre le début du signal
        duree = time_pulse_us(
            ir,
            0,
            150000
        )

        if duree < 8000 or duree > 10000:
            return None

        # Impulsion de 4,5 ms
        duree = time_pulse_us(
            ir,
            1,
            10000
        )

        if duree < 4000 or duree > 5000:
            return None

        code = 0

        for i in range(32):

            # 560 us LOW
            duree = time_pulse_us(
                ir,
                0,
                2000
            )

            if duree < 400 or duree > 800:
                return None

            # Lecture du HIGH
            duree = time_pulse_us(
                ir,
                1,
                3000
            )

            if duree > 1000:
                code |= (1 << i)

        return code

    except:

        return None


# ============================================================
# INITIALISATION AFFICHAGE
# ============================================================

afficher_temps()
afficher_points(False)

buzzer.value(0)

print("====================================")
print("     MINUTEUR GEANT ESP32-S3")
print("====================================")
print("Format : HH:MM")
print("Digit sélectionné :", digit_selectionne)
print("Temps initial : 00:00")
print("====================================")


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

while True:

    # --------------------------------------------------------
    # LECTURE DE LA TELECOMMANDE
    # --------------------------------------------------------

    code = lire_ir()

    if code is not None:

        print("Code IR :", hex(code))

        # ====================================================
        # PLUS
        # ====================================================

        if code == IR_PLUS:

            if not en_marche:
                ajouter_minute()


        # ====================================================
        # MOINS
        # ====================================================

        elif code == IR_MINUS:

            if not en_marche:
                retirer_minute()


        # ====================================================
        # START
        # ====================================================

        elif code == IR_START:

            if heures > 0 or minutes > 0 or secondes > 0:

                en_marche = True

                dernier_decompte = time.ticks_ms()

                print("DECOMPTE DEMARRE")


        # ====================================================
        # PAUSE
        # ====================================================

        elif code == IR_PAUSE:

            en_marche = False

            print(
                "PAUSE - Temps restant : {:02d}:{:02d}:{:02d}".format(
                    heures,
                    minutes,
                    secondes
                )
            )


        # ====================================================
        # RESET
        # ====================================================

        elif code == IR_RESET:

            heures = 0
            minutes = 0
            secondes = 0

            en_marche = False

            afficher_temps()
            afficher_points(False)

            print("RESET -> 00:00")


        # ====================================================
        # SELECTION
        # ====================================================

        elif code == IR_SEL:

            if not en_marche:
                selectionner_digit()


        # ====================================================
        # GAUCHE
        # ====================================================

        elif code == IR_LEFT:

            if not en_marche:
                aller_gauche()


        # ====================================================
        # DROITE
        # ====================================================

        elif code == IR_RIGHT:

            if not en_marche:
                aller_droite()


        # ====================================================
        # PAVE NUMERIQUE
        # ====================================================

        elif code in CODES_NUMERIQUES:

            if not en_marche:

                valeur = CODES_NUMERIQUES[code]

                modifier_digit(valeur)


    # --------------------------------------------------------
    # DECOMPTE CHAQUE SECONDE
    # --------------------------------------------------------

    if en_marche:

        maintenant = time.ticks_ms()

        if time.ticks_diff(
            maintenant,
            dernier_decompte
        ) >= 1000:

            dernier_decompte = maintenant

            # -----------------------------------------------
            # CLIGNOTEMENT DU DOUBLE POINT
            # -----------------------------------------------

            etat_points = not etat_points

            afficher_points(etat_points)


            # -----------------------------------------------
            # DECREMENTATION
            # -----------------------------------------------

            if secondes > 0:

                secondes -= 1

            else:

                secondes = 59

                if minutes > 0:

                    minutes -= 1

                else:

                    if heures > 0:

                        heures -= 1
                        minutes = 59

                    else:

                        # -----------------------------------
                        # FIN DU DECOMPTE
                        # -----------------------------------

                        heures = 0
                        minutes = 0
                        secondes = 0

                        en_marche = False

                        afficher_temps()
                        afficher_points(False)

                        print("================================")
                        print("       FIN DU DECOMPTE")
                        print("            00:00")
                        print("================================")

                        bip()

                        continue


            # -----------------------------------------------
            # AFFICHAGE
            # -----------------------------------------------

            afficher_temps()

            print(
                "Temps restant : {:02d}:{:02d}:{:02d}".format(
                    heures,
                    minutes,
                    secondes
                )
            )


    # Petite pause pour éviter de saturer le processeur
    time.sleep_ms(10)
    