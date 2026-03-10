import cv2
import speech_recognition as sr
import threading
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import time

# --- CONFIGURARE ---
r = sr.Recognizer()
last_text = "Vorbeste acum..."
current_sign_img = None

def find_image(char):
    base_path = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_path, "alfabet_imagini")
    for ext in ['.jpg', '.png', '.jpeg']:
        path = os.path.join(folder, f"{char}{ext}")
        if os.path.exists(path):
            return cv2.imread(path)
    return None

def process_text(text):
    global current_sign_img
    clean_text = "".join(filter(str.isalpha, text.lower()))
    for char in clean_text:
        img = find_image(char)
        if img is not None:
            current_sign_img = cv2.resize(img, (640, 480))
            time.sleep(0.6)
    current_sign_img = None

def listen_bg():
    global last_text
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        while True:
            try:
                audio = r.listen(source)
                text = r.recognize_google(audio, language="ro-RO")
                last_text = text
                threading.Thread(target=process_text, args=(text,), daemon=True).start()
            except: pass

threading.Thread(target=listen_bg, daemon=True).start()

cap = cv2.VideoCapture(0)
# Font standard macOS
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 30)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (640, 480))
    canvas = np.zeros((600, 1280, 3), dtype=np.uint8)
    canvas[0:480, 0:640] = frame
    
    if current_sign_img is not None:
        canvas[0:480, 640:1280] = current_sign_img
    else:
        cv2.putText(canvas, "Astept semne...", (800, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)

    # Subtitrare
    cv2.rectangle(canvas, (0, 480), (1280, 600), (10, 10, 10), -1)
    img_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    draw.text((50, 520), f"Subtitrare: {last_text}", font=font, fill=(0, 255, 255))
    canvas = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    cv2.imshow('Proiect AM', canvas)
    # Aduce fereastra in fata pe Mac
    cv2.setWindowProperty('Proiect AM', cv2.WND_PROP_TOPMOST, 1)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()