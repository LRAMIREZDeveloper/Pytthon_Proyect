import os
import re
import traceback
from typing import List, Dict
import pandas as pd
from PyPDF2 import PdfReader
 
# ----------------------------
# CONFIGURACIÓN
# ----------------------------
# Carpeta raíz que contiene los PDFs (si no se pasa argumento, usa la carpeta actual)
ROOT_DIR = "C:/Users/lramirez/Github/Pytthon_Proyect/PPU"
  
OUTPUT_XLSX = "Certificados_Anotaciones_Vigentes.xlsx"
LOG_CSV = "procesamiento_log.csv"

# ----------------------------
# HELPERS / EXTRACCIÓN
# ----------------------------
def read_pdf_text(path: str) -> str:
    """Lee todas las páginas del PDF y normaliza espacios."""
    reader = PdfReader(path)
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return re.sub(r"\s+", " ", full_text)
 
def get(pattern: str, text: str) -> str:
    """Busca la primera coincidencia del patrón y devuelve el grupo 1, sino vacío."""
    m = re.search(pattern, text, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""
 
def get_prev_owners(text: str) -> List[Dict[str, str]]:
    """
    Extrae bloque 'DATOS DE PROPIETARIOS ANTERIORES' y parsea múltiples propietarios.
    Formato esperado:
      Nombre : X
      R.U.T. : Y
      Repertorio : Z
      Número : N
      de fecha : DD-MM-AAAA
    """
    block_m = re.search(
        r"DATOS DE PROPIETARIOS ANTERIORES(.*?)(Sr\. usuario|FECHA EMISI[oó]N|Valor Pagado)",
        text, flags=re.IGNORECASE
    )
    block = block_m.group(1) if block_m else ""
    owners = []
    for m in re.finditer(
        r"Nombre\s*:\s*([^\n:]+?)\s*R\. ?U\. ?T\.\s*:\s*([0-9\.\-Kk]+)\s*Repertorio\s*:\s*([^\n:]+?)\s*N[úu]mero\s*:\s*([0-9\.]+)\s*de fecha\s*:\s*([0-9\-]+)",
        block, flags=re.IGNORECASE
    ):
        owners.append({
            "Nombre": m.group(1).strip(),
            "RUT": m.group(2).strip(),
            "Repertorio": m.group(3).strip(),
            "Número": m.group(4).strip(),
            "Fecha": m.group(5).strip(),
        })
    return owners
 
def get_subinscripciones(text: str) -> str:
    """Devuelve texto de SUBINSCRIPCIONES o ALTERACION DE CARACTERISTICAS si existen."""
    sub_m = re.search(
        r"SUBINSCRIPCIONES(.*?)(Sr\. usuario|FECHA EMISI[oó]N|Valor Pagado)",
        text, flags=re.IGNORECASE
    )
    if sub_m:
        return sub_m.group(0).strip()
    alt_m = re.search(
        r"ALTERACION DE CARACTERISTICAS(.*?)(Sr\. usuario|FECHA EMISI[oó]N|Valor Pagado)",
        text, flags=re.IGNORECASE
    )
    return alt_m.group(0).strip() if alt_m else ""
 
def fix_inscripcion(val: str) -> str:
    """Normaliza la inscripción al formato SERIE.NUMERO-DÍGITO (p.ej. SBGS.42-8)."""
    if not isinstance(val, str):
        return val
    m = re.search(r"([A-Z]{1,4})\.\s*([0-9]{1,6})\-([0-9A-Z])", val)
    return f"{m.group(1)}.{m.group(2)}-{m.group(3)}" if m else re.sub(r"\s+", "", val)
 
def clean_label_artifacts(df: pd.DataFrame) -> pd.DataFrame:
    """Quita etiquetas pegadas al valor (p.ej., 'Marca' con 'Modelo', etc.)."""
    repl = {
        'Tipo vehículo': [r'\s*Año$'],
        'Marca': [r'\s*Modelo$'],
        'Modelo': [r'\s*Nro\. Motor$'],
        'Color': [r'\s*Combustible$'],
        'Combustible': [r'\s*PBV$'],
        'Institución aseguradora': [r'\s*Numero poliza$'],
        'Oficina repertorio': [r'\s*N[úu]mero$', r'\s*Numero$'],
        'Oficina prop. anterior': [r'\s*N[úu]mero$', r'\s*Numero$'],
    }
    for col, patterns in repl.items():
        if col in df.columns:
            def _fix(x):
                if isinstance(x, str):
                    y = x
                    for pat in patterns:
                        y = re.sub(pat, '', y).strip()
                    return y
                return x
            df[col] = df[col].map(_fix)
    return df
 
def normalize_no_informado(df: pd.DataFrame) -> pd.DataFrame:
    for col in ['Combustible', 'PBV (Kilos)']:
        if col in df.columns:
            df[col] = df[col].replace({
                "(NO INFORMADO )": "(NO INFORMADO)",
                "(NO INFORMADO  )": "(NO INFORMADO)"
            }, regex=False)
    return df
 
def fix_vin_chasis_edge_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Arregla casos detectados (Maxus T60) donde VIN/Chasis arrastran texto extra."""
    if 'Inscripción' not in df.columns:
        return df
    mask_sckk = df['Inscripción'].isin(['SCKK.59-5', 'SCKK.60-9'])
    if mask_sckk.any():
        # Limpiar Nro. Vin si arrastra 'Color...'
        if 'Nro. Vin' in df.columns:
            df.loc[mask_sckk, 'Nro. Vin'] = df.loc[mask_sckk, 'Nro. Vin'].map(
                lambda v: re.sub(r"\s*Color.*$", "", v).strip() if isinstance(v, str) else v
            )
        # Si Chasis está más corto que VIN, usar VIN
        if 'Nº Chasis' in df.columns and 'Nro. Vin' in df.columns:
            def _fix(row):
                ch, vin = row['Nº Chasis'], row['Nro. Vin']
                if isinstance(ch, str) and isinstance(vin, str) and len(ch) < len(vin):
                    return vin
                return ch
            df.loc[mask_sckk, 'Nº Chasis'] = df.loc[mask_sckk].apply(_fix, axis=1)
        # Limpiar Chasis si arrastra 'Nro. Vin'
        if 'Nº Chasis' in df.columns:
            df.loc[mask_sckk, 'Nº Chasis'] = df.loc[mask_sckk, 'Nº Chasis'].map(
                lambda v: re.sub(r"\s*Nro\. Vin.*$", "", v).strip() if isinstance(v, str) else v
            )
    return df
 
# ----------------------------
# PIPELINE PRINCIPAL
# ----------------------------
def parse_pdf_to_row(path: str) -> Dict[str, str]:
    """Parsea un PDF y devuelve un diccionario con todas las columnas."""
    t = read_pdf_text(path)
 
    row = {
        "Archivo": os.path.basename(path),
        "Folio": get(r"FOLIO\s*:\s*([0-9\.]+)", t),
        "Código verificación": get(r"C[oó]digo Verificaci[oó]n\s*:\s*([a-z0-9]+)", t),
        "Inscripción": get(r"Inscripci[oó]n\s*:\s*([A-Z0-9\.\- ]+)", t),
        "Tipo vehículo": get(r"Tipo Veh[ií]culo\s*:\s*([A-ZÁÉÍÓÚÑ/\- ]+)", t),
        "Año": get(r"A[nñ]o\s*:\s*([0-9]{4})", t),
        "Marca": get(r"Marca\s*:\s*([A-Z0-9ÁÉÍÓÚÑ/\- ]+)", t),
        "Modelo": get(r"Modelo\s*:\s*([A-Z0-9\.\- ]+)", t),
        "Nº Motor": get(r"Nro\. Motor\s*:\s*([A-Z0-9\.\-]+)", t),
        "Nº Chasis": get(r"Nro\. Chasis\s*:\s*([A-Z0-9\.\- ]+)", t),
        "Nº Serie": get(r"Nro\. Serie\s*:\s*([A-Z0-9\.\-]+)", t),
        "Nro. Vin": get(r"Nro\. Vin\s*:\s*([A-Z0-9\.\- ]+)", t),
        "Color": get(r"Color\s*:\s*([A-ZÁÉÍÓÚÑ ]+|\(NO INFORMADO\))", t),
        "Combustible": get(r"Combustible\s*:\s*([A-ZÁÉÍÓÚÑ ]+|\(NO INFORMADO\))", t),
        "PBV (Kilos)": get(r"PBV\s*:\s*([0-9\., ]+ KILOS|\(NO INFORMADO\))", t),
        "Institución aseguradora": get(r"Instit\. aseg\.\s*:\s*([A-Z0-9ÁÉÍÓÚÑ\.\- ]+|NO REGISTRA SEGURO OBLIGATORIO VIGENTE)", t),
        "Nº póliza": get(r"Numero poliza\s*:\s*([0-9\.]+)", t),
        "Venc. póliza": get(r"Fec\. ven\. pol\.\s*:\s*([0-9\-]+)", t),
        "Propietario": get(r"Nombre\s*:\s*([A-Z0-9ÁÉÍÓÚÑ\.\- ]+?)\s+R\. ?U\. ?T\.", t),
        "RUT Propietario": get(r"R\. ?U\. ?T\.\s*:\s*([0-9\.\-Kk]+)", t),
        "Fecha adquisición": get(r"Fec\. adquisici[oó]n\s*:\s*([0-9\-]+)", t),
        "Oficina repertorio": get(r"Repertorio\s*:\s*([A-ZÁÉÍÓÚÑ ]+)", t),
        "Nº repertorio": get(r"N[úu]mero\s*:\s*([0-9\.]+)", t),
        "Fecha repertorio": get(r"de fecha\s*:\s*([0-9\-]+)", t),
        "Limitaciones al dominio": get(r"LIMITACIONES AL DOMINIO\s*([A-ZÁÉÍÓÚÑ ]+ INCORPORADAS AL REGISTRO)", t),
        "Subinscripciones": get_subinscripciones(t),
        "Fecha emisión": get(r"FECHA EMISI[oó]N\s*:\s*([0-9]{1,2} [A-Za-zÁÉÍÓÚñ]+ [0-9]{4}, [0-9:]{4,5})", t),
    }
 
    # Normalizar inscripción
    row["Inscripción"] = fix_inscripcion(row["Inscripción"])
 
    # Propietarios anteriores (pueden ser varios)
    prev = get_prev_owners(t)
    row["Prop. anterior"] = " | ".join(o["Nombre"] for o in prev) if prev else ""
    row["RUT Prop. anterior"] = " | ".join(o["RUT"] for o in prev) if prev else ""
    row["Oficina prop. anterior"] = " | ".join(o["Repertorio"] for o in prev) if prev else ""
    row["Nº prop. anterior"] = " | ".join(o["Número"] for o in prev) if prev else ""
    row["Fecha prop. anterior"] = " | ".join(o["Fecha"] for o in prev) if prev else ""
 
    return row
 
# ----------------------------
# PROCESAMIENTO MASIVO
# ----------------------------
def find_all_pdfs(root: str) -> List[str]:
    """Encuentra todos los .pdf (insensible a mayúsculas) en la carpeta y subcarpetas."""
    pdfs = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, fn))
    return sorted(pdfs)
 
def process_all(root: str):
    pdf_paths = find_all_pdfs(root)
    print(f"Encontrados {len(pdf_paths)} PDFs en: {root}")
 
    rows = []
    errors = []
 
    for i, path in enumerate(pdf_paths, 1):
        try:
            row = parse_pdf_to_row(path)
            rows.append(row)
        except Exception as e:
            errors.append({
                "archivo": os.path.basename(path),
                "ruta": path,
                "error": str(e),
                "trace": traceback.format_exc()
            })
        if i % 50 == 0:
            print(f"Procesados {i}/{len(pdf_paths)}...")
 
    df = pd.DataFrame(rows)
 
    # Limpiezas y normalizaciones
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df["Inscripción"] = df["Inscripción"].map(fix_inscripcion)
    df = clean_label_artifacts(df)
    df = normalize_no_informado(df)
    df = fix_vin_chasis_edge_cases(df)
 
    # Guardar Excel principal
    df.to_excel(OUTPUT_XLSX, index=False, engine="openpyxl")
    print(f"Excel generado: {OUTPUT_XLSX} (filas: {len(df)})")
 
    # Crear hoja "Resumen" (KPIs + alertas) usando openpyxl a través de pandas (simple)
    # Cálculos rápidos:
    resumen = {}
 
    # Conteos básicos
    resumen["Total certificados"] = len(df)
    resumen["Por tipo de vehículo"] = df["Tipo vehículo"].value_counts(dropna=False).to_dict() if "Tipo vehículo" in df.columns else {}
    resumen["Por marca"] = df["Marca"].value_counts(dropna=False).to_dict() if "Marca" in df.columns else {}
    resumen["Años (frecuencia)"] = df["Año"].value_counts(dropna=False).to_dict() if "Año" in df.columns else {}
 
    # Pólizas
    def estado_pol(venc):
        # Formato esperado DD-MM-AAAA; aquí solo marcamos texto, no convertimos a fecha real por simplicidad
        if not isinstance(venc, str) or not venc:
            return "Sin información"
        return "Con vencimiento informado"
    df["Estado póliza"] = df["Venc. póliza"].map(estado_pol) if "Venc. póliza" in df.columns else "Sin información"
 
    resumen["Estado póliza (conteo)"] = df["Estado póliza"].value_counts(dropna=False).to_dict() if "Estado póliza" in df.columns else {}
 
    # Alertas “NO INFORMADO”
    for col in ["Combustible", "PBV (Kilos)"]:
        if col in df.columns:
            resumen[f"{col} = (NO INFORMADO)"] = int((df[col] == "(NO INFORMADO)").sum())
 
    # Subinscripciones presentes
    if "Subinscripciones" in df.columns:
        resumen["Con subinscripciones"] = int(df["Subinscripciones"].astype(str).str.len().gt(0).sum())
 
    # Guardar hoja 'Resumen' en el mismo archivo (nueva hoja)
    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        # Tabla resumen general
        pd.DataFrame(
            [{"Métrica": k, "Valor": str(v)} for k, v in resumen.items()]
        ).to_excel(writer, sheet_name="Resumen", index=False)
 
        # (Opcional) Detalle por tipo / marca / año
        if "Tipo vehículo" in df.columns:
            df.groupby("Tipo vehículo").size().reset_index(name="Cantidad").to_excel(writer, sheet_name="Por_Tipo", index=False)
        if "Marca" in df.columns:
            df.groupby("Marca").size().reset_index(name="Cantidad").to_excel(writer, sheet_name="Por_Marca", index=False)
        if "Año" in df.columns:
            df.groupby("Año").size().reset_index(name="Cantidad").to_excel(writer, sheet_name="Por_Año", index=False)
 
        # (Opcional) Semáforo póliza simplificado
        df[["Archivo", "Institución aseguradora", "Nº póliza", "Venc. póliza"]].to_excel(writer, sheet_name="Polizas", index=False)
 
    # Guardar log si hubo errores
    if errors:
        pd.DataFrame(errors).to_csv(LOG_CSV, index=False)
        print(f"Se generó log de incidencias: {LOG_CSV} (errores: {len(errors)})")
    else:
        # Crear un log vacío igualmente para control
        pd.DataFrame(columns=["archivo", "ruta", "error", "trace"]).to_csv(LOG_CSV, index=False)
        print(f"Log de incidencias sin errores: {LOG_CSV}")
 
if __name__ == "__main__":
    print(f"Procesando PDFs en: {ROOT_DIR}")
    process_all(ROOT_DIR)
    print("Terminado.")