"""Run: python3 -m unittest -v
The X11 test is skipped unless an X server is available (e.g. xvfb-run python3 -m unittest)."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

import smartnav


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "sub", "config.ini")

    def tearDown(self):
        self.dir.cleanup()

    def test_creates_defaults(self):
        c = smartnav.load_config(self.path)
        self.assertTrue(os.path.exists(self.path))
        self.assertEqual(c.get("Keys", "next"), "Right")
        self.assertEqual(c.get("Display", "scale"), "auto")

    def test_old_config_gets_new_sections(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as f:
            f.write("[Display]\nresolution = 300x120\nscale = auto\n")
        c = smartnav.load_config(self.path)
        self.assertEqual(c.get("Display", "resolution"), "300x120")
        self.assertEqual(c.get("Keys", "previous"), "Left")
        self.assertEqual(c.get("Window", "x"), "")

    def test_saves_position(self):
        c = smartnav.load_config(self.path)
        c.set("Window", "x", "12")
        smartnav.save_config(c, self.path)
        self.assertEqual(smartnav.load_config(self.path).get("Window", "x"), "12")


class LayoutTest(unittest.TestCase):
    def test_scale(self):
        self.assertEqual(smartnav.scale_factor("auto", 1080), 1.0)
        self.assertEqual(smartnav.scale_factor("auto", 2160), 2.0)  # 4K tahta
        self.assertEqual(smartnav.scale_factor("auto", 768), 1.0)
        self.assertEqual(smartnav.scale_factor("1.5", 2160), 1.5)
        self.assertEqual(smartnav.scale_factor("abc", 1080), 1.0)
        self.assertEqual(smartnav.scale_factor("99", 1080), 4.0)

    def test_window_size(self):
        self.assertEqual(smartnav.window_size("auto", 2.0), (520, 260))
        self.assertEqual(smartnav.window_size("300x120", 2.0), (300, 120))
        self.assertEqual(smartnav.window_size("bad", 1.0), (260, 130))
        self.assertEqual(smartnav.window_size("10x10", 1.0), (260, 130))

    def test_window_position(self):
        self.assertEqual(smartnav.window_position("", "", (200, 100), (1920, 1080)), (1680, 900))
        self.assertEqual(smartnav.window_position("5000", "-30", (200, 100), (1920, 1080)), (1720, 0))
        self.assertEqual(smartnav.window_position("50", "60", (200, 100), (1920, 1080)), (50, 60))


class SenderTest(unittest.TestCase):
    def test_falls_back_to_xdotool(self):
        with mock.patch.object(smartnav.XTestSender, "__init__", side_effect=OSError), \
                mock.patch("shutil.which", return_value="/usr/bin/xdotool"), \
                mock.patch.dict(os.environ, {"XDG_SESSION_TYPE": "x11"}), \
                mock.patch("subprocess.run") as run:
            sender = smartnav.make_sender()
            self.assertIsInstance(sender, smartnav.XdotoolSender)
            sender.send("Right")
            run.assert_called_once_with(["xdotool", "key", "Right"], check=True)

    def test_none_when_nothing_works(self):
        with mock.patch.object(smartnav.XTestSender, "__init__", side_effect=OSError), \
                mock.patch("shutil.which", return_value=None):
            self.assertIsNone(smartnav.make_sender())

    def test_wayland_without_xwayland(self):
        with mock.patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland"}):
            os.environ.pop("DISPLAY", None)  # restored by patch.dict
            self.assertIsNone(smartnav.make_sender())


RECEIVER = """
import tkinter as tk, sys
r = tk.Tk(); r.geometry('200x100+0+0')
got = []
def key(e):
    got.append(e.keysym)
    if len(got) == 2:
        print(' '.join(got)); sys.stdout.flush(); r.destroy()
r.bind('<Key>', key)
r.after(200, lambda: (r.focus_force(), print('ready'), sys.stdout.flush()))
r.after(8000, r.destroy)
r.mainloop()
"""


@unittest.skipUnless(os.environ.get("DISPLAY") and os.environ.get("SMARTNAV_X_TEST"),
                     "set SMARTNAV_X_TEST=1 under xvfb-run to send real keys")
class XTestEndToEnd(unittest.TestCase):
    """Sends real key events to a focused Tk window on a (virtual) X server."""

    def check(self, sender):
        p = subprocess.Popen([sys.executable, "-c", RECEIVER], stdout=subprocess.PIPE, text=True)
        self.assertEqual(p.stdout.readline().strip(), "ready")
        time.sleep(0.3)
        sender.send("Left")
        sender.send("Right")
        out, _ = p.communicate(timeout=10)
        self.assertEqual(out.strip(), "Left Right")

    def test_xtest(self):
        self.check(smartnav.XTestSender())

    @unittest.skipUnless(shutil.which("xdotool"), "xdotool not installed")
    def test_xdotool(self):
        self.check(smartnav.XdotoolSender())


if __name__ == "__main__":
    unittest.main()
