import time

def validate_time_format(time_str):
    """
    Valide que la chaîne est au format HH:MM:SS et que les valeurs sont correctes.
    Retourne (heures, minutes, secondes) si valide, sinon lève ValueError.
    """
    try:
        parts = time_str.strip().split(":")
        if len(parts) != 3:
            raise ValueError("Format invalide. Utilisez HH:MM:SS.")
        
        hours, minutes, seconds = map(int, parts)
        
        if not (0 <= minutes < 60 and 0 <= seconds < 60 and hours >= 0):
            raise ValueError("Valeurs hors plage.")
        
        return hours, minutes, seconds
    except ValueError as e:
        raise ValueError(f"Erreur de format : {e}")

def countdown_timer(hours, minutes, seconds):
    """
    Lance un compte à rebours à partir du temps donné.
    """
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    while total_seconds >= 0:
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        print(f"\r{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}", end="")
        time.sleep(1)
        total_seconds -= 1
    
    print("\n⏰ Temps écoulé !")

if __name__ == "__main__":
    try:
        user_input = input("Entrez la durée (HH:MM:SS) : ")
        h, m, s = validate_time_format(user_input)
        countdown_timer(h, m, s)
    except ValueError as err:
        print(err)

