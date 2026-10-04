"""
main.py — Menú de terminal de Viajes Aventura.

Solo conversa con el usuario: pide datos, revisa el FORMATO y muestra resultados.
No contiene SQL (RNF-12): todo pasa por SistemaViajes (viajes.py).
Ejecutar:  python main.py
"""

import os
import sqlite3
from datetime import datetime
from getpass import getpass

from viajes import Cliente, SistemaViajes


# ---------------------------------------------------------------- entrada de datos (capa 1)

def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  ✗ Este dato es obligatorio.")


def pedir_entero(mensaje, minimo=None):
    while True:
        valor = input(mensaje).strip().replace(".", "")
        if valor.isdigit() and (minimo is None or int(valor) >= minimo):
            return int(valor)
        print(f"  ✗ Ingrese un número entero{'' if minimo is None else f' mayor o igual a {minimo}'}.")


def pedir_fecha(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            return datetime.strptime(valor, "%d-%m-%Y").date()
        except ValueError:
            print("  ✗ Use el formato dd-mm-aaaa (ejemplo: 15-12-2026).")


def pedir_rut(mensaje="RUT (12345678-5): "):
    """H3 (auditoría): el RUT se revisa apenas se escribe, no al final del registro."""
    while True:
        rut = pedir_texto(mensaje)
        if Cliente.validar_rut(rut):
            return rut
        print("  ✗ RUT inválido: revise el dígito verificador (ejemplo: 12345678-5).")


def pedir_clave(mensaje="Contraseña: "):
    return getpass(mensaje)          # no se ve en pantalla mientras se escribe


def pesos(monto):
    return "$" + f"{monto:,}".replace(",", ".")


# ---------------------------------------------------------------- pantallas

def crear_primer_admin(sistema):
    print("\nPrimera vez: cree la cuenta del administrador.")
    nombre = pedir_texto("Nombre: ")
    correo = pedir_texto("Correo: ")
    clave = pedir_clave()
    if clave != pedir_clave("Repita la contraseña: "):
        raise ValueError("Las contraseñas no coinciden.")
    sistema.crear_admin_inicial(nombre, correo, clave)
    print("  ✓ Administrador creado. Ya puede iniciar sesión.")


def registrarse(sistema):
    print("\n— Registro de cliente —")
    nombre = pedir_texto("Nombre completo: ")
    rut = pedir_rut()
    correo = pedir_texto("Correo: ")
    telefono = pedir_texto("Teléfono: ")
    clave = pedir_clave("Contraseña (mínimo 8 caracteres): ")
    if clave != pedir_clave("Repita la contraseña: "):
        raise ValueError("Las contraseñas no coinciden.")
    sistema.registrar_cliente(nombre, rut, correo, telefono, clave)
    print("  ✓ Registro exitoso. Ya puede iniciar sesión.")


def mostrar_destinos(sistema):
    destinos = sistema.listar_destinos()
    if not destinos:
        print("  (no hay destinos registrados)")
    for d in destinos:
        estado = "disponible" if d.disponible else "NO disponible"
        print(f"  [{d.id}] {d.nombre} · {d.zona} · {d.duracion_dias} día(s) · {pesos(d.costo_base)} · {estado}")


def mostrar_paquetes(sistema):
    paquetes = sistema.listar_paquetes_disponibles()
    if not paquetes:
        print("  (no hay paquetes disponibles)")
    for p, libre in paquetes:
        nombres = " · ".join(d.nombre for d in p.destinos)
        print(f"  [{p.id}] {p.nombre}: {nombres}")
        print(f"       {p.fecha_salida:%d-%m-%Y} → {p.fecha_regreso:%d-%m-%Y} · "
              f"{pesos(p.precio_por_persona)} por persona · cupo disponible: {libre}")


def datos_destino():
    return (pedir_texto("Nombre: "), pedir_texto("Zona: "), pedir_texto("Descripción: "),
            pedir_entero("Duración en días: ", 1), pedir_entero("Costo base por persona: ", 1))


def menu_admin(sistema):
    opciones = {
        "1": "Registrar destino", "2": "Modificar destino", "3": "Eliminar / desactivar destino",
        "4": "Listar destinos", "5": "Crear paquete", "6": "Ver paquetes disponibles",
        "0": "Cerrar sesión"}
    while True:
        print("\n=== Administrador ===")
        for k, v in opciones.items():
            print(f"  {k}. {v}")
        op = input("Opción: ").strip()
        if op == "0":
            sistema.cerrar_sesion()
            print("  ✓ Sesión cerrada.")
            return
        try:
            if op == "1":
                d = sistema.registrar_destino(*datos_destino())
                print(f"  ✓ Destino registrado con id {d.id}.")
            elif op == "2":
                mostrar_destinos(sistema)
                id_destino = pedir_entero("Id del destino a modificar: ", 1)
                print("Ingrese los datos nuevos:")
                sistema.modificar_destino(id_destino, *datos_destino())
                print("  ✓ Destino modificado. Los paquetes ya publicados conservan su precio.")
            elif op == "3":
                mostrar_destinos(sistema)
                resultado = sistema.eliminar_destino(pedir_entero("Id del destino: ", 1))
                print(f"  ✓ Destino {resultado}.")
            elif op == "4":
                mostrar_destinos(sistema)
            elif op == "5":
                print("\nDestinos:")
                mostrar_destinos(sistema)
                nombre = pedir_texto("Nombre del paquete: ")
                salida = pedir_fecha("Fecha de salida (dd-mm-aaaa): ")
                regreso = pedir_fecha("Fecha de regreso (dd-mm-aaaa): ")
                cupo = pedir_entero("Cupo máximo de personas: ", 1)
                margen = pedir_entero("Margen en % (habitual 20): ", 0) / 100
                ids = [int(x) for x in pedir_texto("Ids de 2 a 5 destinos separados por coma: ").split(",")
                       if x.strip().isdigit()]
                p = sistema.crear_paquete(nombre, salida, regreso, cupo, margen, ids)
                print(f"  ✓ Paquete publicado con id {p.id}. Precio por persona: {pesos(p.precio_por_persona)}")
            elif op == "6":
                mostrar_paquetes(sistema)
            else:
                print("  ✗ Opción no válida.")
        except (ValueError, PermissionError) as e:
            print(f"  ✗ {e}")


def menu_cliente(sistema, cliente):
    opciones = {"1": "Ver paquetes disponibles", "2": "Reservar paquete",
                "3": "Mi historial de reservas", "4": "Cancelar una reserva", "0": "Cerrar sesión"}
    while True:
        print(f"\n=== Cliente: {cliente.nombre} ===")
        for k, v in opciones.items():
            print(f"  {k}. {v}")
        op = input("Opción: ").strip()
        if op == "0":
            sistema.cerrar_sesion()
            print("  ✓ Sesión cerrada.")
            return
        try:
            if op == "1":
                mostrar_paquetes(sistema)
            elif op == "2":
                mostrar_paquetes(sistema)
                id_paquete = pedir_entero("Id del paquete: ", 1)
                personas = pedir_entero("Cantidad de personas: ", 1)
                r = sistema.reservar(id_paquete, personas)
                print(f"  ✓ Reserva n.º {r.id} confirmada. Total: {pesos(r.total)}")
            elif op == "3":
                reservas = sistema.historial()
                if not reservas:
                    print("  (aún no tiene reservas)")
                for r in reservas:
                    print(f"  [{r.id}] {r.paquete.nombre} · {r.fecha_emision:%d-%m-%Y} · "
                          f"{r.personas} persona(s) · {pesos(r.total)} · {r.estado}")
            elif op == "4":
                sistema.cancelar_reserva(pedir_entero("Número de reserva a cancelar: ", 1))
                print("  ✓ Reserva cancelada. El cupo quedó liberado.")
            else:
                print("  ✗ Opción no válida.")
        except (ValueError, PermissionError) as e:
            print(f"  ✗ {e}")


# ---------------------------------------------------------------- programa principal

def main():
    sistema = SistemaViajes(os.environ.get("DB_PATH", "viajes_aventura.db"))
    print("=" * 44)
    print("   VIAJES AVENTURA · Sistema de reservas")
    print("=" * 44)
    if not sistema.existe_admin():
        crear_primer_admin(sistema)
    while True:
        print("\n1. Iniciar sesión\n2. Registrarme como cliente\n0. Salir")
        op = input("Opción: ").strip()
        try:
            if op == "1":
                usuario = sistema.iniciar_sesion(pedir_texto("Correo: "), pedir_clave())
                print(f"  ✓ Bienvenido/a, {usuario.nombre}.")
                if usuario.es_admin():
                    menu_admin(sistema)
                else:
                    menu_cliente(sistema, usuario)
            elif op == "2":
                registrarse(sistema)
            elif op == "0":
                print("Hasta pronto.")
                return
            else:
                print("  ✗ Opción no válida.")
        except (ValueError, PermissionError) as e:
            print(f"  ✗ {e}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma cerrado por el usuario.")
    except sqlite3.Error:
        # RNF-10: nunca se muestran rutas ni trazas técnicas
        print("\nError de base de datos. Verifique que el archivo no esté abierto en otro programa.")
