import os, io, json, base64, logging
from typing import List, Dict, Any

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ---- 必须最先调用的 Streamlit 配置（修复你的报错）----
st.set_page_config(page_title="植物识别与标注（API/离线JSON）", layout="wide")

# ---------------- 日志与 .env（只打印一次） ----------------
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("plant-vision")

try:
    from dotenv import load_dotenv, find_dotenv
    if "_env_inited" not in st.session_state:
        load_dotenv(find_dotenv(), override=False)
        log.info(".env loaded")
        st.session_state["_env_inited"] = True
except Exception:
    pass

st.title("🌿 植物识别与标注（可切换 API / 手动 JSON）")

# ---------------- 模式与样式 ----------------
st.sidebar.header("模式")
use_manual_json = st.sidebar.checkbox("手动输入坐标 JSON（不调用 API）", value=True)

st.sidebar.header("通用配置")
marker_scale = st.sidebar.slider("标注大小（相对）", 2, 6, 3, 1)
marker_color = st.sidebar.color_picker("标注底色", "#4AC96E")
text_color   = st.sidebar.color_picker("标注数字颜色", "#FFFFFF")

# （占位）API 配置——以后你要接回多厂商时再用
if not use_manual_json:
    st.sidebar.header("模型提供方与 Key（仅 API 模式）")
    provider = st.sidebar.selectbox("提供方", ["openai", "anthropic", "gemini"], index=2)
    api_key  = st.sidebar.text_input(
        "API Key", type="password",
        value=(os.getenv("API_KEY")
               or os.getenv("OPENAI_API_KEY")
               or os.getenv("ANTHROPIC_API_KEY")
               or os.getenv("GEMINI_API_KEY")
               or "")
    )
    MODEL_CHOICES = {
        "openai":   ["gpt-5", "gpt-5-mini", "gpt-5-nano"],
        "anthropic":["claude-3.7-sonnet", "claude-3.7"],
        "gemini":   ["gemini-2.5-pro", "gemini-1.5-pro", "gemini-1.5-flash"],
    }
    model = st.sidebar.selectbox("模型", MODEL_CHOICES.get(provider, ["model"]), index=0)
    custom_model = st.sidebar.text_input("自定义模型名（可留空）", "")
    if custom_model.strip():
        model = custom_model.strip()
    force_cn     = st.sidebar.checkbox("中文名优先（仍返回英文）", True)
    detail_hint  = st.sidebar.selectbox("视觉细节提示", ["low", "medium", "high"], index=0)
    max_items_api= st.sidebar.slider("识别数量上限（API）", 3, 12, 6, 1)

# ---------------- 上传图片 ----------------
upload = st.file_uploader("上传花园/景观图片（JPG/PNG）", type=["jpg","jpeg","png"])

# ---------------- 手动 JSON + 文本输入 ----------------
manual_json_text_default = json.dumps({
    "items": [
        {"id": 1, "name_cn": "造型黄杨球", "name_en": "Topiary Boxwood", "reason": "球形修剪", "cx": 0.15, "cy": 0.42},
        {"id": 2, "name_cn": "绣球花",   "name_en": "Hydrangea",       "reason": "圆球花序", "cx": 0.35, "cy": 0.55},
        {"id": 3, "name_cn": "薰衣草(推测)", "name_en": "Lavender",     "reason": "穗状紫花", "cx": 0.58, "cy": 0.50}
    ]
}, ensure_ascii=False, indent=2)

manual_desc_text_default = (
    "• 结构以整形常绿灌木为骨架，搭配多簇绣球花；\n"
    "• 1. 造型黄杨球 / Topiary Boxwood — 球形修剪、常绿小叶；\n"
    "• 2. 绣球花 / Hydrangea — 圆球花序成团成片；\n"
    "• 3. 薰衣草(推测) / Lavender — 细叶、穗状紫花（推测）。"
)

uploaded_json_file = None
if use_manual_json:
    st.subheader("手动输入（文本 + JSON）")
    colj1, colj2 = st.columns([0.55, 0.45])
    with colj1:
        manual_desc_text = st.text_area("① 植物描述文本（展示在界面上）",
                                        value=manual_desc_text_default, height=180)
    with colj2:
        manual_json_text = st.text_area("② 坐标 JSON（结构：{'items':[...]}）",
                                        value=manual_json_text_default, height=180)
        uploaded_json_file = st.file_uploader("或上传 JSON 文件", type=["json"], key="json_upload")

# ---------------- 工具函数 ----------------
def parse_json_only(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("empty text")
    s = text.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s.startswith("json"): s = s[4:]
    return json.loads(s)

def norm_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items = items or []
    for i, it in enumerate(items):
        it["id"] = int(it.get("id", 0)) or (i + 1)
        it["cx"] = max(0.0, min(1.0, round(float(it.get("cx", 0.5)), 3)))
        it["cy"] = max(0.0, min(1.0, round(float(it.get("cy", 0.5)), 3)))
        it["name_cn"] = it.get("name_cn", "未知植物")
        it["name_en"] = it.get("name_en", "Unknown")
        it["reason"]  = it.get("reason", "")
    return items

def draw_markers(im: Image.Image, items: List[Dict[str,Any]], marker_scale=3,
                 fill_hex="#4AC96E", text_hex="#FFFFFF") -> Image.Image:
    out = im.convert("RGBA")
    W, H = out.size
    r = int(min(W, H) * (0.02 + (marker_scale - 3) * 0.005))

    def hex_rgba(h, a=235):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (a,)

    fill = hex_rgba(fill_hex, 235)
    txtc = tuple(int(text_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    draw = ImageDraw.Draw(out)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(r * 1.1))
    except Exception:
        font = ImageFont.load_default()

    def measure_text(d: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont):
        """兼容 Pillow>=10 的文字尺寸测量"""
        try:
            # Pillow 10+ 推荐
            bbox = d.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            try:
                # 旧版兼容
                return font.getsize(text)
            except Exception:
                # 兜底
                return len(text) * 10, 14

    for it in items:
        x, y = int(it["cx"] * W), int(it["cy"] * H)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)
        s = str(it["id"])
        tw, th = measure_text(draw, s, font)
        draw.text((x - tw / 2, y - th / 2 - r * 0.03), s, font=font, fill=txtc)

    return out


# ---------------- API 调用占位（以后接回多厂商实现） ----------------
def call_model_vision(*args, **kwargs):
    raise NotImplementedError("当前为手动 JSON 模式；若需启用 API，请切换侧边栏开关并实现此函数。")

# ---------------- 主渲染区 ----------------
col1, col2 = st.columns([0.62, 0.38])
with col1:
    if upload:
        img = Image.open(upload).convert("RGB")
        st.image(img, caption="原图预览", use_column_width=True)
    else:
        st.info("请上传一张 JPG/PNG 图片。")
with col2:
    st.write("输出")

btn_label = "根据手动 JSON 标注" if use_manual_json else "调用 API 并标注"
if st.button(btn_label, type="primary"):
    try:
        if not upload:
            st.error("请先上传图片。")
        else:
            img = Image.open(upload).convert("RGB")

            if use_manual_json:
                desc_text = manual_desc_text if 'manual_desc_text' in locals() else ""
                if uploaded_json_file is not None:
                    raw = uploaded_json_file.read().decode("utf-8")
                else:
                    raw = manual_json_text
                data = parse_json_only(raw)
                items = norm_items(data.get("items", []))
            else:
                result = call_model_vision()  # 以后接回
                items = result["items"]; desc_text = result.get("description","")

            df = pd.DataFrame(items, columns=["id","name_cn","name_en","reason","cx","cy"])
            annotated = draw_markers(img, items, marker_scale=marker_scale,
                                     fill_hex=marker_color, text_hex=text_color)

            st.subheader("标注结果")
            st.image(annotated, use_column_width=True, caption="标注后的图片")
            if desc_text:
                st.markdown("**植物描述**")
                st.write(desc_text)

            st.markdown("**JSON**")
            st.json({"items": items})
            st.dataframe(df, use_container_width=True)

            buf_png = io.BytesIO(); annotated.save(buf_png, format="PNG")
            st.download_button("下载标注图（PNG）", buf_png.getvalue(), "annotated.png", "image/png")
            st.download_button("下载识别JSON", json.dumps({"items": items}, ensure_ascii=False, indent=2).encode("utf-8"),
                               "plants.json", "application/json")
            st.download_button("下载表格（CSV）", df.to_csv(index=False).encode("utf-8-sig"),
                               "plants.csv", "text/csv")
    except Exception as e:
        st.error(f"出错：{e}")

# 首次加载提示一次
if "_app_logged" not in st.session_state:
    log.info("Streamlit app loaded. Open http://localhost:8501")
    st.session_state["_app_logged"] = True
