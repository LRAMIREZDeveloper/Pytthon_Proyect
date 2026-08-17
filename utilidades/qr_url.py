import qrcode
from PIL import Image, ImageDraw

def generate_qr_around_logo(url: str,
                            logo_path: str,
                            out_path: str = "qr_around_logo.png",
                            logo_scale: float = 0.35,   # 🔹 ahora más grande
                            box_size: int = 10,
                            border: int = 4,
                            error_correction=qrcode.constants.ERROR_CORRECT_H,
                            min_logo_scale: float = 0.10):
    """
    Genera un QR "construido alrededor" del logo (no dibuja módulos donde va el logo).
    Ajusta automáticamente logo_scale si el hueco invade los finder patterns.
    """

    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    matrix_size = len(matrix)

    logo = Image.open(logo_path).convert("RGBA")

    qr_px = (matrix_size + 2 * border) * box_size
    desired_logo_px = int(qr_px * logo_scale)

    def resize_logo_to(px):
        w, h = logo.size
        scale = px / max(w, h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        return logo.copy().resize((new_w, new_h), Image.LANCZOS)

    logo_resized = resize_logo_to(desired_logo_px)

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

    current_logo = logo_resized
    while True:
        lr = logo_rect_px(current_logo)
        overlap = any(rects_intersect(lr, fr) for fr in finder_rects_px)
        if not overlap:
            break
        logo_scale *= 0.90
        if logo_scale < min_logo_scale:
            raise ValueError("Logo demasiado grande. Reduce manualmente el tamaño.")
        desired_logo_px = int(qr_px * logo_scale)
        current_logo = resize_logo_to(desired_logo_px)

    logo_final = current_logo

    qr_img = Image.new("RGB", (qr_px, qr_px), "white")
    draw = ImageDraw.Draw(qr_img)
    logo_rect = logo_rect_px(logo_final)

    # 🔹 Menor margen para permitir logo más grande
    for r in range(matrix_size):
        for c in range(matrix_size):
            if not matrix[r][c]:
                continue
            x1 = (c + border) * box_size
            y1 = (r + border) * box_size
            x2 = x1 + box_size
            y2 = y1 + box_size
            module_rect = (x1, y1, x2, y2)
            pad = int(box_size * 0.10)  # 🔹 margen reducido
            module_rect_padded = (x1 - pad, y1 - pad, x2 + pad, y2 + pad)
            if rects_intersect(module_rect_padded, logo_rect):
                continue
            draw.rectangle(module_rect, fill="black")

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

    qr_img.save(out_path)
    print(f"✅ Guardado: {out_path} (logo_scale final: {logo_scale:.3f})")


# Ejemplo de uso
if __name__ == "__main__":
    generate_qr_around_logo(
        url="https://tsm.cl/certification/?id=T232446",
        logo_path="logo.png",
        out_path="qr_con_logo_grande.png",
        logo_scale=0.35,  # 🔹 puedes subir hasta 0.45
        box_size=10,
        border=4
    )
