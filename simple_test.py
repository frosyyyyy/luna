import ctypes
import time
import win32api

print("=== EINFACHER MAUS-TEST ===")

# Windows API Strukturen
PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def move_mouse(dx, dy):
    """Bewegt die Maus relativ"""
    try:
        print(f"Bewege Maus: dx={dx}, dy={dy}")
        extra = ctypes.c_ulong(0)
        ii = Input_I()
        ii.mi = MouseInput(int(dx), int(dy), 0, 0x0001, 0, ctypes.pointer(extra))
        input_obj = Input(ctypes.c_ulong(0), ii)
        result = ctypes.windll.user32.SendInput(1, ctypes.byref(input_obj), ctypes.sizeof(input_obj))
        print(f"Ergebnis: {result}")
        return result
    except Exception as e:
        print(f"Fehler: {e}")
        return 0

def left_click():
    """Führt einen Linksklick aus"""
    try:
        print("Linksklick ausgeführt")
        ctypes.windll.user32.mouse_event(0x0002)  # Linksklick runter
        time.sleep(0.001)
        ctypes.windll.user32.mouse_event(0x0004)  # Linksklick hoch
    except Exception as e:
        print(f"Klick-Fehler: {e}")

def is_right_mouse_pressed():
    """Prüft ob rechte Maustaste gedrückt ist"""
    try:
        return win32api.GetKeyState(0x02) in (-127, -128)
    except:
        return False

def is_left_mouse_pressed():
    """Prüft ob linke Maustaste gedrückt ist"""
    try:
        return win32api.GetKeyState(0x01) in (-127, -128)
    except:
        return False

print("Teste Maus-Bewegung...")
print("Drücke ENTER um zu starten...")
input()

print("1. Teste kleine Bewegung nach rechts...")
move_mouse(50, 0)
time.sleep(1)

print("2. Teste kleine Bewegung nach unten...")
move_mouse(0, 50)
time.sleep(1)

print("3. Teste Bewegung zurück...")
move_mouse(-50, -50)
time.sleep(1)

print("4. Teste Linksklick...")
left_click()
time.sleep(1)

print("5. Teste Maus-Status...")
print(f"Rechte Maustaste gedrückt: {is_right_mouse_pressed()}")
print(f"Linke Maustaste gedrückt: {is_left_mouse_pressed()}")

print("Test abgeschlossen!")
print("Hat sich die Maus bewegt? (j/n)")
antwort = input().lower()
if antwort == 'j':
    print("Maus-Bewegung funktioniert!")
else:
    print("Maus-Bewegung funktioniert NICHT!")
