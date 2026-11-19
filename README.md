# GrafoShop

Tienda en línea con recomendaciones de productos, hecha en Python y conectada a una base de datos de grafos **Neo4j AuraDB** en la nube.

Parcial 2 de Bases de Datos Avanzadas. Universidad Anáhuac Mayab.
Autor: Miguel Ángel Espinosa de los Monteros Osuna (00515042).

## Qué hace

- **CRUD completo** de productos y de clientes.
- **Carrito de compras**: el carrito es una relación entre el cliente y el producto.
- **Compra en una sola transacción**: crea el pedido, descuenta el stock y vacía el carrito. Si falta stock no se guarda nada.
- **Recomendaciones** con recorridos del grafo:
  - "Clientes como tú también compraron" (filtrado colaborativo).
  - "Se compra junto con" (productos del mismo pedido).
  - Sugerencias según lo que hay en el carrito.
  - Clientes con gustos parecidos (similitud de Jaccard).
- **Explorador del grafo**: camino más corto entre dos clientes y vecindad de un cliente, dibujados como grafo.
- Cada pantalla tiene un botón "Ver consulta Cypher" que muestra la consulta que se ejecutó.

## Requerimientos

- Python 3.10 o más reciente.
- Una instancia de Neo4j AuraDB (la versión Free es suficiente).
- Las librerías de `requirements.txt`:
  - `neo4j`: driver oficial de Neo4j para Python.
  - `streamlit`: interfaz web.
  - `python-dotenv`: lee las credenciales del archivo `.env`.
  - `pandas`: tablas de la interfaz.

## Instalación

1. Descargar o clonar el proyecto y entrar a la carpeta:

   ```bash
   cd grafoshop
   ```

2. Crear un entorno virtual e instalar las librerías:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Crear la instancia en la nube:
   - Entrar a <https://console.neo4j.io> e iniciar sesión.
   - Crear una instancia nueva de tipo **AuraDB Free**.
   - Descargar el archivo de credenciales que ofrece la consola al crearla. La contraseña solo se muestra en ese momento.

4. Configurar las credenciales. Copiar `.env.example` como `.env` y llenar los valores con los del archivo descargado:

   ```bash
   cp .env.example .env
   ```

   ```
   NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
   NEO4J_USERNAME=usuario-de-la-instancia
   NEO4J_PASSWORD=contraseña-de-la-instancia
   NEO4J_DATABASE=nombre-de-la-base
   ```

   El archivo `.env` está en `.gitignore`, así que las credenciales no se suben al repositorio.

5. Probar la conexión:

   ```bash
   python scripts/verificar_conexion.py
   ```

## Cargar los datos iniciales

```bash
python scripts/seed.py
```

El script crea las restricciones e índices de `scripts/esquema.cypher` y carga 25 productos, 7 categorías, 13 clientes y 30 pedidos.

Si la base ya tiene datos, el script no hace nada. Para borrar todo y volver a cargar:

```bash
python scripts/seed.py --reiniciar
```

**Cuidado:** `--reiniciar` borra todos los nodos y relaciones de la instancia.

## Ejecutar la aplicación

```bash
streamlit run app.py
```

Se abre en el navegador en `http://localhost:8501`. La interfaz corre en la computadora, pero todos los datos se leen y se guardan en AuraDB. La pantalla de Inicio muestra el servidor al que está conectada.

## Prueba de punta a punta

```bash
python scripts/prueba_flujo.py
```

Recorre el flujo completo contra la base real (CRUD, carrito, compra rechazada por falta de stock, compra correcta, recomendaciones y caminos) y al final borra lo que creó.

## Estructura del proyecto

```
grafoshop/
├── app.py                    Punto de entrada de Streamlit y menú
├── requirements.txt
├── .env.example              Plantilla de las variables de entorno
├── src/                      Lógica y acceso a datos (no depende de Streamlit)
│   ├── config.py             Lee las variables de entorno
│   ├── db.py                 Driver de Neo4j, lecturas, escrituras y transacciones
│   ├── errores.py            Error de reglas del negocio
│   ├── productos.py          CRUD de productos y categorías
│   ├── clientes.py           CRUD de clientes
│   ├── carrito.py            Carrito, compra e historial
│   ├── recomendaciones.py    Consultas de recomendación
│   └── grafo.py              Camino más corto, vecindad y totales
├── vistas/                   Pantallas de la interfaz
│   ├── comun.py              Tablas, selectores y dibujo del grafo
│   ├── inicio.py
│   ├── catalogo.py
│   ├── clientes.py
│   ├── carrito.py
│   ├── recomendaciones.py
│   └── explorador.py
└── scripts/
    ├── esquema.cypher        Restricciones e índices
    ├── datos_iniciales.py    Productos, clientes y pedidos de ejemplo
    ├── seed.py               Crea el esquema y carga los datos
    ├── verificar_conexion.py
    └── prueba_flujo.py
```

## Modelo del grafo

Nodos: `Cliente`, `Producto`, `Categoria`, `Pedido`.

Relaciones:

- `(Cliente)-[:TIENE_EN_CARRITO {cantidad, agregado}]->(Producto)`
- `(Cliente)-[:REALIZO]->(Pedido)`
- `(Pedido)-[:CONTIENE {cantidad, precio_unitario}]->(Producto)`
- `(Producto)-[:PERTENECE_A]->(Categoria)`

## Notas sobre AuraDB Free

- La instancia se pausa sola después de 3 días sin uso. Antes de usar la aplicación hay que entrar a la consola y reanudarla si aparece pausada.
- El cupo gratuito es de una instancia por cuenta.
