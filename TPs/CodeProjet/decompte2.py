import time

def decompte(secondes_totales):
    while secondes_totales >= 0:
        # Conversion des secondes en heures, minutes et secondes
        heures = secondes_totales // 3600
        minutes = (secondes_totales % 3600) // 60
        secondes = secondes_totales % 60

        # Formatage HH:MM:SS avec zéros de remplissage
        minuterie = f"{heures:02d}:{minutes:02d}:{secondes:02d}"

        # '\r' permet de réécrire sur la même ligne dans le terminal
        print(minuterie, end="\r")

        time.sleep(1)
        secondes_totales -= 1

    print("\nTemps écoulé !")

# Exemple : Décompte de 1 heure, 2 minutes et 30 secondes (3750 secondes)
decompte(10)