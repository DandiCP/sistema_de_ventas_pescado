#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import datetime
import sys

DB_NAME = "ventas_pescado.db"

def limpiar_pantalla():
    print("\033[H\033[J", end="")

def inicializar_bd():
    """Crea la base de datos, la tabla y agrega la columna cantidad_peces si no existe."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Crear tabla si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                nombre_cliente TEXT,
                cantidad_libras REAL NOT NULL,
                cantidad_gramos REAL NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('venta', 'pedido')),
                total REAL NOT NULL
            )
        """)
        # Agregar columna cantidad_peces (opcional) si no existe
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN cantidad_peces INTEGER")
        except sqlite3.OperationalError:
            # La columna ya existe, ignorar
            pass
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def obtener_entero_positivo(mensaje):
    """Solicita un número entero positivo al usuario, con validación."""
    while True:
        try:
            valor = input(mensaje).strip()
            if not valor:
                print("El valor no puede estar vacío.")
                continue
            num = int(valor)
            if num <= 0:
                print("Debe ingresar un número positivo.")
                continue
            return num
        except ValueError:
            print("Entrada inválida. Debe ser un número entero.")

def obtener_flotante_positivo(mensaje):
    """Solicita un número decimal positivo al usuario, con validación."""
    while True:
        try:
            valor = input(mensaje).strip()
            if not valor:
                print("El valor no puede estar vacío.")
                continue
            num = float(valor)
            if num <= 0:
                print("Debe ingresar un número positivo.")
                continue
            return num
        except ValueError:
            print("Entrada inválida. Debe ser un número (puede tener decimales).")

def guardar_en_bd(nombre, tipo, libras, gramos, total, cantidad_peces=None):
    """Inserta un registro en la base de datos."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO ventas (fecha_hora, nombre_cliente, cantidad_libras, cantidad_gramos, tipo, total, cantidad_peces)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (fecha_hora, nombre, libras, gramos, tipo, total, cantidad_peces))
        conn.commit()
        print("Registro guardado correctamente.")
    except sqlite3.Error as e:
        print(f"Error al guardar en la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def registrar_operacion():
    """Flujo para registrar una venta o pedido, incluyendo la opción por peces."""
    print("\n--- Registrar venta o pedido ---")

    nombre = input("Nombre del cliente (opcional): ").strip()
    if nombre == "":
        nombre = None

    tipo = ""
    while tipo not in ("venta", "pedido"):
        tipo = input("Tipo (venta/pedido): ").strip().lower()
        if tipo not in ("venta", "pedido"):
            print("Error: debe ser 'venta' o 'pedido'.")

    if tipo == "venta":
        # Solo dos modalidades para venta
        modalidad = ""
        while modalidad not in ("l", "d"):
            modalidad = input("¿Vender por libras o por dinero? (l/d): ").strip().lower()
            if modalidad not in ("l", "d"):
                print("Error: ingrese 'l' para libras o 'd' para dinero.")
        if modalidad == "l":
            libras = obtener_flotante_positivo("Cantidad en libras: ")
            gramos = libras * 500
            total = libras * 6000
            print(f"\nCalculado: {libras:.2f} libras = {gramos:.2f} gramos, total ${total:,.2f}")
            confirmar = input("¿Guardar? (s/n): ").strip().lower()
            if confirmar == "s":
                guardar_en_bd(nombre, tipo, libras, gramos, total)
            else:
                print("Operación cancelada.")
        else:  # dinero
            monto = obtener_flotante_positivo("Monto en COP: ")
            libras = monto / 6000.0
            gramos = libras * 500
            print(f"Equivalencia aproximada: {libras:.2f} libras, {gramos:.2f} gramos")
            total_final = obtener_flotante_positivo("Ingrese el total final a registrar (COP): ")
            print(f"\nDatos a guardar: {libras:.2f} libras, {gramos:.2f} gramos, total ${total_final:,.2f}")
            confirmar = input("¿Guardar? (s/n): ").strip().lower()
            if confirmar == "s":
                guardar_en_bd(nombre, tipo, libras, gramos, total_final)
            else:
                print("Operación cancelada.")
    else:  # tipo == "pedido"
        # Tres modalidades para pedido
        modalidad = ""
        while modalidad not in ("l", "d", "p"):
            modalidad = input("¿Registrar por libras, por dinero o por cantidad de peces? (l/d/p): ").strip().lower()
            if modalidad not in ("l", "d", "p"):
                print("Error: ingrese 'l' para libras, 'd' para dinero o 'p' para peces.")
        if modalidad == "l":
            libras = obtener_flotante_positivo("Cantidad en libras: ")
            gramos = libras * 500
            total = libras * 6000
            print(f"\nCalculado: {libras:.2f} libras = {gramos:.2f} gramos, total ${total:,.2f}")
            confirmar = input("¿Guardar? (s/n): ").strip().lower()
            if confirmar == "s":
                guardar_en_bd(nombre, tipo, libras, gramos, total)
            else:
                print("Operación cancelada.")
        elif modalidad == "d":
            monto = obtener_flotante_positivo("Monto en COP: ")
            libras = monto / 6000.0
            gramos = libras * 500
            print(f"Equivalencia aproximada: {libras:.2f} libras, {gramos:.2f} gramos")
            total_final = obtener_flotante_positivo("Ingrese el total final a registrar (COP): ")
            print(f"\nDatos a guardar: {libras:.2f} libras, {gramos:.2f} gramos, total ${total_final:,.2f}")
            confirmar = input("¿Guardar? (s/n): ").strip().lower()
            if confirmar == "s":
                guardar_en_bd(nombre, tipo, libras, gramos, total_final)
            else:
                print("Operación cancelada.")
        else:  # modalidad == "p" (por peces)
            cantidad = obtener_entero_positivo("Cantidad de peces: ")
            print(f"\nRegistrando pedido por {cantidad} peces. Peso y total pendientes.")
            confirmar = input("¿Guardar? (s/n): ").strip().lower()
            if confirmar == "s":
                # Guardamos con libras, gramos y total en 0 (pendiente)
                guardar_en_bd(nombre, tipo, 0.0, 0.0, 0.0, cantidad_peces=cantidad)
            else:
                print("Operación cancelada.")

def ver_resumen():
    """Muestra los totales de ventas, pedidos y general."""
    print("\n--- Resumen ---")
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(total) FROM ventas WHERE tipo='venta'")
        total_ventas = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT SUM(total) FROM ventas WHERE tipo='pedido'")
        total_pedidos = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT SUM(total) FROM ventas")
        total_general = cursor.fetchone()[0] or 0.0

        print(f"Total ventas:  ${total_ventas:,.2f}")
        print(f"Total pedidos: ${total_pedidos:,.2f}")
        print(f"Total general: ${total_general:,.2f}")
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def ver_historial():
    """Muestra todos los registros ordenados por fecha descendente, incluyendo peces si existen."""
    print("\n--- Historial de operaciones ---")
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, fecha_hora, nombre_cliente, cantidad_libras, cantidad_gramos, tipo, total, cantidad_peces
            FROM ventas
            ORDER BY fecha_hora DESC
        """)
        registros = cursor.fetchall()
        if not registros:
            print("No hay registros para mostrar.")
            return

        for reg in registros:
            id_, fecha, nombre, libras, gramos, tipo, total, peces = reg
            nombre_mostrar = nombre if nombre else "(sin nombre)"
            print(f"ID: {id_} | Fecha: {fecha} | Cliente: {nombre_mostrar}")
            print(f"   Libras: {libras:.2f} | Gramos: {gramos:.2f} | Tipo: {tipo} | Total: ${total:,.2f}", end="")
            if peces is not None:
                print(f" | Peces: {peces}")
            else:
                print()
            print("-" * 50)
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def convertir_pedido_a_venta():
    """Convierte un pedido existente (con peso definido) en venta."""
    print("\n--- Convertir pedido en venta ---")
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Solo pedidos que NO sean por peces (tienen cantidad_peces NULL)
        cursor.execute("""
            SELECT id, fecha_hora, nombre_cliente, cantidad_libras, cantidad_gramos, total
            FROM ventas
            WHERE tipo = 'pedido' AND cantidad_peces IS NULL
            ORDER BY fecha_hora DESC
        """)
        pedidos = cursor.fetchall()

        if not pedidos:
            print("No hay pedidos pendientes (con peso definido) para convertir.")
            return

        print("\nPedidos pendientes:")
        print("-" * 80)
        for p in pedidos:
            id_, fecha, nombre, libras, gramos, total = p
            nombre_mostrar = nombre if nombre else "(sin nombre)"
            print(f"ID: {id_} | Fecha: {fecha} | Cliente: {nombre_mostrar}")
            print(f"   Libras: {libras:.2f} | Gramos: {gramos:.2f} | Total: ${total:,.2f}")
            print("-" * 80)

        while True:
            try:
                id_input = input("\nIngrese el ID del pedido a convertir (0 para cancelar): ").strip()
                if not id_input:
                    print("Debe ingresar un valor.")
                    continue
                id_pedido = int(id_input)
                if id_pedido == 0:
                    print("Operación cancelada.")
                    return
                break
            except ValueError:
                print("ID inválido. Debe ser un número entero.")

        # Validar que el ID exista, sea pedido y no tenga peces
        cursor.execute("SELECT tipo, cantidad_peces FROM ventas WHERE id = ?", (id_pedido,))
        resultado = cursor.fetchone()
        if not resultado:
            print(f"No existe ningún registro con ID {id_pedido}.")
            return
        tipo_actual, cantidad_peces = resultado
        if tipo_actual != 'pedido' or cantidad_peces is not None:
            print(f"El registro con ID {id_pedido} no es un pedido convertible (solo pedidos con peso definido).")
            return

        print(f"\nVa a convertir el pedido ID {id_pedido} en una venta.")
        confirmar = input("¿Confirmar conversión? (s/n): ").strip().lower()
        if confirmar != 's':
            print("Conversión cancelada.")
            return

        actualizar_fecha = input("¿Actualizar también la fecha a la actual? (s/n): ").strip().lower()
        if actualizar_fecha == 's':
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE ventas
                SET tipo = 'venta', fecha_hora = ?
                WHERE id = ?
            """, (fecha_actual, id_pedido))
        else:
            cursor.execute("UPDATE ventas SET tipo = 'venta' WHERE id = ?", (id_pedido,))
        conn.commit()
        print(f"Pedido ID {id_pedido} convertido a venta exitosamente.")
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def completar_pedido_por_peces():
    """Completa un pedido registrado por cantidad de peces, actualizando peso y total."""
    print("\n--- Completar pedido por peces ---")
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Pedidos por peces pendientes
        cursor.execute("""
            SELECT id, fecha_hora, nombre_cliente, cantidad_peces
            FROM ventas
            WHERE tipo = 'pedido' AND cantidad_peces IS NOT NULL
            ORDER BY fecha_hora DESC
        """)
        pedidos = cursor.fetchall()
        if not pedidos:
            print("No hay pedidos por peces pendientes de completar.")
            return

        print("\nPedidos por peces pendientes:")
        print("-" * 60)
        for p in pedidos:
            id_, fecha, nombre, cantidad = p
            nombre_mostrar = nombre if nombre else "(sin nombre)"
            print(f"ID: {id_} | Fecha: {fecha} | Cliente: {nombre_mostrar} | Peces: {cantidad}")
        print("-" * 60)

        while True:
            try:
                id_input = input("\nIngrese el ID del pedido a completar (0 para cancelar): ").strip()
                if not id_input:
                    print("Debe ingresar un valor.")
                    continue
                id_pedido = int(id_input)
                if id_pedido == 0:
                    print("Operación cancelada.")
                    return
                break
            except ValueError:
                print("ID inválido. Debe ser un número entero.")

        # Verificar que el ID corresponda a un pedido por peces
        cursor.execute("SELECT tipo, cantidad_peces FROM ventas WHERE id = ?", (id_pedido,))
        resultado = cursor.fetchone()
        if not resultado:
            print(f"No existe ningún registro con ID {id_pedido}.")
            return
        tipo_actual, cantidad_peces = resultado
        if tipo_actual != 'pedido' or cantidad_peces is None:
            print(f"El registro con ID {id_pedido} no es un pedido por peces pendiente.")
            return

        # Solicitar peso y total
        print("\nIngrese los datos finales del pedido:")
        modalidad_peso = ""
        while modalidad_peso not in ("l", "g"):
            modalidad_peso = input("¿Ingresar peso en libras o gramos? (l/g): ").strip().lower()
            if modalidad_peso not in ("l", "g"):
                print("Error: ingrese 'l' para libras o 'g' para gramos.")
        if modalidad_peso == "l":
            libras = obtener_flotante_positivo("Cantidad en libras: ")
            gramos = libras * 500
        else:
            gramos = obtener_flotante_positivo("Cantidad en gramos: ")
            libras = gramos / 500.0

        total = obtener_flotante_positivo("Total pagado (COP): ")

        print(f"\nDatos a actualizar: Libras: {libras:.2f}, Gramos: {gramos:.2f}, Total: ${total:,.2f}")
        confirmar = input("¿Confirmar actualización? (s/n): ").strip().lower()
        if confirmar != 's':
            print("Operación cancelada.")
            return

        actualizar_fecha = input("¿Actualizar también la fecha a la actual? (s/n): ").strip().lower()
        if actualizar_fecha == 's':
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE ventas
                SET tipo = 'venta', cantidad_libras = ?, cantidad_gramos = ?, total = ?, fecha_hora = ?
                WHERE id = ?
            """, (libras, gramos, total, fecha_actual, id_pedido))
        else:
            cursor.execute("""
                UPDATE ventas
                SET tipo = 'venta', cantidad_libras = ?, cantidad_gramos = ?, total = ?
                WHERE id = ?
            """, (libras, gramos, total, id_pedido))
        conn.commit()
        print(f"Pedido ID {id_pedido} completado y convertido a venta exitosamente.")
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def exportar_pedidos_html():
    """Genera un archivo HTML con todos los pedidos pendientes."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, fecha_hora, nombre_cliente, cantidad_peces, cantidad_libras, cantidad_gramos, total
            FROM ventas
            WHERE tipo = 'pedido'
            ORDER BY fecha_hora DESC
        """)
        pedidos = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
        return
    finally:
        if conn:
            conn.close()

    # Generar el HTML
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pedidos Pendientes - Pescadería</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        table {
            width: 100%;
            max-width: 1200px;
            margin: 20px auto;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #2c3e50;
            color: white;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .pendiente {
            color: #e67e22;
            font-style: italic;
        }
        .total-pie {
            text-align: right;
            margin-top: 20px;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
    <h1>Pedidos Pendientes</h1>
"""
    if not pedidos:
        html_content += "<p style='text-align:center;'>No hay pedidos pendientes.</p>"
    else:
        html_content += """    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Peces</th>
                <th>Libras</th>
                <th>Gramos</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
"""
        for p in pedidos:
            id_, fecha, nombre, peces, libras, gramos, total = p
            nombre_mostrar = nombre if nombre else "(sin nombre)"
            # Manejar valores NULL o cero
            peces_mostrar = peces if peces is not None else "Pendiente"
            # Para libras, gramos y total, si son 0 y hay peces, podría ser pendiente
            # Pero según lógica, si es pedido por peces, libras y gramos son 0, total 0
            # Queremos mostrarlos como "Pendiente" si son cero y además hay peces (es decir, pedido sin peso)
            # Mejor: si peces no es NULL, entonces libras/gramos/total son cero y deben mostrarse como Pendiente
            # Si peces es NULL, entonces son pedidos normales con valores definidos
            if peces is not None:
                libras_mostrar = "Pendiente"
                gramos_mostrar = "Pendiente"
                total_mostrar = "Pendiente"
            else:
                libras_mostrar = f"{libras:.2f}"
                gramos_mostrar = f"{gramos:.2f}"
                total_mostrar = f"${total:,.2f}"

            html_content += f"""            <tr>
                <td>{id_}</td>
                <td>{fecha}</td>
                <td>{nombre_mostrar}</td>
                <td>{peces_mostrar}</td>
                <td>{libras_mostrar}</td>
                <td>{gramos_mostrar}</td>
                <td>{total_mostrar}</td>
            </tr>
"""
        html_content += """        </tbody>
    </table>
"""
    html_content += """</body>
</html>"""

    # Escribir archivo
    try:
        with open("pedidos_pendientes.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Archivo 'pedidos_pendientes.html' generado correctamente.")
    except IOError as e:
        print(f"Error al escribir el archivo HTML: {e}")


def exportar_ventas_html():
    """Genera un archivo HTML con todas las ventas realizadas y total acumulado."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, fecha_hora, nombre_cliente, cantidad_peces, cantidad_libras, cantidad_gramos, total
            FROM ventas
            WHERE tipo = 'venta'
            ORDER BY fecha_hora DESC
        """)
        ventas = cursor.fetchall()

        # Calcular total acumulado
        cursor.execute("SELECT SUM(total) FROM ventas WHERE tipo='venta'")
        total_acumulado = cursor.fetchone()[0] or 0.0
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
        return
    finally:
        if conn:
            conn.close()

    # Generar HTML
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ventas Realizadas - Pescadería</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        table {
            width: 100%;
            max-width: 1200px;
            margin: 20px auto;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #27ae60;
            color: white;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .total-general {
            text-align: right;
            margin: 20px auto;
            max-width: 1200px;
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Ventas Realizadas</h1>
"""
    if not ventas:
        html_content += "<p style='text-align:center;'>No hay ventas registradas.</p>"
    else:
        html_content += """    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Peces</th>
                <th>Libras</th>
                <th>Gramos</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
"""
        for v in ventas:
            id_, fecha, nombre, peces, libras, gramos, total = v
            nombre_mostrar = nombre if nombre else "(sin nombre)"
            # Para ventas, siempre hay valores definidos (aunque si vino de peces, se actualizó)
            # Mostramos peces si no es NULL
            peces_mostrar = peces if peces is not None else "-"
            libras_mostrar = f"{libras:.2f}"
            gramos_mostrar = f"{gramos:.2f}"
            total_mostrar = f"${total:,.2f}"

            html_content += f"""            <tr>
                <td>{id_}</td>
                <td>{fecha}</td>
                <td>{nombre_mostrar}</td>
                <td>{peces_mostrar}</td>
                <td>{libras_mostrar}</td>
                <td>{gramos_mostrar}</td>
                <td>{total_mostrar}</td>
            </tr>
"""
        html_content += """        </tbody>
    </table>
"""
    # Agregar total acumulado
    html_content += f"""    <div class="total-general">
        Total acumulado de ventas: ${total_acumulado:,.2f}
    </div>
</body>
</html>"""

    try:
        with open("ventas_realizadas.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Archivo 'ventas_realizadas.html' generado correctamente.")
    except IOError as e:
        print(f"Error al escribir el archivo HTML: {e}")

def exportar_pedidos_html():
    """Genera un archivo HTML con todos los pedidos pendientes."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, fecha_hora, nombre_cliente, cantidad_peces, cantidad_libras, cantidad_gramos, total
            FROM ventas
            WHERE tipo = 'pedido'
            ORDER BY fecha_hora DESC
        """)
        pedidos = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
        return
    finally:
        if conn:
            conn.close()

    # Generar el HTML
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pedidos Pendientes - Pescadería</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        table {
            width: 100%;
            max-width: 1200px;
            margin: 20px auto;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #2c3e50;
            color: white;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .pendiente {
            color: #e67e22;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Pedidos Pendientes</h1>
"""
    if not pedidos:
        html_content += "<p style='text-align:center;'>No hay pedidos pendientes.</p>"
    else:
        html_content += """    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Peces</th>
                <th>Libras</th>
                <th>Gramos</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
"""
        for p in pedidos:
            id_, fecha, nombre, peces, libras, gramos, total = p
            nombre_mostrar = nombre if nombre else "(sin nombre)"
            if peces is not None:
                peces_mostrar = peces
                libras_mostrar = "Pendiente"
                gramos_mostrar = "Pendiente"
                total_mostrar = "Pendiente"
            else:
                peces_mostrar = "-"
                libras_mostrar = f"{libras:.2f}"
                gramos_mostrar = f"{gramos:.2f}"
                total_mostrar = f"${total:,.2f}"

            html_content += f"""            <tr>
                <td>{id_}</td>
                <td>{fecha}</td>
                <td>{nombre_mostrar}</td>
                <td>{peces_mostrar}</td>
                <td>{libras_mostrar}</td>
                <td>{gramos_mostrar}</td>
                <td>{total_mostrar}</td>
            </tr>
"""
        html_content += """        </tbody>
    </table>
"""
    html_content += """</body>
</html>"""

    # Escribir archivo
    try:
        with open("pedidos_pendientes.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Archivo 'pedidos_pendientes.html' generado correctamente.")
    except IOError as e:
        print(f"Error al escribir el archivo HTML: {e}")


def exportar_ventas_html():
    """Genera un archivo HTML con todas las ventas realizadas y total acumulado."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, fecha_hora, nombre_cliente, cantidad_peces, cantidad_libras, cantidad_gramos, total
            FROM ventas
            WHERE tipo = 'venta'
            ORDER BY fecha_hora DESC
        """)
        ventas = cursor.fetchall()

        # Calcular total acumulado
        cursor.execute("SELECT SUM(total) FROM ventas WHERE tipo='venta'")
        total_acumulado = cursor.fetchone()[0] or 0.0
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
        return
    finally:
        if conn:
            conn.close()

    # Generar HTML
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ventas Realizadas - Pescadería</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        table {
            width: 100%;
            max-width: 1200px;
            margin: 20px auto;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #27ae60;
            color: white;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .total-general {
            text-align: right;
            margin: 20px auto;
            max-width: 1200px;
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Ventas Realizadas</h1>
"""
    if not ventas:
        html_content += "<p style='text-align:center;'>No hay ventas registradas.</p>"
    else:
        html_content += """    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Peces</th>
                <th>Libras</th>
                <th>Gramos</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
"""
        for v in ventas:
            id_, fecha, nombre, peces, libras, gramos, total = v
            nombre_mostrar = nombre if nombre else "(sin nombre)"
            peces_mostrar = peces if peces is not None else "-"
            libras_mostrar = f"{libras:.2f}"
            gramos_mostrar = f"{gramos:.2f}"
            total_mostrar = f"${total:,.2f}"

            html_content += f"""            <tr>
                <td>{id_}</td>
                <td>{fecha}</td>
                <td>{nombre_mostrar}</td>
                <td>{peces_mostrar}</td>
                <td>{libras_mostrar}</td>
                <td>{gramos_mostrar}</td>
                <td>{total_mostrar}</td>
            </tr>
"""
        html_content += """        </tbody>
    </table>
"""
    html_content += f"""    <div class="total-general">
        Total acumulado de ventas: ${total_acumulado:,.2f}
    </div>
</body>
</html>"""

    try:
        with open("ventas_realizadas.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Archivo 'ventas_realizadas.html' generado correctamente.")
    except IOError as e:
        print(f"Error al escribir el archivo HTML: {e}")

def menu_principal():
    while True:
        limpiar_pantalla()
        print("=== SISTEMA DE VENTAS DE PESCADO ===")
        print("1. Registrar venta o pedido")
        print("2. Ver resumen")
        print("3. Ver historial")
        print("4. Exportar pedidos pendientes a HTML")
        print("5. Exportar ventas realizadas a HTML")
        print("6. Convertir pedido en venta")
        print("7. Completar pedido por peces")
        print("8. Salir")

        opcion = input("\nSeleccione una opción (1-8): ").strip()

        if opcion == "1":
            registrar_operacion()
        elif opcion == "2":
            ver_resumen()
        elif opcion == "3":
            ver_historial()
        elif opcion == "4":
            exportar_pedidos_html()
        elif opcion == "5":
            exportar_ventas_html()
        elif opcion == "6":
            convertir_pedido_a_venta()
        elif opcion == "7":
            completar_pedido_por_peces()
        elif opcion == "8":
            print("Saliendo del sistema.")
            break
        else:
            print("Opción no válida.")

        input("\nPresione Enter para volver.")

if __name__ == "__main__":
    inicializar_bd()
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nInterrupción detectada. Saliendo...")
        sys.exit(0)