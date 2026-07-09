#!/usr/bin/env python3
"""
Custom Hoodie Logo Maker
By BeatrixKiddo
"""

import json
import math
import os
import subprocess
import sys


def ensure_package(import_name, package_name):
    try:
        __import__(import_name)
    except ImportError:
        print(f"Installing {package_name}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=False)
        if result.returncode != 0:
            raise SystemExit(f"Could not install {package_name}. Run: {sys.executable} -m pip install {package_name}")


ensure_package("PIL", "pillow")
ensure_package("lzokay", "lzokay")

from PIL import Image, ImageTk
import lzokay
import tkinter as tk
from tkinter import messagebox, colorchooser

HERE = os.path.dirname(os.path.abspath(__file__))
BASES = os.path.join(HERE, "bases")
OUT = os.path.join(HERE, "out")
LOGOS = os.path.join(HERE, "logos")
PLACEMENTS_FILE = os.path.join(HERE, "placements.json")
SETTINGS_FILE = os.path.join(HERE, "settings.json")
BACK_LOGO = os.path.join(LOGOS, "back.png")
FRONT_LOGO = os.path.join(LOGOS, "front.png")

MOD_NAME = "Custom_Server_Hoodie"
CLASSNAME = "BK_Hoodie"
DISPLAY_NAME = "Server Hoodie"
DESCRIPTION = "Custom server hoodie - Mod by BeatrixKiddo"
MOD_ROOT = os.path.join(HERE, MOD_NAME)
MOD_DATA = os.path.join(MOD_ROOT, "data")
CARGO_X = 10
CARGO_Y = 5
DEFAULT_PLACEMENT = {
    "back": [0.065455, 0.169091, 0.240909, 0.56],
    "front": [0.5, 0.22, 0.555455, 0.338182],
    "back_rotate": 7.0,
    "front_rotate": 0.0,
}
GARMENTS = {
    # Optional overrides only. Any base file in bases\ that is NOT listed here
    # gets an auto-generated class inheriting Hoodie_Black (see default_garment).
    # Add an entry only when a garment needs a different parent class / addon,
    # },
}

def default_garment(stem):
    """
    Fallback for any base file not explicitly listed in GARMENTS.
    Every dropped-in base gets a class automatically. Parent defaults to the
    vanilla hoodie, which is a safe, dependency-free base that any retexture
    will at least load on. Override per-file in GARMENTS if a garment needs a
    different parent (e.g. a jacket from another mod).
    """
    cls = "BK_" + "".join(p.capitalize() for p in stem.split("_"))
    display = stem.replace("_", " ").title()
    return {
        "parent": "Hoodie_Black",
        "classname": cls,
        "display": display,
        "addons": ["DZ_Characters_Tops"],
    }
    
DEFAULT_SETTINGS = {"hoodie_color": [18, 19, 20, 255]}

IMAGETOPAA_CANDIDATES = [
    r"D:\SteamLibrary\steamapps\common\DayZ Tools\Bin\ImageToPAA\ImageToPAA.exe",
    r"C:\Program Files (x86)\Steam\steamapps\common\DayZ Tools\Bin\ImageToPAA\ImageToPAA.exe",
]

EXTS = (".paa", ".png", ".tga", ".jpg", ".jpeg")
PAA_FORMATS = {0xFF01: (1, 8), 0xFF03: (2, 16), 0xFF05: (3, 16)}
PICKER_MAX_W = 1100
PICKER_MAX_H = 850


def ensure_dirs():
    os.makedirs(BASES, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LOGOS, exist_ok=True)
    os.makedirs(MOD_DATA, exist_ok=True)


def write_config(files=None):
    ensure_dirs()
    if files is None:
        files = texture_files()

    # Unique base stems, in stable order.
    stems = []
    for f in files:
        s = clean_source_stem(f)
        if s not in stems:
            stems.append(s)

    garments = []
    for s in stems:
        g = dict(GARMENTS[s]) if s in GARMENTS else default_garment(s)
        garments.append((g, s))

    classnames = [g["classname"] for g, _ in garments]

    parents = []
    for g, _ in garments:
        if g["parent"] not in parents:
            parents.append(g["parent"])

    addons = ["DZ_Data"]
    for g, _ in garments:
        for a in g.get("addons", []):
            if a not in addons:
                addons.append(a)

    units_str = ", ".join(f'"{c}"' for c in classnames)
    addons_str = ", ".join(f'"{a}"' for a in addons)

    lines = []
    lines.append("class CfgPatches")
    lines.append("{")
    lines.append(f"    class {MOD_NAME}")
    lines.append("    {")
    lines.append(f"        units[] = {{{units_str}}};")
    lines.append("        weapons[] = {};")
    lines.append("        requiredVersion = 0.1;")
    lines.append(f"        requiredAddons[] = {{{addons_str}}};")
    lines.append("    };")
    lines.append("};")
    lines.append("")
    lines.append("class CfgVehicles")
    lines.append("{")
    for p in parents:
        lines.append(f"    class {p};")
    lines.append("")

    for g, stem in garments:
        ground = g.get("ground", r"\dz\characters\tops\data\hoodie_m_grd_black_co.paa")
        male = f"{MOD_NAME}\\data\\{stem}_m_co.paa"
        female = f"{MOD_NAME}\\data\\{stem}_f_co.paa"
        lines.append(f'    class {g["classname"]} : {g["parent"]}')
        lines.append("    {")
        lines.append("        scope = 2;")
        lines.append(f'        displayName = "SERVER HOODIE";')
        lines.append(f'        descriptionShort = "{DESCRIPTION}";')
        lines.append(f"        itemsCargoSize[] = {{{CARGO_X}, {CARGO_Y}}};")
lines.append("        hiddenSelectionsTextures[] =")
        lines.append("        {")
        lines.append('            "",')
        lines.append('            "",')
        lines.append('            "",')
        lines.append('            "",')
        lines.append(f'            "{ground}",')
        lines.append(f'            "{male}",')
        lines.append(f'            "{female}"')
        lines.append("        };")
        lines.append("    };")
        lines.append("")

    lines.append("};")
    config = "\n".join(lines) + "\n"

    path = os.path.join(MOD_ROOT, "config.cpp")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(config)
    return path


def write_types_xml():
    types = f'''<type name="{CLASSNAME}">
    <nominal>2</nominal>
    <lifetime>7200</lifetime>
    <restock>1800</restock>
    <min>1</min>
    <quantmin>-1</quantmin>
    <quantmax>-1</quantmax>
    <cost>100</cost>
    <flags count_in_cargo="0" count_in_hoarder="0" count_in_map="1" count_in_player="0" crafted="0" deloot="0"/>
    <category name="clothes"/>
    <usage name="Town"/>
</type>
'''
    path = os.path.join(HERE, "types.xml")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(types)
    return path


def load_settings():
    if not os.path.isfile(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)
        return settings
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def selected_hoodie_color():
    """
    Returns:
      None          -> keep/use the original base texture
      (r,g,b,255)   -> replace the source texture with selected solid color
    """
    settings = load_settings()
    color = settings.get("hoodie_color", DEFAULT_SETTINGS["hoodie_color"])

    if color is None:
        return None

    if not isinstance(color, list) or len(color) < 3:
        return None

    return tuple(int(v) for v in color[:3]) + (255,)


# def choose_hoodie_color():
#     from tkinter import colorchooser
#     root = tk.Tk()
#     root.withdraw()
#     current = selected_hoodie_color() or (18, 19, 20, 255)
#     current_hex = "#{:02x}{:02x}{:02x}".format(current[0], current[1], current[2])
#     picked = colorchooser.askcolor(color=current_hex, title="Choose Hoodie Color")
#     root.destroy()
#     if not picked or not picked[0]:
#         print("\nColor selection cancelled.")
#         return
#     r, g, b = [int(v) for v in picked[0]]
#     settings = load_settings()
#     settings["hoodie_color"] = [r, g, b, 255]
#     save_settings(settings)
#     print(f"\nSaved hoodie color: RGB({r}, {g}, {b})")
#     print("Run option 1 or 2 to rebuild the hoodie with this color.")

def _apply_hoodie_color(value):
    settings = load_settings()
    if value is None:
        settings["hoodie_color"] = ""   # matches your reset = normal base texture
        save_settings(settings)
        print("\nUsing the normal base texture from bases.")
        return
    r, g, b = [int(v) for v in value[:3]]
    settings["hoodie_color"] = [r, g, b, 255]
    save_settings(settings)
    print(f"\nSaved hoodie color: RGB({r}, {g}, {b})")
    print("Run Bake to rebuild the hoodie with this color.")


def _after_color_prompt(parent):
    """
    After a color is saved, ask the user what to do next:
    bake everything now, or pick a base to rely on first then bake.
    """
    files = texture_files()
    if not files:
        messagebox.showinfo("Color saved", "Color saved, but bases is empty so there is nothing to bake yet.", parent=parent)
        return

    choice = {"value": None}

    win = tk.Toplevel(parent)
    win.title("Color Saved")
    win.geometry("460x300")
    win.transient(parent)
    win.grab_set()

    bg = "#101214"
    fg = "#f2f2f2"
    muted = "#a9b0b8"
    accent = "#00d9ff"
    panel2 = "#20242a"

    win.configure(bg=bg)

    tk.Label(
        win, text="Color saved. What next?",
        bg=bg, fg=fg, font=("Arial", 16, "bold"),
    ).pack(anchor="w", padx=16, pady=(16, 4))

    tk.Label(
        win,
        text="Bake every file in bases now with the saved placement, or pick which base to rely on for placement first and then bake all.",
        bg=bg, fg=muted, wraplength=420, justify="left", font=("Arial", 10),
    ).pack(anchor="w", padx=16, pady=(0, 16))

    def pick(action):
        choice["value"] = action
        win.destroy()

    def styled(text, action, primary=False):
        b = "#00a6c8" if primary else panel2
        f = "#001014" if primary else fg
        tk.Button(
            win, text=text, command=lambda: pick(action),
            bg=b, fg=f, relief="flat", bd=0,
            font=("Arial", 11, "bold"), padx=14, pady=12,
            cursor="hand2", anchor="w",
        ).pack(fill="x", padx=16, pady=5)

    styled("Bake New Hoodie With Color (use saved placement)", "bake_saved", primary=True)
    styled("Pick Placement + Bake All", "pick_default")
    styled("Pick Base To Rely On + Bake All", "pick_manual")
    # styled("Do Nothing", "none")

    win.bind("<Escape>", lambda e: pick("none"))
    parent.wait_window(win)

    action = choice["value"]
    if action == "bake_saved":
        print("\n=== Bake With Saved Placement ===")
        placement = load_shared()
        if placement is None:
            messagebox.showinfo(
                "No saved placement",
                "There is no saved placement yet. Use 'Pick Base To Rely On' or 'Pick Placement' first.",
                parent=parent,
            )
            return
        bake_all(texture_files(), placement)
    elif action == "pick_manual":
        print("\n=== Pick Base To Rely On + Bake All ===")
        pick_any_sample_then_bake_all()
    elif action == "pick_default":
        print("\n=== Pick Placement + Bake All ===")
        pick_then_bake_all()
        
def choose_hoodie_color():
    """
    Styled color picker that matches choose_sample_manual.
    Reuses the existing GUI root via Toplevel (no second tk.Tk()).
    """
    presets = [
        ("Normal Base Texture", None),
        ("Black", [18, 19, 20]),
        ("Dark Charcoal", [28, 30, 32]),
        ("Grey", [80, 84, 86]),
        ("White", [220, 220, 215]),
        ("Olive", [73, 82, 56]),
        ("Tan", [128, 111, 78]),
        ("Brown", [75, 55, 38]),
        ("Red", [120, 25, 30]),
        ("Blue", [30, 55, 105]),
        ("Green", [38, 85, 48]),
        ("Custom color...", "custom"),
    ]

    parent = tk._default_root

    # Fallback for running from a terminal with no GUI root.
    if parent is None:
        print("\nChoose hoodie color mode:")
        for i, (label, _) in enumerate(presets, 1):
            print(f"  {i}. {label}")
        while True:
            answer = input(f"\nChoose 1-{len(presets)}: ").strip()
            try:
                n = int(answer)
                if 1 <= n <= len(presets):
                    label, value = presets[n - 1]
                    break
            except ValueError:
                pass
            print("Invalid number.")
        if value == "custom":
            print("Custom color needs the GUI. Cancelled.")
            return
        _apply_hoodie_color(value)
        return

    selected = {"done": False}

    win = tk.Toplevel(parent)
    win.title("Choose Hoodie Color")
    win.geometry("520x520")
    win.transient(parent)
    win.grab_set()

    bg = "#101214"
    panel = "#181b1f"
    fg = "#f2f2f2"
    muted = "#a9b0b8"
    accent = "#00d9ff"

    win.configure(bg=bg)

    tk.Label(
        win,
        text="Choose the hoodie color",
        bg=bg,
        fg=fg,
        font=("Arial", 16, "bold"),
    ).pack(anchor="w", padx=16, pady=(16, 4))

    tk.Label(
        win,
        text="Pick a preset, or 'Custom color...' for the full color wheel. 'Normal Base Texture' keeps the original bases texture.",
        bg=bg,
        fg=muted,
        wraplength=480,
        justify="left",
        font=("Arial", 10),
    ).pack(anchor="w", padx=16, pady=(0, 12))

    frame = tk.Frame(win, bg=panel, highlightthickness=1, highlightbackground="#303740")
    frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(
        frame,
        bg="#090a0c",
        fg=fg,
        selectbackground=accent,
        selectforeground="#001014",
        relief="flat",
        bd=0,
        font=("Consolas", 11),
        activestyle="none",
        yscrollcommand=scrollbar.set,
    )
    listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.config(command=listbox.yview)

    for label, value in presets:
        if value is None or value == "custom":
            listbox.insert("end", label)
        else:
            listbox.insert("end", f"{label}  RGB({value[0]}, {value[1]}, {value[2]})")

    listbox.selection_set(0)
    listbox.activate(0)

    buttons = tk.Frame(win, bg=bg)
    buttons.pack(fill="x", padx=16, pady=(0, 16))

    def ok(event=None):
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Choose Hoodie Color", "Pick a color first.", parent=win)
            return
        label, value = presets[selection[0]]

        if value == "custom":
            current = selected_hoodie_color() or (18, 19, 20)
            current_hex = "#{:02x}{:02x}{:02x}".format(current[0], current[1], current[2])
            picked = colorchooser.askcolor(color=current_hex, title="Custom Hoodie Color", parent=win)
            if not picked or not picked[0]:
                return  # keep the dialog open if they cancel the wheel
            value = [int(v) for v in picked[0]]

        _apply_hoodie_color(value)
        selected["done"] = True
        selected["value"] = value
        win.destroy()

    def cancel(event=None):
        win.destroy()

    tk.Button(
        buttons, text="OK", command=ok,
        bg=accent, fg="#001014", relief="flat",
        padx=18, pady=8, font=("Arial", 10, "bold"),
    ).pack(side="right", padx=(8, 0))

    tk.Button(
        buttons, text="Cancel", command=cancel,
        bg="#2b3139", fg=fg, relief="flat",
        padx=18, pady=8, font=("Arial", 10, "bold"),
    ).pack(side="right")

    listbox.bind("<Double-Button-1>", ok)
    win.bind("<Return>", ok)
    win.bind("<Escape>", cancel)

    parent.wait_window(win)

    if selected["done"]:
        _after_color_prompt(parent)
    else:
        print("\nColor selection cancelled.")

def reset_hoodie_color():
    settings = load_settings()
    settings["hoodie_color"] = ""
    save_settings(settings)
    print("\nHoodie resetted to its default texure.")


def reset_logo_rotation():
    save_shared(dict(DEFAULT_PLACEMENT), "DEFAULT_RESET")
    print("\nLogo placement and rotation reset to default.")
    
    
def find_imagetopaa():
    for path in IMAGETOPAA_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


def require_imagetopaa():
    exe = find_imagetopaa()
    if exe:
        return exe
    raise RuntimeError("ImageToPAA.exe was not found. Edit IMAGETOPAA_CANDIDATES near the top of the script.")


def texture_files():
    return sorted(f for f in os.listdir(BASES) if os.path.splitext(f)[1].lower() in EXTS)


def trim_transparent(image):
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    return image.crop(bbox) if bbox else image


def load_logo(path, name):
    if not os.path.isfile(path):
        raise RuntimeError(f"Missing {name}. Put it here: {path}")
    return trim_transparent(Image.open(path).convert("RGBA"))


def read_u16(data, pos):
    return data[pos] | (data[pos + 1] << 8)


def read_u24(data, pos):
    return data[pos] | (data[pos + 1] << 8) | (data[pos + 2] << 16)


def paa_to_image(path):
    with open(path, "rb") as f:
        data = f.read()
    if len(data) < 9:
        raise ValueError("PAA file is too small.")
    paa_type = read_u16(data, 0)
    if paa_type not in PAA_FORMATS:
        raise ValueError(f"Unsupported PAA format 0x{paa_type:04X}; expected DXT1, DXT3 or DXT5.")
    bcn_format, block_size = PAA_FORMATS[paa_type]
    pos = 2
    while pos + 4 <= len(data) and data[pos:pos + 4] == b"GGAT":
        if pos + 12 > len(data):
            raise ValueError("Broken PAA TAGG metadata.")
        tag_size = int.from_bytes(data[pos + 8:pos + 12], "little")
        pos += 12 + tag_size
    if pos + 9 > len(data):
        raise ValueError("PAA has no mipmap header.")
    pos += 2
    raw_w = read_u16(data, pos); pos += 2
    height = read_u16(data, pos); pos += 2
    stored_size = read_u24(data, pos); pos += 3
    compressed = bool(raw_w & 0x8000)
    width = raw_w & 0x7FFF
    if width <= 0 or height <= 0:
        raise ValueError("Invalid PAA dimensions.")
    if pos + stored_size > len(data):
        raise ValueError("PAA mipmap data is incomplete.")
    raw = data[pos:pos + stored_size]
    expected = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * block_size
    if compressed:
        raw = lzokay.decompress(raw, expected)
    if len(raw) < expected:
        raise ValueError("Decoded PAA data is incomplete.")
    return Image.frombytes("RGBA", (width, height), raw[:expected], "bcn", (bcn_format,))


def load_base(path):
    if path.lower().endswith(".paa"):
        return paa_to_image(path).convert("RGBA")
    return Image.open(path).convert("RGBA")


def load_shared():
    if not os.path.isfile(PLACEMENTS_FILE):
        return dict(DEFAULT_PLACEMENT)
    try:
        with open(PLACEMENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        placement = data.get("shared")
        if not placement or "back" not in placement or "front" not in placement:
            return dict(DEFAULT_PLACEMENT)
        placement.setdefault("back_rotate", 0)
        placement.setdefault("front_rotate", 0)
        return placement
    except Exception:
        return dict(DEFAULT_PLACEMENT)


def save_shared(placement, sample_name):
    with open(PLACEMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump({"shared": placement, "picked_from": sample_name}, f, indent=2)


def choose_sample(files):
    if "bk_hoodie_co.paa" in files:
        return "bk_hoodie_co.paa"
    print("\nChoose the file used only as the UV reference for the picker:")
    for i, name in enumerate(files, 1):
        print(f"  {i}. {name}")
    while True:
        answer = input(f"\nChoose 1-{len(files)} [Enter = 1]: ").strip()
        if not answer:
            return files[0]
        try:
            n = int(answer)
            if 1 <= n <= len(files):
                return files[n - 1]
        except ValueError:
            pass
        print("Invalid number.")


def choose_sample_manual(files):
    """
    GUI picker for selecting which file in bases should be used as the UV reference.
    No terminal input(), so the GUI will not freeze.
    """
    if not files:
        return None

    parent = tk._default_root

    # Fallback only for running from terminal without a Tk root.
    if parent is None:
        print("\nChoose which file to RELY ON as the UV reference for the picker:")
        for i, name in enumerate(files, 1):
            print(f"  {i}. {name}")

        while True:
            answer = input(f"\nChoose 1-{len(files)}: ").strip()
            try:
                n = int(answer)
                if 1 <= n <= len(files):
                    return files[n - 1]
            except ValueError:
                pass
            print("Invalid number.")

    selected = {"value": None}

    win = tk.Toplevel(parent)
    win.title("Select Base Texture")
    win.geometry("520x420")
    win.transient(parent)
    win.grab_set()

    bg = "#101214"
    panel = "#181b1f"
    fg = "#f2f2f2"
    muted = "#a9b0b8"
    accent = "#00d9ff"

    win.configure(bg=bg)

    tk.Label(
        win,
        text="Choose the base texture to rely on",
        bg=bg,
        fg=fg,
        font=("Arial", 16, "bold"),
    ).pack(anchor="w", padx=16, pady=(16, 4))

    tk.Label(
        win,
        text="This file is only used as the visual UV reference. The saved placement will apply to ALL files in bases.",
        bg=bg,
        fg=muted,
        wraplength=480,
        justify="left",
        font=("Arial", 10),
    ).pack(anchor="w", padx=16, pady=(0, 12))

    frame = tk.Frame(win, bg=panel, highlightthickness=1, highlightbackground="#303740")
    frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(
        frame,
        bg="#090a0c",
        fg=fg,
        selectbackground=accent,
        selectforeground="#001014",
        relief="flat",
        bd=0,
        font=("Consolas", 11),
        activestyle="none",
        yscrollcommand=scrollbar.set,
    )
    listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.config(command=listbox.yview)

    for name in files:
        listbox.insert("end", name)

    listbox.selection_set(0)
    listbox.activate(0)

    buttons = tk.Frame(win, bg=bg)
    buttons.pack(fill="x", padx=16, pady=(0, 16))

    def ok(event=None):
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Select Base Texture", "Choose one texture first.", parent=win)
            return
        selected["value"] = files[selection[0]]
        win.destroy()

    def cancel(event=None):
        selected["value"] = None
        win.destroy()

    tk.Button(
        buttons,
        text="OK",
        command=ok,
        bg=accent,
        fg="#001014",
        relief="flat",
        padx=18,
        pady=8,
        font=("Arial", 10, "bold"),
    ).pack(side="right", padx=(8, 0))

    tk.Button(
        buttons,
        text="Cancel",
        command=cancel,
        bg="#2b3139",
        fg=fg,
        relief="flat",
        padx=18,
        pady=8,
        font=("Arial", 10, "bold"),
    ).pack(side="right")

    listbox.bind("<Double-Button-1>", ok)
    win.bind("<Return>", ok)
    win.bind("<Escape>", cancel)

    parent.wait_window(win)
    return selected["value"]



def make_picker_preview_image(image):
    """
    Some DayZ/PAA textures have an alpha channel that makes the Tk preview appear
    blank/white even though the RGB texture data is there. For the picker only,
    force the texture to display opaque on a dark background.
    This does not change the final baked texture logic.
    """
    rgba = image.convert("RGBA")

    # If alpha is fully or mostly transparent, ignore it for the picker preview.
    alpha = rgba.getchannel("A")
    extrema = alpha.getextrema()

    if extrema == (0, 0) or extrema[1] < 32:
        r, g, b, a = rgba.split()
        alpha = Image.new("L", rgba.size, 255)
        rgba = Image.merge("RGBA", (r, g, b, alpha))

    bg = Image.new("RGBA", rgba.size, (55, 58, 62, 255))
    bg.alpha_composite(rgba)
    return bg.convert("RGB")


def pick_boxes(image, title):
    scale = min(PICKER_MAX_W / image.width, PICKER_MAX_H / image.height, 1.0)
    view_w = max(1, int(image.width * scale))
    view_h = max(1, int(image.height * scale))
    preview = image.convert("RGB").resize((view_w, view_h), Image.Resampling.LANCZOS)

    # Reuse the existing GUI root. A second tk.Tk() creates a separate Tcl
    # interpreter, and ImageTk.PhotoImage then binds to the wrong one, so the
    # canvas image never renders and the canvas stays blank/gray.
    parent = tk._default_root
    owns_root = parent is None
    root = tk.Tk() if owns_root else tk.Toplevel(parent)
    root.title(title)
    stage = [0]
    start = [None, None]
    active_rect = [None]
    result = {}
    angles = {"back": 0.0, "front": 0.0}
    fixed = []
    done = [False]
    names = ("back", "front")
    labels = ("BACK", "FRONT")
    colors = ("#ff2e2e", "#00e65a")
    msg = tk.StringVar(); size_msg = tk.StringVar()
    tk.Label(root, textvariable=msg, font=("Arial", 12, "bold")).pack(padx=12, pady=(12, 4))
    tk.Label(root, text=("Red = BACK logo | Green = FRONT logo | Box size controls logo size\n"
                         "After both boxes: Q/E rotate BACK | A/D rotate FRONT | Shift = 5°"), font=("Arial", 10), justify="center").pack(padx=12, pady=(0, 4))
    tk.Label(root, textvariable=size_msg, font=("Arial", 10)).pack(padx=12, pady=(0, 8))
    canvas = tk.Canvas(root, width=view_w, height=view_h, highlightthickness=0, bg="#373a3e")
    canvas.pack(padx=12, pady=(0, 12))
    tk_img = ImageTk.PhotoImage(preview, master=root)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img

    def refresh_message():
        if stage[0] == 0:
            msg.set("Draw the BACK logo box.")
        elif stage[0] == 1:
            msg.set("Draw the FRONT logo box.")
        else:
            msg.set("Rotate boxes with Q/E (BACK) and A/D (FRONT). Press ENTER to save or R to redraw.")

    def remove_active():
        if active_rect[0] is not None:
            canvas.delete(active_rect[0]); active_rect[0] = None

    def rotated_points(rect, angle):
        l, t, r, b = rect
        x1, y1 = l * view_w, t * view_h
        x2, y2 = r * view_w, b * view_h
        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        rad = math.radians(angle)
        cosv, sinv = math.cos(rad), math.sin(rad)
        pts = []
        for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            dx, dy = x - cx, y - cy
            pts.extend((cx + dx * cosv + dy * sinv, cy - dx * sinv + dy * cosv))
        return pts, cx, cy

    def clear_saved():
        for item in fixed:
            canvas.delete(item)
        fixed.clear()

    def draw_saved(key):
        idx = names.index(key)
        points, cx, cy = rotated_points(result[key], angles[key])
        fixed.extend([
            canvas.create_polygon(points, outline=colors[idx], fill="", width=4),
            canvas.create_text(cx, cy, text=f"{labels[idx]}\n{angles[key]:+.0f}°", fill=colors[idx], font=("Arial", 12, "bold"), justify="center"),
        ])

    def redraw_saved():
        clear_saved()
        for key in names:
            if key in result:
                draw_saved(key)

    def reset(event=None):
        result.clear(); angles["back"] = 0.0; angles["front"] = 0.0
        remove_active(); clear_saved(); stage[0] = 0; size_msg.set(""); refresh_message()

    def down(event):
        if stage[0] >= 2: return
        start[0], start[1] = event.x, event.y
        remove_active()
        active_rect[0] = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline=colors[stage[0]], width=4)

    def move(event):
        if active_rect[0] is None: return
        canvas.coords(active_rect[0], start[0], start[1], event.x, event.y)
        w = abs(event.x - start[0]) / view_w * 100
        h = abs(event.y - start[1]) / view_h * 100
        size_msg.set(f"{labels[stage[0]]}: {w:.1f}% wide × {h:.1f}% high")

    def up(event):
        if active_rect[0] is None or stage[0] >= 2: return
        x1, x2 = sorted((start[0], event.x)); y1, y2 = sorted((start[1], event.y))
        if x2 - x1 < 8 or y2 - y1 < 8:
            remove_active(); size_msg.set("Box too small. Draw again."); return
        key = names[stage[0]]
        result[key] = [round(x1 / view_w, 6), round(y1 / view_h, 6), round(x2 / view_w, 6), round(y2 / view_h, 6)]
        remove_active(); redraw_saved(); stage[0] += 1
        size_msg.set(f"BACK Q/E: {angles['back']:+.0f}°   |   FRONT A/D: {angles['front']:+.0f}°" if stage[0] == 2 else "Now draw the FRONT box.")
        refresh_message()

    def save(event=None):
        if "back" not in result or "front" not in result:
            size_msg.set("Draw both boxes first."); return
        done[0] = True; root.destroy()

    def on_key(event):
        key = event.keysym.lower()
        if key == "escape": root.destroy(); return
        if key == "r": reset(); return
        if key in ("return", "kp_enter"): save(); return
        if stage[0] < 2: return
        step = 5.0 if (event.state & 0x0001) else 1.0
        changed = None
        if key == "q": angles["back"] -= step; changed = "back"
        elif key == "e": angles["back"] += step; changed = "back"
        elif key == "a": angles["front"] -= step; changed = "front"
        elif key == "d": angles["front"] += step; changed = "front"
        if changed:
            angles[changed] = round(angles[changed], 1)
            redraw_saved()
            size_msg.set(f"BACK Q/E: {angles['back']:+.0f}°   |   FRONT A/D: {angles['front']:+.0f}°")

    canvas.bind("<ButtonPress-1>", down); canvas.bind("<B1-Motion>", move); canvas.bind("<ButtonRelease-1>", up)
    root.bind("<Key>", on_key)
    refresh_message(); root.focus_force()
    if owns_root:
        root.mainloop()
    else:
        root.grab_set(); parent.wait_window(root)
    if not done[0]: raise RuntimeError("Picker cancelled.")
    return {"back": result["back"], "front": result["front"], "back_rotate": angles["back"], "front_rotate": angles["front"]}


def apply_user_color(base_image):
    """
    If the user chose a color, rebuild the texture as that solid color.
    If no color is selected, keep the original base texture from bases\.
    """
    color = selected_hoodie_color()

    if color is None:
        return base_image.copy()

    return Image.new("RGBA", base_image.size, color)


def paste_fit(canvas, logo, rect, rotate=0):
    logo = trim_transparent(logo)
    if rotate:
        logo = logo.rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
        logo = trim_transparent(logo)
    l, t, r, b = rect
    W, H = canvas.size
    box_w = max(1, int((r - l) * W)); box_h = max(1, int((b - t) * H))
    scale = min(box_w / logo.width, box_h / logo.height)
    new_w = max(1, int(logo.width * scale)); new_h = max(1, int(logo.height * scale))
    resized = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)
    x = int(l * W) + (box_w - new_w) // 2; y = int(t * H) + (box_h - new_h) // 2
    canvas.alpha_composite(resized, (x, y))


def clean_source_stem(filename):
    stem = os.path.splitext(os.path.basename(filename))[0]
    for suffix in ("_m_co", "_f_co", "_co"):
        if stem.lower().endswith(suffix):
            return stem[:-len(suffix)]
    return stem


def write_paa_pair(image, source_filename, imagetopaa):
    ensure_dirs()
    base_name = clean_source_stem(source_filename)
    male_paa = os.path.join(MOD_DATA, f"{base_name}_m_co.paa")
    female_paa = os.path.join(MOD_DATA, f"{base_name}_f_co.paa")
    preview_png = os.path.join(OUT, base_name + ".png")
    temp_tga = os.path.join(OUT, base_name + "_build_temp.tga")
    image.convert("RGBA").save(preview_png)
    image.convert("RGBA").save(temp_tga)
    for dest in (male_paa, female_paa):
        if os.path.isfile(dest): os.remove(dest)
        result = subprocess.run([imagetopaa, temp_tga, dest], check=False)
        if result.returncode != 0 or not os.path.isfile(dest):
            raise RuntimeError(f"ImageToPAA failed while writing {os.path.basename(dest)}")
    if os.path.isfile(temp_tga): os.remove(temp_tga)
    return male_paa, female_paa, preview_png


def bake_all(files, placement):
    ensure_dirs()
    config_path = write_config(); types_path = write_types_xml()
    imagetopaa = require_imagetopaa()
    back = load_logo(BACK_LOGO, "logos/back.png")
    front = load_logo(FRONT_LOGO, "logos/front.png")
    color = selected_hoodie_color()

    print(f"\nConfig created: {config_path}")
    print(f"Types XML created: {types_path}")

    if color is None:
        print("Hoodie color: using ORIGINAL BASE TEXTURE from bases\\")
    else:
        print(f"Selected hoodie color: RGB{color[:3]}")

    print(f"\nBaking {len(files)} file(s) with the same user-selected positions...\n")
    failed = []
    for filename in files:
        try:
            base = load_base(os.path.join(BASES, filename))
            baked = apply_user_color(base)
            paste_fit(baked, back, placement["back"], placement.get("back_rotate", 0))
            paste_fit(baked, front, placement["front"], placement.get("front_rotate", 0))
            male_paa, female_paa, preview_png = write_paa_pair(baked, filename, imagetopaa)
            print(f"  OK: {filename}")
            print(f"      male:   {male_paa}")
            print(f"      female: {female_paa}")
            print(f"      preview:{preview_png}")
        except Exception as e:
            failed.append((filename, str(e))); print(f"  FAIL: {filename} -> {e}")
    print("\nFinished.")
    print(f"Final PAA files: {MOD_DATA}")
    print(f"Preview PNG files: {OUT}")
    if failed:
        print("\nFailed:")
        for filename, error in failed:
            print(f"  {filename}: {error}")


def bake_saved():
    files = texture_files()
    if not files:
        print("\nbases\\ is empty."); return
    placement = load_shared()
    if placement is None:
        print("\nNo saved positions. Use option 2 first."); return
    bake_all(files, placement)


def pick_then_bake_all():
    files = texture_files()
    if not files:
        print("\nbases\\ is empty."); return
    sample_name = choose_sample(files)
    try:
        sample = load_base(os.path.join(BASES, sample_name))
    except Exception as e:
        print(f"\nCould not open {sample_name}: {e}"); return
    print("\nDraw the red BACK box, then the green FRONT box.")
    print("After both boxes: Q/E rotate BACK, A/D rotate FRONT, Shift = 5 degrees.")
    print("After ENTER, every file in bases\\ will be baked immediately.\n")
    try:
        placement = pick_boxes(sample, f"Shared placement — {sample_name}")
    except Exception as e:
        print(f"\nNothing was baked: {e}"); return
    save_shared(placement, sample_name)
    print("\nSaved placement:")
    print(json.dumps(placement, indent=2))
    bake_all(files, placement)


def pick_any_sample_then_bake_all():
    """
    Advanced option:
      - user manually chooses which file in bases the picker should rely on
      - user draws/rotates BACK + FRONT once
      - script applies it to ALL files in bases
    """
    files = texture_files()

    if not files:
        print("\nbases\\ is empty.")
        return

    sample_name = choose_sample_manual(files)
    sample_path = os.path.join(BASES, sample_name)

    try:
        sample = load_base(sample_path)
    except Exception as error:
        print(f"\nCould not open {sample_name}: {error}")
        return

    print(f"\nUsing this file as UV reference: {sample_name}")
    print("Draw the red BACK box, then the green FRONT box.")
    print("After both boxes: Q/E rotate BACK, A/D rotate FRONT, Shift = 5 degrees.")
    print("After ENTER, the placement will be applied to ALL files in bases\\.\n")

    try:
        placement = pick_boxes(sample, f"Shared placement — {sample_name}")
    except Exception as error:
        print(f"\nNothing was baked: {error}")
        return

    save_shared(placement, sample_name)

    print("\nSaved placement:")
    print(json.dumps(placement, indent=2))

    bake_all(files, placement)


def reset_saved():
    if os.path.isfile(PLACEMENTS_FILE):
        os.remove(PLACEMENTS_FILE); print("\nSaved positions deleted.")
    else:
        print("\nNo saved positions exist.")


# ---------------------------------------------------------------------------
# GUI APP
# ---------------------------------------------------------------------------

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        if not message:
            return
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", message)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")
        self.text_widget.update_idletasks()

    def flush(self):
        pass


class CustomHoodieGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Hoodie Maker | By BeatrixKiddo")
        self.root.geometry("980x680")
        self.root.minsize(880, 600)

        self.bg = "#101214"
        self.panel = "#181b1f"
        self.panel2 = "#20242a"
        self.fg = "#f2f2f2"
        self.muted = "#a9b0b8"
        self.accent = "#00d9ff"

        self.root.configure(bg=self.bg)

        self.make_layout()
        self.refresh_status()

        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = TextRedirector(self.log)
        sys.stderr = TextRedirector(self.log)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        ensure_dirs()
        write_config()
        write_types_xml()

    def on_close(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.root.destroy()

    def make_layout(self):
        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=18, pady=(18, 10))

        tk.Label(
            header, text="CUSTOM HOODIE MAKER",
            bg=self.bg, fg=self.fg, font=("Arial", 26, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="GUI builder • logo placement • rotation picker • color mode • automatic config.cpp + PAA output",
            bg=self.bg, fg=self.accent, font=("Arial", 11)
        ).pack(anchor="w", pady=(3, 0))

        body = tk.Frame(self.root, bg=self.bg)
        body.pack(fill="both", expand=True, padx=18, pady=10)

        left = tk.Frame(body, bg=self.panel, highlightthickness=1, highlightbackground="#303740")
        left.pack(side="left", fill="y", padx=(0, 12))

        right = tk.Frame(body, bg=self.bg)
        right.pack(side="right", fill="both", expand=True)

        status_frame = tk.Frame(right, bg=self.panel, highlightthickness=1, highlightbackground="#303740")
        status_frame.pack(fill="x", pady=(0, 12))

        tk.Label(status_frame, text="Status", bg=self.panel, fg=self.fg, font=("Arial", 13, "bold")).pack(
            anchor="w", padx=14, pady=(12, 4)
        )

        self.status_text = tk.Label(
            status_frame, text="", bg=self.panel, fg=self.muted,
            justify="left", anchor="w", font=("Consolas", 10)
        )
        self.status_text.pack(fill="x", padx=14, pady=(0, 12))

        log_frame = tk.Frame(right, bg=self.panel, highlightthickness=1, highlightbackground="#303740")
        log_frame.pack(fill="both", expand=True)

        tk.Label(log_frame, text="Build Log", bg=self.panel, fg=self.fg, font=("Arial", 13, "bold")).pack(
            anchor="w", padx=14, pady=(12, 4)
        )

        self.log = tk.Text(
            log_frame, bg="#090a0c", fg="#d8f7ff", insertbackground=self.fg,
            relief="flat", height=20, font=("Consolas", 10),
            state="disabled", wrap="word"
        )
        self.log.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.add_button(left, "Bake With Saved Placement", self.run_bake_saved, primary=True)
        self.add_button(left, "Pick Placement + Bake All", self.run_pick_default)
        self.add_button(left, "Pick Base To Rely On + Bake All", self.run_pick_manual)
        self.add_separator(left)
        self.add_button(left, "Choose Hoodie Color", self.run_choose_color)
        self.add_button(left, "Reset To Base Texture", self.run_reset_color)
        self.add_button(left, "Reset Logo Placement + Rotation", self.run_reset_rotation)
        self.add_separator(left)
        self.add_button(left, "Reset Saved Placement", self.run_reset_placement)
        self.add_button(left, "Open Mod Data Folder", lambda: self.open_folder(MOD_DATA))
        self.add_button(left, "Open Output Preview Folder", lambda: self.open_folder(OUT))
        self.add_button(left, "Open Tool Folder", lambda: self.open_folder(HERE))
        self.add_separator(left)
        self.add_button(left, "Refresh Status", self.refresh_status)
        self.add_button(left, "Exit", self.on_close, danger=True)

        info = tk.Label(
            left,
            text=(
                "Required:\n"
                "  logos\\back.png\n"
                "  logos\\front.png\n"
                "  bases\\bk_hoodie_co.paa\n\n"
                "Pick Base To Rely On:\n"
                "choose any file in bases\\ as the UV\n"
                "reference, then apply that placement\n"
                "to every file in bases\\."
            ),
            bg=self.panel, fg=self.muted, justify="left", font=("Consolas", 9)
        )
        info.pack(fill="x", padx=14, pady=(12, 14))

    def add_separator(self, parent):
        tk.Frame(parent, bg="#303740", height=1).pack(fill="x", padx=14, pady=10)

    def add_button(self, parent, text, command, primary=False, danger=False):
        if primary:
            bg, active, fg = "#00a6c8", "#00c7ef", "#001014"
        elif danger:
            bg, active, fg = "#5a1e22", "#7a282e", self.fg
        else:
            bg, active, fg = self.panel2, "#2b3139", self.fg

        btn = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=active, activeforeground=fg,
            relief="flat", bd=0, font=("Arial", 11, "bold"),
            padx=14, pady=10, cursor="hand2", anchor="w"
        )
        btn.pack(fill="x", padx=14, pady=5)
        return btn

    def refresh_status(self):
        ensure_dirs()
        files = texture_files()
        placement = load_shared()
        color = selected_hoodie_color()
        color_text = "NORMAL BASE TEXTURE" if color is None else f"RGB{color[:3]}"
        placement_text = "YES" if placement else "NO"
        imagetopaa = find_imagetopaa() or "NOT FOUND"

        self.status_text.configure(text="\n".join([
            f"Tool folder:        {HERE}",
            f"Base textures:      {len(files)} file(s) in bases\\",
            f"Saved placement:    {placement_text}",
            f"Hoodie color mode:  {color_text}",
            f"ImageToPAA:         {imagetopaa}",
            f"Mod data output:    {MOD_DATA}",
        ]))

    def run_bake_saved(self):
        print("\n=== Bake With Saved Placement ===")
        bake_saved()
        self.refresh_status()

    def run_pick_default(self):
        print("\n=== Pick Placement + Bake All ===")
        pick_then_bake_all()
        self.refresh_status()

    def run_pick_manual(self):
        print("\n=== Pick Base To Rely On + Bake All ===")
        pick_any_sample_then_bake_all()
        self.refresh_status()

    def run_choose_color(self):
        print("\n=== Choose Hoodie Color ===")
        choose_hoodie_color()
        self.refresh_status()

    def run_reset_color(self):
        print("\n=== Reset To Base Texture ===")
        reset_hoodie_color()
        self.refresh_status()

    def run_reset_rotation(self):
        print("\n=== Reset Logo Rotation ===")
        reset_logo_rotation()
        self.refresh_status()

    def run_reset_placement(self):
        print("\n=== Reset Saved Placement ===")
        reset_saved()
        self.refresh_status()

    def open_folder(self, path):
        os.makedirs(path, exist_ok=True)
        if hasattr(os, "startfile"):
            os.startfile(path)
        else:
            subprocess.run(["open", path], check=False)


def main():
    root = tk.Tk()
    CustomHoodieGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
