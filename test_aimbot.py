import ctypes
import cv2
import json
import math
import mss
import os
import sys
import time
import torch
import numpy as np
import win32api
from termcolor import colored
from ultralytics import YOLO

# Windows API Strukturen für Maus-Input
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class SimpleAimbot:
    def __init__(self):
        print(colored("[INFO] Starte einfachen Aimbot-Test...", "green"))
        
        # Bildschirmauflösung
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        self.screen_center_x = self.screen_width // 2
        self.screen_center_y = self.screen_height // 2
        
        print(f"[INFO] Bildschirmauflösung: {self.screen_width}x{self.screen_height}")
        print(f"[INFO] Bildschirmmitte: ({self.screen_center_x}, {self.screen_center_y})")
        
        # Konfiguration laden
        with open("lib/config/config.json", "r") as f:
            self.config = json.load(f)
        print(f"[INFO] Konfiguration geladen: {self.config}")
        
        # Maus-Steuerung
        self.extra = ctypes.c_ulong(0)
        self.ii_ = Input_I()
        
        # YOLO-Modell laden
        print("[INFO] Lade YOLO-Modell...")
        self.model = YOLO('lib/best.pt')
        print("[INFO] Modell geladen")
        
        # Screen Capture
        self.screen = mss.mss()
        
        # Einstellungen
        self.aimbot_enabled = True
        self.triggerbot_enabled = True
        self.confidence_threshold = 0.3
        self.aim_height_offset = 8
        
        print(colored("[INFO] Einfacher Aimbot bereit!", "green"))
        print(colored("[INFO] Drücke 'q' zum Beenden", "yellow"))
    
    def move_mouse(self, dx, dy):
        """Bewegt die Maus relativ"""
        try:
            print(f"[MOUSE] Bewege Maus: dx={dx}, dy={dy}")
            self.ii_.mi = MouseInput(int(dx), int(dy), 0, 0x0001, 0, ctypes.pointer(self.extra))
            input_obj = Input(ctypes.c_ulong(0), self.ii_)
            result = ctypes.windll.user32.SendInput(1, ctypes.byref(input_obj), ctypes.sizeof(input_obj))
            print(f"[MOUSE] Ergebnis: {result}")
        except Exception as e:
            print(f"[MOUSE] Fehler: {e}")
    
    def left_click(self):
        """Führt einen Linksklick aus"""
        try:
            print("[CLICK] Linksklick ausgeführt")
            ctypes.windll.user32.mouse_event(0x0002)  # Linksklick runter
            time.sleep(0.001)
            ctypes.windll.user32.mouse_event(0x0004)  # Linksklick hoch
        except Exception as e:
            print(f"[CLICK] Fehler: {e}")
    
    def is_right_mouse_pressed(self):
        """Prüft ob rechte Maustaste gedrückt ist"""
        try:
            return win32api.GetKeyState(0x02) in (-127, -128)
        except:
            return False
    
    def is_left_mouse_pressed(self):
        """Prüft ob linke Maustaste gedrückt ist"""
        try:
            return win32api.GetKeyState(0x01) in (-127, -128)
        except:
            return False
    
    def find_closest_target(self, detections):
        """Findet das nächste Ziel"""
        if not detections:
            return None
        
        closest_target = None
        min_distance = float('inf')
        
        for detection in detections:
            x1, y1, x2, y2 = detection
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Zielhöhe berechnen (Kopf-Position)
            height = y2 - y1
            target_y = center_y - height // self.aim_height_offset
            
            # Distanz zur Bildschirmmitte berechnen
            distance = math.sqrt((center_x - self.screen_center_x)**2 + (target_y - self.screen_center_y)**2)
            
            # Eigenen Spieler ausschließen (in der Mitte)
            if distance < 100:  # Zu nah zur Mitte = eigener Spieler
                continue
            
            if distance < min_distance:
                min_distance = distance
                closest_target = {
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                    'center_x': center_x, 'center_y': center_y,
                    'target_x': center_x, 'target_y': target_y,
                    'distance': distance
                }
        
        return closest_target
    
    def aim_at_target(self, target):
        """Zielt auf das gefundene Ziel"""
        if not target:
            return
        
        # Absolute Koordinaten
        target_x = target['target_x']
        target_y = target['target_y']
        
        # Distanz zur Bildschirmmitte
        dx = target_x - self.screen_center_x
        dy = target_y - self.screen_center_y
        
        print(f"[AIM] Ziel: ({target_x}, {target_y})")
        print(f"[AIM] Distanz: ({dx}, {dy})")
        
        # Empfindlichkeit anwenden
        if self.is_right_mouse_pressed():
            scale = self.config["targeting_scale"]
            print(f"[AIM] Verwende targeting_scale: {scale}")
        else:
            scale = self.config["xy_scale"]
            print(f"[AIM] Verwende xy_scale: {scale}")
        
        # Maus bewegen
        move_x = dx * scale
        move_y = dy * scale
        
        print(f"[AIM] Berechnete Bewegung: ({move_x}, {move_y})")
        
        if abs(move_x) > 1 or abs(move_y) > 1:
            print(f"[AIM] Bewege Maus um ({move_x}, {move_y})")
            self.move_mouse(move_x, move_y)
        else:
            print("[AIM] Keine Bewegung nötig")
    
    def triggerbot(self, target):
        """Automatisches Schießen wenn Ziel erfasst"""
        if not target or not self.triggerbot_enabled:
            return
        
        # Prüfe ob Ziel im Fadenkreuz
        target_x = target['target_x']
        target_y = target['target_y']
        
        # Distanz zur Bildschirmmitte
        distance = math.sqrt((target_x - self.screen_center_x)**2 + (target_y - self.screen_center_y)**2)
        
        print(f"[TRIGGER] Distanz zum Fadenkreuz: {distance}")
        
        # Schießen wenn Ziel nah genug am Fadenkreuz
        if distance < 20 and not self.is_left_mouse_pressed():
            print("[TRIGGER] Schieße!")
            time.sleep(0.05)  # Kleine Verzögerung
            self.left_click()
    
    def start(self):
        """Startet die Hauptschleife"""
        print(colored("[INFO] Starte Bildschirm-Erkennung...", "green"))
        
        try:
            while True:
                start_time = time.time()
                
                # Bildschirm erfassen (Vollbildschirm)
                screenshot = self.screen.grab({
                    'left': 0,
                    'top': 0,
                    'width': self.screen_width,
                    'height': self.screen_height
                })
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # YOLO-Detektion
                results = self.model.predict(frame, verbose=False, conf=self.confidence_threshold)
                
                detections = []
                if len(results) > 0 and len(results[0].boxes) > 0:
                    for box in results[0].boxes.xyxy:
                        x1, y1, x2, y2 = map(int, box)
                        detections.append((x1, y1, x2, y2))
                
                # Nächstes Ziel finden
                target = self.find_closest_target(detections)
                
                # Visuelle Anzeige
                if target:
                    # Ziel markieren
                    cv2.rectangle(frame, (target['x1'], target['y1']), (target['x2'], target['y2']), (0, 255, 0), 2)
                    cv2.circle(frame, (target['target_x'], target['target_y']), 5, (0, 0, 255), -1)
                    
                    # Linie zum Fadenkreuz
                    cv2.line(frame, (target['target_x'], target['target_y']), (self.screen_center_x, self.screen_center_y), (255, 255, 0), 2)
                    
                    # Status-Text
                    cv2.putText(frame, "TARGET LOCKED", (target['x1'], target['y1'] - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Aimbot und Triggerbot
                    if self.aimbot_enabled:
                        self.aim_at_target(target)
                        self.triggerbot(target)
                
                # FPS und Status anzeigen
                fps = int(1 / (time.time() - start_time))
                cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, f"AIMBOT: {'ON' if self.aimbot_enabled else 'OFF'}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"TRIGGERBOT: {'ON' if self.triggerbot_enabled else 'OFF'}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"TARGETS: {len(detections)}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Fenster anzeigen
                cv2.imshow("Simple Aimbot Test", frame)
                
                # Beenden bei 'q' oder ESC
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
                    
        except KeyboardInterrupt:
            print(colored("\n[INFO] Programm durch Benutzer beendet", "yellow"))
        except Exception as e:
            print(colored(f"[FEHLER] Unerwarteter Fehler: {e}", "red"))
            import traceback
            print(traceback.format_exc())
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Bereinigt Ressourcen"""
        print(colored("\n[INFO] Bereinige Ressourcen...", "yellow"))
        try:
            self.screen.close()
            cv2.destroyAllWindows()
        except:
            pass
        print(colored("[INFO] Programm beendet", "green"))

if __name__ == "__main__":
    try:
        aimbot = SimpleAimbot()
        aimbot.start()
    except Exception as e:
        print(colored(f"[FEHLER] {e}", "red"))
        import traceback
        print(traceback.format_exc())
