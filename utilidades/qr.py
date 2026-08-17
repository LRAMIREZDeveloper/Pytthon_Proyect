#!/usr/bin/env python3
# qr.py
import math
import qrcode
from PIL import Image, ImageOps, ImageDraw
import sys
import json
import os

def try_parse_arg(raw):
    """
    Intenta convertir 'raw' (sys.argv[1]) a dict:
    - si es ruta a archivo .json -> leerlo
    - intentar json.loads(raw)
    - si viene con comillas externas, remover y reintentar
    - intentar interpretar escapes unicode
    """
    # 1) si es ruta a archivo JSON
    if isinstance(raw, str) and os.path.exists(raw) and raw.lower().endswith('.json'):
        with open(raw, 'r', encoding='utf-8') as f:
            return json.load(f)

    # 2) intento directo
    try:
        return json.loads(raw)
    except Exception:
        pass

    # 3) quitar comillas externas y reintentar
    s = raw.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s2 = s[1:-1]
        try:
            return json.loads(s2)
        except Exception:
            # intentar des-escaped de comillas \" -> "
            s3 = s2.replace('\\"', '"').replace("\\'", "'")
            try:
                return json.loads(s3)
            except Exception:
                pass

    # 4) intentar decode unicode escapes (por problemas de encoding)
    try:
        s4 = bytes(raw, 'utf-8').decode('unicode_escape')
        return json.loads(s4)
    except Exception:
        pass

    # 5) falló todo
    raise ValueError(f"ERROR: el argumento no es JSON válido. Se recibió: {raw}")

def format_dict_pretty(d: dict, order: list = None) -> str:
    """
    Devuelve un string con formato 'CLAVE: VALOR' por línea.
    Si se proporciona 'order' (lista de claves) mantiene ese orden
    y luego agrega las claves restantes en orden natural.
    """
    lines = []
    if order:
        for k in order:
            if k in d:
                v = d[k]
                lines.append(f"{k}: {'' if v is None else v}")
    # Añadir claves restantes que no estaban en order
    for k in d:
        if order and k in order:
            continue
        v = d[k]
        lines.append(f"{k}: {'' if v is None else v}")
    return "\n".join(lines)

def generate_qr_around_logo_from_text(text: str,
                                      logo_path: str,
                                      out_path: str = "qr_con_texto.png",
                                      logo_scale: float = 0.30,
                                      box_size: int = 10,
                                      border: int = 4,
                                      error_correction=qrcode.constants.ERROR_CORRECT_H,
                                      min_logo_scale: float = 0.10):
    """
    Genera un QR construido alrededor del logo cuyo contenido es el texto `text`.
    Devuelve el texto que fue codificado (útil para debug).
    """
    # 1) Obtener la matriz del QR a partir del texto
    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    matrix_size = len(matrix)

    # 2) Cargar logo (verifica que exista)
    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo no encontrado en: {logo_path}")
    logo = Image.open(logo_path).convert("RGBA")

    # 3) Calcular tamaños
    qr_px = (matrix_size + 2 * border) * box_size
    desired_logo_px = int(qr_px * logo_scale)

    def resize_logo_to(px):
        w, h = logo.size
        scale = px / max(w, h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS
        return logo.copy().resize((new_w, new_h), resample=resample)

    logo_resized = resize_logo_to(desired_logo_px)

    # 4) Finder patterns (7x7 módulos)
    FINDER_SIZE = 7

    def modules_rect_to_px(mod_x, mod_y, mod_w, mod_h):
        x1 = (mod_x + border) * box_size
        y1 = (mod_y + border) * box_size
        x2 = x1 + mod_w * box_size
        y2 = y1 + mod_h * box_size
        return x1, y1, x2, y2

    def rects_intersect(r1, r2):
        x11, y11, x12, y12 = r1
        x21, y21, x22, y22 = r2
        return not (x12 <= x21 or x22 <= x11 or y12 <= y21 or y22 <= y11)

    def logo_rect_px(logo_img):
        lw, lh = logo_img.size
        x = (qr_px - lw) // 2
        y = (qr_px - lh) // 2
        return (x, y, x + lw, y + lh)

    finder_rects_px = []
    for fx, fy in [(0, 0), (matrix_size - FINDER_SIZE, 0), (0, matrix_size - FINDER_SIZE)]:
        finder_rects_px.append(modules_rect_to_px(fx, fy, FINDER_SIZE, FINDER_SIZE))

    # 5) Reducir logo si invade finders
    current_logo = logo_resized
    while True:
        lr = logo_rect_px(current_logo)
        overlap = any(rects_intersect(lr, fr) for fr in finder_rects_px)
        if not overlap:
            break
        logo_scale *= 0.90
        if logo_scale < min_logo_scale:
            raise ValueError("Logo demasiado grande. Reduce manualmente el tamaño o usa min_logo_scale menor.")
        desired_logo_px = int(qr_px * logo_scale)
        current_logo = resize_logo_to(desired_logo_px)

    logo_final = current_logo

    # 6) Construir la imagen del QR dibujando módulo por módulo, exceptuando el hueco del logo
    qr_img = Image.new("RGB", (qr_px, qr_px), "white")
    draw = ImageDraw.Draw(qr_img)
    logo_rect = logo_rect_px(logo_final)

    pad = max(1, int(box_size * 0.10))
    for r in range(matrix_size):
        for c in range(matrix_size):
            if not matrix[r][c]:
                continue
            x1 = (c + border) * box_size
            y1 = (r + border) * box_size
            x2 = x1 + box_size
            y2 = y1 + box_size
            module_rect_padded = (x1 - pad, y1 - pad, x2 + pad, y2 + pad)
            if rects_intersect(module_rect_padded, logo_rect):
                continue
            draw.rectangle([x1, y1, x2, y2], fill="black")

    # 7) Fondo blanco redondeado detrás del logo para contraste
    lw, lh = logo_final.size
    padding_px = max(3, int(min(lw, lh) * 0.10))
    bg_w, bg_h = lw + padding_px * 2, lh + padding_px * 2
    bg = Image.new("RGBA", (bg_w, bg_h), (255, 255, 255, 255))
    mask = Image.new("L", (bg_w, bg_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = int(min(bg_w, bg_h) * 0.12)
    mask_draw.rounded_rectangle([0, 0, bg_w, bg_h], radius=radius, fill=255)
    bg.putalpha(mask)
    bg.paste(logo_final, (padding_px, padding_px), logo_final)

    pos_x = (qr_px - bg_w) // 2
    pos_y = (qr_px - bg_h) // 2
    qr_img.paste(bg, (pos_x, pos_y), bg)

    # 8) Guardar
    qr_img.save(out_path)
    print(f"Guardado: {out_path} (logo_scale final: {logo_scale:.3f})")
    # devolver el texto codificado para debug
    return text

# -------------------------
# Uso desde sys.argv
# -------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: se espera el diccionario como JSON o la ruta a un .json en sys.argv[1].")
        sys.exit(1)

    raw = sys.argv[1]
    try:
        data = try_parse_arg(raw)
    except Exception as e:
        print(str(e))
        sys.exit(1)

    if not isinstance(data, dict):
        print("ERROR: se esperaba un diccionario JSON (object). Tipo recibido:", type(data))
        sys.exit(1)

    # Orden personalizado de campos (opcional)
    order = ["SERVICIO TÉCNICO", "PATENTE", "MARCA", "MODELO", "YEAR", "VIN", "FECHA OT", "ORDEN DE TRABAJO", "PAUTA PREVENTIVA", "KILOMETROS"]

    pretty_text = format_dict_pretty(data, order=order)

    # Muestra el texto que se codificó (útil para debugging)
    print("=== Texto que se codificará en el QR ===")
    print(pretty_text)

    # Generar QR (ajusta logo_path / out_path si hace falta)
    try:
        result_text = generate_qr_around_logo_from_text(
            text=pretty_text,
            logo_path="asset/image/logo.png",
            out_path="asset/image/qr.png",
            logo_scale=0.35,
            box_size=10,
            border=4
        )
        # imprimir el texto devuelto (igual a pretty_text)
        print("\nJSON/formato codificado:\n")
        sys.exit(0)
    except Exception as e:
        print("ERROR al generar QR:", e)
        sys.exit(2)
