import cv2
import speech_recognition as sr
import threading
import numpy as np
from PIL import Image, ImageOps, ImageTk
import os
import time
import queue
import customtkinter as ctk
import random

# Setări vizuale de bază
ctk.set_appearance_mode("Dark")

class InclusiveSignAI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. DEFINIM CULORILE PRIMELE (ca să fie disponibile pentru Splash)
        self.colors = {
            "bg": "#0A0A0C",
            "sidebar": "#111114",
            "card": "#18181D",
            "accent": "#007AFF", 
            "accent_light": "#3395FF",
            "text_main": "#FFFFFF",
            "text_dim": "#8E8E93",
            "success": "#28CD41",
            "error": "#FF3B30",
            "border": "#2C2C2E"
        }

        # 2. ASCUNDEM FEREASTRA ȘI ARĂTĂM SPLASH-UL
        self.withdraw()
        self.show_splash()

        self.title("INCLUSIVE | Neural Accessibility Suite")
        self.geometry("1400x900")
        
        # State & Logic
        self.sign_queue = queue.Queue()
        self.running = False
        self.cap = None
        self.stars = 0
        
        # Braille Mapping
        self.braille_alphabet = {
            'A': [1], 'B': [1, 2], 'C': [1, 4], 'D': [1, 4, 5], 'E': [1, 5],
            'F': [1, 2, 4], 'G': [1, 2, 4, 5], 'H': [1, 2, 5], 'I': [2, 4], 'J': [2, 4, 5],
            'K': [1, 3], 'L': [1, 2, 3], 'M': [1, 3, 4], 'N': [1, 3, 4, 5], 'O': [1, 3, 5],
            'P': [1, 2, 3, 4], 'Q': [1, 2, 3, 4, 5], 'R': [1, 2, 3, 5], 'S': [2, 3, 4], 'T': [2, 3, 4, 5],
            'U': [1, 3, 6], 'V': [1, 2, 3, 6], 'W': [2, 4, 5, 6], 'X': [1, 3, 4, 6], 'Y': [1, 3, 4, 5, 6], 'Z': [1, 3, 5, 6]
        }
        
        self.configure(fg_color=self.colors["bg"])
        self.setup_layout()

    def show_splash(self):
        splash = ctk.CTkToplevel()
        splash.geometry("500x350+500+300")
        splash.overrideredirect(True)
        splash.configure(fg_color=self.colors["sidebar"])
        splash.attributes("-topmost", True) # Se asigură că stă deasupra pe Mac
        
        # Titlu minimalist
        ctk.CTkLabel(splash, text="INCLUSIVE", font=("Inter", 42, "bold"), text_color=self.colors["accent"]).pack(expand=True)
        ctk.CTkLabel(splash, text="NEURAL INTERPRETER SYSTEM", font=("Inter", 12, "bold"), text_color=self.colors["text_dim"]).pack(pady=(0, 40))
        
        # Închidere automată după 2 secunde
        self.after(2000, lambda: [splash.destroy(), self.deiconify()])

    def setup_layout(self):
        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=self.colors["sidebar"], border_width=1, border_color=self.colors["border"])
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="INCLUSIVE AI", font=("Inter", 20, "bold"), text_color=self.colors["accent"]).pack(pady=(40, 40), padx=30, anchor="w")
        
        self.create_nav_button("DASHBOARD", self.init_dashboard)
        self.create_nav_button("NEURAL INTERPRETER", self.init_translator)
        self.create_nav_button("SIGN ACADEMY", self.init_kids_zone)
        self.create_nav_button("BRAILLE MODULE", self.init_braille_game)
        
        self.stats_frame = ctk.CTkFrame(self.sidebar, fg_color=self.colors["card"], corner_radius=12, border_width=1, border_color=self.colors["border"])
        self.stats_frame.pack(side="bottom", pady=40, padx=20, fill="x")
        self.stars_label = ctk.CTkLabel(self.stats_frame, text=f"EXP: {self.stars}", font=("Inter", 13, "bold"), text_color=self.colors["accent"])
        self.stars_label.pack(pady=15)

        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.pack(side="right", fill="both", expand=True, padx=60, pady=60)
        self.init_dashboard()

    def create_nav_button(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, height=40, corner_radius=8, fg_color="transparent", 
                            text_color=self.colors["text_dim"], font=("Inter", 12, "bold"), 
                            hover_color=self.colors["card"], anchor="w", command=command)
        btn.pack(pady=4, padx=15, fill="x")

    def clear_view(self):
        for w in self.main_view.winfo_children(): w.destroy()
        self.stop_all()

    def init_dashboard(self):
        self.clear_view()
        header = ctk.CTkFrame(self.main_view, fg_color="transparent")
        header.pack(fill="x", pady=(0, 50))
        ctk.CTkLabel(header, text="System Overview", font=("Inter", 32, "bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Select a specialized neural module to continue.", font=("Inter", 15), text_color=self.colors["text_dim"]).pack(anchor="w", pady=5)

        grid = ctk.CTkFrame(self.main_view, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1), weight=1)
        self.create_card(grid, 0, 0, "SIGN INTERPRETER", "Real-time sign language translation using computer vision.", self.init_translator)
        self.create_card(grid, 0, 1, "BRAILLE SYSTEM", "Interactive training for tactile communication patterns.", self.init_braille_game)

    def create_card(self, parent, r, c, title, desc, command):
        card = ctk.CTkFrame(parent, fg_color=self.colors["card"], corner_radius=16, border_width=1, border_color=self.colors["border"])
        card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=("Inter", 18, "bold"), text_color=self.colors["accent"]).pack(pady=(30, 10), padx=30, anchor="w")
        ctk.CTkLabel(card, text=desc, font=("Inter", 13), text_color=self.colors["text_dim"], wraplength=250, justify="left").pack(pady=(0, 30), padx=30, anchor="w")
        ctk.CTkButton(card, text="INITIALIZE", fg_color=self.colors["accent"], hover_color=self.colors["accent_light"],
                     text_color="white", font=("Inter", 12, "bold"), height=35, corner_radius=6, command=command).pack(pady=(0, 30), padx=30, anchor="w")

    def init_translator(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Neural Interpreter Engine", font=("Inter", 24, "bold")).pack(pady=(0, 30), anchor="w")
        layout = ctk.CTkFrame(self.main_view, fg_color="transparent")
        layout.pack(fill="both", expand=True)
        layout.grid_columnconfigure((0, 1), weight=1)
        self.vid_card = ctk.CTkFrame(layout, fg_color="#000000", corner_radius=12, border_width=1, border_color=self.colors["border"])
        self.vid_card.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        self.vid_label = ctk.CTkLabel(self.vid_card, text="ENGINE STANDBY", font=("Inter", 12, "bold"), text_color=self.colors["text_dim"])
        self.vid_label.pack(expand=True)
        self.sign_card = ctk.CTkFrame(layout, fg_color=self.colors["card"], corner_radius=12, border_width=1, border_color=self.colors["border"])
        self.sign_card.grid(row=0, column=1, padx=(15, 0), sticky="nsew")
        self.sign_label = ctk.CTkLabel(self.sign_card, text="")
        self.sign_label.pack(expand=True)
        self.action_btn = ctk.CTkButton(self.main_view, text="BOOT SYSTEM", height=50, corner_radius=8,
                                        fg_color=self.colors["accent"], font=("Inter", 14, "bold"), command=self.toggle_engine)
        self.action_btn.pack(pady=40, fill="x")

    def init_braille_game(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Braille Pattern Recognition", font=("Inter", 24, "bold")).pack(pady=(0, 30), anchor="w")
        display = ctk.CTkFrame(self.main_view, fg_color=self.colors["card"], corner_radius=20, border_width=1, border_color=self.colors["border"])
        display.pack(pady=10, fill="both", expand=True)
        self.braille_dots = []
        dot_positions = [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1)]
        grid_inner = ctk.CTkFrame(display, fg_color="transparent")
        grid_inner.place(relx=0.5, rely=0.5, anchor="center")
        for i in range(6):
            dot = ctk.CTkFrame(grid_inner, width=50, height=50, corner_radius=25, fg_color=self.colors["border"])
            dot.grid(row=dot_positions[i][0], column=dot_positions[i][1], padx=20, pady=20)
            self.braille_dots.append(dot)
        self.options_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.options_frame.pack(pady=40, fill="x")
        self.option_buttons = []
        for i in range(3):
            btn = ctk.CTkButton(self.options_frame, text="", height=50, corner_radius=8, fg_color=self.colors["card"],
                                border_width=1, border_color=self.colors["border"], font=("Inter", 16, "bold"),
                                command=lambda idx=i: self.check_braille_option(idx))
            btn.pack(side="left", expand=True, padx=10)
            self.option_buttons.append(btn)
        self.load_next_braille()

    def load_next_braille(self):
        for btn in self.option_buttons: btn.configure(fg_color=self.colors["card"], text_color="white")
        all_chars = list(self.braille_alphabet.keys())
        self.target_braille = random.choice(all_chars)
        options = [self.target_braille]
        while len(options) < 3:
            wrong = random.choice(all_chars)
            if wrong not in options: options.append(wrong)
        random.shuffle(options)
        self.current_options = options
        active_indices = self.braille_alphabet[self.target_braille]
        for i, dot in enumerate(self.braille_dots):
            dot.configure(fg_color=self.colors["accent"] if (i + 1) in active_indices else self.colors["border"])
        for i, btn in enumerate(self.option_buttons): btn.configure(text=f"Character {options[i]}")

    def check_braille_option(self, idx):
        if self.current_options[idx] == self.target_braille:
            self.stars += 10
            self.option_buttons[idx].configure(fg_color=self.colors["success"])
            self.stars_label.configure(text=f"EXP: {self.stars}")
            self.after(600, self.load_next_braille)
        else:
            self.option_buttons[idx].configure(fg_color=self.colors["error"])
            self.stars = max(0, self.stars - 5)
            self.stars_label.configure(text=f"EXP: {self.stars}")

    def init_kids_zone(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Sign Recognition Academy", font=("Inter", 24, "bold")).pack(pady=(0, 30), anchor="w")
        self.game_display = ctk.CTkFrame(self.main_view, fg_color=self.colors["card"], corner_radius=20, border_width=1, border_color=self.colors["border"])
        self.game_display.pack(pady=10, fill="both", expand=True)
        self.img_label = ctk.CTkLabel(self.game_display, text="ANALYZING...", font=("Inter", 14, "bold"), text_color=self.colors["text_dim"])
        self.img_label.place(relx=0.5, rely=0.5, anchor="center")
        self.btn_mic_kids = ctk.CTkButton(self.main_view, text="VOICE VERIFICATION", height=50, corner_radius=8,
                                          fg_color=self.colors["accent"], font=("Inter", 14, "bold"), command=self.run_kids_game)
        self.btn_mic_kids.pack(pady=40, fill="x")
        self.load_next_char()

    def toggle_engine(self):
        if not self.running:
            self.running = True
            self.cap = cv2.VideoCapture(0)
            self.action_btn.configure(text="TERMINATE SYSTEM", fg_color=self.colors["error"])
            threading.Thread(target=self.audio_thread, daemon=True).start()
            threading.Thread(target=self.sign_thread, daemon=True).start()
            self.update_vid_stream()
        else: 
            self.stop_all()
            self.action_btn.configure(text="BOOT SYSTEM", fg_color=self.colors["accent"])

    def stop_all(self):
        self.running = False
        if self.cap: self.cap.release()
        self.cap = None

    def update_vid_stream(self):
        if self.running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                ctk_img = ctk.CTkImage(img, size=(600, 450))
                self.vid_label.configure(image=ctk_img, text="")
            self.after(10, self.update_vid_stream)

    def audio_thread(self):
        r = sr.Recognizer()
        with sr.Microphone() as src:
            while self.running:
                try:
                    audio = r.listen(src, phrase_time_limit=3)
                    text = r.recognize_google(audio, language="ro-RO").lower()
                    for char in text.replace(" ", ""): self.sign_queue.put(char)
                except: pass

    def sign_thread(self):
        while self.running:
            if not self.sign_queue.empty():
                char = self.sign_queue.get()
                path = self.get_path(char)
                if path:
                    img = Image.open(path)
                    ctk_img = ctk.CTkImage(img, size=(380, 380))
                    self.sign_label.configure(image=ctk_img)
                    time.sleep(1.0)
                    self.sign_label.configure(image="")
            time.sleep(0.1)

    def get_path(self, char):
        f = os.path.join(os.path.dirname(__file__), "alfabet_imagini")
        if not os.path.exists(f): return None
        for ext in ['.jpg', '.png']:
            p = os.path.join(f, f"{char.upper()}{ext}")
            if os.path.exists(p): return p
        return None

    def load_next_char(self):
        f = os.path.join(os.path.dirname(__file__), "alfabet_imagini")
        if os.path.exists(f):
            files = [x for x in os.listdir(f) if x.lower().endswith(('.png', '.jpg'))]
            if files:
                self.target_kids = random.choice(files)
                img = Image.open(os.path.join(f, self.target_kids))
                ctk_img = ctk.CTkImage(img, size=(350, 350))
                self.img_label.configure(image=ctk_img, text="")

    def run_kids_game(self):
        self.btn_mic_kids.configure(text="LISTENING...", fg_color=self.colors["accent_light"])
        threading.Thread(target=self.check_voice_kids, daemon=True).start()

    def check_voice_kids(self):
        r = sr.Recognizer()
        with sr.Microphone() as src:
            try:
                audio = r.listen(src, timeout=3, phrase_time_limit=2)
                voice = r.recognize_google(audio, language="ro-RO").lower()
                if self.target_kids[0].lower() in voice:
                    self.stars += 5
                    self.stars_label.configure(text=f"EXP: {self.stars}")
                    self.btn_mic_kids.configure(text="VERIFIED", fg_color=self.colors["success"])
                    self.after(1000, self.load_next_char)
                else: 
                    self.btn_mic_kids.configure(text="RETRY", fg_color=self.colors["error"])
            except: 
                self.btn_mic_kids.configure(text="SIGNAL LOST")
            self.after(1500, lambda: self.btn_mic_kids.configure(text="VOICE VERIFICATION", fg_color=self.colors["accent"]))

if __name__ == "__main__":
    app = InclusiveSignAI()
    app.mainloop()