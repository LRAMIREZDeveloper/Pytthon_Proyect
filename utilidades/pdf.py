import fitz  # PyMuPDF

# Abrir el PDF
pdf = fitz.open("raciales.pdf")

for num_pagina in range(len(pdf)):
    pagina = pdf[num_pagina]
    imagenes = pagina.get_images(full=True)
    for idx, img in enumerate(imagenes):
        xref = img[0]
        pix = fitz.Pixmap(pdf, xref)
        if pix.n < 5:  # RGB o escala de grises
            pix.save(f"pagina{num_pagina+1}_img{idx+1}.png")
        else:  # CMYK
            pix = fitz.Pixmap(fitz.csRGB, pix)
            pix.save(f"pagina{num_pagina+1}_img{idx+1}.png")