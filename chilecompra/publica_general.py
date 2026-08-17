import requests
import json

def obtener_licitacion(numero, ticket):
    url = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"

    params = {
        "estado": numero,
        "ticket": ticket
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # 🔹 Guardar en archivo JSON
        nombre_archivo = f"licitacion_{numero}.json"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"✅ Archivo guardado como: {nombre_archivo}")

    except requests.exceptions.Timeout:
        print("⏱️ Timeout: el servidor no respondió")

    except requests.exceptions.ConnectionError as e:
        print("🔌 Error de conexión:", e)

    except Exception as e:
        print("❌ Error general:", e)


# USO
obtener_licitacion(
    "publicada",
    "213B3ED9-EDAD-4C7D-AC36-F5CEE8E75CD7"
)