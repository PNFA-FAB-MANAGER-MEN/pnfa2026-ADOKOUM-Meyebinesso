from machine import Pin, time_pulse_us
import neopixel
import time


# ============================================================
# CONFIGURATION
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

# Pendant la programmation
COULEUR_PROGRAMMATION = (30, 30, 30)

# Pendant le décompte normal
COULEUR_VERTE = (0, 255, 0)

# À partir de 75 % du temps écoulé
COULEUR_ORANGE = (255, 80, 0)

# À partir de 95 % du temps écoulé
COULEUR_ROUGE = (255, 0, 0)

# LED éteinte
ETEINT = (0, 0, 0)


# ============================================================
# CODES TELECOMMANDE IR
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
# PAVE NUMERIQUE
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
# VARIABLES
# ============================================================

heures = 0
minutes = 0
secondes = 0

en_marche = False

# ------------------------------------------------------------
# Sélection du digit
#
# 0 = dizaine des heures
# 1 = unité des heures
# 2 = dizaine des minutes
# 3 = unité des minutes
# ------------------------------------------------------------

digit_selectionne = 0

# Clignotement
digit_visible = True
dernier_clignotement = time.ticks_ms()

# Double point
points_allumes = False

# Décompte
dernier_decompte = time.ticks_ms()

# Temps total programmé en secondes
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
# ETEINDRE UN DIGIT
# ============================================================

def eteindre_digit(bandeau, position):

    debut = position * 7

    for i in range(7):
        bandeau[debut + i] = ETEINT


# ============================================================
# ETEINDRE TOUT
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
# CALCUL DE LA COULEUR DU DECOMPTE
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


    # 95 % ou plus
    if pourcentage >= 95:

        return COULEUR_ROUGE


    # 75 % ou plus
    elif pourcentage >= 75:

        return COULEUR_ORANGE


    # Avant 75 %
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


    # --------------------------------------------------------
    # Choix de la couleur
    # --------------------------------------------------------

    if en_marche:

        couleur = couleur_du_decompte()

    else:

        couleur = COULEUR_PROGRAMMATION


    # ========================================================
    # DIGIT 0 : DIZAINE HEURES
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
    # DIGIT 1 : UNITE HEURES
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
    # DIGIT 2 : DIZAINE MINUTES
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
    # DIGIT 3 : UNITE MINUTES
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

        bandeau_points[0] = couleur
        bandeau_points[1] = couleur

    else:

        bandeau_points[0] = ETEINT
        bandeau_points[1] = ETEINT


    # ========================================================
    # ENVOI AUX LED
    # ========================================================

    bandeau_heures.write()
    bandeau_minutes.write()
    bandeau_points.write()


# ============================================================
# MODIFICATION DU DIGIT SELECTIONNE
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
    # DIGIT 0 : DIZAINE DES HEURES
    # ========================================================

    if digit_selectionne == 0:

        nouveau = digits[0] + valeur

        if nouveau < 0:
            nouveau = 9

        elif nouveau > 9:
            nouveau = 0

        digits[0] = nouveau


    # ========================================================
    # DIGIT 1 : UNITE DES HEURES
    # ========================================================

    elif digit_selectionne == 1:

        nouveau = digits[1] + valeur

        if nouveau < 0:
            nouveau = 9

        elif nouveau > 9:
            nouveau = 0

        digits[1] = nouveau


    # ========================================================
    # DIGIT 2 : DIZAINE DES MINUTES
    # ========================================================

    elif digit_selectionne == 2:

        nouveau = digits[2] + valeur

        if nouveau < 0:
            nouveau = 5

        elif nouveau > 5:
            nouveau = 0

        digits[2] = nouveau


    # ========================================================
    # DIGIT 3 : UNITE DES MINUTES
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
# SELECTION DU DIGIT
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
# DEPLACEMENT A GAUCHE
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
# DEPLACEMENT A DROITE
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
# BUZZER OFF
# ============================================================

def buzzer_off():

    buzzer.value(0)


# ============================================================
# UN SEUL BIP
# ============================================================

def bip_unique():

    buzzer.value(1)

    time.sleep_ms(300)

    buzzer.value(0)


# ============================================================
# DOUBLE BIP
# ============================================================

def double_bip():

    # Premier bip
    buzzer.value(1)
    time.sleep_ms(300)

    buzzer.value(0)
    time.sleep_ms(150)

    # Deuxième bip
    buzzer.value(1)
    time.sleep_ms(300)

    buzzer.value(0)


# ============================================================
# BUZZER FINAL : 10 SECONDES
# ============================================================

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
# VERIFICATION DES ALERTES
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


    temps_ecoule = (
        temps_total_programme -
        temps_restant
    )


    pourcentage = (
        temps_ecoule * 100
    ) / temps_total_programme


    # ========================================================
    # 50 %
    # UN SEUL BIP
    # ========================================================

    if (
        not alerte_50
        and pourcentage >= 50
    ):

        alerte_50 = True

        bip_unique()


    # ========================================================
    # 75 %
    # DEUX BIPS
    # ========================================================

    if (
        not alerte_75
        and pourcentage >= 75
    ):

        alerte_75 = True

        double_bip()


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

    buzzer_off()

    afficher_temps()


# ============================================================
# DEMARRER LE DECOMPTE
# ============================================================

def demarrer():

    global en_marche
    global temps_total_programme
    global dernier_decompte
    global alerte_50
    global alerte_75
    global points_allumes
    global digit_visible

    # Calcul du temps total programmé

    temps_total_programme = (
        heures * 3600 +
        minutes * 60 +
        secondes
    )


    # Ne pas démarrer à 00:00
    if temps_total_programme <= 0:
        return


    # Démarrage

    en_marche = True

    alerte_50 = False
    alerte_75 = False

    points_allumes = True

    digit_visible = True

    dernier_decompte = time.ticks_ms()

    buzzer_off()

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

    buzzer_off()

    afficher_temps()


# ============================================================
# DECOMPTER UNE SECONDE
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
    # DECREMENTATION
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
    # FIN
    # ========================================================

    if (
        heures == 0
        and minutes == 0
        and secondes == 0
    ):

        return True


    return False


# ============================================================
# CLIGNOTEMENT DU DIGIT SELECTIONNE
# ============================================================

def gerer_clignotement():

    global digit_visible
    global dernier_clignotement

    # Pas de clignotement pendant le décompte

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
# DECODAGE IR NEC
# ============================================================

def lire_ir():

    try:

        # Début de trame

        duree = time_pulse_us(
            ir,
            0,
            150000
        )


        if duree < 8000 or duree > 10000:
            return None


        # Impulsion haute

        duree = time_pulse_us(
            ir,
            1,
            10000
        )


        if duree < 4000 or duree > 5500:
            return None


        valeur = 0


        # Lecture des 32 bits

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
# TRAITEMENT DES COMMANDES IR
# ============================================================

def traiter_commande(code):

    global digit_visible


    # ========================================================
    # PLUS
    # ========================================================

    if code == IR_PLUS:

        if not en_marche:

            # MODIFICATION UNIQUEMENT
            # DU DIGIT SELECTIONNE

            modifier_digit(+1)

            digit_visible = True

            afficher_temps()


    # ========================================================
    # MOINS
    # ========================================================

    elif code == IR_MINUS:

        if not en_marche:

            # MODIFICATION UNIQUEMENT
            # DU DIGIT SELECTIONNE

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
    # LEFT
    # ========================================================

    elif code == IR_LEFT:

        if not en_marche:

            aller_gauche()


    # ========================================================
    # RIGHT
    # ========================================================

    elif code == IR_RIGHT:

        if not en_marche:

            aller_droite()


    # ========================================================
    # PAVE NUMERIQUE
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


            # Le chiffre remplace uniquement
            # le digit sélectionné

            valeur_actuelle = digits[
                digit_selectionne
            ]


            difference = (
                chiffre -
                valeur_actuelle
            )


            modifier_digit(difference)

            digit_visible = True

            afficher_temps()


# ============================================================
# INITIALISATION FINALE
# ============================================================

buzzer_off()

eteindre_tout()

afficher_temps()


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

while True:


    # ========================================================
    # LECTURE TELECOMMANDE
    # ========================================================

    code = lire_ir()


    if code is not None:

        traiter_commande(code)

        # Éviter les doubles détections

        time.sleep_ms(150)


    # ========================================================
    # CLIGNOTEMENT DU DIGIT
    # ========================================================

    gerer_clignotement()


    # ========================================================
    # DECOMPTE
    # ========================================================

    if en_marche:

        termine = decrementer_temps()


        # Vérification des alertes
        # uniquement pendant le décompte

        if not termine:

            verifier_alertes()


        # ====================================================
        # FIN DU DECOMPTE
        # ====================================================

        if termine:

            # Passage en état terminé

            en_marche = False

            points_allumes = False


            # Le temps reste à 00:00
            # et les LED restent rouges

            afficher_temps()


            # =================================================
            # SEUL SON DE FIN
            # =================================================

            buzzer_fin_10s()


            # Sécurité : buzzer éteint

            buzzer_off()


            # Affichage final

            afficher_temps()


    time.sleep_ms(10)