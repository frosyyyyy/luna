import json
import os
import sys
import logging
from pynput import keyboard
from termcolor import colored

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lunar.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def on_release(key):
    try:
        if key == keyboard.Key.f1:
            logger.info("F1 gedrückt - Aimbot-Status wird geändert")
            Aimbot.update_status_aimbot()
        elif key == keyboard.Key.f2:
            logger.info("F2 gedrückt - Programm wird beendet")
            Aimbot.cleanup()
            sys.exit(0)
        elif key == keyboard.Key.f3:
            logger.info("F3 gedrückt - Aimbot ein/aus")
            lunar.toggle_aimbot()
        elif key == keyboard.Key.f4:
            logger.info("F4 gedrückt - Triggerbot ein/aus")
            lunar.toggle_triggerbot()
        elif key == keyboard.Key.f5:
            logger.info("F5 gedrückt - Einstellungsmenü wird angezeigt")
            lunar.show_menu()
        elif key == keyboard.Key.f6:
            logger.info("F6 gedrückt - Status wird angezeigt")
            lunar.show_status()
        elif key == keyboard.Key.f7:
            logger.info("F7 gedrückt - Erkennungsmodus wird umgeschaltet")
            lunar.toggle_detection_mode()
        elif key == keyboard.Key.f8:
            logger.info("F8 gedrückt - Maus-Bewegung wird getestet")
            lunar.test_mouse_movement()
    except NameError:
        logger.warning("Aimbot-Klasse noch nicht geladen")
    except Exception as e:
        logger.error(f"Fehler beim Verarbeiten der Tasteneingabe: {e}")

def main():
    global lunar
    try:
        logger.info("Lunar Aimbot wird gestartet...")
        lunar = Aimbot(collect_data="collect_data" in sys.argv)
        lunar.start()
    except Exception as e:
        logger.error(f"Fehler beim Starten des Aimbots: {e}")
        print(colored(f"[FEHLER] {e}", "red"))
        sys.exit(1)

def setup():
    """Konfiguriert die Empfindlichkeitseinstellungen für den Aimbot"""
    path = "lib/config"
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Konfigurationsverzeichnis erstellt: {path}")

    print(colored("[INFO] Die X- und Y-Achsen-Empfindlichkeit im Spiel sollten gleich sein", "yellow"))
    
    def prompt(prompt_text, min_val=0.1, max_val=100.0):
        """Sichere Eingabeaufforderung mit Validierung"""
        valid_input = False
        while not valid_input:
            try:
                number = float(input(prompt_text))
                if min_val <= number <= max_val:
                    valid_input = True
                else:
                    print(colored(f"[!] Eingabe muss zwischen {min_val} und {max_val} liegen", "red"))
            except ValueError:
                print(colored("[!] Ungültige Eingabe. Bitte nur Zahlen eingeben (z.B. 6.9)", "red"))
            except KeyboardInterrupt:
                print(colored("\n[!] Setup abgebrochen", "red"))
                sys.exit(0)
        return number

    try:
        xy_sens = prompt("X- und Y-Achsen-Empfindlichkeit (aus den Spiel-Einstellungen): ", 0.1, 50.0)
        targeting_sens = prompt("Ziel-Empfindlichkeit (aus den Spiel-Einstellungen): ", 0.1, 100.0)

        print(colored("[INFO] Deine Ziel-Empfindlichkeit im Spiel muss der Zoom-Empfindlichkeit entsprechen", "yellow"))
        
        # Berechnung der Skalierungsfaktoren
        xy_scale = 10 / xy_sens
        targeting_scale = 1000 / (targeting_sens * xy_sens)
        
        sensitivity_settings = {
            "xy_sens": xy_sens, 
            "targeting_sens": targeting_sens, 
            "xy_scale": xy_scale, 
            "targeting_scale": targeting_scale
        }

        with open('lib/config/config.json', 'w') as outfile:
            json.dump(sensitivity_settings, outfile, indent=4)
        
        logger.info("Empfindlichkeitskonfiguration abgeschlossen")
        print(colored("[INFO] Empfindlichkeitskonfiguration abgeschlossen", "green"))
        
    except Exception as e:
        logger.error(f"Fehler beim Setup: {e}")
        print(colored(f"[FEHLER] Setup fehlgeschlagen: {e}", "red"))
        sys.exit(1)

def check_dependencies():
    """Überprüft, ob alle erforderlichen Abhängigkeiten verfügbar sind"""
    required_modules = ['cv2', 'torch', 'ultralytics', 'mss', 'numpy', 'win32api', 'pynput']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(colored(f"[FEHLER] Fehlende Module: {', '.join(missing_modules)}", "red"))
        print(colored("Bitte installiere die fehlenden Module mit: pip install -r requirements.txt", "yellow"))
        return False
    return True

if __name__ == "__main__":
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

        print(colored('''

  _    _   _ _   _    _    ____     _     ___ _____ _____ 
 | |  | | | | \ | |  / \  |  _ \   | |   |_ _|_   _| ____|
 | |  | | | |  \| | / _ \ | |_) |  | |    | |  | | |  _|  
 | |__| |_| | |\  |/ ___ \|  _ <   | |___ | |  | | | |___ 
 |_____\___/|_| \_/_/   \_\_| \_\  |_____|___| |_| |_____|
                                                                         
(Neural Network Aimbot)''', "green"))
        
        print(colored('Für die Vollversion von Lunar V2, besuche https://gannonr.com/lunar ODER trete dem Discord bei: discord.gg/aiaimbot', "red"))
        
        print(colored("""
╔══════════════════════════════════════════════════════════════╗
║                        HOTKEYS                               ║
╠══════════════════════════════════════════════════════════════╣
║  F1 - Aimbot ein/aus (Hauptschalter)                         ║
║  F2 - Programm beenden                                        ║
║  F3 - Aimbot ein/aus (separat)                               ║
║  F4 - Triggerbot ein/aus                                     ║
║  F5 - Einstellungsmenü anzeigen                              ║
║  F6 - Status anzeigen                                        ║
║  F7 - Erkennungsmodus umschalten (FOV/Vollbildschirm)        ║
║  F8 - Maus-Bewegung testen                                   ║
╚══════════════════════════════════════════════════════════════╝""", "cyan"))

        # Abhängigkeiten überprüfen
        if not check_dependencies():
            sys.exit(1)

        # Konfiguration überprüfen
        path_exists = os.path.exists("lib/config/config.json")
        if not path_exists or ("setup" in sys.argv):
            if not path_exists:
                print(colored("[!] Empfindlichkeitskonfiguration ist nicht gesetzt", "yellow"))
            setup()
        
        # Datenverzeichnis für Datensammlung erstellen
        path_exists = os.path.exists("lib/data")
        if "collect_data" in sys.argv and not path_exists:
            os.makedirs("lib/data")
            logger.info("Datenverzeichnis für Datensammlung erstellt")
        
        # Aimbot importieren und starten
        from lib.aimbot import Aimbot
        listener = keyboard.Listener(on_release=on_release)
        listener.start()
        logger.info("Tastatur-Listener gestartet")
        main()
        
    except KeyboardInterrupt:
        print(colored("\n[INFO] Programm durch Benutzer beendet", "yellow"))
        logger.info("Programm durch Benutzer beendet")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        print(colored(f"[FEHLER] Unerwarteter Fehler: {e}", "red"))
        sys.exit(1)