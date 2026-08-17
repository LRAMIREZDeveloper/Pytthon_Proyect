

import json

# Leer archivo de Espada Sagrada
with open("cartas_espada_sagrada.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Filtrar: excluir aliados
no_aliados = [
    carta for carta in data
    if carta.get("tipo") != "Aliado"
]

# Guardar nuevo archivo
with open("no_aliados_espada_sagrada.json", "w", encoding="utf-8") as f:
    json.dump(no_aliados, f, ensure_ascii=False, indent=2)

print(f"Cartas no Aliado: {len(no_aliados)}")
