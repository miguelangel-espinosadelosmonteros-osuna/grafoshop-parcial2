"""Datos de ejemplo para poblar la base (los usa scripts/seed.py).

Los pedidos están escritos a mano para que los clientes formen grupos con
gustos parecidos (oficina, gamers, fotografía y casa inteligente) y las
recomendaciones tengan sentido durante la demostración.
"""

# (id, nombre, categoría, precio en MXN, stock)
PRODUCTOS = [
    ("P001", "Laptop Ultrabook 14 pulgadas", "Laptops", 18999.0, 12),
    ("P002", "Laptop Gamer 16 pulgadas", "Laptops", 32999.0, 6),
    ("P003", "Mouse inalámbrico", "Periféricos", 449.0, 60),
    ("P004", "Teclado mecánico", "Periféricos", 1599.0, 35),
    ("P005", "Monitor 27 pulgadas 4K", "Periféricos", 7499.0, 14),
    ("P006", "Base enfriadora", "Accesorios", 599.0, 40),
    ("P007", "Mochila para laptop", "Accesorios", 899.0, 30),
    ("P008", "Hub USB-C 7 en 1", "Accesorios", 749.0, 45),
    ("P009", "Audífonos Bluetooth", "Audio", 1299.0, 50),
    ("P010", "Headset gamer", "Audio", 1799.0, 25),
    ("P011", "Bocina portátil", "Audio", 999.0, 40),
    ("P012", "Barra de sonido", "Audio", 3499.0, 10),
    ("P013", "Consola de videojuegos", "Gaming", 11999.0, 9),
    ("P014", "Control inalámbrico", "Gaming", 1399.0, 30),
    ("P015", "Silla gamer", "Gaming", 4999.0, 8),
    ("P016", "Mousepad XL", "Gaming", 349.0, 70),
    ("P017", "Cámara mirrorless", "Fotografía", 21999.0, 5),
    ("P018", "Tripié de aluminio", "Fotografía", 899.0, 20),
    ("P019", "Tarjeta SD 128 GB", "Fotografía", 399.0, 80),
    ("P020", "Aro de luz LED", "Fotografía", 649.0, 25),
    ("P021", "Foco inteligente", "Casa inteligente", 249.0, 100),
    ("P022", "Enchufe inteligente", "Casa inteligente", 299.0, 90),
    ("P023", "Asistente de voz", "Casa inteligente", 1199.0, 30),
    ("P024", "Cámara de seguridad WiFi", "Casa inteligente", 899.0, 22),
    ("P025", "Webcam Full HD", "Periféricos", 899.0, 3),
]

# (id, nombre, correo, ciudad)
CLIENTES = [
    ("C001", "Ana Torres", "ana.torres@correo.mx", "Mérida"),
    ("C002", "Luis Herrera", "luis.herrera@correo.mx", "Ciudad de México"),
    ("C003", "Sofía Ramírez", "sofia.ramirez@correo.mx", "Guadalajara"),
    ("C004", "Diego Castillo", "diego.castillo@correo.mx", "Monterrey"),
    ("C005", "Valeria Peña", "valeria.pena@correo.mx", "Mérida"),
    ("C006", "Carlos Mendoza", "carlos.mendoza@correo.mx", "Puebla"),
    ("C007", "Fernanda Ruiz", "fernanda.ruiz@correo.mx", "Querétaro"),
    ("C008", "Jorge Salazar", "jorge.salazar@correo.mx", "Cancún"),
    ("C009", "Daniela Ortiz", "daniela.ortiz@correo.mx", "Ciudad de México"),
    ("C010", "Andrés Navarro", "andres.navarro@correo.mx", "Mérida"),
    ("C011", "Paola Vega", "paola.vega@correo.mx", "Tijuana"),
    ("C012", "Emilio Cruz", "emilio.cruz@correo.mx", "Campeche"),
    # Cliente nuevo sin compras: sirve para probar el caso sin historial.
    ("C013", "Renata Solís", "renata.solis@correo.mx", "Mérida"),
]

# (cliente, hace cuántos días, [(producto, cantidad), ...])
PEDIDOS = [
    # Oficina
    ("C001", 58, [("P001", 1), ("P003", 1), ("P007", 1)]),
    ("C001", 30, [("P008", 1), ("P005", 1)]),
    ("C001", 6, [("P009", 1)]),
    ("C002", 51, [("P001", 1), ("P003", 1), ("P008", 1)]),
    ("C002", 20, [("P004", 1), ("P005", 1)]),
    ("C002", 5, [("P012", 1)]),
    ("C007", 44, [("P001", 1), ("P007", 1), ("P008", 1)]),
    ("C007", 12, [("P003", 1), ("P025", 1)]),
    ("C007", 2, [("P009", 1)]),
    ("C009", 39, [("P001", 1), ("P003", 1), ("P005", 1)]),
    ("C009", 15, [("P021", 4), ("P022", 2), ("P023", 1)]),
    # Gamers
    ("C004", 55, [("P002", 1), ("P006", 1), ("P016", 1)]),
    ("C004", 25, [("P004", 1), ("P010", 1)]),
    ("C004", 4, [("P015", 1)]),
    ("C006", 47, [("P013", 1), ("P014", 2)]),
    ("C006", 18, [("P010", 1), ("P016", 1)]),
    ("C006", 1, [("P011", 1), ("P012", 1)]),
    ("C010", 41, [("P013", 1), ("P014", 1), ("P010", 1)]),
    ("C010", 9, [("P015", 1), ("P004", 1)]),
    ("C008", 33, [("P002", 1), ("P006", 1), ("P004", 1)]),
    ("C008", 7, [("P014", 1), ("P016", 1)]),
    # Fotografía
    ("C003", 50, [("P017", 1), ("P019", 2), ("P018", 1)]),
    ("C003", 22, [("P020", 1), ("P001", 1)]),
    ("C005", 36, [("P017", 1), ("P019", 1)]),
    ("C005", 10, [("P009", 1), ("P020", 1)]),
    ("C011", 28, [("P018", 1), ("P020", 1), ("P019", 1)]),
    ("C011", 3, [("P009", 1), ("P011", 1)]),
    # Casa inteligente
    ("C012", 45, [("P021", 6), ("P022", 3)]),
    ("C012", 16, [("P023", 1), ("P024", 2)]),
    ("C012", 2, [("P011", 1)]),
]

# (cliente, producto, cantidad): carritos que ya vienen con algo.
CARRITOS = [
    ("C005", "P018", 1),
]
