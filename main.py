import cv2
import speech_recognition as sr
import threading
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import time
import queue
import unicodedata

# --- CONFIGURARE ---
sign_queue = queue.Queue()
last_full_text = "SISTEM ACTIV"
current_char_display = None
is_listening = False

def remove_diacritics(text):
    """Transformă 'ă' în 'a', 'ș' în 's' etc."""
    return "".join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

def find_image(char):
    char = remove_diacritics(char).upper()
    base_path = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_path, "alfabet_imagini")
    for ext in ['.jpg', '.png', '.jpeg']:
        p = os.path.join(folder, f"{char}{ext}")
        if os.path.exists(p): return cv2.imread(p)
    return None

def speech_worker():
    global last_full_text, is_listening
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Microfon pregatit...")
        while True:
            is_listening = True
            try:
                audio = r.listen(source, phrase_time_limit=5)
                text = r.recognize_google(audio, language="ro-RO")
                last_full_text = text.upper()
                for char in text.lower().replace(" ", ""):
                    sign_queue.put(char)
            except: pass

threading.Thread(target=speech_worker, daemon=True).start()

cap = cv2.VideoCapture(0)
char_timer = 0

# Culori PRO
CLR_ACCENT = (0, 255, 200) # Mint Neon
CLR_BG = (15, 15, 18)

while True:
    ret, frame = cap.read()
    if not ret: break

    # Logică Coadă
    if current_char_display is None and not sign_queue.empty():
        current_char = sign_queue.get()
        img_raw = find_image(current_char)
        if img_raw is not None:
            current_char_display = cv2.resize(img_raw, (400, 400))
            char_timer = time.time()
    
    if current_char_display is not None and time.time() - char_timer > 0.7:
        current_char_display = None

    # --- EFECT PRO: DETECTIE CONTUR MANA ---
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Desenăm doar conturul cel mai mare (mâna) cu efect de neon
    if contours:
        max_cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_cnt) > 5000:
            cv2.drawContours(frame, [max_cnt], -1, CLR_ACCENT, 2)

    # --- UI DASHBOARD ---
    canvas = np.full((720, 1280, 3), CLR_BG, dtype=np.uint8)
    
    # Video (Stânga)
    vid_res = cv2.resize(frame, (560, 420))
    canvas[140:560, 40:600] = vid_res
    cv2.rectangle(canvas, (40, 140), (600, 560), CLR_ACCENT, 1)

    # Sign (Dreapta)
    cv2.rectangle(canvas, (680, 140), (1240, 560), (25, 25, 30), -1)
    if current_char_display is not None:
        canvas[150:550, 760:1160] = current_char_display
        cv2.rectangle(canvas, (760, 150), (1160, 550), CLR_ACCENT, 2)

    # Text Overlay cu OpenCV (pentru viteză)
    cv2.putText(canvas, "AI SIGN INTERPRETER PRO", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, CLR_ACCENT, 2)
    cv2.putText(canvas, f"STATUS: {'LISTENING' if is_listening else 'IDLE'}", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 1)
    
    # Casetă Subtitrare
    cv2.rectangle(canvas, (40, 600), (1240, 700), (30, 30, 35), -1)
    cv2.putText(canvas, f"OUTPUT: {last_full_text}", (70, 660), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.imshow('SignAI Master', canvas)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()