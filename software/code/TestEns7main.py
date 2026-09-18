from machine import Pin, time_pulse_us
import neopixel
import time


# ============================================================
# CONFIGURATION DES LED
# ============================================================

# Bandeau HEURES : 14 LEDs = 2 digits
PIN_HEURES = 4
NB_LED_HEURES = 14

# Bandeau MINUTES : 14 LEDs = 2 digits
PIN_MINUTES = 2
NB_LED_MINUTES = 14

# Double point :
PIN_POINTS = 3
NB_LED_POINTS = 2

# Récepteur infrarouge
PIN_IR = 5

# Buzzer
PIN_BUZZER = 7


# ============================================================
# INITIALISATION
# ============================================================

bandeau_heures = neopixel.NeoPixel(
    Pin(PIN_HEURES), NB_LED_HEURES
)

bandeau_minutes = neopixel.NeoPixel(
    Pin(PIN_MINUTES), NB_LED_MINUTES
)

bandeau_points = neopixel.NeoPixel(
    Pin(PIN_POINTS), NB_LED_POINTS
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
# SEGMENTS DES DIGITS
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
# 0 = dizaine des heures
# 1 = unité des heures
# 2 = dizaine des minutes
# 3 = unité des minutes

digit_selectionne = 0

# Clignotement du digit sélectionné
digit_visible = True
dernier_clignotement = time.ticks_ms()

# Double point
points_allumes = False
dernier_points = time.ticks_ms()

# Décompte
dernier_decompte = time.ticks_ms()

# Temps total programmé au démarrage
temps_total_programme = 0

# Alertes
alerte_50 = False
alerte_75 = False
alerte_fin = False


# ============================================================
# AFFICHAGE D'UN DIGIT
# ============================================================

def afficher_chiffre(bandeau, chiffre, position, couleur):
    """
    position = 0 : premier digit
    position = 1 : deuxième digit
    """

    debut = position * 7

    segments = SEGMENTS[chiffre]

    for i in range(7):

        if segments[i]:
            bandeau[debut + i] = couleur
        else:
            bandeau[debut + i] = ETEINT


# ============================================================
# EFFACER LES BANDEAUX
# ============================================================

def eteindre_tout():

    for i in range(NB_LED_HEURES):
        bandeau_heures[i] = ETEINT

    for i in range(NB_LED_MINUTES):
        bandeau_minutes[i] = ETEINT

    for i in range(NB_LED_POINTS):
        bandeau_points[i] = ETEINT

    bandeau_heures.write()
    bandeau_minutes.write()
    bandeau_points.write()


# ============================================================
# AFFICHAGE DU TEMPS
# ============================================================

def afficher_temps():

    # --------------------------------------------------------
    # Les 4 digits
    # --------------------------------------------------------

    digit0 = heures // 10
    digit1 = heures % 10

    digit2 = minutes // 10
    digit3 = minutes % 10


    # --------------------------------------------------------
    # HEURES
    # --------------------------------------------------------

    if not (
        digit_selectionne == 0 and
        not digit_visible and
        not en_marche
    ):
        afficher_chiffre(
            bandeau_heures,
            digit0,
            0,
            COULEUR_HEURE
        )

    else:
        # Éteindre le digit sélectionné
        for i in range(7):
            bandeau_heures[i] = ETEINT


    if not (
        digit_selectionne == 1 and
        not digit_visible and
        not en_marche
    ):
        afficher_chiffre(
            bandeau_heures,
            digit1,
            1,
            COULEUR_HEURE
        )

    else:
        for i in range(7, 14):
            bandeau_heures[i] = ETEINT


    # --------------------------------------------------------
    # MINUTES
    # --------------------------------------------------------

    if not (
        digit_selectionne == 2 and
        not digit_visible and
        not en_marche
    ):
        afficher_chiffre(
            bandeau_minutes,
            digit2,
            0,
            COULEUR_MINUTE
        )

    else:
        for i in range(7):
            bandeau_minutes[i] = ETEINT


    if not (
        digit_selectionne == 3 and
        not digit_visible and
        not en_marche
    ):
        afficher_chiffre(
            bandeau_minutes,
            digit3,
            1,
            COULEUR_MINUTE
        )

    else:
        for i in range(7, 14):
            bandeau_minutes[i] = ETEINT


    # --------------------------------------------------------
    # Double point
    # --------------------------------------------------------

    if points_allumes:
        bandeau_points[0] = COULEUR_POINTS
        bandeau_points[1] = COULEUR_POINTS
    else:
        bandeau_points[0] = ETEINT
        bandeau_points[1] = ETEINT


    bandeau_heures.write()
    bandeau_minutes.write()
    bandeau_points.write()


# ============================================================
# MODIFIER UNIQUEMENT LE DIGIT SÉLECTIONNÉ
# ============================================================

def modifier_digit(valeur):

    global heures
    global minutes

    # Lire les quatre digits actuels

    digits = [
        heures // 10,      # digit 0
        heures % 10,       # digit 1
        minutes // 10,     # digit 2
        minutes % 10       # digit 3
    ]


    # ========================================================
    # DIGIT 0 : DIZAINE DES HEURES
    # ========================================================

    if digit_selectionne == 0:

        nouveau = digits[0] + valeur

        if nouveau < 0:
            nouveau = 9

        if nouveau > 9:
            nouveau = 0

        digits[0] = nouveau


    # ========================================================
    # DIGIT 1 : UNITÉ DES HEURES
    # ========================================================

    elif digit_selectionne == 1:

        nouveau = digits[1] + valeur

        if nouveau < 0:
            nouveau = 9

        if nouveau > 9:
            nouveau = 0

        digits[1] = nouveau


    # ========================================================
    # DIGIT 2 : DIZAINE DES MINUTES
    # ========================================================

    elif digit_selectionne == 2:

        nouveau = digits[2] + valeur

        if nouveau < 0:
            nouveau = 5

        if nouveau > 5:
            nouveau = 0

        digits[2] = nouveau


    # ========================================================
    # DIGIT 3 : UNITÉ DES MINUTES
    # ========================================================

    elif digit_selectionne == 3:

        nouveau = digits[3] + valeur

        if nouveau < 0:
            nouveau = 9

        if nouveau > 9:
            nouveau = 0

        digits[3] = nouveau


    # Reconstruire heures et minutes

    heures = digits[0] * 10 + digits[1]

    minutes = digits[2] * 10 + digits[3]


# ============================================================
# SÉLECTION DU DIGIT
# ============================================================

def selectionner_digit():

    global digit_selectionne
    global digit_visible
    global dernier_clignotement

    digit_selectionne += 1

    if digit_selectionne > 3:
        digit_selectionne = 0

    digit_visible = True
    dernier_clignotement = time.ticks_ms()

    afficher_temps()


# ============================================================
# DÉPLACEMENT À GAUCHE
# ============================================================

def aller_gauche():

    global digit_selectionne
    global digit_visible
    global dernier_clignotement

    digit_selectionne -= 1

    if digit_selectionne < 0:
        digit_selectionne = 3

    digit_visible = True
    dernier_clignotement = time.ticks_ms()

    afficher_temps()


# ============================================================
# DÉPLACEMENT À DROITE
# ============================================================

def aller_droite():

    global digit_selectionne
    global digit_visible
    global dernier_clignotement

    digit_selectionne += 1

    if digit_selectionne > 3:
        digit_selectionne = 0

    digit_visible = True
    dernier_clignotement = time.ticks_ms()

    afficher_temps()


# ============================================================
# BUZZER : UN BIP
# ============================================================

def bip():

    buzzer.value(1)
    time.sleep_ms(300)

    buzzer.value(0)
    time.sleep_ms(100)


# ============================================================
# BUZZER : DEUX BIPS
# ============================================================

def deux_bips():

    bip()
    bip()


# ============================================================
# BUZZER FIN : 10 SECONDES
# ============================================================

def buzzer_fin():

    debut = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), debut) < 10000:

        buzzer.value(1)
        time.sleep_ms(250)

        buzzer.value(0)
        time.sleep_ms(250)

    buzzer.value(0)


# ============================================================
# DÉCODAGE IR NEC
# ============================================================

def lire_ir():

    try:

        # Attendre le début du signal
        duree = time_pulse_us(ir, 0, 150000)

        if duree < 8000 or duree > 10000:
            return None


        # Impulsion suivante
        duree = time_pulse_us(ir, 1, 10000)

        if duree < 4000 or duree > 5500:
            return None


        valeur = 0


        # Lire les 32 bits

        for i in range(32):

            # Impulsion basse
            duree = time_pulse_us(ir, 0, 3000)

            if duree < 300 or duree > 800:
                return None


            # Impulsion haute
            duree = time_pulse_us(ir, 1, 3000)

            if duree < 300:
                return None


            if duree > 1000:
                valeur |= (1 << i)


        return valeur


    except:

        return None


# ============================================================
# CLIGNOTEMENT DU DIGIT SÉLECTIONNÉ
# ============================================================

def gerer_clignotement():

    global digit_visible
    global dernier_clignotement

    if en_marche:
        return

    maintenant = time.ticks_ms()

    if time.ticks_diff(
        maintenant,
        dernier_clignotement
    ) >= 500:

        digit_visible = not digit_visible

        dernier_clignotement = maintenant

        afficher_temps()


# ============================================================
# DÉCOMPTE
# ============================================================

def decrementer_temps():

    global heures
    global minutes
    global secondes
    global dernier_decompte
    global points_allumes

    maintenant = time.ticks_ms()

    if time.ticks_diff(
        maintenant,
        dernier_decompte
    ) < 1000:
        return False

    dernier_decompte = maintenant


    # --------------------------------------------------------
    # Si le temps est terminé
    # --------------------------------------------------------

    if heures == 0 and minutes == 0 and secondes == 0:
        return True


    # --------------------------------------------------------
    # Décrémenter les secondes
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Clignotement du double point
    # --------------------------------------------------------

    points_allumes = not points_allumes

    afficher_temps()

    return (
        heures == 0 and
        minutes == 0 and
        secondes == 0
    )


# ============================================================
# VARIABLES DES ALERTES
# ============================================================

alerte_50 = False
alerte_75 = False


# ============================================================
# VÉRIFICATION DES ALERTES
# ============================================================

def verifier_alertes():

    global alerte_50
    global alerte_75

    if temps_total_programme <= 0:
        return


    temps_restant = (
        heures * 3600 +
        minutes * 60 +
        secondes
    )


    # ========================================================
    # 50 % DU TEMPS ÉCOULÉ
    # ========================================================

    if (
        not alerte_50 and
        temps_restant <= temps_total_programme / 2
    ):

        alerte_50 = True

        bip()


    # ========================================================
    # 75 % DU TEMPS ÉCOULÉ
    # ========================================================

    if (
        not alerte_75 and
        temps_restant <= temps_total_programme / 4
    ):

        alerte_75 = True

        deux_bips()


# ============================================================
# RESET
# ============================================================

def reset_minuteur():

    global heures
    global minutes
    global secondes
    global en_marche
    global points_allumes
    global alerte_50
    global alerte_75
    global digit_visible
    global dernier_clignotement

    heures = 0
    minutes = 0
    secondes = 0

    en_marche = False

    points_allumes = False

    alerte_50 = False
    alerte_75 = False

    digit_visible = True
    dernier_clignotement = time.ticks_ms()

    afficher_temps()


# ============================================================
# DÉMARRER LE MINUTEUR
# ============================================================

def demarrer():

    global en_marche
    global temps_total_programme
    global dernier_decompte
    global alerte_50
    global alerte_75
    global points_allumes

    temps_total_programme = (
        heures * 3600 +
        minutes * 60 +
        secondes
    )

    if temps_total_programme <= 0:
        return


    en_marche = True

    alerte_50 = False
    alerte_75 = False

    points_allumes = True

    dernier_decompte = time.ticks_ms()

    afficher_temps()


# ============================================================
# PAUSE
# ============================================================

def pause():

    global en_marche
    global points_allumes

    en_marche = False

    points_allumes = False

    afficher_temps()


# ============================================================
# TRAITEMENT DES COMMANDES IR
# ============================================================

def traiter_commande(code):

    global dernier_decompte

    # ========================================================
    # PLUS
    # ========================================================

    if code == IR_PLUS:

        if not en_marche:

            # IMPORTANT :
            # + modifie UNIQUEMENT le digit sélectionné

            modifier_digit(+1)

            afficher_temps()


    # ========================================================
    # MOINS
    # ========================================================

    elif code == IR_MINUS:

        if not en_marche:

            # IMPORTANT :
            # - modifie UNIQUEMENT le digit sélectionné

            modifier_digit(-1)

            afficher_temps()


    # ========================================================
    # START
    # ========================================================

    elif code == IR_START:

        if not en_marche:

            demarrer()


    # ========================================================
    # PAUSE
    # ========================================================

    elif code == IR_PAUSE:

        pause()


    # ========================================================
    # RESET
    # ========================================================

    elif code == IR_RESET:

        reset_minuteur()


    # ========================================================
    # SELECT
    # ========================================================

    elif code == IR_SEL:

        if not en_marche:

            selectionner_digit()


    # ========================================================
    # GAUCHE
    # ========================================================

    elif code == IR_LEFT:

        if not en_marche:

            aller_gauche()


    # ========================================================
    # DROITE
    # ========================================================

    elif code == IR_RIGHT:

        if not en_marche:

            aller_droite()


    # ========================================================
    # PAVÉ NUMÉRIQUE
    # ========================================================

    elif code in CODES_NUMERIQUES:

        if not en_marche:

            chiffre = CODES_NUMERIQUES[code]

            # Le chiffre entré est appliqué
            # UNIQUEMENT au digit sélectionné

            modifier_digit(
                chiffre - (
                    [
                        heures // 10,
                        heures % 10,
                        minutes // 10,
                        minutes % 10
                    ][digit_selectionne]
                )
            )

            afficher_temps()


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

eteindre_tout()

afficher_temps()


while True:

    # ========================================================
    # LECTURE DE LA TÉLÉCOMMANDE
    # ========================================================

    code = lire_ir()

    if code is not None:

        traiter_commande(code)

        # Petite pause pour éviter les doubles commandes
        time.sleep_ms(150)


    # ========================================================
    # CLIGNOTEMENT DU DIGIT SÉLECTIONNÉ
    # ========================================================

    gerer_clignotement()


    # ========================================================
    # DÉCOMPTE
    # ========================================================

    if en_marche:

        termine = decrementer_temps()


        # Vérifier les alertes 50 % et 75 %
        verifier_alertes()


        # ====================================================
        # FIN DU MINUTEUR
        # ====================================================

        if termine:

            en_marche = False

            points_allumes = False

            afficher_temps()

            # Buzzer pendant 10 secondes
            buzzer_fin()

            # Retour à l'état normal
            afficher_temps()


    time.sleep_ms(10)