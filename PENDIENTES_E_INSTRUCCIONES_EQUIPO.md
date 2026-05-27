# Proyecto 03 - Estado, pendientes e instrucciones de equipo

Este documento compara lo implementado contra el enunciado de [Proyecto 03 - Elección de tecnologías de base de datos.pdf](Proyecto%2003%20-%20Elección%20de%20tecnologías%20de%20base%20de%20datos.pdf) y define que falta para entregar.

## 1) Verificacion contra el enunciado

1. Analizar caracteristicas de rompecabezas: PARCIAL
- Hay modelado general de piezas, conexiones y enlaces.
- Falta documentar analisis de los rompecabezas fisicos reales que recibio el equipo (observaciones/fotos/notas).

2. Diseñar modelo de datos escalable: CUMPLIDO (base tecnica)
- Implementado en Neo4j con nodos `Puzzle`, `Pieza`, `Conex` y relacion `ENLAZA`.
- Formato de carga estandar en [formato_rompecabezas.txt](formato_rompecabezas.txt).

3. Elegir tecnologia y justificar (SQL vs NoSQL): PENDIENTE DOCUMENTAL
- Codigo usa Neo4j (NoSQL grafo), pero falta documento formal de justificacion comparativa.

4. Implementar modelo y poblar base: CUMPLIDO (base tecnica)
- Se puede importar desde TXT usando la UI en [main.py](main.py).
- Falta cargar todos los rompecabezas reales del equipo.

5. Programa que arma desde cualquier pieza inicial: CUMPLIDO
- UI permite elegir puzzle, pieza inicial y generar pasos.
- BFS implementado en [src/puzzle_app/solver.py](src/puzzle_app/solver.py).

6. Manejo de piezas faltantes: CUMPLIDO FUNCIONAL, PENDIENTE AJUSTE DE INTERPRETACION
- Funcionalmente SI arma parcial cuando se declaran faltantes en la UI.
- Ojo: el enunciado dice "y esto se registra en la base de datos". Ahorita faltantes se registran en ejecucion (no persistente).
- Si el docente lo exige literal, hay que agregar persistencia de faltantes en Neo4j.

7. Preparar presentacion <= 15 min: PENDIENTE
- No hay presentacion en el repo.

8. Documentos a entregar (zip final): PENDIENTE PARCIAL
- Codigo fuente: SI.
- Documento de evidencias + justificacion: NO (pendiente).
- Presentacion: NO (pendiente).

## 2) Pendientes concretos para cerrar el proyecto

Prioridad alta:
1. Cargar en Neo4j Aura TODOS los rompecabezas reales del equipo (archivos en carpeta `puzzles/`).
2. Crear documento de evidencias (diagramas, capturas, fotos, pasos de replicacion, justificacion tecnica de Neo4j).
3. Preparar presentacion de 15 min con demo real.
4. Decidir si faltantes deben persistirse en BD:
- Opcion A: defender que se registran por sesion de armado (UI) y mostrarlo en demo.
- Opcion B: implementar persistencia (recomendado por literal del enunciado).

Prioridad media:
1. Agregar al menos 2 casos de prueba de demo:
- Caso sin faltantes.
- Caso con 1+ faltantes.
2. Afinar guion de exposicion por tiempos.

## 3) Instrucciones para conectar a Neo4j Aura (equipo)

1. Crear instancia AuraDB
- Entrar a Neo4j Aura y crear una instancia (Free sirve para proyecto).
- Guardar:
  - URI (formato `neo4j+s://...databases.neo4j.io`)
  - User (`neo4j`)
  - Password

2. Configurar variables de entorno (Linux/macOS)

```bash
export NEO4J_URI='neo4j+s://<tu-instancia>.databases.neo4j.io'
export NEO4J_USER='neo4j'
export NEO4J_PASSWORD='<tu-password>'
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
```

4. Ejecutar aplicacion

```bash
python main.py
```

5. Flujo de uso en la UI
1. Opcion 1: importar rompecabezas desde archivo TXT.
2. Opcion 2: resolver rompecabezas.
3. Elegir pieza inicial.
4. Declarar piezas faltantes (si aplica).
5. Mostrar instrucciones de armado parcial/completo.

## 4) Estructura esperada de archivos de rompecabezas

Usar como guia [formato_rompecabezas.txt](formato_rompecabezas.txt).

Reglas clave:
1. Secciones obligatorias: `[PUZZLE]`, `[PIEZAS]`, `[CONEXIONES]`, `[ENLACES]`.
2. En `[PIEZAS]` va solo el label de la pieza (una por linea).
3. En `[CONEXIONES]`: `pieza_label|numero_conexion|tipo`.
4. En `[ENLACES]`: `pieza_a|conexion_a|pieza_b|conexion_b`.
5. Cada enlace debe unir `MACHO` con `HEMBRA`.

## 5) Reparticion sugerida para companeros

1. Persona A: Documento de evidencias y justificacion tecnica (incluye comparacion Neo4j vs SQL).
2. Persona B: Carga de todos los rompecabezas a Aura y validacion de datos.
3. Persona C: Presentacion (diagrama del modelo + demo + conclusiones).
4. Persona D: Demo tecnica en vivo y control de tiempo.

## 6) Checklist de pre-entrega

1. Todos los rompecabezas del equipo cargados y verificados en Aura.
2. Demo sin faltantes funciona.
3. Demo con faltantes funciona.
4. Justificacion escrita y clara de eleccion de tecnologia.
5. Documento de evidencias completo.
6. Presentacion lista (<= 15 min).
7. ZIP final contiene: documento, codigo, presentacion.
