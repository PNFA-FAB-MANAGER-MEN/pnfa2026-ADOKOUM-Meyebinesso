from machine import Pin, time_pulse_us
import neopixel
import time


# ============================================================
# CONFIGURATION DES BROCHES
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

led_heure = neopixel.NeoPixel(
    Pin(PIN_HEURE, Pin.OUT),
    NB_LED_HEURE
)

led_minute = neopixel.NeoPixel(
    Pin(PIN_MINUTE, Pin.OUT),
    NB_LED_MINUTE
)

led_points = neopixel.NeoPixel(
    Pin(PIN_POINTS, Pin.OUT),
    NB_LED_POINTS
)

ir = Pin(PIN_IR, Pin.IN)
buzzer = Pin(PIN_BUZZER, Pin.OUT)

buzzer.value(0)


# ============================================================
# CODES INFRAROUGES
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
# COULEURS
# ============================================================

COULEUR_PROGRAMMATION = (30, 30, 30)

COULEUR_VERTE = (0, 255, 0)

COULEUR_ORANGE = (255, 80, 0)

COULEUR_ROUGE = (255, 0, 0)

ETEINT = (0, 0, 0)


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

etat_points = False

# Digit sélectionné :
#
# 0 = dizaine heures
# 1 = unité heures
# 2 = dizaine minutes
# 3 = unité minutes
#
digit_selectionne = 0

selection_visible = True

dernier_clignotement = time.ticks_ms()

dernier_decompte = time.ticks_ms()


# ============================================================
# VARIABLES POUR LES ALERTES
# ============================================================

temps_total_programme = 0

alerte_50 = False
alerte_75 = False
alerte_95 = False


# ============================================================
# FONCTION : ÉTEINDRE LES LEDS
# ============================================================

def eteindre_leds():

    for i in range(NB_LED_HEURE):
        led_heure[i] = ETEINT

    for i in range(NB_LED_MINUTE):
        led_minute[i] = ETEINT

    for i in range(NB_LED_POINTS):
        led_points[i] = ETEINT

    led_heure.write()
    led_minute.write()
    led_points.write()


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
# COULEUR DU DÉCOMPTE
# ============================================================

def couleur_du_decompte():

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
# AFFICHAGE DU TEMPS
# ============================================================

def afficher_temps():

    global digit_selectionne
    global selection_visible

    # --------------------------------------------------------
    # Séparation heures / minutes
    # --------------------------------------------------------

    h_dizaine = heures // 10
    h_unite = heures % 10

    m_dizaine = minutes // 10
    m_unite = minutes % 10


    # --------------------------------------------------------
    # Couleur
    # --------------------------------------------------------

    if en_marche:

        couleur = couleur_du_decompte()

    else:

        couleur = COULEUR_PROGRAMMATION


    # --------------------------------------------------------
    # Affichage heures
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
    # Affichage minutes
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
    # Sélection du digit
    #
    # Le digit sélectionné clignote uniquement
    # pendant la programmation.
    # --------------------------------------------------------

    if not en_marche and not selection_visible:

        if digit_selectionne == 0:

            for i in range(7):
                led_heure[i] = ETEINT

        elif digit_selectionne == 1:

            for i in range(7, 14):
                led_heure[i] = ETEINT

        elif digit_selectionne == 2:

            for i in range(7):
                led_minute[i] = ETEINT

        elif digit_selectionne == 3:

            for i in range(7, 14):
                led_minute[i] = ETEINT


    # --------------------------------------------------------
    # Double point
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
    # Envoi vers les LEDs
    # --------------------------------------------------------

    led_heure.write()
    led_minute.write()
    led_points.write()


# ============================================================
# MODIFICATION D'UN DIGIT
# ============================================================

def modifier_digit(nouvelle_valeur):

    global heures
    global minutes

    if en_marche:

        return


    # --------------------------------------------------------
    # DIZAINE DES HEURES
    # --------------------------------------------------------

    if digit_selectionne == 0:

        nouvelle_valeur = nouvelle_valeur % 10

        heures = (
            nouvelle_valeur * 10
            + heures % 10
        )


    # --------------------------------------------------------
    # UNITE DES HEURES
    # --------------------------------------------------------

    elif digit_selectionne == 1:

        nouvelle_valeur = nouvelle_valeur % 10

        heures = (
            (heures // 10) * 10
            + nouvelle_valeur
        )


    # --------------------------------------------------------
    # DIZAINE DES MINUTES
    # --------------------------------------------------------

    elif digit_selectionne == 2:

        # Les dizaines de minutes vont de 0 à 5

        if nouvelle_valeur > 5:

            nouvelle_valeur = 0

        minutes = (
            nouvelle_valeur * 10
            + minutes % 10
        )


    # --------------------------------------------------------
    # UNITE DES MINUTES
    # --------------------------------------------------------

    elif digit_selectionne == 3:

        nouvelle_valeur = nouvelle_valeur % 10

        minutes = (
            (minutes // 10) * 10
            + nouvelle_valeur
        )


    afficher_temps()


# ============================================================
# +1 SUR LE DIGIT SÉLECTIONNÉ
# ============================================================

def augmenter_digit():

    global heures
    global minutes

    if en_marche:

        return


    # Dizaine heures

    if digit_selectionne == 0:

        valeur = heures // 10

        valeur += 1

        if valeur > 9:

            valeur = 0

        heures = valeur * 10 + heures % 10


    # Unité heures

    elif digit_selectionne == 1:

        valeur = heures % 10

        valeur += 1

        if valeur > 9:

            valeur = 0

        heures = (heures // 10) * 10 + valeur


    # Dizaine minutes

    elif digit_selectionne == 2:

        valeur = minutes // 10

        valeur += 1

        if valeur > 5:

            valeur = 0

        minutes = valeur * 10 + minutes % 10


    # Unité minutes

    elif digit_selectionne == 3:

        valeur = minutes % 10

        valeur += 1

        if valeur > 9:

            valeur = 0

        minutes = (minutes // 10) * 10 + valeur


    afficher_temps()


# ============================================================
# -1 SUR LE DIGIT SÉLECTIONNÉ
# ============================================================

def diminuer_digit():

    global heures
    global minutes

    if en_marche:

        return


    # Dizaine heures

    if digit_selectionne == 0:

        valeur = heures // 10

        valeur -= 1

        if valeur < 0:

            valeur = 9

        heures = valeur * 10 + heures % 10


    # Unité heures

    elif digit_selectionne == 1:

        valeur = heures % 10

        valeur -= 1

        if valeur < 0:

            valeur = 9

        heures = (heures // 10) * 10 + valeur


    # Dizaine minutes

    elif digit_selectionne == 2:

        valeur = minutes // 10

        valeur -= 1

        if valeur < 0:

            valeur = 5

        minutes = valeur * 10 + minutes % 10


    # Unité minutes

    elif digit_selectionne == 3:

        valeur = minutes % 10

        valeur -= 1

        if valeur < 0:

            valeur = 9

        minutes = (minutes // 10) * 10 + valeur


    afficher_temps()


# ============================================================
# SÉLECTION SUIVANTE
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


# ============================================================
# DÉPLACEMENT GAUCHE
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


# ============================================================
# DÉPLACEMENT DROITE
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


# ============================================================
# BUZZER : 1 BIP COURT
# ============================================================

def bip_unique():

    buzzer.value(1)

    time.sleep_ms(250)

    buzzer.value(0)


# ============================================================
# BUZZER : 2 BIPS COURTS
# ============================================================

def double_bip():

    buzzer.value(1)

    time.sleep_ms(250)

    buzzer.value(0)

    time.sleep_ms(150)

    buzzer.value(1)

    time.sleep_ms(250)

    buzzer.value(0)


# ============================================================
# BUZZER : 3 BIPS TRÈS COURTS
# ============================================================

def triple_bip():

    buzzer.value(1)

    time.sleep_ms(120)

    buzzer.value(0)

    time.sleep_ms(100)

    buzzer.value(1)

    time.sleep_ms(120)

    buzzer.value(0)

    time.sleep_ms(100)

    buzzer.value(1)

    time.sleep_ms(120)

    buzzer.value(0)


# ============================================================
# BUZZER FIN : 10 SECONDES
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
# VÉRIFICATION DES ALERTES
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


    # --------------------------------------------------------
    # 50 %
    # --------------------------------------------------------

    if not alerte_50 and pourcentage >= 50:

        alerte_50 = True

        bip_unique()


    # --------------------------------------------------------
    # 75 %
    # --------------------------------------------------------

    if not alerte_75 and pourcentage >= 75:

        alerte_75 = True

        double_bip()


    # --------------------------------------------------------
    # 95 %
    # --------------------------------------------------------

    if not alerte_95 and pourcentage >= 95:

        alerte_95 = True

        triple_bip()


# ============================================================
# DÉCRÉMENTATION D'UNE SECONDE
# ============================================================

def decrementer_temps():

    global heures
    global minutes
    global secondes
    global etat_points

    # --------------------------------------------------------
    # Si le temps est déjà terminé
    # --------------------------------------------------------

    if heures == 0 and minutes == 0 and secondes == 0:

        return True


    # --------------------------------------------------------
    # Décrémentation
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


    # --------------------------------------------------------
    # Clignotement du double point
    # --------------------------------------------------------

    etat_points = not etat_points


    afficher_temps()


    # --------------------------------------------------------
    # Vérification de la fin
    # --------------------------------------------------------

    if heures == 0 and minutes == 0 and secondes == 0:

        return True


    return False


# ============================================================
# DÉCODEUR INFRAROUGE NEC
# ============================================================

def lire_ir():

    try:

        # Attendre le début du signal

        duree = time_pulse_us(
            ir,
            0,
            150000
        )

        if duree < 8500 or duree > 9500:

            return None


        # Espace NEC

        duree = time_pulse_us(
            ir,
            1,
            10000
        )

        if duree < 4000 or duree > 5000:

            return None


        valeur = 0


        # Lire 32 bits

        for i in range(32):

            # Impulsion LOW

            duree = time_pulse_us(
                ir,
                0,
                3000
            )

            if duree < 300 or duree > 800:

                return None


            # Mesure du HIGH

            duree = time_pulse_us(
                ir,
                1,
                3000
            )


            if duree > 1400:

                bit = 1

            elif duree > 300:

                bit = 0

            else:

                return None


            valeur <<= 1

            valeur |= bit


        return valeur


    except:

        return None


# ============================================================
# TRAITEMENT DES COMMANDES IR
# ============================================================

def traiter_ir(code):

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

            # Calcul du temps total programmé

            temps_total_programme = (
                heures * 3600
                + minutes * 60
                + secondes
            )


            # Ne pas démarrer à zéro

            if temps_total_programme > 0:

                en_marche = True

                alerte_50 = False
                alerte_75 = False
                alerte_95 = False

                dernier_decompte = time.ticks_ms()

                etat_points = True

                afficher_temps()


    # ========================================================
    # PAUSE
    # ========================================================

    elif code == IR_PAUSE:

        if en_marche:

            en_marche = False

            afficher_temps()


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

        afficher_temps()


    # ========================================================
    # SÉLECTION
    # ========================================================

    elif code == IR_SEL:

        selection_suivante()


    # ========================================================
    # GAUCHE
    # ========================================================

    elif code == IR_LEFT:

        aller_gauche()


    # ========================================================
    # DROITE
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
    # PAVÉ NUMÉRIQUE
    # ========================================================

    elif code in CODES_CHIFFRES:

        modifier_digit(
            CODES_CHIFFRES[code]
        )


# ============================================================
# INITIALISATION DE L'AFFICHAGE
# ============================================================

afficher_temps()


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

while True:

    # --------------------------------------------------------
    # Lecture IR
    # --------------------------------------------------------

    code = lire_ir()

    if code is not None:

        traiter_ir(code)


    # --------------------------------------------------------
    # Clignotement du digit sélectionné
    # --------------------------------------------------------

    if not en_marche:

        maintenant = time.ticks_ms()

        if time.ticks_diff(
            maintenant,
            dernier_clignotement
        ) >= 500:

            dernier_clignotement = maintenant

            selection_visible = not selection_visible

            afficher_temps()


    # --------------------------------------------------------
    # DÉCOMPTE
    # --------------------------------------------------------

    if en_marche:

        maintenant = time.ticks_ms()

        if time.ticks_diff(
            maintenant,
            dernier_decompte
        ) >= 1000:

            dernier_decompte += 1000

            termine = decrementer_temps()


            # ------------------------------------------------
            # Vérification des alertes
            # ------------------------------------------------

            if not termine:

                verifier_alertes()


            # ------------------------------------------------
            # FIN DU MINUTEUR
            # ------------------------------------------------

            else:

                en_marche = False

                etat_points = False

                # Affichage final rouge

                couleur = COULEUR_ROUGE

                afficher_chiffre(
                    led_heure,
                    0,
                    0,
                    couleur
                )

                afficher_chiffre(
                    led_heure,
                    0,
                    1,
                    couleur
                )

                afficher_chiffre(
                    led_minute,
                    0,
                    0,
                    couleur
                )

                afficher_chiffre(
                    led_minute,
                    0,
                    1,
                    couleur
                )

                led_points[0] = ETEINT
                led_points[1] = ETEINT

                led_heure.write()
                led_minute.write()
                led_points.write()


                # Buzzer pendant 10 secondes

                buzzer_fin_10s()

                buzzer.value(0)


    # --------------------------------------------------------
    # Petite pause pour éviter de saturer le processeur
    # --------------------------------------------------------

    time.sleep_ms(10)