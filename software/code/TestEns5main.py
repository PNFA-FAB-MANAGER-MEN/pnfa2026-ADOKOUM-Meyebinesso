from machine import Pin, time_pulse_us
import neopixel
import time


# ============================================================
# CONFIGURATION
# ============================================================

PIN_HEURE = 4
PIN_MINUTE = 2
PIN_POINTS = 3
PIN_IR = 5
PIN_BUZZER = 7

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

# Couleur utilisée pour le digit sélectionné
COULEUR_SELECTION = (30, 30, 30)

ETEINT = (0, 0, 0)


# ============================================================
# CODES IR
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
# VARIABLES DU MINUTEUR
# ============================================================

heures = 0
minutes = 0
secondes = 0

en_marche = False

# Digit sélectionné :
#
# 0 = dizaine heure
# 1 = unité heure
# 2 = dizaine minute
# 3 = unité minute

digit_selectionne = 0

# Etat du clignotement du digit
etat_clignotement_digit = True

dernier_clignotement_digit = time.ticks_ms()

# Etat du double point
etat_points = False

dernier_decompte = time.ticks_ms()


# ============================================================
# TEMPS TOTAL PROGRAMMÉ
# ============================================================

temps_total_programme = 0

# Alertes déjà déclenchées
alerte_50 = False
alerte_75 = False


# ============================================================
# AFFICHAGE D'UN CHIFFRE
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
# AFFICHAGE NORMAL DES DIGITS
# ============================================================

def afficher_temps():

    # --------------------------------------------------------
    # Récupération des 4 digits
    # --------------------------------------------------------

    digits = [
        heures // 10,
        heures % 10,
        minutes // 10,
        minutes % 10
    ]

    # --------------------------------------------------------
    # Bandeau HEURES
    # --------------------------------------------------------

    for i in range(2):

        position_digit = i

        # Si le digit est sélectionné et doit être éteint
        if (
            position_digit == digit_selectionne
            and not en_marche
            and not etat_clignotement_digit
        ):

            afficher_chiffre(
                bandeau_heure,
                digits[i],
                i,
                ETEINT
            )

        else:

            afficher_chiffre(
                bandeau_heure,
                digits[i],
                i,
                COULEUR_HEURE
            )

    bandeau_heure.write()

    # --------------------------------------------------------
    # Bandeau MINUTES
    # --------------------------------------------------------

    for i in range(2):

        position_digit = i + 2

        if (
            position_digit == digit_selectionne
            and not en_marche
            and not etat_clignotement_digit
        ):

            afficher_chiffre(
                bandeau_minute,
                digits[position_digit],
                i,
                ETEINT
            )

        else:

            afficher_chiffre(
                bandeau_minute,
                digits[position_digit],
                i,
                COULEUR_MINUTE
            )

    bandeau_minute.write()


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
# APPLIQUER LES 4 DIGITS
# ============================================================

def appliquer_digits(digits):

    global heures
    global minutes

    nouvelle_heure = digits[0] * 10 + digits[1]
    nouvelle_minute = digits[2] * 10 + digits[3]

    # Limites
    if nouvelle_heure > 99:
        return False

    if nouvelle_minute > 59:
        return False

    heures = nouvelle_heure
    minutes = nouvelle_minute

    return True


# ============================================================
# MODIFIER LE DIGIT SÉLECTIONNÉ
# ============================================================

def modifier_digit(valeur):

    digits = obtenir_digits()

    # --------------------------------------------------------
    # DIZAINE DES HEURES
    # --------------------------------------------------------

    if digit_selectionne == 0:

        digits[0] = valeur

        appliquer_digits(digits)


    # --------------------------------------------------------
    # UNITÉ DES HEURES
    # --------------------------------------------------------

    elif digit_selectionne == 1:

        digits[1] = valeur

        appliquer_digits(digits)


    # --------------------------------------------------------
    # DIZAINE DES MINUTES
    # --------------------------------------------------------

    elif digit_selectionne == 2:

        # 0 à 5 seulement
        if valeur <= 5:

            digits[2] = valeur

            appliquer_digits(digits)

        else:

            print(
                "Valeur impossible pour la dizaine des minutes."
            )

            return


    # --------------------------------------------------------
    # UNITÉ DES MINUTES
    # --------------------------------------------------------

    elif digit_selectionne == 3:

        digits[3] = valeur

        appliquer_digits(digits)


    afficher_temps()

    print(
        "Digit {} modifié avec {}".format(
            digit_selectionne,
            valeur
        )
    )

    print(
        "Temps programmé : {:02d}:{:02d}".format(
            heures,
            minutes
        )
    )


# ============================================================
# SELECTION
# ============================================================

def selectionner_digit():

    global digit_selectionne
    global etat_clignotement_digit

    digit_selectionne += 1

    if digit_selectionne > 3:
        digit_selectionne = 0

    etat_clignotement_digit = True

    afficher_temps()

    print(
        "Digit sélectionné :",
        digit_selectionne
    )


# ============================================================
# GAUCHE
# ============================================================

def aller_gauche():

    global digit_selectionne
    global etat_clignotement_digit

    digit_selectionne -= 1

    if digit_selectionne < 0:
        digit_selectionne = 3

    etat_clignotement_digit = True

    afficher_temps()

    print(
        "Digit sélectionné :",
        digit_selectionne
    )


# ============================================================
# DROITE
# ============================================================

def aller_droite():

    global digit_selectionne
    global etat_clignotement_digit

    digit_selectionne += 1

    if digit_selectionne > 3:
        digit_selectionne = 0

    etat_clignotement_digit = True

    afficher_temps()

    print(
        "Digit sélectionné :",
        digit_selectionne
    )


# ============================================================
# +1 MINUTE
# ============================================================

def ajouter_minute():

    global heures
    global minutes

    total = heures * 60 + minutes

    total += 1

    if total > (99 * 60 + 59):

        total = 99 * 60 + 59

    heures = total // 60
    minutes = total % 60

    afficher_temps()

    print(
        "Temps : {:02d}:{:02d}".format(
            heures,
            minutes
        )
    )


# ============================================================
# -1 MINUTE
# ============================================================

def retirer_minute():

    global heures
    global minutes

    total = heures * 60 + minutes

    if total > 0:
        total -= 1

    heures = total // 60
    minutes = total % 60

    afficher_temps()

    print(
        "Temps : {:02d}:{:02d}".format(
            heures,
            minutes
        )
    )


# ============================================================
# BUZZER : 1 BIP
# ============================================================

def bip_une_fois():

    buzzer.value(1)
    time.sleep_ms(300)

    buzzer.value(0)

    print("ALERTE : 50 %")


# ============================================================
# BUZZER : 2 BIPS
# ============================================================

def bip_deux_fois():

    for i in range(2):

        buzzer.value(1)
        time.sleep_ms(300)

        buzzer.value(0)
        time.sleep_ms(300)

    print("ALERTE : 75 %")


# ============================================================
# BUZZER : 10 SECONDES
# ============================================================

def bip_fin():

    debut = time.ticks_ms()

    print("FIN DU DECOMPTE : BUZZER 10 secondes")

    while time.ticks_diff(
        time.ticks_ms(),
        debut
    ) < 10000:

        buzzer.value(1)
        time.sleep_ms(250)

        buzzer.value(0)
        time.sleep_ms(250)

    buzzer.value(0)


# ============================================================
# DECODAGE IR NEC
# ============================================================

def lire_ir():

    try:

        duree = time_pulse_us(
            ir,
            0,
            150000
        )

        if duree < 8000 or duree > 10000:
            return None

        duree = time_pulse_us(
            ir,
            1,
            10000
        )

        if duree < 4000 or duree > 5000:
            return None

        code = 0

        for i in range(32):

            duree = time_pulse_us(
                ir,
                0,
                2000
            )

            if duree < 400 or duree > 800:
                return None

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
# INITIALISATION
# ============================================================

afficher_temps()
afficher_points(False)

buzzer.value(0)

print("======================================")
print("       MINUTEUR GEANT ESP32-S3")
print("======================================")
print("Format : HH:MM")
print("0 = dizaine heure")
print("1 = unité heure")
print("2 = dizaine minute")
print("3 = unité minute")
print("======================================")


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

while True:

    # ========================================================
    # CLIGNOTEMENT DU DIGIT SELECTIONNE
    # ========================================================

    if not en_marche:

        maintenant = time.ticks_ms()

        if time.ticks_diff(
            maintenant,
            dernier_clignotement_digit
        ) >= 500:

            dernier_clignotement_digit = maintenant

            etat_clignotement_digit = not etat_clignotement_digit

            afficher_temps()


    # ========================================================
    # LECTURE IR
    # ========================================================

    code = lire_ir()

    if code is not None:

        print("IR :", hex(code))

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

                # --------------------------------------------
                # Calcul du temps total au démarrage
                # --------------------------------------------

                temps_total_programme = (
                    heures * 3600
                    + minutes * 60
                    + secondes
                )

                # --------------------------------------------
                # Réinitialisation des alertes
                # --------------------------------------------

                alerte_50 = False
                alerte_75 = False

                en_marche = True

                dernier_decompte = time.ticks_ms()

                afficher_points(True)

                print("================================")
                print("DECOMPTE DEMARRE")
                print(
                    "Temps programmé : {:02d}:{:02d}".format(
                        heures,
                        minutes
                    )
                )

                print(
                    "Temps total :",
                    temps_total_programme,
                    "secondes"
                )

                print("================================")


        # ====================================================
        # PAUSE
        # ====================================================

        elif code == IR_PAUSE:

            en_marche = False

            afficher_points(False)

            print(
                "PAUSE : {:02d}:{:02d}:{:02d}".format(
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

            temps_total_programme = 0

            alerte_50 = False
            alerte_75 = False

            en_marche = False

            afficher_temps()
            afficher_points(False)

            print("RESET -> 00:00")


        # ====================================================
        # SEL
        # ====================================================

        elif code == IR_SEL:

            if not en_marche:

                selectionner_digit()


        # ====================================================
        # LEFT
        # ====================================================

        elif code == IR_LEFT:

            if not en_marche:

                aller_gauche()


        # ====================================================
        # RIGHT
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


    # ========================================================
    # DECOMPTE
    # ========================================================

    if en_marche:

        maintenant = time.ticks_ms()

        if time.ticks_diff(
            maintenant,
            dernier_decompte
        ) >= 1000:

            dernier_decompte = maintenant

            # ------------------------------------------------
            # CLIGNOTEMENT DU DOUBLE POINT
            # ------------------------------------------------

            etat_points = not etat_points

            afficher_points(etat_points)


            # ------------------------------------------------
            # CALCUL DU TEMPS RESTANT AVANT DECREMENT
            # ------------------------------------------------

            temps_restant = (
                heures * 3600
                + minutes * 60
                + secondes
            )


            # =================================================
            # ALERTE 50 %
            # =================================================

            # Temps écoulé >= 50 %
            if (
                not alerte_50
                and temps_total_programme > 0
                and temps_restant
                <= temps_total_programme * 0.50
            ):

                alerte_50 = True

                bip_une_fois()


            # =================================================
            # ALERTE 75 %
            # =================================================

            if (
                not alerte_75
                and temps_total_programme > 0
                and temps_restant
                <= temps_total_programme * 0.25
            ):

                alerte_75 = True

                bip_deux_fois()


            # ------------------------------------------------
            # DECREMENTATION
            # ------------------------------------------------

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

                        # =====================================
                        # FIN DU DECOMPTE
                        # =====================================

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

                        # Buzzer pendant 10 secondes
                        bip_fin()

                        continue


            # ------------------------------------------------
            # AFFICHAGE
            # ------------------------------------------------

            afficher_temps()

            print(
                "Temps restant : {:02d}:{:02d}:{:02d}".format(
                    heures,
                    minutes,
                    secondes
                )
            )


    time.sleep_ms(10)
    