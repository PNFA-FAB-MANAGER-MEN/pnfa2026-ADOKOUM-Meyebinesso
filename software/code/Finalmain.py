from machine import Pin, time_pulse_us
import neopixel
import time


# ============================================================
#                    CONFIGURATION
# ============================================================

# -------------------------
# LEDs HEURES
# GPIO4 - 14 LEDs
# -------------------------

PIN_HEURE = 4
NB_HEURE = 14

led_heure = neopixel.NeoPixel(
    Pin(PIN_HEURE, Pin.OUT),
    NB_HEURE
)


# -------------------------
# LEDs MINUTES
# GPIO2 - 14 LEDs
# -------------------------

PIN_MINUTE = 2
NB_MINUTE = 14

led_minute = neopixel.NeoPixel(
    Pin(PIN_MINUTE, Pin.OUT),
    NB_MINUTE
)


# -------------------------
# DOUBLE POINT
# GPIO3 - 2 LEDs
# -------------------------

PIN_POINTS = 3
NB_POINTS = 2

led_points = neopixel.NeoPixel(
    Pin(PIN_POINTS, Pin.OUT),
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


# ============================================================
#                 CODES TELECOMMANDE IR
# ============================================================

IR_PLUS  = 0xB946FF00
IR_MINUS = 0xEA15FF00

IR_START = 0xBA45FF00
IR_PAUSE = 0xBF40FF00
IR_RESET = 0xB847FF00

IR_SEL   = 0xE619FF00
IR_LEFT  = 0xBB44FF00
IR_RIGHT = 0xBC43FF00

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


CODES_CHIFFRES = {
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
#                       COULEURS
# ============================================================

# Programmation
COULEUR_PROGRAMMATION = (30, 30, 30)

# 0 à 74 %
COULEUR_VERTE = (0, 255, 0)

# 75 à 94 %
COULEUR_ORANGE = (255, 80, 0)

# 95 à 100 %
COULEUR_ROUGE = (255, 0, 0)

ETEINT = (0, 0, 0)


# ============================================================
#                 TABLE DES SEGMENTS
# ============================================================

# Chaque bandeau possède 14 LEDs :
#
# Digit 1 :
# LED 0 à 6
#
# Digit 2 :
# LED 7 à 13
#
# Ordre :
# A B C D E F G

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
#                   VARIABLES DU MINUTEUR
# ============================================================

heures = 0
minutes = 0
secondes = 0

en_marche = False

etat_points = False


# ------------------------------------------------------------
# Digit sélectionné
#
# 0 = dizaine heures
# 1 = unité heures
# 2 = dizaine minutes
# 3 = unité minutes
# ------------------------------------------------------------

digit_selectionne = 0

selection_visible = True

dernier_clignotement = time.ticks_ms()


# ------------------------------------------------------------
# Gestion du temps
# ------------------------------------------------------------

dernier_decompte = time.ticks_ms()


# ============================================================
#                VARIABLES DES ALERTES
# ============================================================

temps_total_programme = 0

alerte_50 = False
alerte_75 = False
alerte_95 = False


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
#                ETEINDRE UN DIGIT
# ============================================================

def eteindre_digit(bandeau, position):

    if position == 0:

        debut = 0

    else:

        debut = 7

    for i in range(7):

        bandeau[debut + i] = ETEINT


# ============================================================
#                 COULEUR DU MINUTEUR
# ============================================================

def obtenir_couleur():

    global temps_total_programme

    if temps_total_programme <= 0:

        return COULEUR_VERTE


    temps_restant = (
        heures * 3600
        + minutes * 60
        + secondes
    )


    temps_ecoule = (
        temps_total_programme
        - temps_restant
    )


    pourcentage = (
        temps_ecoule * 100
        / temps_total_programme
    )


    if pourcentage >= 95:

        return COULEUR_ROUGE

    elif pourcentage >= 75:

        return COULEUR_ORANGE

    else:

        return COULEUR_VERTE


# ============================================================
#                    AFFICHAGE COMPLET
# ============================================================

def afficher_temps():

    global selection_visible


    # --------------------------------------------------------
    # Séparation des digits
    # --------------------------------------------------------

    h_dizaine = heures // 10
    h_unite = heures % 10

    m_dizaine = minutes // 10
    m_unite = minutes % 10


    # --------------------------------------------------------
    # Choix de la couleur
    # --------------------------------------------------------

    if en_marche:

        couleur = obtenir_couleur()

    else:

        couleur = COULEUR_PROGRAMMATION


    # --------------------------------------------------------
    # AFFICHAGE DES HEURES
    # --------------------------------------------------------

    afficher_chiffre(
        led_heure,
        h_dizaine,
        0,
        couleur
    )

    afficher_chiffre(
        led_heure,
        h_unite,
        1,
        couleur
    )


    # --------------------------------------------------------
    # AFFICHAGE DES MINUTES
    # --------------------------------------------------------

    afficher_chiffre(
        led_minute,
        m_dizaine,
        0,
        couleur
    )

    afficher_chiffre(
        led_minute,
        m_unite,
        1,
        couleur
    )


    # --------------------------------------------------------
    # CLIGNOTEMENT DU DIGIT SELECTIONNE
    # --------------------------------------------------------

    if not en_marche and not selection_visible:

        if digit_selectionne == 0:

            eteindre_digit(
                led_heure,
                0
            )


        elif digit_selectionne == 1:

            eteindre_digit(
                led_heure,
                1
            )


        elif digit_selectionne == 2:

            eteindre_digit(
                led_minute,
                0
            )


        elif digit_selectionne == 3:

            eteindre_digit(
                led_minute,
                1
            )


    # --------------------------------------------------------
    # DOUBLE POINT
    # --------------------------------------------------------

    if en_marche:

        if etat_points:

            led_points[0] = couleur
            led_points[1] = couleur

        else:

            led_points[0] = ETEINT
            led_points[1] = ETEINT

    else:

        led_points[0] = COULEUR_PROGRAMMATION
        led_points[1] = COULEUR_PROGRAMMATION


    # --------------------------------------------------------
    # ENVOI AUX BANDEAUX
    # --------------------------------------------------------

    led_heure.write()

    led_minute.write()

    led_points.write()


# ============================================================
#                     POINTS ON
# ============================================================

def points_on():

    couleur = obtenir_couleur()

    led_points[0] = couleur
    led_points[1] = couleur

    led_points.write()


# ============================================================
#                     POINTS OFF
# ============================================================

def points_off():

    led_points[0] = ETEINT
    led_points[1] = ETEINT

    led_points.write()


# ============================================================
#             MODIFIER LE DIGIT AVEC UN CHIFFRE
# ============================================================

def modifier_digit(valeur):

    global heures
    global minutes


    # --------------------------------------------------------
    # Aucune modification pendant le décompte
    # --------------------------------------------------------

    if en_marche:

        return


    # ========================================================
    # DIGIT 0 : DIZAINE DES HEURES
    # ========================================================

    if digit_selectionne == 0:

        heures = (
            valeur * 10
            + heures % 10
        )


    # ========================================================
    # DIGIT 1 : UNITE DES HEURES
    # ========================================================

    elif digit_selectionne == 1:

        heures = (
            (heures // 10) * 10
            + valeur
        )


    # ========================================================
    # DIGIT 2 : DIZAINE DES MINUTES
    # ========================================================

    elif digit_selectionne == 2:

        # Les dizaines des minutes vont seulement
        # de 0 à 5.

        if valeur > 5:

            return

        minutes = (
            valeur * 10
            + minutes % 10
        )


    # ========================================================
    # DIGIT 3 : UNITE DES MINUTES
    # ========================================================

    elif digit_selectionne == 3:

        minutes = (
            (minutes // 10) * 10
            + valeur
        )


    afficher_temps()


# ============================================================
#                       TOUCHE +
# ============================================================

def augmenter_digit():

    global heures
    global minutes


    if en_marche:

        return


    # --------------------------------------------------------
    # DIZAINE HEURES
    # --------------------------------------------------------

    if digit_selectionne == 0:

        valeur = heures // 10

        valeur += 1

        if valeur > 9:

            valeur = 0

        heures = (
            valeur * 10
            + heures % 10
        )


    # --------------------------------------------------------
    # UNITE HEURES
    # --------------------------------------------------------

    elif digit_selectionne == 1:

        valeur = heures % 10

        valeur += 1

        if valeur > 9:

            valeur = 0

        heures = (
            (heures // 10) * 10
            + valeur
        )


    # --------------------------------------------------------
    # DIZAINE MINUTES
    # --------------------------------------------------------

    elif digit_selectionne == 2:

        valeur = minutes // 10

        valeur += 1

        if valeur > 5:

            valeur = 0

        minutes = (
            valeur * 10
            + minutes % 10
        )


    # --------------------------------------------------------
    # UNITE MINUTES
    # --------------------------------------------------------

    elif digit_selectionne == 3:

        valeur = minutes % 10

        valeur += 1

        if valeur > 9:

            valeur = 0

        minutes = (
            (minutes // 10) * 10
            + valeur
        )


    afficher_temps()


# ============================================================
#                       TOUCHE -
# ============================================================

def diminuer_digit():

    global heures
    global minutes


    if en_marche:

        return


    # --------------------------------------------------------
    # DIZAINE HEURES
    # --------------------------------------------------------

    if digit_selectionne == 0:

        valeur = heures // 10

        valeur -= 1

        if valeur < 0:

            valeur = 9

        heures = (
            valeur * 10
            + heures % 10
        )


    # --------------------------------------------------------
    # UNITE HEURES
    # --------------------------------------------------------

    elif digit_selectionne == 1:

        valeur = heures % 10

        valeur -= 1

        if valeur < 0:

            valeur = 9

        heures = (
            (heures // 10) * 10
            + valeur
        )


    # --------------------------------------------------------
    # DIZAINE MINUTES
    # --------------------------------------------------------

    elif digit_selectionne == 2:

        valeur = minutes // 10

        valeur -= 1

        if valeur < 0:

            valeur = 5

        minutes = (
            valeur * 10
            + minutes % 10
        )


    # --------------------------------------------------------
    # UNITE MINUTES
    # --------------------------------------------------------

    elif digit_selectionne == 3:

        valeur = minutes % 10

        valeur -= 1

        if valeur < 0:

            valeur = 9

        minutes = (
            (minutes // 10) * 10
            + valeur
        )


    afficher_temps()


# ============================================================
#                       TOUCHE SEL
# ============================================================

def selection_suivante():

    global digit_selectionne
    global selection_visible


    if en_marche:

        return


    digit_selectionne += 1


    if digit_selectionne > 3:

        digit_selectionne = 0


    selection_visible = True

    afficher_temps()


    print(
        "Digit sélectionné :",
        digit_selectionne
    )


# ============================================================
#                       TOUCHE LEFT
# ============================================================

def aller_gauche():

    global digit_selectionne
    global selection_visible


    if en_marche:

        return


    digit_selectionne -= 1


    if digit_selectionne < 0:

        digit_selectionne = 3


    selection_visible = True

    afficher_temps()


    print(
        "Digit sélectionné :",
        digit_selectionne
    )


# ============================================================
#                       TOUCHE RIGHT
# ============================================================

def aller_droite():

    global digit_selectionne
    global selection_visible


    if en_marche:

        return


    digit_selectionne += 1


    if digit_selectionne > 3:

        digit_selectionne = 0


    selection_visible = True

    afficher_temps()


    print(
        "Digit sélectionné :",
        digit_selectionne
    )


# ============================================================
#                        BUZZER
# ============================================================

# ------------------------------------------------------------
# 1 BIP COURT
# ------------------------------------------------------------

def bip_unique():

    buzzer.value(1)

    time.sleep_ms(250)

    buzzer.value(0)


# ------------------------------------------------------------
# 2 BIPS COURTS
# ------------------------------------------------------------

def double_bip():

    buzzer.value(1)

    time.sleep_ms(250)

    buzzer.value(0)

    time.sleep_ms(150)

    buzzer.value(1)

    time.sleep_ms(250)

    buzzer.value(0)


# ------------------------------------------------------------
# 3 BIPS TRES COURTS
# ------------------------------------------------------------

def triple_bip():

    for i in range(3):

        buzzer.value(1)

        time.sleep_ms(120)

        buzzer.value(0)

        time.sleep_ms(100)


# ------------------------------------------------------------
# BUZZER DE FIN : 10 SECONDES
# ------------------------------------------------------------

def buzzer_fin_10s():

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
#                VERIFICATION DES ALERTES
# ============================================================

def verifier_alertes():

    global alerte_50
    global alerte_75
    global alerte_95


    if temps_total_programme <= 0:

        return


    temps_restant = (
        heures * 3600
        + minutes * 60
        + secondes
    )


    temps_ecoule = (
        temps_total_programme
        - temps_restant
    )


    pourcentage = (
        temps_ecoule * 100
        / temps_total_programme
    )


    # ========================================================
    # 50 %
    # ========================================================

    if not alerte_50:

        if pourcentage >= 50:

            alerte_50 = True

            print(">>> 50 % : 1 BIP")

            bip_unique()


    # ========================================================
    # 75 %
    # ========================================================

    if not alerte_75:

        if pourcentage >= 75:

            alerte_75 = True

            print(">>> 75 % : 2 BIPS")

            double_bip()


    # ========================================================
    # 95 %
    # ========================================================

    if not alerte_95:

        if pourcentage >= 95:

            alerte_95 = True

            print(">>> 95 % : 3 BIPS")

            triple_bip()


# ============================================================
#                  DECREMENTER 1 SECONDE
# ============================================================

def decrementer_temps():

    global heures
    global minutes
    global secondes

    global etat_points


    # --------------------------------------------------------
    # Décrémentation des secondes
    # --------------------------------------------------------

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

                return True


    # --------------------------------------------------------
    # Clignotement du double point
    # --------------------------------------------------------

    etat_points = not etat_points


    # --------------------------------------------------------
    # Affichage
    # --------------------------------------------------------

    afficher_temps()


    # --------------------------------------------------------
    # Vérification de la fin
    # --------------------------------------------------------

    if (
        heures == 0
        and minutes == 0
        and secondes == 0
    ):

        return True


    return False


# ============================================================
#                   LECTURE IR NEC
# ============================================================
#
# IMPORTANT :
# Cette partie reprend la logique du programme précédent.
# Les bits sont reconstruits avec :
#
# code |= (bit << i)
#
# Cela permet de conserver la correspondance avec les codes
# IR de ta télécommande.
#
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
    # Impulsion HIGH de 4,5 ms
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

        # LOW environ 560 us

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


        # ----------------------------------------------------
        # Bit 0
        # ----------------------------------------------------

        if 300 < t < 900:

            bit = 0


        # ----------------------------------------------------
        # Bit 1
        # ----------------------------------------------------

        elif 1200 < t < 2100:

            bit = 1


        else:

            return None


        # ----------------------------------------------------
        # Reconstruction NEC
        # ----------------------------------------------------

        code |= (bit << i)


    return code


# ============================================================
#                  TRAITEMENT DES COMMANDES
# ============================================================

def traiter_commande(code):

    global en_marche

    global heures
    global minutes
    global secondes

    global temps_total_programme

    global alerte_50
    global alerte_75
    global alerte_95

    global dernier_decompte

    global selection_visible


    # ========================================================
    # START
    # ========================================================

    if code == IR_START:

        if not en_marche:

            temps = (
                heures * 3600
                + minutes * 60
                + secondes
            )


            if temps > 0:

                temps_total_programme = temps

                en_marche = True

                alerte_50 = False
                alerte_75 = False
                alerte_95 = False

                dernier_decompte = time.ticks_ms()

                print()
                print("================================")
                print("           START")
                print("Temps total : {:02d}:{:02d}:{:02d}".format(
                    heures,
                    minutes,
                    secondes
                ))
                print("================================")
                print()


                # Double point allumé au départ

                etat_points = True

                afficher_temps()


    # ========================================================
    # PAUSE
    # ========================================================

    elif code == IR_PAUSE:

        if en_marche:

            en_marche = False

            points_off()

            afficher_temps()

            print(">>> PAUSE")


    # ========================================================
    # RESET
    # ========================================================

    elif code == IR_RESET:

        en_marche = False

        heures = 0
        minutes = 0
        secondes = 0

        temps_total_programme = 0

        alerte_50 = False
        alerte_75 = False
        alerte_95 = False

        selection_visible = True

        buzzer.value(0)

        points_off()

        afficher_temps()

        print(">>> RESET")


    # ========================================================
    # SEL
    # ========================================================

    elif code == IR_SEL:

        selection_suivante()


    # ========================================================
    # LEFT
    # ========================================================

    elif code == IR_LEFT:

        aller_gauche()


    # ========================================================
    # RIGHT
    # ========================================================

    elif code == IR_RIGHT:

        aller_droite()


    # ========================================================
    # PLUS
    # ========================================================

    elif code == IR_PLUS:

        augmenter_digit()


    # ========================================================
    # MOINS
    # ========================================================

    elif code == IR_MINUS:

        diminuer_digit()


    # ========================================================
    # CHIFFRES
    # ========================================================

    elif code in CODES_CHIFFRES:

        chiffre = CODES_CHIFFRES[code]

        modifier_digit(chiffre)


# ============================================================
#                     INITIALISATION
# ============================================================

afficher_temps()

points_off()

buzzer.value(0)


print()
print("==============================================")
print("       MINUTEUR GEANT - XIAO ESP32-S3")
print("==============================================")
print()
print("GPIO4 : HEURES")
print("GPIO2 : MINUTES")
print("GPIO3 : DOUBLE POINT")
print("GPIO5 : RECEPTEUR IR")
print("GPIO7 : BUZZER")
print()
print("DIGITS :")
print("0 = dizaine heures")
print("1 = unite heures")
print("2 = dizaine minutes")
print("3 = unite minutes")
print()
print("TELECOMMANDE :")
print("SEL   =", hex(IR_SEL))
print("LEFT  =", hex(IR_LEFT))
print("RIGHT =", hex(IR_RIGHT))
print("PLUS  =", hex(IR_PLUS))
print("MINUS =", hex(IR_MINUS))
print("START =", hex(IR_START))
print("PAUSE =", hex(IR_PAUSE))
print("RESET =", hex(IR_RESET))
print()
print("Systeme pret.")
print()


# ============================================================
#                  BOUCLE PRINCIPALE
# ============================================================

while True:


    # ========================================================
    # 1. LECTURE DE LA TELECOMMANDE
    # ========================================================

    code = lire_ir()


    if code is not None:

        print(
            "IR recu :",
            hex(code)
        )


        traiter_commande(code)


        # Petit délai pour éviter une répétition immédiate

        time.sleep_ms(150)


    # ========================================================
    # 2. CLIGNOTEMENT DU DIGIT SELECTIONNE
    # ========================================================

    if not en_marche:

        maintenant = time.ticks_ms()


        if time.ticks_diff(
            maintenant,
            dernier_clignotement
        ) >= 500:

            dernier_clignotement = maintenant

            selection_visible = not selection_visible

            afficher_temps()


    # ========================================================
    # 3. DECOMPTE
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
            # Décrémentation
            # ------------------------------------------------

            termine = decrementer_temps()


            # ------------------------------------------------
            # Vérification des alertes
            # ------------------------------------------------

            if not termine:

                verifier_alertes()


            # ------------------------------------------------
            # FIN
            # ------------------------------------------------

            else:

                en_marche = False

                points_off()


                # Affichage 00:00 en ROUGE

                afficher_chiffre(
                    led_heure,
                    0,
                    0,
                    COULEUR_ROUGE
                )

                afficher_chiffre(
                    led_heure,
                    0,
                    1,
                    COULEUR_ROUGE
                )

                afficher_chiffre(
                    led_minute,
                    0,
                    0,
                    COULEUR_ROUGE
                )

                afficher_chiffre(
                    led_minute,
                    0,
                    1,
                    COULEUR_ROUGE
                )


                led_heure.write()
                led_minute.write()


                print()
                print("================================")
                print("         FIN DE L'EPREUVE")
                print("================================")
                print()


                # ------------------------------------------------
                # BUZZER PENDANT 10 SECONDES
                # ------------------------------------------------

                buzzer_fin_10s()

                buzzer.value(0)


    # ========================================================
    # 4. PETITE PAUSE
    # ========================================================

    time.sleep_ms(10)