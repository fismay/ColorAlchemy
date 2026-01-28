import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import colorsys
import random
import math

# --- Проверка наличия библиотеки Pillow ---
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# --- КОНСТАНТЫ ДИЗАЙНА (DARK MATTER THEME) ---
THEME = {
    "bg_main": "#121212",       # Глубокий черный
    "bg_card": "#1E1E1E",       # Темно-серый для карточек
    "accent": "#BB86FC",        # Неоновый фиолетовый
    "accent_2": "#03DAC6",      # Неоновый бирюзовый
    "text_main": "#FFFFFF",     # Белый текст
    "text_sec": "#B0B0B0",      # Серый текст
    "danger": "#CF6679",        # Красный (ошибки)
    "font_ui": ("Segoe UI", 10),
    "font_bold": ("Segoe UI", 10, "bold"),
    "font_head": ("Segoe UI", 16, "bold"),
    "font_mono": ("Consolas", 12, "bold")
}

class ModernColorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ColorAlchemy v5: Pro Studio")
        self.root.geometry("1000x800")
        self.root.configure(bg=THEME["bg_main"])

        # Состояние
        self.current_hsv_colors = [] # Храним HSV (h, s, v) для точной настройки
        self.mode_var = tk.StringVar(value="🧠 Smart UI")

        self.setup_styles()
        self.build_ui()
        self.generate_palette()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Настройка общих цветов виджетов
        self.style.configure("TFrame", background=THEME["bg_main"])
        self.style.configure("Card.TFrame", background=THEME["bg_card"], relief="flat")
        
        # Labels
        self.style.configure("TLabel", background=THEME["bg_main"], foreground=THEME["text_main"], font=THEME["font_ui"])
        self.style.configure("Card.TLabel", background=THEME["bg_card"], foreground=THEME["text_main"], font=THEME["font_ui"])
        self.style.configure("Sub.Card.TLabel", background=THEME["bg_card"], foreground=THEME["text_sec"], font=("Segoe UI", 8))
        
        # Buttons (Custom styling)
        self.style.configure("Action.TButton", 
                             font=THEME["font_bold"], 
                             background=THEME["accent"], 
                             foreground="#000000", 
                             borderwidth=0, 
                             focuscolor="none")
        self.style.map("Action.TButton", background=[('active', THEME["accent_2"])])

        self.style.configure("Ghost.TButton", 
                             font=THEME["font_ui"], 
                             background=THEME["bg_card"], 
                             foreground=THEME["text_main"], 
                             borderwidth=1,
                             bordercolor=THEME["text_sec"])
        self.style.map("Ghost.TButton", background=[('active', '#333333')])

    def build_ui(self):
        # Главный скролл (если окно маленькое)
        main_frame = tk.Frame(self.root, bg=THEME["bg_main"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- HEADER & CONTROLS ---
        header = tk.Frame(main_frame, bg=THEME["bg_main"])
        header.pack(fill=tk.X, pady=(0, 20))

        # Логотип / Заголовок
        tk.Label(header, text="COLOR // ALCHEMY", font=("Impact", 24), bg=THEME["bg_main"], fg=THEME["accent"]).pack(side=tk.LEFT)

        # Панель управления (Справа)
        controls = tk.Frame(header, bg=THEME["bg_main"])
        controls.pack(side=tk.RIGHT)

        # Инпут цвета
        tk.Label(controls, text="HEX:", bg=THEME["bg_main"], fg=THEME["text_sec"]).pack(side=tk.LEFT, padx=(0,5))
        self.hex_entry = tk.Entry(controls, bg=THEME["bg_card"], fg=THEME["accent_2"], insertbackground="white", 
                                  font=THEME["font_mono"], width=8, bd=0, relief=tk.FLAT)
        self.hex_entry.pack(side=tk.LEFT, padx=(0, 15), ipady=5)
        self.hex_entry.insert(0, "#BB86FC")

        # Выбор режима (Стилизованный OptionMenu)
        modes = ["🧠 Smart UI", "Комплементарный", "Триада", "Тетрада", "Аналоговый", "Рандом"]
        self.mode_menu = tk.OptionMenu(controls, self.mode_var, modes[0], *modes, command=lambda _: self.generate_palette())
        self.mode_menu.config(bg=THEME["bg_card"], fg=THEME["text_main"], highlightthickness=0, bd=0, activebackground=THEME["accent"])
        self.mode_menu["menu"].config(bg=THEME["bg_card"], fg=THEME["text_main"])
        self.mode_menu.pack(side=tk.LEFT, padx=(0, 15))

        # Кнопки
        ttk.Button(controls, text="🎲 RANDOM", style="Ghost.TButton", command=self.random_base).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="⚡ GENERATE", style="Action.TButton", command=self.generate_palette).pack(side=tk.LEFT, padx=5)
        
        if PIL_AVAILABLE:
            ttk.Button(controls, text="💾 PNG", style="Ghost.TButton", command=self.save_palette_to_image).pack(side=tk.LEFT, padx=5)

        # --- WORKSPACE ---
        self.workspace = tk.Frame(main_frame, bg=THEME["bg_main"])
        self.workspace.pack(fill=tk.BOTH, expand=True)
        
        # Контейнер для карточек (Grid)
        self.cards_container = tk.Frame(self.workspace, bg=THEME["bg_main"])
        self.cards_container.pack(fill=tk.BOTH, expand=True)

    # --- ЛОГИКА ---

    def calculate_wcag(self, hex_color, text_color_hex):
        """Считает контраст по стандарту WCAG 2.0"""
        def get_luminance(hex_c):
            r, g, b = tuple(int(hex_c[i:i+2], 16) / 255.0 for i in (1, 3, 5))
            colors = [c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4 for c in (r,g,b)]
            return 0.2126 * colors[0] + 0.7152 * colors[1] + 0.0722 * colors[2]

        lum1 = get_luminance(hex_color)
        lum2 = get_luminance(text_color_hex)
        ratio = (max(lum1, lum2) + 0.05) / (min(lum1, lum2) + 0.05)
        return ratio

    def get_wcag_badge(self, ratio):
        if ratio >= 7: return "AAA (Perfect)", THEME["accent_2"]
        if ratio >= 4.5: return "AA (Good)", THEME["accent"]
        if ratio >= 3: return "AA Large (Ok)", "#FFD700"
        return "FAIL", THEME["danger"]

    def hex_to_hsv(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6: return (0, 0, 0)
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return colorsys.rgb_to_hsv(r/255, g/255, b/255)

    def hsv_to_hex(self, h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        r, g, b = [max(0, min(255, int(c * 255))) for c in (r, g, b)]
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)

    def random_base(self):
        h = random.random()
        s = random.uniform(0.5, 1.0)
        v = random.uniform(0.5, 1.0)
        self.hex_entry.delete(0, tk.END)
        self.hex_entry.insert(0, self.hsv_to_hex(h, s, v))
        self.generate_palette()

    def generate_palette(self):
        try:
            base_hex = self.hex_entry.get()
            if not base_hex.startswith("#"): base_hex = "#" + base_hex
            h, s, v = self.hex_to_hsv(base_hex)
        except: return

        mode = self.mode_var.get()
        new_hsv_colors = []

        # Генерация базовых оттенков
        if "Smart UI" in mode:
             # Логика UI (Фон, Текст, Акцент, Вторичный)
             is_dark = v < 0.5
             bg = (h, s*0.2, 0.12 if is_dark else 0.98)
             text = (h, 0.1, 0.95 if is_dark else 0.1)
             accent = ((h+0.5)%1.0, 0.8, 0.9)
             sec = ((h+0.1)%1.0, 0.6, 0.8)
             new_hsv_colors = [bg, text, accent, sec]
        elif "Комплементарный" in mode:
            new_hsv_colors = [(h, s, v), ((h + 0.5) % 1.0, s, v)]
        elif "Триада" in mode:
            new_hsv_colors = [(h, s, v), ((h + 0.33) % 1.0, s, v), ((h + 0.66) % 1.0, s, v)]
        elif "Тетрада" in mode:
            new_hsv_colors = [(h, s, v), ((h + 0.25) % 1.0, s, v), ((h + 0.5) % 1.0, s, v), ((h + 0.75) % 1.0, s, v)]
        elif "Аналоговый" in mode:
            new_hsv_colors = [((h - 0.1) % 1.0, s, v), (h, s, v), ((h + 0.1) % 1.0, s, v)]
        elif "Рандом" in mode:
            new_hsv_colors = [(h, s, v)] + [(random.random(), random.uniform(0.4,1), random.uniform(0.4,1)) for _ in range(3)]

        self.current_hsv_colors = new_hsv_colors
        self.render_cards()

    # --- ОТРИСОВКА КАРТОЧЕК ---
    def render_cards(self):
        # Очистка
        for w in self.cards_container.winfo_children(): w.destroy()
        
        roles = ["Background", "Text", "Accent", "Secondary"] if "Smart" in self.mode_var.get() else [f"Color {i+1}" for i in range(4)]
        
        # Адаптивная сетка
        count = len(self.current_hsv_colors)
        
        for i, (h, s, v) in enumerate(self.current_hsv_colors):
            hex_code = self.hsv_to_hex(h, s, v)
            
            # --- CARD CONTAINER ---
            card = ttk.Frame(self.cards_container, style="Card.TFrame", padding=15)
            card.grid(row=0, column=i, sticky="nsew", padx=10, pady=10)
            self.cards_container.grid_columnconfigure(i, weight=1)

            # 1. Заголовок роли (если Smart UI)
            if "Smart" in self.mode_var.get() and i < len(roles):
                tk.Label(card, text=roles[i].upper(), font=("Segoe UI", 8, "bold"), bg=THEME["bg_card"], fg=THEME["text_sec"]).pack(anchor="w")

            # 2. Большая цветовая плашка
            swatch = tk.Label(card, bg=hex_code, height=6)
            swatch.pack(fill=tk.X, pady=(5, 10))
            swatch.bind("<Button-1>", lambda e, c=hex_code: self.copy_to_clip(c))

            # 3. HEX код
            hex_lbl = tk.Entry(card, font=THEME["font_mono"], bg=THEME["bg_card"], fg=THEME["text_main"], justify="center", bd=0, relief="flat")
            hex_lbl.insert(0, hex_code)
            hex_lbl.pack(fill=tk.X, pady=(0, 10))

            # --- 4. ACCESSIBILITY CHECK ---
            access_frame = tk.Frame(card, bg=THEME["bg_card"])
            access_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Проверка белого текста
            wcag_w = self.calculate_wcag(hex_code, "#FFFFFF")
            badge_w, color_w = self.get_wcag_badge(wcag_w)
            
            row_w = tk.Frame(access_frame, bg=THEME["bg_card"])
            row_w.pack(fill=tk.X, pady=2)
            
            # ИСПРАВЛЕНО: Теперь используем ttk.Label для стилей
            ttk.Label(row_w, text="On White:", style="Sub.Card.TLabel", width=8).pack(side=tk.LEFT)
            tk.Label(row_w, text=badge_w, bg=THEME["bg_card"], fg=color_w, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

            # Проверка черного текста
            wcag_b = self.calculate_wcag(hex_code, "#000000")
            badge_b, color_b = self.get_wcag_badge(wcag_b)
            
            row_b = tk.Frame(access_frame, bg=THEME["bg_card"])
            row_b.pack(fill=tk.X, pady=2)
            
            # ИСПРАВЛЕНО: Теперь используем ttk.Label для стилей
            ttk.Label(row_b, text="On Black:", style="Sub.Card.TLabel", width=8).pack(side=tk.LEFT)
            tk.Label(row_b, text=badge_b, bg=THEME["bg_card"], fg=color_b, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

            # --- 5. FINE TUNING SLIDERS ---
            tk.Label(card, text="FINE TUNING", font=("Segoe UI", 8, "bold"), bg=THEME["bg_card"], fg=THEME["text_sec"]).pack(anchor="w", pady=(5,0))
            
            tune_frame = tk.Frame(card, bg=THEME["bg_card"])
            tune_frame.pack(fill=tk.X)

            # S (Saturation) Slider
            # ИСПРАВЛЕНО: ttk.Label вместо tk.Label
            ttk.Label(tune_frame, text="Sat", style="Sub.Card.TLabel").pack(anchor="w")
            s_scale = ttk.Scale(tune_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL)
            s_scale.set(s)
            s_scale.pack(fill=tk.X)
            s_scale.configure(command=lambda val, idx=i, _h=h, _v=v: self.update_single_color(idx, _h, float(val), _v))

            # V (Brightness) Slider
            # ИСПРАВЛЕНО: ttk.Label вместо tk.Label
            ttk.Label(tune_frame, text="Bright", style="Sub.Card.TLabel").pack(anchor="w", pady=(5,0))
            v_scale = ttk.Scale(tune_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL)
            v_scale.set(v)
            v_scale.pack(fill=tk.X)
            v_scale.configure(command=lambda val, idx=i, _h=h, _s=s: self.update_single_color(idx, _h, _s, float(val)))

    def update_single_color(self, index, h, s, v):
        """Обновляет один цвет при движении слайдера без полной перерисовки всего"""
        # Обновляем данные в памяти
        self.current_hsv_colors[index] = (h, s, v)
        new_hex = self.hsv_to_hex(h, s, v)
        
        # Находим виджеты карточки и обновляем их напрямую (для производительности)
        # Структура: cards_container -> card (grid slave)
        slaves = self.cards_container.grid_slaves(row=0, column=index)
        if not slaves: return
        card = slaves[0]
        
        children = card.winfo_children()
        
        for widget in children:
            if isinstance(widget, tk.Label) and widget.cget("height") == 6:
                widget.configure(bg=new_hex)
                widget.bind("<Button-1>", lambda e, c=new_hex: self.copy_to_clip(c))
            
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, new_hex)
            
            if isinstance(widget, tk.Frame) and widget.winfo_name().startswith("!frame"): 
                if not widget.winfo_children() or isinstance(widget.winfo_children()[0], tk.Label):
                     pass # Это не то (это может быть пустой фрейм)
                
                # Ищем фрейм, внутри которого есть лейблы с проверкой WCAG
                # Нам нужен фрейм, у которого дети - это фреймы row_w и row_b
                sub_frames = widget.winfo_children()
                if len(sub_frames) >= 2 and isinstance(sub_frames[0], tk.Frame):
                     # White check update
                     wcag_w = self.calculate_wcag(new_hex, "#FFFFFF")
                     badge_w, col_w = self.get_wcag_badge(wcag_w)
                     try: sub_frames[0].winfo_children()[1].configure(text=badge_w, fg=col_w)
                     except: pass
                     
                     # Black check update
                     wcag_b = self.calculate_wcag(new_hex, "#000000")
                     badge_b, col_b = self.get_wcag_badge(wcag_b)
                     try: sub_frames[1].winfo_children()[1].configure(text=badge_b, fg=col_b)
                     except: pass

    def copy_to_clip(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        messagebox.showinfo("Copied", f"Code {text} copied to clipboard!")

    def save_palette_to_image(self):
        if not PIL_AVAILABLE: return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if not file_path: return
        
        w, h = 1200, 400
        img = Image.new("RGB", (w, h), THEME["bg_main"])
        draw = ImageDraw.Draw(img)
        
        col_w = w // len(self.current_hsv_colors)
        
        try: font = ImageFont.truetype("arialbd.ttf", 24)
        except: font = ImageFont.load_default()
        
        for i, (hue, sat, val) in enumerate(self.current_hsv_colors):
            hex_c = self.hsv_to_hex(hue, sat, val)
            x0 = i * col_w
            # Цветная полоса
            draw.rectangle([x0, 0, x0+col_w, h-100], fill=hex_c)
            # Инфо
            draw.text((x0+20, h-80), hex_c, fill="white", font=font)
            
            # WCAG info
            wcag = self.calculate_wcag(hex_c, "#FFFFFF")
            draw.text((x0+20, h-40), f"On White: {wcag:.1f}", fill="#888", font=font)

        img.save(file_path)
        messagebox.showinfo("Saved", "Palette render saved!")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1) # High DPI fix
    except: pass
    app = ModernColorApp(root)
    root.mainloop()