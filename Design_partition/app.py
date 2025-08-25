#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Garden Plan Visualization Script (app.py)

Version: 3.0 (Robust & Format-Agnostic)
Description:
  - Reads both YAML and JSON configuration files.
  - Implements a defensive validation system that automatically fixes common
    errors (e.g., missing sections) and gracefully handles invalid values
    (e.g., unknown style presets), providing clear feedback to the user.
"""

import argparse
import sys
import yaml
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager

# ==============================================================================
# 样式预设库 (Style Presets Library)
# ==============================================================================
STYLE_PRESETS = {
    "default": {
        "facecolor": "#EAEAEA", "edgecolor": "#BDBDBD", "linewidth": 1, "alpha": 0.8,
    },
    "house": {
        "facecolor": "#C5B4A5", "edgecolor": "#8D8D8D", "linewidth": 0.5, "label": "住宅 / House"
    },
    "zen_garden": {
        "facecolor": "#EAE8E4", "edgecolor": "#A0A0A0", "linewidth": 1.5,
        "hatch": "...", "hatch_color": "#BDBDBD"
    },
    "lawn": {
        "facecolor": "#C4D6A4", "edgecolor": "#7E9C6B", "linewidth": 2, "linestyle": "--",
        "hatch": "...", "hatch_color": "#AEC08D", "border_radius": 0.05,
    },
    "deck": {
        "facecolor": "#D3BFA8", "edgecolor": "#8D7A68", "linewidth": 1.5,
        "hatch": "///", "hatch_color": "#AF9E8E", "border_radius": 0.03,
    },
    "water_feature": {
        "facecolor": "#B8D4E3", "edgecolor": "#7BA2B8", "linewidth": 1.5, "alpha": 0.7,
    },
    "path_stone": {
        "color": "#795548", "linestyle": ":", "linewidth": 3.5,
    },
    "feature_tree": {
        "facecolor": "#9CB89C", "edgecolor": "#6B8E6B", "alpha": 0.85,
    },
    "feature_lantern": {
        "facecolor": "#606060", "edgecolor": "#303030",
    },
    "label_style": {
        "font_size": 10, "font_color": "#2E2E2E",
        "box_bg_color": (1.0, 1.0, 1.0, 0.85), # Corrected tuple format
        "box_edge_color": (0.74, 0.74, 0.74, 0.9), # Corrected tuple format
    }
}

# ==============================================================================
# 默认配置模块 (Default Configuration Module)
# ==============================================================================
DEFAULTS = {
    "title": "Garden Plan (Auto-Generated)",
    "canvas": {"width": 1600, "height": 1000, "margin": 60, "bg_color": "#FDFBF8"},
    "house": {"rect": [0.0, 0.0, 1.0, 0.15]},
    "zones": [],
    "paths": [],
    "features": []
}

# ==============================================================================
# 字体 & 语言处理 (Font & Language Handling)
# ==============================================================================
CJK_CANDIDATES = [
    "Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "PingFang SC",
    "Hiragino Sans GB", "DengXian", "SimHei"
]

def pick_cjk_font():
    available = {f.name for f in font_manager.fontManager.ttflist}
    for font in CJK_CANDIDATES:
        if font in available: return font
    return None

def setup_fonts(label_mode):
    if label_mode in ("cn", "bilingual"):
        cjk_font = pick_cjk_font()
        if cjk_font:
            matplotlib.rcParams["font.family"] = "sans-serif"
            matplotlib.rcParams["font.sans-serif"] = [cjk_font, "DejaVu Sans"] # Corrected key
            return label_mode, f"[OK] Using CJK font: {cjk_font}"
        else:
            print("[WARN] No CJK font found. Auto-fallback to English-only labels.")
            return "en", "[WARN] Fallback to English labels."
    matplotlib.rcParams["font.family"] = "DejaVu Sans"
    return "en", "[OK] Using English-only labels."

# ==============================================================================
# 配置加载 (Configuration Loading)
# ==============================================================================
def load_cfg(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            if path.lower().endswith('.json'):
                return json.load(f)
            elif path.lower().endswith(('.yml', '.yaml')):
                return yaml.safe_load(f)
            else:
                raise SystemExit(f"[ERROR] Unsupported config file format: {path}. Use .json or .yaml.")
    except FileNotFoundError:
        raise SystemExit(f"[ERROR] Config file not found at: {path}")
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise SystemExit(f"[ERROR] Error parsing config file '{path}': {e}")

# ==============================================================================
# 验证与修复 (Validation & Auto-Fixing)
# ==============================================================================
def validate_and_fix_cfg(cfg: dict):
    if not isinstance(cfg, dict):
        return None, [], [], [f"Config file is invalid. Expected a dictionary (JSON object), but got {type(cfg).__name__}."]

    fixes, warnings, errors = [], [], []
    
    for key in ["title", "canvas", "house", "zones"]:
        if key not in cfg:
            cfg[key] = DEFAULTS[key]
            fixes.append(f"Top-level key '{key}' was missing. Added default values.")

    if "rect" not in cfg.get("house", {}):
        cfg.setdefault("house", {})["rect"] = DEFAULTS["house"]["rect"]
        fixes.append("'house' section was missing 'rect' key. Added a default.")
    
    for i, z in enumerate(cfg.get("zones", [])):
        preset = z.get("style_preset")
        if preset not in STYLE_PRESETS:
            warnings.append(f"Zone '{z.get('id', i+1)}' has invalid style_preset: '{preset}'. Falling back to 'default'.")
            z["style_preset"] = "default"
        if "rect" not in z and "polygon" not in z:
            errors.append(f"Zone '{z.get('id', i+1)}' has no shape (missing 'rect' or 'polygon'). It will not be drawn.")
            
    return cfg, fixes, warnings, errors

# ==============================================================================
# 坐标换算 (Coordinate Conversion)
# ==============================================================================
def to_px(cfg, nx, ny):
    W, H = cfg["canvas"]["width"], cfg["canvas"]["height"]
    m = cfg["canvas"].get("margin", 40)
    return (m + nx * (W - 2 * m), m + ny * (H - 2 * m))

def size_px(cfg, nw, nh):
    W, H = cfg["canvas"]["width"], cfg["canvas"]["height"]
    m = cfg["canvas"].get("margin", 40)
    return (nw * (W - 2 * m), nh * (H - 2 * m))

# ==============================================================================
# 核心绘图函数 (Core Drawing Function)
# ==============================================================================
def draw(cfg, out_path: str, dpi: int, label_mode: str):
    label_mode, font_msg = setup_fonts(label_mode)
    print(font_msg)

    W, H = cfg["canvas"]["width"], cfg["canvas"]["height"]
    fig, ax = plt.subplots(figsize=(W / 100, H / 100), dpi=100)
    fig.patch.set_facecolor(cfg["canvas"].get("bg_color", "#FDFBF8"))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.set_aspect('equal', adjustable='box')
    ax.invert_yaxis()

    m = cfg["canvas"].get("margin", 40)
    ax.add_patch(patches.Rectangle((m, m), W - 2*m, H - 2*m, fill=False, edgecolor="#8D8D8D", linewidth=1.5))
    ax.text(W / 2, m / 2, cfg.get("title", ""), ha="center", va="center", fontsize=20, color="#2E2E2E", weight="bold")

    house_cfg = cfg.get("house", {})
    if "rect" in house_cfg:
        styles = STYLE_PRESETS["house"]
        hx, hy = to_px(cfg, *house_cfg["rect"][:2])
        hw, hh = size_px(cfg, *house_cfg["rect"][2:])
        ax.add_patch(patches.Rectangle((hx, hy), hw, hh, facecolor=styles["facecolor"], edgecolor=styles["edgecolor"], linewidth=styles["linewidth"]))
        ax.text(hx + hw / 2, hy + hh / 2, styles["label"], ha="center", va="center", color="#FFFFFF", fontsize=12, weight="bold")

    for z in cfg.get("zones", []):
        preset_name = z.get("style_preset", "default")
        styles = STYLE_PRESETS.get(preset_name, STYLE_PRESETS["default"]).copy()
        styles.update(z.get("style_override", {}))
        patch, label_pos = None, None

        if "rect" in z:
            zx, zy = to_px(cfg, *z["rect"][:2])
            zw, zh = size_px(cfg, *z["rect"][2:])
            radius = styles.get("border_radius", 0)
            if radius > 0:
                frame_w, _ = size_px(cfg, 1, 1)
                boxstyle = f"round,pad=0,rounding_size={radius * frame_w}"
                patch = patches.FancyBboxPatch((zx, zy), zw, zh, boxstyle=boxstyle)
            else:
                patch = patches.Rectangle((zx, zy), zw, zh)
            label_pos = (zx + zw / 2, zy + zh / 2)
        elif "polygon" in z:
            points_px = [to_px(cfg, *p) for p in z["polygon"]]
            patch = patches.Polygon(points_px, closed=True)
            cx = sum(p[0] for p in points_px) / len(points_px)
            cy = sum(p[1] for p in points_px) / len(points_px)
            label_pos = (cx, cy)
        
        if patch:
            patch.set_facecolor(styles.get("facecolor"))
            patch.set_edgecolor(styles.get("edgecolor"))
            patch.set_linewidth(styles.get("linewidth"))
            patch.set_linestyle(styles.get("linestyle", "-"))
            patch.set_alpha(styles.get("alpha", 1.0))
            if styles.get("hatch"):
                patch.set_hatch(styles["hatch"])
                patch.set_edgecolor(styles.get("hatch_color", styles.get("edgecolor")))
            ax.add_patch(patch)

        if label_pos:
            if label_mode == "bilingual": label = f"{z.get('name_cn', '')}\n{z.get('name_en', '')}"
            elif label_mode == "cn": label = f"{z.get('name_cn', '')}"
            else: label = f"{z.get('name_en', '')}"
            label_style = STYLE_PRESETS["label_style"]
            ax.text(label_pos[0], label_pos[1], label, ha="center", va="center", fontsize=label_style["font_size"], color=label_style["font_color"], linespacing=1.4, bbox=dict(boxstyle="round,pad=0.4", fc=label_style["box_bg_color"], ec=label_style["box_edge_color"]))

    for p in cfg.get("paths", []):
        if "points" not in p: continue
        styles = STYLE_PRESETS.get(p.get("style_preset", "path_stone")).copy()
        pts_px = [to_px(cfg, *pt) for pt in p["points"]]
        x_coords, y_coords = zip(*pts_px)
        ax.plot(x_coords, y_coords, color=styles["color"], linestyle=styles["linestyle"], linewidth=styles["linewidth"])

    for f in cfg.get("features", []):
        if "position" not in f or "size" not in f or "type" not in f: continue
        styles = STYLE_PRESETS.get(f.get("style_preset", "default")).copy()
        fx, fy = to_px(cfg, *f["position"])
        fw, _ = size_px(cfg, f["size"], f["size"])
        feature_patch = None
        if f["type"] == 'tree': feature_patch = patches.Circle((fx, fy), fw / 2)
        elif f["type"] == 'lantern': feature_patch = patches.Rectangle((fx - fw / 2, fy - fw / 2), fw, fw)
        if feature_patch:
            feature_patch.set_facecolor(styles["facecolor"])
            feature_patch.set_edgecolor(styles["edgecolor"])
            feature_patch.set_alpha(styles.get("alpha", 1.0))
            ax.add_patch(feature_patch)
            ax.text(fx, fy + fw, f.get("name_en", ""), ha="center", va="center", fontsize=8, color="#555")

    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_visible(False)
    
    plt.tight_layout(pad=0)
    plt.savefig(out_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"\n[SUCCESS] Garden plan saved to: {out_path}")

# ==============================================================================
# 主函数 (Main Function & CLI)
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Generate a garden plan from a JSON or YAML config.")
    parser.add_argument("--config", required=True, help="Path to the JSON or YAML configuration file.")
    parser.add_argument("--output", required=True, help="Path to save the output PNG image.")
    parser.add_argument("--dpi", type=int, default=250, help="Resolution of the output image in DPI.")
    parser.add_argument("--label-mode", choices=["bilingual", "en", "cn"], default="bilingual", help="Language for labels.")
    args = parser.parse_args()

    raw_cfg = load_cfg(args.config)
    cfg, fixes, warnings, errors = validate_and_fix_cfg(raw_cfg)

    if fixes:
        print("\n--- Auto-Fixes Applied ---")
        for f in fixes: print(f"[FIX] {f}")
    if warnings:
        print("\n--- Warnings ---")
        for w in warnings: print(f"[WARN] {w}")
    
    if errors:
        print("\n--- FATAL ERRORS ---")
        for e in errors: print(f"[ERROR] {e}")
        print("\nScript cannot continue due to fatal errors.")
        sys.exit(1)
    
    print("\n[OK] Configuration loaded and processed. Starting renderer...")
    
    draw(cfg, args.output, args.dpi, args.label_mode)

if __name__ == "__main__":
    main()