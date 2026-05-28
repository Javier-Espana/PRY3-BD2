# Proyecto 3 — Elección de tecnologías de base de datos

Roberto Barreda, 23354
Javier España, 23361
Diego López, 23747
Ángel Esquit, 23221
Mia Fuentes, 23775
Anggelie Velásquez, 221181

---

## Requisitos

- Python 3.10+
- Cuenta en [Neo4j Aura](https://neo4j.com/cloud/aura/) (Free tier funciona)

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```
NEO4J_URI=neo4j+s://<instancia>.databases.neo4j.io
NEO4J_USERNAME=<usuario>
NEO4J_PASSWORD=<password>
```

## Instalación y ejecución

```bash
pip install -r requirements.txt
python main.py
```

## Uso

1. **Opción 1** — Importar rompecabezas desde un archivo `.txt` (ver `formato_rompecabezas.txt`)
2. **Opción 2** — Resolver: elegir rompecabezas, pieza inicial y piezas faltantes (se persisten en la BD)
3. **Opción 3** — Restaurar todas las piezas de un rompecabezas a disponible
