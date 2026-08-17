import requests
from openpyxl import Workbook

def obtener_licitaciones_excel(estado, ticket):
    url = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"

    params = {
        "estado": estado,
        "ticket": ticket
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("Cantidad", 0) == 0:
            print("No hay datos")
            return

        listado = data["Listado"]

        # 📊 Crear Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Licitaciones"

        # 🔹 Encabezados
        headers_excel = [
            "Codigo",
            "Nombre",
            "Estado",
            "FechaCierre"
        ]
        ws.append(headers_excel)

        # 🔹 Datos
        for lic in listado:
            fila = [
                lic.get("CodigoExterno"),
                lic.get("Nombre"),
                lic.get("CodigoEstado"),
                lic.get("FechaCierre")
            ]
            ws.append(fila)

        # 💾 Guardar archivo
        nombre_archivo = f"licitaciones_{estado}.xlsx"
        wb.save(nombre_archivo)

        print(f"✅ Excel generado: {nombre_archivo}")

    except requests.exceptions.Timeout:
        print("⏱️ Timeout")

    except requests.exceptions.ConnectionError as e:
        print("🔌 Error de conexión:", e)

    except Exception as e:
        print("❌ Error:", e)


# USO
obtener_licitaciones_excel(
    "publicada",
    "213B3ED9-EDAD-4C7D-AC36-F5CEE8E75CD7"
)