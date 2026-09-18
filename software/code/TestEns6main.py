from machine import Pin, time_pulse_us
import neopixel
import time


# ============================================================
#                 CONFIGURATION DES BROCHES
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
#                    INITIALISATION
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
buzzer.value(0)


# ============================================================
#                       COULEURS
# ============================================================

COULEUR_HEURE = (30, 30, 30)
COULEUR_MINUTE = (30, 30, 30)
COULEUR_POINTS = (30, 30, 30)

ETEINT = (0, 0, 0)


# ============================================================
#                    CODES TELECOMMANDE IR
# ============================================================

IR_PLUS = 0xB946FF00
IR_MINUS = 0xEA15FF00

IR_START = 0xBA45FF00
IR_PAUSE = 0xBF40FF00
IR_RESET = 0xB847FF00

IR_SEL = 0xE619FF00
IR_LEFT = 0xBB44FF00
IR_RIGHT = 0xBC43FF00


# ============================================================
#                     PAVE NUMERIQUE
# ============================================================

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
#                       SEGMENTS
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
#                    VARIABLES DU MINUTEUR
# ============================================================

heures = 0
minutes = 0
secondes = 0

en_marche = False


# ============================================================
#                    GESTION DE LA SELECTION
# ============================================================

# 0 = dizaine des heures
# 1 = unité des heures
# 2 = dizaine des minutes
# 3 = unité des minutes

digit_selectionne = 0


# Etat du clignotement du digit sélectionné
etat_clignotement_digit = True

dernier_clignotement_digit = time.ticks_ms()


# ============================================================
#                    DOUBLE POINT
# ============================================================

etat_points = False

dernier_decompte = time.ticks_ms()


# ============================================================
#                    ALERTES SONORES
# ============================================================

temps_total_programme = 0

alerte_50 = False
alerte_75 = False


# ============================================================
#                  AFFICHER UN CHIFFRE
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
#                  AFFICHER HH:MM
# ============================================================

def afficher_temps():

    # --------------------------------------------------------
    # Les quatre digits
    # --------------------------------------------------------

    digits = [
        heures // 10,
        heures % 10,
        minutes // 10,
        minutes % 10
    ]


    # ========================================================
    #                 DIGITS DES HEURES
    # ========================================================

    for i in range(2):

        numero_digit = i

        # Digit sélectionné + phase OFF du clignotement
        if (
            numero_digit == digit_selectionne
            and not en_marche
            and not etat_clignotement_digit
        ):

            afficher_chiffre(
                bandeau_heure,
                digits[numero_digit],
                i,
                ETEINT
            )

        else:

            afficher_chiffre(
                bandeau_heure,
                digits[numero_digit],
                i,
                COULEUR_HEURE
            )


    bandeau_heure.write()


    # ========================================================
    #                 DIGITS DES MINUTES
    # ========================================================

    for i in range(2):

        numero_digit = i + 2

        # Digit sélectionné + phase OFF
        if (
            numero_digit == digit_selectionne
            and not en_marche
            and not etat_clignotement_digit
        ):

            afficher_chiffre(
                bandeau_minute,
                digits[numero_digit],
                i,
                ETEINT
            )

        else:

            afficher_chiffre(
                bandeau_minute,
                digits[numero_digit],
                i,
                COULEUR_MINUTE
            )


    bandeau_minute.write()


# ============================================================
#                  AFFICHER DOUBLE POINT
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
#                   +1 MINUTE
# ============================================================

def ajouter_minute():

    global heures
    global minutes

    total = heures * 60 + minutes

    total += 1

    # Maximum = 99:59
    if total > 99 * 60 + 59:

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
#                   -1 MINUTE
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
#             MODIFIER UNIQUEMENT LE DIGIT SELECTIONNE
# ============================================================

def modifier_digit(valeur):

    global heures
    global minutes

    # --------------------------------------------------------
    # Récupérer les valeurs actuelles
    # --------------------------------------------------------

    d0 = heures // 10
    d1 = heures % 10

    d2 = minutes // 10
    d3 = minutes % 10


    # ========================================================
    # DIGIT 0
    # DIZAINE DES HEURES
    # ========================================================

    if digit_selectionne == 0:

        # Seul d0 change
        d0 = valeur

        heures = d0 * 10 + d1


    # ========================================================
    # DIGIT 1
    # UNITE DES HEURES
    # ========================================================

    elif digit_selectionne == 1:

        # Seul d1 change
        d1 = valeur

        heures = d0 * 10 + d1


    # ========================================================
    # DIGIT 2
    # DIZAINE DES MINUTES
    # ========================================================

    elif digit_selectionne == 2:

        # Les dizaines de minutes sont limitées à 0-5
        if valeur > 5:

            print(
                "Valeur interdite : "
                "la dizaine des minutes doit être entre 0 et 5."
            )

            return

        # Seul d2 change
        d2 = valeur

        minutes = d2 * 10 + d3


    # ========================================================
    # DIGIT 3
    # UNITE DES MINUTES
    # ========================================================

    elif digit_selectionne == 3:

        # Seul d3 change
        d3 = valeur

        minutes = d2 * 10 + d3


    # --------------------------------------------------------
    # Affichage
    # --------------------------------------------------------

    afficher_temps()

    print(
        "Digit sélectionné : {} | Valeur entrée : {}".format(
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
#                    SEL
# ============================================================

def selectionner_digit():

    global digit_selectionne
    global etat_clignotement_digit

    digit_selectionne += 1

    if digit_selectionne > 3:

        digit_selectionne = 0

    # Quand on change de digit,
    # on le laisse immédiatement visible
    etat_clignotement_digit = True

    afficher_temps()

    print(
        "Digit sélectionné :",
        digit_selectionne
    )


# ============================================================
#                    LEFT
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
#                    RIGHT
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
#                       1 BIP
# ============================================================

def bip_une_fois():

    print(">>> ALERTE 50 % : 1 BIP")

    buzzer.value(1)

    time.sleep_ms(300)

    buzzer.value(0)


# ============================================================
#                       2 BIPS
# ============================================================

def bip_deux_fois():

    print(">>> ALERTE 75 % : 2 BIPS")

    for i in range(2):

        buzzer.value(1)

        time.sleep_ms(300)

        buzzer.value(0)

        time.sleep_ms(300)


# ============================================================
#                  BUZZER FINAL 10 SECONDES
# ============================================================

def bip_fin():

    print(">>> FIN : BUZZER PENDANT 10 SECONDES")

    debut = time.ticks_ms()

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
#                    DECODAGE IR NEC
# ============================================================

def lire_ir():

    try:

        # ----------------------------------------------------
        # Début du signal NEC
        # ----------------------------------------------------

        duree = time_pulse_us(
            ir,
            0,
            150000
        )

        if duree < 8000 or duree > 10000:

            return None


        # ----------------------------------------------------
        # 4,5 ms HIGH
        # ----------------------------------------------------

        duree = time_pulse_us(
            ir,
            1,
            10000
        )

        if duree < 4000 or duree > 5000:

            return None


        # ----------------------------------------------------
        # Lecture des 32 bits
        # ----------------------------------------------------

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


            # HIGH
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
#                    INITIALISATION
# ============================================================

afficher_temps()

afficher_points(False)

buzzer.value(0)


print("")
print("==========================================")
print("          MINUTEUR GEANT ESP32-S3")
print("==========================================")
print("Format : HH:MM")
print("")
print("DIGIT 0 = dizaine des heures")
print("DIGIT 1 = unité des heures")
print("DIGIT 2 = dizaine des minutes")
print("DIGIT 3 = unité des minutes")
print("")
print("SEL   = sélectionner")
print("LEFT  = gauche")
print("RIGHT = droite")
print("0-9   = modifier le digit sélectionné")
print("==========================================")
print("")


# ============================================================
#                    BOUCLE PRINCIPALE
# ============================================================

while True:


    # ========================================================
    #          CLIGNOTEMENT DU DIGIT SELECTIONNE
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
    #                    LECTURE IR
    # ========================================================

    code = lire_ir()


    if code is not None:

        print("Code IR :", hex(code))


        # ====================================================
        #                      PLUS
        # ====================================================

        if code == IR_PLUS:

            if not en_marche:

                ajouter_minute()


        # ====================================================
        #                      MOINS
        # ====================================================

        elif code == IR_MINUS:

            if not en_marche:

                retirer_minute()


        # ====================================================
        #                      START
        # ====================================================

        elif code == IR_START:

            if (
                heures > 0
                or minutes > 0
                or secondes > 0
            ):

                # --------------------------------------------
                # Mémoriser le temps total
                # --------------------------------------------

                temps_total_programme = (
                    heures * 3600
                    + minutes * 60
                    + secondes
                )

                # --------------------------------------------
                # Réinitialiser les alertes
                # --------------------------------------------

                alerte_50 = False
                alerte_75 = False

                # --------------------------------------------
                # Lancer
                # --------------------------------------------

                en_marche = True

                dernier_decompte = time.ticks_ms()

                afficher_points(True)

                print("")
                print("================================")
                print("       DECOMPTE DEMARRE")
                print("================================")
                print(
                    "Temps programme : {:02d}:{:02d}".format(
                        heures,
                        minutes
                    )
                )
                print(
                    "Total secondes :",
                    temps_total_programme
                )
                print("")


        # ====================================================
        #                      PAUSE
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
        #                      RESET
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
        #                       SEL
        # ====================================================

        elif code == IR_SEL:

            if not en_marche:

                selectionner_digit()


        # ====================================================
        #                      LEFT
        # ====================================================

        elif code == IR_LEFT:

            if not en_marche:

                aller_gauche()


        # ====================================================
        #                      RIGHT
        # ====================================================

        elif code == IR_RIGHT:

            if not en_marche:

                aller_droite()


        # ====================================================
        #                  PAVE NUMERIQUE
        # ====================================================

        elif code in CODES_NUMERIQUES:

            if not en_marche:

                valeur = CODES_NUMERIQUES[code]

                modifier_digit(valeur)


    # ========================================================
    #                     DECOMPTE
    # ========================================================

    if en_marche:

        maintenant = time.ticks_ms()

        if time.ticks_diff(
            maintenant,
            dernier_decompte
        ) >= 1000:

            dernier_decompte = maintenant


            # =================================================
            # DOUBLE POINT
            # =================================================

            etat_points = not etat_points

            afficher_points(etat_points)


            # =================================================
            # TEMPS RESTANT AVANT DECREMENTATION
            # =================================================

            temps_restant = (
                heures * 3600
                + minutes * 60
                + secondes
            )


            # =================================================
            # ALERTE 50 %
            # =================================================

            if (
                not alerte_50
                and temps_total_programme > 0
                and temps_restant
                <= temps_total_programme / 2
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
                <= temps_total_programme / 4
            ):

                alerte_75 = True

                bip_deux_fois()


            # =================================================
            # DECREMENTATION DES SECONDES
            # =================================================

            if secondes > 0:

                secondes -= 1


            else:

                secondes = 59


                # ------------------------------------------------
                # Décrémentation des minutes
                # ------------------------------------------------

                if minutes > 0:

                    minutes -= 1


                else:

                    # ------------------------------------------------
                    # Décrémentation des heures
                    # ------------------------------------------------

                    if heures > 0:

                        heures -= 1

                        minutes = 59


                    else:

                        # ============================================
                        #              FIN DU DECOMPTE
                        # ============================================

                        heures = 0
                        minutes = 0
                        secondes = 0

                        en_marche = False

                        afficher_temps()

                        afficher_points(False)

                        print("")
                        print("================================")
                        print("       FIN DU DECOMPTE")
                        print("            00:00")
                        print("================================")
                        print("")

                        # Buzzer pendant 10 secondes
                        bip_fin()

                        continue


            # =================================================
            # AFFICHAGE DU TEMPS RESTANT
            # =================================================

            afficher_temps()

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