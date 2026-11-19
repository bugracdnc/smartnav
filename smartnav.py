#!/usr/bin/env python3
"""SmartNav: akıllı tahtalarda sunum/PDF gezinmesi için her zaman üstte duran ◀ ▶ düğmeleri.

Tuşlar X11 XTest ile gönderilir (libXtst, her X masaüstünde vardır); o yoksa xdotool denenir.
Ayarlar: ~/.config/smartnav/config.ini
"""
import configparser
import ctypes
import ctypes.util
import os
import shutil
import subprocess

__version__ = "1.0.0"

BASE_W, BASE_H = 260, 130  # 1080p ekrandaki boyut; daha büyük ekranlarda ölçeklenir

DEFAULTS = {
    "Display": {"resolution": "auto", "scale": "auto"},
    "Keys": {"previous": "Left", "next": "Right"},
    "Window": {"x": "", "y": ""},
}

COLORS = {
    "bar": "#1f2937", "bar_fg": "#e5e7eb", "bar_btn": "#374151", "close": "#dc2626",
    "btn": "#4f46e5", "btn_pressed": "#3730a3", "btn_fg": "#ffffff", "bg": "#111827",
    "error": "#fbbf24",
}


# ---------- Ayarlar ----------

def config_path():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "smartnav", "config.ini")


def load_config(path=None):
    """Ayar dosyasını okur; yoksa ya da eksik bölüm varsa varsayılanlarla tamamlayıp yazar."""
    path = path or config_path()
    config = configparser.ConfigParser()
    config.read_dict(DEFAULTS)
    existed = os.path.exists(path)
    if existed:
        config.read(path, encoding="utf-8")
    if not existed:
        save_config(config, path)
    return config


def save_config(config, path=None):
    path = path or config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        config.write(f)


def scale_factor(setting, screen_h):
    """'auto' -> ekran yüksekliği / 1080 (en az 1); aksi halde sayı (0.5-4 arası)."""
    if setting.strip().lower() != "auto":
        try:
            return min(max(float(setting), 0.5), 4.0)
        except ValueError:
            pass
    return max(1.0, screen_h / 1080)


def window_size(resolution, scale):
    """'auto' ya da '300x120' biçimindeki ayardan (genişlik, yükseklik)."""
    try:
        w, h = (int(p) for p in resolution.lower().split("x"))
        if w >= 80 and h >= 50:
            return w, h
    except ValueError:
        pass
    return int(BASE_W * scale), int(BASE_H * scale)


def window_position(x, y, size, screen):
    """Kayıtlı konumu ekrana sığdırır; kayıt yoksa sağ alt köşe."""
    (w, h), (sw, sh) = size, screen
    try:
        x, y = int(x), int(y)
    except ValueError:
        x, y = sw - w - 40, sh - h - 80
    return min(max(x, 0), max(sw - w, 0)), min(max(y, 0), max(sh - h, 0))


# ---------- Tuş gönderme ----------

class XTestSender:
    """libXtst ile tuş basar; ek paket gerektirmez."""

    def __init__(self):
        x11 = ctypes.cdll.LoadLibrary(ctypes.util.find_library("X11") or "libX11.so.6")
        xtst = ctypes.cdll.LoadLibrary(ctypes.util.find_library("Xtst") or "libXtst.so.6")
        x11.XOpenDisplay.restype = ctypes.c_void_p
        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x11.XStringToKeysym.restype = ctypes.c_ulong
        x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
        x11.XKeysymToKeycode.restype = ctypes.c_ubyte
        x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        x11.XFlush.argtypes = [ctypes.c_void_p]
        xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
        self.x11, self.xtst = x11, xtst
        self.display = x11.XOpenDisplay(None)
        if not self.display:
            raise OSError("X ekranı açılamadı")

    def send(self, keysym):
        code = self.x11.XKeysymToKeycode(self.display, self.x11.XStringToKeysym(keysym.encode()))
        if not code:
            raise ValueError(f"bilinmeyen tuş: {keysym}")
        self.xtst.XTestFakeKeyEvent(self.display, code, 1, 0)
        self.xtst.XTestFakeKeyEvent(self.display, code, 0, 0)
        self.x11.XFlush(self.display)


class XdotoolSender:
    def __init__(self):
        if not shutil.which("xdotool"):
            raise OSError("xdotool yok")

    def send(self, keysym):
        subprocess.run(["xdotool", "key", keysym], check=True)


def make_sender():
    """Çalışan ilk yöntemi döndürür; hiçbiri yoksa None."""
    if os.environ.get("XDG_SESSION_TYPE") == "wayland" and not os.environ.get("DISPLAY"):
        return None
    for cls in (XTestSender, XdotoolSender):
        try:
            return cls()
        except (OSError, ValueError):
            continue
    return None


# ---------- Arayüz ----------

def run():
    import tkinter as tk
    from tkinter import font as tkfont

    config = load_config()
    root = tk.Tk()
    root.title("SmartNav")
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.configure(bg=COLORS["bg"])

    screen = root.winfo_screenwidth(), root.winfo_screenheight()
    scale = scale_factor(config.get("Display", "scale"), screen[1])
    size = window_size(config.get("Display", "resolution"), scale)
    pos = window_position(config.get("Window", "x"), config.get("Window", "y"), size, screen)
    root.geometry(f"{size[0]}x{size[1]}+{pos[0]}+{pos[1]}")

    family = next((f for f in ("Noto Sans", "DejaVu Sans") if f in tkfont.families()), "TkDefaultFont")
    s = lambda n: max(1, int(n * scale))
    sender = make_sender()

    # Üst çubuk: tutup sürükleme, ayarlar, kapatma
    bar = tk.Frame(root, bg=COLORS["bar"], height=s(30))
    bar.pack(fill=tk.X)
    bar.pack_propagate(False)
    title = tk.Label(bar, text=" ⠿ SmartNav", bg=COLORS["bar"], fg=COLORS["bar_fg"], font=(family, s(10)))
    title.pack(side=tk.LEFT, fill=tk.Y)

    drag = {}

    def start_move(e):
        drag["x"], drag["y"] = e.x_root - root.winfo_x(), e.y_root - root.winfo_y()

    def do_move(e):
        root.geometry(f"+{e.x_root - drag['x']}+{e.y_root - drag['y']}")

    def stop_move(_):
        config.set("Window", "x", str(root.winfo_x()))
        config.set("Window", "y", str(root.winfo_y()))
        save_config(config)

    for w in (bar, title):
        w.bind("<ButtonPress-1>", start_move)
        w.bind("<B1-Motion>", do_move)
        w.bind("<ButtonRelease-1>", stop_move)

    def bar_button(text, bg, command):
        b = tk.Label(bar, text=text, bg=bg, fg="white", font=(family, s(12), "bold"), width=3, cursor="hand2")
        b.pack(side=tk.RIGHT, fill=tk.Y)
        b.bind("<ButtonRelease-1>", lambda e: command())
        return b

    bar_button("✕", COLORS["close"], root.destroy)
    bar_button("⚙", COLORS["bar_btn"], lambda: subprocess.Popen(["xdg-open", config_path()]))

    body = tk.Frame(root, bg=COLORS["bg"])
    body.pack(expand=True, fill=tk.BOTH, padx=s(4), pady=s(4))

    if sender is None:
        tk.Label(body, text="Tuş gönderilemiyor.\nX11 oturumu gerekli\n(Wayland desteklenmiyor).",
                 bg=COLORS["bg"], fg=COLORS["error"], font=(family, s(10)), justify=tk.CENTER
                 ).pack(expand=True, fill=tk.BOTH)
    else:
        # Label + basma rengi: tk.Button'dan daha düz görünür ve dokunmatikte anında tepki verir.
        def nav_button(text, keysym, side):
            b = tk.Label(body, text=text, bg=COLORS["btn"], fg=COLORS["btn_fg"], font=(family, s(30), "bold"),
                         cursor="hand2")
            b.pack(side=side, expand=True, fill=tk.BOTH, padx=s(2))
            b.bind("<ButtonPress-1>", lambda e: b.configure(bg=COLORS["btn_pressed"]))

            def release(e):
                b.configure(bg=COLORS["btn"])
                if 0 <= e.x < b.winfo_width() and 0 <= e.y < b.winfo_height():  # parmak düğmenin dışına kaydıysa gönderme
                    try:
                        sender.send(keysym)
                    except Exception as err:  # yanlış tuş adı vb.: çökme yerine düğmede göster
                        b.configure(text="!", bg=COLORS["close"])
                        print("smartnav:", err)

            b.bind("<ButtonRelease-1>", release)

        nav_button("◀", config.get("Keys", "previous"), tk.LEFT)
        nav_button("▶", config.get("Keys", "next"), tk.LEFT)

    root.mainloop()


if __name__ == "__main__":
    run()
