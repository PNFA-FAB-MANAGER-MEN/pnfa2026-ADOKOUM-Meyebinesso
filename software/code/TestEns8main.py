from machine import Pin, time_pulse_us
import neopixel
import time


# ============================================================
# CONFIGURATION DES LED
# ============================================================

PIN_HEURES = 4
NB_LED_HEURES = 14

PIN_MINUTES = 2
NB_LED_MINUTES = 14

PIN_POINTS = 3
NB_LED_POINTS = 2

PIN_IR = 5
PIN_BUZZER = 7


# ============================================================
# INITIALISATION
# ============================================================

bandeau_heures = neopixel.NeoPixel(
    Pin(PIN_HEURES),
    NB_LED_HEURES
)

bandeau_minutes = neopixel.NeoPixel(
    Pin(PIN_MINUTES),
    NB_LED_MINUTES
)

bandeau_points = neopixel.NeoPixel(
    Pin(PIN_POINTS),
    NB_LED_POINTS
)

ir = Pin(PIN_IR, Pin.IN)

buzzer = Pin(PIN_BUZZER, Pin.OUT)
buzzer.value(0)


# ============================================================
# COULEURS
# ============================================================

# Couleur pendant la programmation / sélection
COULEUR_PROGRAMMATION = (30, 30, 30)

# Couleur pendant le décompte
COULEUR_VERTE = (0, 255, 0)

# Couleur à partir de 75 % du temps écoulé
COULEUR_ORANGE = (255, 80, 0)

# Couleur à partir de 95 % du temps écoulé
COULEUR_ROUGE = (255, 0, 0)

# Éteint
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


# ============================================================
# PAVÉ NUMÉRIQUE
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
# SEGMENTS 7 SEGMENTS
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

# 0 = dizaine heures
# 1 = unité heures
# 2 = dizaine minutes
# 3 = unité minutes

digit_selectionne = 0

# Clignotement du digit sélectionné
digit_visible = True
dernier_clignotement = time.ticks_ms()

# Double point
points_allumes = False
dernier_points = time.ticks_ms()

# Décompte
dernier_decompte = time.ticks_ms()

# Temps total programmé
temps_total_programme = 0

# Alertes sonores
alerte_50 = False
alerte_75 = False


# ============================================================
# AFFICHER UN CHIFFRE
# ============================================================

def afficher_chiffre(bandeau, chiffre, position, couleur):

    debut = position * 7

    segments = SEGMENTS[chiffre]

    for i in range(7):

        if segments[i]:
            bandeau[debut + i] = couleur
        else:
            bandeau[debut + i] = ETEINT


# ============================================================
# EFFACER UN DIGIT
# ============================================================

def eteindre_digit(bandeau, position):

    debut = position * 7

    for i in range(7):
        bandeau[debut + i] = ETEINT


# ============================================================
# DÉTERMINER LA COULEUR DU DÉCOMPTE
# ============================================================

def couleur_du_decompte():

    if temps_total_programme <= 0:
        return COULEUR_VERTE

    temps_restant = (
        heures * 3600 +
        minutes * 60 +
        secondes
    )

    temps_ecoule = (
        temps_total_programme -
        temps_restant
    )

    pourcentage = (
        temps_ecoule * 100
    ) / temps_total_programme


    # --------------------------------------------------------
    # À partir de 95 % : ROUGE
    # --------------------------------------------------------

    if pourcentage >= 95:
        return COULEUR_ROUGE


    # --------------------------------------------------------
    # À partir de 75 % : ORANGE
    # --------------------------------------------------------

    elif pourcentage >= 75:
        return COULEUR_ORANGE


    # --------------------------------------------------------
    # Avant 75 % : VERT
    # --------------------------------------------------------

    else:
        return COULEUR_VERTE


# ============================================================
# AFFICHAGE DU TEMPS
# ============================================================

def afficher_temps():

    digit0 = heures // 10
    digit1 = heures % 10

    digit2 = minutes // 10
    digit3 = minutes % 10


    # ========================================================
    # COULEUR
    # ========================================================

    if en_marche:
        couleur = couleur_du_decompte()
    else:
        couleur = COULEUR_PROGRAMMATION


    # ========================================================
    # DIGIT 0
    # ========================================================

    if (
        not en_marche
        and digit_selectionne == 0
        and not digit_visible
    ):

        eteindre_digit(
            bandeau_heures,
            0
        )

    else:

        afficher_chiffre(
            bandeau_heures,
            digit0,
            0,
            couleur
        )


    # ========================================================
    # DIGIT 1
    # ========================================================

    if (
        not en_marche
        and digit_selectionne == 1
        and not digit_visible
    ):

        eteindre_digit(
            bandeau_heures,
            1
        )

    else:

        afficher_chiffre(
            bandeau_heures,
            digit1,
            1,
            couleur
        )


    # ========================================================
    # DIGIT 2
    # ========================================================

    if (
        not en_marche
        and digit_selectionne == 2
        and not digit_visible
    ):

        eteindre_digit(
            bandeau_minutes,
            0
        )

    else:

        afficher_chiffre(
            bandeau_minutes,
            digit2,
            0,
            couleur
        )


    # ========================================================
    # DIGIT 3
    # ========================================================

    if (
        not en_marche
        and digit_selectionne == 3
        and not digit_visible
    ):

        eteindre_digit(
            bandeau_minutes,
            1
        )

    else:

        afficher_chiffre(
            bandeau_minutes,
            digit3,
            1,
            couleur
        )


    # ========================================================
    # DOUBLE POINT
    # ========================================================

    if points_allumes:

        couleur_points = couleur

        bandeau_points[0] = couleur_points
        bandeau_points[1] = couleur_points

    else:

        bandeau_points[0] = ETEINT
        bandeau_points[1] = ETEINT


    # Écriture vers les bandeaux

    bandeau_heures.write()
    bandeau_minutes.write()
    bandeau_points.write()


# ============================================================
# MODIFIER UNIQUEMENT LE DIGIT SÉLECTIONNÉ
# ============================================================

def modifier_digit(valeur):

    global heures
    global minutes

    digits = [
        heures // 10,
        heures % 10,
        minutes // 10,
        minutes % 10
    ]


    # ========================================================
    # DIZAINE DES HEURES
    # ========================================================

    if digit_selectionne == 0:

        nouveau = digits[0] + valeur

        if nouveau < 0:
            nouveau = 9

        elif nouveau > 9:
            nouveau = 0

        digits[0] = nouveau


    # ========================================================
    # UNITÉ DES HEURES
    # ========================================================

    elif digit_selectionne == 1:

        nouveau = digits[1] + valeur

        if nouveau < 0:
            nouveau = 9

        elif nouveau > 9:
            nouveau = 0

        digits[1] = nouveau


    # ========================================================
    # DIZAINE DES MINUTES
    # ========================================================

    elif digit_selectionne == 2:

        nouveau = digits[2] + valeur

        if nouveau < 0:
            nouveau = 5

        elif nouveau > 5:
            nouveau = 0

        digits[2] = nouveau


    # ========================================================
    # UNITÉ DES MINUTES
    # ========================================================

    elif digit_selectionne == 3:

        nouveau = digits[3] + valeur

        if nouveau < 0:
            nouveau = 9

        elif nouveau > 9:
            nouveau = 0

        digits[3] = nouveau


    # Reconstruire le temps

    heures = digits[0] * 10 + digits[1]

    minutes = digits[2] * 10 + digits[3]


# ============================================================
# SÉLECTIONNER LE DIGIT SUIVANT
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
# ALLER À GAUCHE
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
# ALLER À DROITE
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
# UN BIP
# ============================================================

def bip():

    buzzer.value(1)
    time.sleep_ms(300)

    buzzer.value(0)
    time.sleep_ms(100)


# ============================================================
# DEUX BIPS
# ============================================================

def deux_bips():

    bip()
    bip()


# ============================================================
# BUZZER FINAL PENDANT 10 SECONDES
# ============================================================

def buzzer_fin():

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
# DÉCODAGE IR NEC
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

        if duree < 4000 or duree > 5500:
            return None


        valeur = 0


        for i in range(32):

            duree = time_pulse_us(
                ir,
                0,
                3000
            )

            if duree < 300 or duree > 800:
                return None


            duree = time_pulse_us(
                ir,
                1,
                3000
            )

            if duree < 300:
                return None


            if duree > 1000:
                valeur |= (1 << i)


        return valeur


    except:

        return None


# ============================================================
# CLIGNOTEMENT DU DIGIT
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
# DÉCOMPTER UNE SECONDE
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


    # ========================================================
    # DÉCOMPTE
    # ========================================================

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


    # ========================================================
    # DOUBLE POINT
    # ========================================================

    points_allumes = not points_allumes

    afficher_temps()


    # ========================================================
    # TEMPS TERMINÉ
    # ========================================================

    if (
        heures == 0 and
        minutes == 0 and
        secondes == 0
    ):

        return True


    return False


# ============================================================
# VÉRIFICATION DES ALERTES SONORES
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

    buzzer.value(0)

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
    global digit_visible

    temps_total_programme = (
        heures * 3600 +
        minutes * 60 +
        secondes
    )


    if temps_total_programme <= 0:
        return


    # Enregistrer le temps de départ

    en_marche = True

    alerte_50 = False
    alerte_75 = False

    points_allumes = True

    digit_visible = True

    dernier_decompte = time.ticks_ms()

    afficher_temps()


# ============================================================
# PAUSE
# ============================================================

def pause():

    global en_marche
    global points_allumes
    global digit_visible
    global dernier_clignotement

    en_marche = False

    points_allumes = False

    digit_visible = True

    dernier_clignotement = time.ticks_ms()

    afficher_temps()


# ============================================================
# TRAITER UNE COMMANDE IR
# ============================================================

def traiter_commande(code):

    # ========================================================
    # PLUS
    # ========================================================

    if code == IR_PLUS:

        if not en_marche:

            # +1 UNIQUEMENT SUR LE DIGIT SÉLECTIONNÉ

            modifier_digit(+1)

            digit_visible = True

            afficher_temps()


    # ========================================================
    # MOINS
    # ========================================================

    elif code == IR_MINUS:

        if not en_marche:

            # -1 UNIQUEMENT SUR LE DIGIT SÉLECTIONNÉ

            modifier_digit(-1)

            digit_visible = True

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


            digits = [
                heures // 10,
                heures % 10,
                minutes // 10,
                minutes % 10
            ]


            # Le pavé numérique remplace
            # uniquement le digit sélectionné

            modifier_digit(
                chiffre -
                digits[digit_selectionne]
            )


            digit_visible = True

            afficher_temps()


# ============================================================
# INITIALISATION
# ============================================================

eteindre_digit(bandeau_heures, 0)
eteindre_digit(bandeau_heures, 1)

eteindre_digit(bandeau_minutes, 0)
eteindre_digit(bandeau_minutes, 1)

bandeau_points[0] = ETEINT
bandeau_points[1] = ETEINT

bandeau_heures.write()
bandeau_minutes.write()
bandeau_points.write()

afficher_temps()


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

while True:

    # ========================================================
    # TÉLÉCOMMANDE IR
    # ========================================================

    code = lire_ir()

    if code is not None:

        traiter_commande(code)

        time.sleep_ms(150)


    # ========================================================
    # CLIGNOTEMENT DU DIGIT
    # ========================================================

    gerer_clignotement()


    # ========================================================
    # DÉCOMPTE
    # ========================================================

    if en_marche:

        termine = decrementer_temps()


        # Vérifier les alertes sonores

        if not termine:
            verifier_alertes()


        # ====================================================
        # FIN DU DÉCOMPTE
        # ====================================================

        if termine:

            en_marche = False

            points_allumes = False

            # Affichage rouge à 00:00
            afficher_temps()

            # Buzzer pendant 10 secondes
            buzzer_fin()

            # Après le buzzer, rester à 00:00 rouge
            afficher_temps()


    time.sleep_ms(10)