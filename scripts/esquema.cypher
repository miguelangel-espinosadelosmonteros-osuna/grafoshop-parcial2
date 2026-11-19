// Esquema de GrafoShop: restricciones de unicidad e índices.
// Neo4j no exige un esquema fijo, pero estas restricciones evitan duplicados
// y crean un índice para que buscar un nodo por su id sea rápido.

CREATE CONSTRAINT cliente_id IF NOT EXISTS
FOR (c:Cliente) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT cliente_email IF NOT EXISTS
FOR (c:Cliente) REQUIRE c.email IS UNIQUE;

CREATE CONSTRAINT producto_id IF NOT EXISTS
FOR (p:Producto) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT categoria_nombre IF NOT EXISTS
FOR (cat:Categoria) REQUIRE cat.nombre IS UNIQUE;

CREATE CONSTRAINT pedido_id IF NOT EXISTS
FOR (pe:Pedido) REQUIRE pe.id IS UNIQUE;

CREATE INDEX producto_nombre IF NOT EXISTS
FOR (p:Producto) ON (p.nombre);
