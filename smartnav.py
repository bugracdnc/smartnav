import tkinter as tk
import subprocess
import os
import configparser

def get_config_path():
    """Pardus/Linux için standart ~/.config dizinini kullanır."""
    base_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    target_dir = os.path.join(base_dir, "smartnav")
    os.makedirs(target_dir, exist_ok=True)
    return os.path.join(target_dir, "config.ini")

def load_or_create_config():
    """Yapılandırma dosyasını okur, yoksa varsayılan değerlerle oluşturur."""
    config_path = get_config_path()
    config = configparser.ConfigParser()
    
    if not os.path.exists(config_path):
        config["Display"] = {
            "resolution": "auto",  # 'auto' veya özel değer, örn: '300x120'
            "scale": "auto"        # 'auto' veya özel çarpan, örn: '1.5'
        }
        with open(config_path, "w", encoding="utf-8") as f:
            config.write(f)
            
    config.read(config_path, encoding="utf-8")
    return config_path, config

def open_config_file():
    """Yapılandırma dosyasını Pardus'un varsayılan metin düzenleyicisiyle açar."""
    config_path = get_config_path()
    subprocess.run(["xdg-open", config_path])

def send_key(key_type):
    """xdotool kullanarak yerel tuş vuruşu gönderir."""
    key_map = {"left": "Left", "right": "Right"}
    subprocess.run(["xdotool", "key", key_map[key_type]])

# --- Pencere Sürükleme Mantığı ---
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

# --- Ana Kurulum ve Ölçeklendirme (Scaling) ---
root = tk.Tk()
root.title("SmartNav")
root.attributes("-topmost", True)
root.overrideredirect(True)

config_path, config = load_or_create_config()
res_setting = config.get("Display", "resolution", fallback="auto")
scale_setting = config.get("Display", "scale", fallback="auto")

# Ölçek Çarpanını Belirle
screen_width = root.winfo_screenwidth()
if scale_setting.lower() == "auto":
    scale_factor = 1.0
else:
    try:
        scale_factor = float(scale_setting)
    except ValueError:
        scale_factor = 1.0

# Pencere Boyutunu Belirle
if res_setting.lower() == "auto":
    win_w = int(240 * scale_factor)
    win_h = int(120 * scale_factor)
else:
    try:
        parts = res_setting.lower().split("x")
        win_w = int(parts[0])
        win_h = int(parts[1])
    except Exception:
        win_w = int(240 * scale_factor)
        win_h = int(120 * scale_factor)

root.geometry(f"{win_w}x{win_h}")

# Dinamik Font Boyutları
btn_font_size = int(28 * scale_factor)
title_font_size = int(12 * scale_factor)
if title_font_size < 8: title_font_size = 8

# --- Arayüz Çizimi ---
# Taşıma Çubuğu
title_bar = tk.Frame(root, bg="#595959", height=int(25 * scale_factor))
title_bar.pack(fill=tk.X)
title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)

# Taşıma Yazısı
title_label = tk.Label(title_bar, text=" SmartNav", bg="#595959", fg="white", font=("Arial", 10))
title_label.pack(side=tk.LEFT)
title_label.bind("<ButtonPress-1>", start_move)
title_label.bind("<B1-Motion>", do_move)

# Kapatma Butonu
close_btn = tk.Button(title_bar, text="✕", command=root.destroy, bg="#c0392b", fg="white", bd=0, font=("Arial", title_font_size, "bold"))
close_btn.pack(side=tk.RIGHT, padx=int(5 * scale_factor))

# Ayarlar (Gear) Butonu
config_btn = tk.Button(title_bar, text="⚙", command=open_config_file, bg="#7f8c8d", fg="white", bd=0, font=("Arial", title_font_size, "bold"))
config_btn.pack(side=tk.RIGHT, padx=int(5 * scale_factor))

# Gezinme Butonları
frame = tk.Frame(root, bg="#ecf0f1")
frame.pack(expand=True, fill=tk.BOTH)

tk.Button(frame, text="◀", font=("Arial", btn_font_size), command=lambda: send_key("left")).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
tk.Button(frame, text="▶", font=("Arial", btn_font_size), command=lambda: send_key("right")).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

root.mainloop()