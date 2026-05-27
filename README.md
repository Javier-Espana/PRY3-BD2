# PRY3-BD2

Proyecto de rompecabezas con Neo4j: carga de rompecabezas desde formato TXT estandar y resolucion por BFS con soporte para piezas faltantes.

## Estructura

- `src/puzzle_app/`: codigo principal.
- `puzzles/`: archivos TXT de rompecabezas.
- `formato_rompecabezas.txt`: especificacion del formato.
- `main.py`: punto de entrada unico de la aplicacion.

## Configuracion

Definir variables de entorno para Neo4j (Aura o local):

- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`

Ejemplo:

```bash
export NEO4J_URI='neo4j+s://<tu-instancia>.databases.neo4j.io'
export NEO4J_USER='neo4j'
export NEO4J_PASSWORD='<tu-password>'
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar UI

```bash
python main.py
```

Desde la UI puedes:

1. Importar rompecabezas desde un `.txt`.
2. Elegir uno de los rompecabezas ya cargados.
3. Elegir pieza inicial.
4. Marcar piezas faltantes (una o varias).
5. Obtener instrucciones para armar lo maximo posible.
