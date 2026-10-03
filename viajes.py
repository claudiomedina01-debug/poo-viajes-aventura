"""
viajes.py — Dominio del sistema Viajes Aventura.

Contiene las 8 clases del diagrama UML (diagramas/Clases_ViajesAventura.png):
Usuario (abstracta), Cliente, Administrador, Destino, Paquete, Reserva,
BaseDatos y SistemaViajes.

Reglas de diseño (método EcoTech):
- Solo librería estándar de Python (sqlite3, hashlib, secrets, re, abc, datetime).
- Todas las consultas SQL usan parámetros "?" (RNF-09).
- La conexión se abre y se cierra en cada operación.
- Validación en 3 capas: menú (main.py) → clases (aquí) → base de datos (CHECK/UNIQUE/FK).

Pruebas automáticas:  python viajes.py   → debe terminar en "TODAS LAS PRUEBAS OK".
"""

import hashlib
import re
import secrets
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import date

# Formatos aceptados (RNF-07)
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
PATRON_TELEFONO = re.compile(r"^\+?\d{8,12}$")
LARGO_MINIMO_CLAVE = 8          # RNF-03


# =====================================================================
#  PERSONAS: Usuario (abstracta) → Cliente / Administrador
# =====================================================================

class Usuario(ABC):
    """Cualquier persona con cuenta. Es abstracta: nunca se crea un 'Usuario' a secas."""

    MAX_INTENTOS = 3            # RNF-02: bloqueo tras 3 intentos fallidos

    def __init__(self, nombre, correo, clave=None, *, id=None,
                 hash_clave=None, sal=None, intentos=0):
        nombre = (nombre or "").strip()
        correo = (correo or "").strip().lower()
        if not nombre:
            raise ValueError("El nombre es obligatorio.")
        if not PATRON_CORREO.match(correo):
            raise ValueError("El correo no tiene un formato válido.")
        self.id = id
        self.nombre = nombre
        self.correo = correo
        if clave is not None:
            # Usuario nuevo: se recibe la clave y se guarda SOLO su hash (R10, RNF-01)
            if len(clave) < LARGO_MINIMO_CLAVE:
                raise ValueError(f"La contraseña debe tener al menos {LARGO_MINIMO_CLAVE} caracteres.")
            self._sal = secrets.token_bytes(16)
            self._hash_clave = Usuario.generar_hash(clave, self._sal)
        elif hash_clave is not None and sal is not None:
            # Usuario leído desde la base: ya viene con hash y sal
            self._sal = sal
            self._hash_clave = hash_clave
        else:
            raise ValueError("Falta la contraseña.")
        self._intentos_fallidos = intentos

    @staticmethod
    def generar_hash(clave, sal):
        """scrypt: función lenta a propósito, para que adivinar claves sea muy costoso."""
        return hashlib.scrypt(clave.encode("utf-8"), salt=sal, n=2**14, r=8, p=1, dklen=64)

    def verificar_clave(self, clave):
        calculado = Usuario.generar_hash(clave, self._sal)
        return secrets.compare_digest(calculado, self._hash_clave)   # comparación en tiempo constante

    def registrar_intento_fallido(self):
        self._intentos_fallidos += 1

    def reiniciar_intentos(self):
        self._intentos_fallidos = 0

    def esta_bloqueado(self):
        return self._intentos_fallidos >= Usuario.MAX_INTENTOS

    @abstractmethod
    def es_admin(self):
        """Cada clase hija responde a su manera (polimorfismo)."""


class Cliente(Usuario):
    """Quien reserva. RUT y teléfono son privados y nunca se muestran completos (R17)."""

    def __init__(self, nombre, rut, correo, telefono, clave=None, **guardado):
        super().__init__(nombre, correo, clave, **guardado)
        rut = (rut or "").replace(".", "").strip().upper()
        telefono = (telefono or "").replace(" ", "").strip()
        if not Cliente.validar_rut(rut):
            raise ValueError("El RUT no es válido (revise el dígito verificador).")
        if not PATRON_TELEFONO.match(telefono):
            raise ValueError("El teléfono debe tener entre 8 y 12 dígitos.")
        self._rut = rut
        self._telefono = telefono

    @staticmethod
    def validar_rut(rut):
        """Valida el dígito verificador con el algoritmo módulo 11. Formato: 12345678-5."""
        rut = (rut or "").replace(".", "").strip().upper()
        if not re.match(r"^\d{7,8}-[\dK]$", rut):
            return False
        numero, dv = rut.split("-")
        suma, factor = 0, 2
        for digito in reversed(numero):
            suma += int(digito) * factor
            factor = 2 if factor == 7 else factor + 1
        resto = 11 - (suma % 11)
        esperado = "0" if resto == 11 else "K" if resto == 10 else str(resto)
        return dv == esperado

    def rut_enmascarado(self):
        numero = self._rut.split("-")[0]
        return numero[:2] + "." + "*" * 3 + "." + "*" * 3 + "-*"

    def telefono_enmascarado(self):
        return "*" * (len(self._telefono) - 4) + self._telefono[-4:]

    def es_admin(self):
        return False


class Administrador(Usuario):
    """Socio que gestiona el catálogo (supuesto S3)."""

    def __init__(self, nombre, correo, clave=None, **guardado):
        super().__init__(nombre, correo, clave, **guardado)

    def es_admin(self):
        return True


# =====================================================================
#  NEGOCIO: Destino, Paquete, Reserva
# =====================================================================

class Destino:
    def __init__(self, nombre, zona, descripcion, duracion_dias, costo_base,
                 disponible=True, id=None):
        self.id = id
        self.nombre = (nombre or "").strip()
        self.zona = (zona or "").strip()
        self.descripcion = (descripcion or "").strip()
        self.duracion_dias = duracion_dias
        self.costo_base = costo_base
        self.disponible = bool(disponible)
        self.validar()

    def validar(self):
        """R1 y R2."""
        if not self.nombre or not self.zona or not self.descripcion:
            raise ValueError("Nombre, zona y descripción son obligatorios.")
        if not isinstance(self.duracion_dias, int) or self.duracion_dias < 1:
            raise ValueError("La duración debe ser de al menos 1 día.")
        if not isinstance(self.costo_base, int) or self.costo_base <= 0:
            raise ValueError("El costo base debe ser mayor que cero.")

    def marcar_no_disponible(self):
        """R8: deja de ofrecerse para paquetes nuevos, pero no se borra."""
        self.disponible = False


class Paquete:
    MIN_DESTINOS = 2
    MAX_DESTINOS = 5

    def __init__(self, nombre, fecha_salida, fecha_regreso, cupo_maximo, margen,
                 destinos, precio_por_persona=None, id=None):
        self.id = id
        self.nombre = (nombre or "").strip()
        self.fecha_salida = fecha_salida
        self.fecha_regreso = fecha_regreso
        self.cupo_maximo = cupo_maximo
        self.margen = margen
        self.destinos = list(destinos)
        self.validar()
        # R7: si viene de la base se respeta el precio fijado al publicar; si es nuevo, se calcula
        self.precio_por_persona = precio_por_persona if precio_por_persona is not None else self.calcular_precio()

    def validar(self):
        """R3 y R5."""
        if not self.nombre:
            raise ValueError("El nombre del paquete es obligatorio.")
        if self.fecha_regreso <= self.fecha_salida:
            raise ValueError("La fecha de regreso debe ser posterior a la de salida.")
        if not isinstance(self.cupo_maximo, int) or self.cupo_maximo <= 0:
            raise ValueError("El cupo máximo debe ser mayor que cero.")
        if self.margen < 0:
            raise ValueError("El margen no puede ser negativo.")
        if not (Paquete.MIN_DESTINOS <= len(self.destinos) <= Paquete.MAX_DESTINOS):
            raise ValueError("Un paquete combina entre 2 y 5 destinos.")
        nombres = [d.nombre.lower() for d in self.destinos]
        if len(nombres) != len(set(nombres)):
            raise ValueError("Un destino no puede repetirse dentro del mismo paquete.")

    def calcular_precio(self):
        """R6: suma de costos base + margen. Ej.: 83.000 con 20 % → 99.600."""
        suma = sum(d.costo_base for d in self.destinos)
        return round(suma * (1 + self.margen))

    def esta_vigente(self, hoy):
        """R15: se puede reservar mientras la salida no haya pasado."""
        return self.fecha_salida >= hoy

    def cupo_disponible(self, reservadas):
        """R14: cupo máximo menos personas ya reservadas."""
        return self.cupo_maximo - reservadas


class Reserva:
    ESTADO_ACTIVA = "confirmada"      # S4
    ESTADO_CANCELADA = "cancelada"    # S1

    def __init__(self, cliente, paquete, fecha_emision, personas,
                 total=None, estado=ESTADO_ACTIVA, id=None):
        if not isinstance(personas, int) or personas < 1:
            raise ValueError("La reserva debe ser al menos para 1 persona.")   # R16
        self.id = id
        self.cliente = cliente
        self.paquete = paquete
        self.fecha_emision = fecha_emision
        self.personas = personas
        self.estado = estado
        # R13: el total se calcula al reservar y luego no cambia
        self.total = total if total is not None else self.calcular_total()

    def calcular_total(self):
        return self.paquete.precio_por_persona * self.personas

    def cancelar(self, hoy):
        """S1: no se borra; cambia de estado y libera el cupo."""
        if not self.esta_activa():
            raise ValueError("La reserva ya estaba cancelada.")
        if not self.paquete.esta_vigente(hoy):
            raise ValueError("No se puede cancelar: la fecha de salida ya pasó.")
        self.estado = Reserva.ESTADO_CANCELADA

    def esta_activa(self):
        return self.estado == Reserva.ESTADO_ACTIVA


# =====================================================================
#  MOTOR: BaseDatos y SistemaViajes
# =====================================================================

class BaseDatos:
    def __init__(self, ruta="viajes_aventura.db"):
        self._ruta = ruta

    @contextmanager
    def conectar(self):
        """Abre la conexión, hace todo en UNA transacción y siempre la cierra."""
        con = sqlite3.connect(self._ruta, isolation_level=None)
        try:
            con.execute("PRAGMA foreign_keys = ON")
            con.execute("BEGIN IMMEDIATE")      # bloquea mientras se verifica el cupo
            yield con
            con.execute("COMMIT")
        except Exception:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise
        finally:
            con.close()

    def crear_tablas(self):
        """Tercera capa de validación: la base rechaza datos inválidos (RNF-08)."""
        with self.conectar() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre            TEXT    NOT NULL,
                    correo            TEXT    NOT NULL UNIQUE,
                    rut               TEXT,
                    telefono          TEXT,
                    rol               TEXT    NOT NULL CHECK (rol IN ('cliente', 'admin')),
                    hash_clave        BLOB    NOT NULL,
                    sal               BLOB    NOT NULL,
                    intentos_fallidos INTEGER NOT NULL DEFAULT 0 CHECK (intentos_fallidos >= 0),
                    CHECK (rol = 'admin' OR (rut IS NOT NULL AND telefono IS NOT NULL))
                )""")
            con.execute("""
                CREATE TABLE IF NOT EXISTS destinos (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                    zona          TEXT    NOT NULL,
                    descripcion   TEXT    NOT NULL,
                    duracion_dias INTEGER NOT NULL CHECK (duracion_dias > 0),
                    costo_base    INTEGER NOT NULL CHECK (costo_base > 0),
                    disponible    INTEGER NOT NULL DEFAULT 1 CHECK (disponible IN (0, 1))
                )""")
            con.execute("""
                CREATE TABLE IF NOT EXISTS paquetes (
                    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre             TEXT    NOT NULL,
                    fecha_salida       TEXT    NOT NULL,
                    fecha_regreso      TEXT    NOT NULL,
                    cupo_maximo        INTEGER NOT NULL CHECK (cupo_maximo > 0),
                    margen             REAL    NOT NULL CHECK (margen >= 0),
                    precio_por_persona INTEGER NOT NULL CHECK (precio_por_persona > 0),
                    CHECK (fecha_regreso > fecha_salida)
                )""")
            con.execute("""
                CREATE TABLE IF NOT EXISTS paquete_destino (
                    paquete_id INTEGER NOT NULL REFERENCES paquetes(id) ON DELETE CASCADE,
                    destino_id INTEGER NOT NULL REFERENCES destinos(id) ON DELETE RESTRICT,
                    PRIMARY KEY (paquete_id, destino_id)
                )""")
            con.execute("""
                CREATE TABLE IF NOT EXISTS reservas (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id    INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
                    paquete_id    INTEGER NOT NULL REFERENCES paquetes(id) ON DELETE RESTRICT,
                    fecha_emision TEXT    NOT NULL,
                    personas      INTEGER NOT NULL CHECK (personas >= 1),
                    total         INTEGER NOT NULL CHECK (total > 0),
                    estado        TEXT    NOT NULL CHECK (estado IN ('confirmada', 'cancelada'))
                )""")
            # S6: un cliente no puede tener 2 reservas ACTIVAS del mismo paquete
            con.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS ux_reserva_activa
                ON reservas (cliente_id, paquete_id) WHERE estado = 'confirmada'""")


class SistemaViajes:
    """El 'recepcionista': coordina clases y base de datos y revisa permisos."""

    def __init__(self, ruta="viajes_aventura.db"):
        self._bd = BaseDatos(ruta)
        self._bd.crear_tablas()
        self._sesion = None

    # ------------------------------------------------------------ permisos
    def _exigir_admin(self):
        if self._sesion is None or not self._sesion.es_admin():
            raise PermissionError("Acción permitida solo para administradores.")

    def _exigir_cliente(self):
        if self._sesion is None or self._sesion.es_admin():
            raise PermissionError("Acción permitida solo para clientes con sesión iniciada.")

    # ------------------------------------------------------- usuarios
    def existe_admin(self):
        with self._bd.conectar() as con:
            return con.execute("SELECT 1 FROM usuarios WHERE rol = 'admin'").fetchone() is not None

    def crear_admin_inicial(self, nombre, correo, clave):
        """RF-04: solo funciona si todavía no existe ningún administrador."""
        if self.existe_admin():
            raise PermissionError("Ya existe un administrador.")
        admin = Administrador(nombre, correo, clave)
        with self._bd.conectar() as con:
            cur = con.execute(
                "INSERT INTO usuarios (nombre, correo, rol, hash_clave, sal) VALUES (?, ?, 'admin', ?, ?)",
                (admin.nombre, admin.correo, admin._hash_clave, admin._sal))
            admin.id = cur.lastrowid
        return admin

    def registrar_cliente(self, nombre, rut, correo, telefono, clave):
        """RF-01."""
        cliente = Cliente(nombre, rut, correo, telefono, clave)
        try:
            with self._bd.conectar() as con:
                cur = con.execute(
                    "INSERT INTO usuarios (nombre, correo, rut, telefono, rol, hash_clave, sal) "
                    "VALUES (?, ?, ?, ?, 'cliente', ?, ?)",
                    (cliente.nombre, cliente.correo, cliente._rut, cliente._telefono,
                     cliente._hash_clave, cliente._sal))
                cliente.id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("Ese correo ya está registrado.") from None
        return cliente

    def iniciar_sesion(self, correo, clave):
        """RF-02 + RNF-02 (bloqueo) + RNF-03 (mensaje genérico)."""
        generico = "Correo o contraseña incorrectos."
        bloqueado = "Cuenta bloqueada por intentos fallidos. Contacte a la agencia."
        correo = (correo or "").strip().lower()
        with self._bd.conectar() as con:
            fila = con.execute(
                "SELECT id, nombre, correo, rut, telefono, rol, hash_clave, sal, intentos_fallidos "
                "FROM usuarios WHERE correo = ?", (correo,)).fetchone()
            if fila is None:
                raise ValueError(generico)
            usuario = _usuario_desde_fila(fila)
            if usuario.esta_bloqueado():
                raise PermissionError(bloqueado)
            clave_correcta = usuario.verificar_clave(clave or "")
            if clave_correcta:
                usuario.reiniciar_intentos()
            else:
                usuario.registrar_intento_fallido()
            # El contador se guarda ANTES de avisar el error; si no, la transacción se desharía
            con.execute("UPDATE usuarios SET intentos_fallidos = ? WHERE id = ?",
                        (usuario._intentos_fallidos, usuario.id))
        if not clave_correcta:
            raise PermissionError(bloqueado) if usuario.esta_bloqueado() else ValueError(generico)
        self._sesion = usuario
        return usuario

    def cerrar_sesion(self):
        self._sesion = None

    # -------------------------------------------------------- destinos
    def registrar_destino(self, nombre, zona, desc, dias, costo):
        """RF-05."""
        self._exigir_admin()
        destino = Destino(nombre, zona, desc, dias, costo)
        try:
            with self._bd.conectar() as con:
                cur = con.execute(
                    "INSERT INTO destinos (nombre, zona, descripcion, duracion_dias, costo_base) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (destino.nombre, destino.zona, destino.descripcion, destino.duracion_dias, destino.costo_base))
                destino.id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("Ya existe un destino con ese nombre.") from None
        return destino

    def modificar_destino(self, id, nombre, zona, desc, dias, costo):
        """RF-06. Los paquetes ya publicados conservan su precio (R7)."""
        self._exigir_admin()
        actual = self._buscar_destino(id)
        destino = Destino(nombre, zona, desc, dias, costo, actual.disponible, id)
        try:
            with self._bd.conectar() as con:
                con.execute(
                    "UPDATE destinos SET nombre = ?, zona = ?, descripcion = ?, duracion_dias = ?, "
                    "costo_base = ? WHERE id = ?",
                    (destino.nombre, destino.zona, destino.descripcion, destino.duracion_dias,
                     destino.costo_base, id))
        except sqlite3.IntegrityError:
            raise ValueError("Ya existe otro destino con ese nombre.") from None
        return destino

    def eliminar_destino(self, id):
        """RF-07 / R8: se elimina si no está en paquetes; si está, queda 'no disponible'."""
        self._exigir_admin()
        destino = self._buscar_destino(id)
        with self._bd.conectar() as con:
            en_uso = con.execute("SELECT 1 FROM paquete_destino WHERE destino_id = ?", (id,)).fetchone()
            if en_uso:
                destino.marcar_no_disponible()
                con.execute("UPDATE destinos SET disponible = 0 WHERE id = ?", (id,))
                return "no disponible"
            con.execute("DELETE FROM destinos WHERE id = ?", (id,))
            return "eliminado"

    def listar_destinos(self):
        """RF-08."""
        self._exigir_admin()
        with self._bd.conectar() as con:
            filas = con.execute(
                "SELECT nombre, zona, descripcion, duracion_dias, costo_base, disponible, id "
                "FROM destinos ORDER BY nombre").fetchall()
        return [Destino(*f) for f in filas]

    # -------------------------------------------------------- paquetes
    def crear_paquete(self, nombre, salida, regreso, cupo, margen, ids_destinos):
        """RF-09 y RF-10: el precio lo calcula el sistema y queda fijo (R7, S5)."""
        self._exigir_admin()
        if len(ids_destinos) != len(set(ids_destinos)):
            raise ValueError("Un destino no puede repetirse dentro del mismo paquete.")
        if salida <= date.today():
            raise ValueError("La fecha de salida debe ser posterior a hoy.")
        destinos = [self._buscar_destino(i) for i in ids_destinos]
        if any(not d.disponible for d in destinos):
            raise ValueError("Solo se pueden usar destinos disponibles.")      # R8
        paquete = Paquete(nombre, salida, regreso, cupo, margen, destinos)
        with self._bd.conectar() as con:
            cur = con.execute(
                "INSERT INTO paquetes (nombre, fecha_salida, fecha_regreso, cupo_maximo, margen, "
                "precio_por_persona) VALUES (?, ?, ?, ?, ?, ?)",
                (paquete.nombre, salida.isoformat(), regreso.isoformat(), cupo, margen,
                 paquete.precio_por_persona))
            paquete.id = cur.lastrowid
            con.executemany("INSERT INTO paquete_destino (paquete_id, destino_id) VALUES (?, ?)",
                            [(paquete.id, d.id) for d in destinos])
        return paquete

    def listar_paquetes_disponibles(self):
        """RF-11: solo vigentes (R15) y con cupo (R14). Devuelve (paquete, cupo_disponible)."""
        if self._sesion is None:
            raise PermissionError("Debe iniciar sesión.")
        hoy = date.today()
        with self._bd.conectar() as con:
            ids = [f[0] for f in con.execute("SELECT id FROM paquetes ORDER BY fecha_salida")]
            resultado = []
            for id_paquete in ids:
                paquete = _cargar_paquete(con, id_paquete)
                libre = paquete.cupo_disponible(_personas_reservadas(con, id_paquete))
                if paquete.esta_vigente(hoy) and libre > 0:
                    resultado.append((paquete, libre))
        return resultado

    # -------------------------------------------------------- reservas
    def reservar(self, id_paquete, personas):
        """RF-12 y RF-13: valida fecha, cupo, personas y duplicado (R14, R15, R16, S6)."""
        self._exigir_cliente()
        hoy = date.today()
        with self._bd.conectar() as con:
            paquete = _cargar_paquete(con, id_paquete)
            if not paquete.esta_vigente(hoy):
                raise ValueError("No se puede reservar: la fecha de salida ya pasó.")
            libre = paquete.cupo_disponible(_personas_reservadas(con, id_paquete))
            if personas > libre:
                raise ValueError(f"No hay cupo suficiente. Lugares disponibles: {libre}.")
            duplicada = con.execute(
                "SELECT 1 FROM reservas WHERE cliente_id = ? AND paquete_id = ? AND estado = 'confirmada'",
                (self._sesion.id, id_paquete)).fetchone()
            if duplicada:
                raise ValueError("Ya tiene una reserva activa de este paquete. Cancélela para cambiarla.")
            reserva = Reserva(self._sesion, paquete, hoy, personas)
            cur = con.execute(
                "INSERT INTO reservas (cliente_id, paquete_id, fecha_emision, personas, total, estado) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (self._sesion.id, paquete.id, hoy.isoformat(), personas, reserva.total, reserva.estado))
            reserva.id = cur.lastrowid
        return reserva

    def historial(self):
        """RF-14: cada cliente ve SOLO sus reservas (R11)."""
        self._exigir_cliente()
        with self._bd.conectar() as con:
            filas = con.execute(
                "SELECT id, paquete_id, fecha_emision, personas, total, estado FROM reservas "
                "WHERE cliente_id = ? ORDER BY fecha_emision DESC, id DESC", (self._sesion.id,)).fetchall()
            return [Reserva(self._sesion, _cargar_paquete(con, f[1]), date.fromisoformat(f[2]),
                            f[3], f[4], f[5], f[0]) for f in filas]

    def cancelar_reserva(self, id_reserva):
        """RF-15 / S1."""
        self._exigir_cliente()
        with self._bd.conectar() as con:
            fila = con.execute(
                "SELECT id, paquete_id, fecha_emision, personas, total, estado FROM reservas "
                "WHERE id = ? AND cliente_id = ?", (id_reserva, self._sesion.id)).fetchone()
            if fila is None:
                raise ValueError("No existe una reserva suya con ese número.")
            reserva = Reserva(self._sesion, _cargar_paquete(con, fila[1]), date.fromisoformat(fila[2]),
                              fila[3], fila[4], fila[5], fila[0])
            reserva.cancelar(date.today())
            con.execute("UPDATE reservas SET estado = ? WHERE id = ?", (reserva.estado, reserva.id))

    # ------------------------------------------------- apoyo interno
    def _buscar_destino(self, id):
        with self._bd.conectar() as con:
            fila = con.execute(
                "SELECT nombre, zona, descripcion, duracion_dias, costo_base, disponible, id "
                "FROM destinos WHERE id = ?", (id,)).fetchone()
        if fila is None:
            raise ValueError(f"No existe un destino con id {id}.")
        return Destino(*fila)


# ---------------------------------------------------------------------
#  Funciones de apoyo: convierten filas de la base en objetos
# ---------------------------------------------------------------------

def _usuario_desde_fila(fila):
    id, nombre, correo, rut, telefono, rol, hash_clave, sal, intentos = fila
    guardado = dict(id=id, hash_clave=hash_clave, sal=sal, intentos=intentos)
    if rol == "admin":
        return Administrador(nombre, correo, **guardado)
    return Cliente(nombre, rut, correo, telefono, **guardado)


def _cargar_paquete(con, id_paquete):
    fila = con.execute(
        "SELECT id, nombre, fecha_salida, fecha_regreso, cupo_maximo, margen, precio_por_persona "
        "FROM paquetes WHERE id = ?", (id_paquete,)).fetchone()
    if fila is None:
        raise ValueError(f"No existe un paquete con id {id_paquete}.")
    destinos = [Destino(*f) for f in con.execute(
        "SELECT d.nombre, d.zona, d.descripcion, d.duracion_dias, d.costo_base, d.disponible, d.id "
        "FROM destinos d JOIN paquete_destino pd ON pd.destino_id = d.id "
        "WHERE pd.paquete_id = ? ORDER BY d.id", (id_paquete,))]
    return Paquete(fila[1], date.fromisoformat(fila[2]), date.fromisoformat(fila[3]),
                   fila[4], fila[5], destinos, fila[6], fila[0])


def _personas_reservadas(con, id_paquete):
    return con.execute(
        "SELECT COALESCE(SUM(personas), 0) FROM reservas WHERE paquete_id = ? AND estado = 'confirmada'",
        (id_paquete,)).fetchone()[0]


# =====================================================================
#  PRUEBAS AUTOMÁTICAS  (python viajes.py)
# =====================================================================

def _pruebas():
    import os
    import tempfile
    from datetime import timedelta

    ruta = os.path.join(tempfile.mkdtemp(), "prueba.db")
    s = SistemaViajes(ruta)
    hoy = date.today()
    resultados = []

    def ok(nombre):
        resultados.append(nombre)
        print(f"  OK  {nombre}")

    def falla_con(error, funcion, *args):
        try:
            funcion(*args)
        except error:
            return True
        return False

    print("Pruebas de viajes.py")

    # RF-04 / S3
    assert not s.existe_admin()
    s.crear_admin_inicial("Paulina Ovalle", "paulina@viajesaventura.cl", "ClaveAdmin2026")
    assert falla_con(PermissionError, s.crear_admin_inicial, "Otro", "otro@x.cl", "ClaveOtra2026")
    ok("RF-04 primer administrador (y solo uno)")

    # RF-01 + R9 + RNF-03 + RNF-07
    assert falla_con(ValueError, s.registrar_cliente, "Ana", "12345678-9", "ana@x.cl", "912345678", "Clave2026x")
    assert falla_con(ValueError, s.registrar_cliente, "Ana", "12345678-5", "ana-sin-arroba", "912345678", "Clave2026x")
    assert falla_con(ValueError, s.registrar_cliente, "Ana", "12345678-5", "ana@x.cl", "912345678", "corta")
    s.registrar_cliente("Carolina Reyes", "12.345.678-5", "carolina@correo.cl", "+56912345678", "Carolina2026")
    assert falla_con(ValueError, s.registrar_cliente, "Otra", "11111111-1", "CAROLINA@correo.cl", "912345678", "Clave2026x")
    ok("RF-01 registro con RUT válido, correo único y clave mínima")

    # RF-02 + RNF-01 + RNF-02 + RNF-03 + RNF-09
    with s._bd.conectar() as con:
        h1 = con.execute("SELECT hash_clave FROM usuarios WHERE correo='carolina@correo.cl'").fetchone()[0]
    assert b"Carolina2026" not in h1
    assert falla_con(ValueError, s.iniciar_sesion, "' OR 1=1 --", "x")
    s.registrar_cliente("Andrés Pinto", "11111111-1", "andres@correo.cl", "987654321", "Andres2026")
    for _ in range(2):
        assert falla_con(ValueError, s.iniciar_sesion, "andres@correo.cl", "mala")
    assert falla_con(PermissionError, s.iniciar_sesion, "andres@correo.cl", "mala")
    assert falla_con(PermissionError, s.iniciar_sesion, "andres@correo.cl", "Andres2026")
    ok("RNF-01/02/03/09 hash, bloqueo a los 3 intentos, mensaje genérico, inyección SQL")

    # RNF-04 control de acceso
    s.iniciar_sesion("carolina@correo.cl", "Carolina2026")
    assert falla_con(PermissionError, s.registrar_destino, "X", "Y", "Z", 1, 1000)
    s.cerrar_sesion()
    assert falla_con(PermissionError, s.historial)
    ok("RNF-04 un cliente no puede gestionar el catálogo; sin sesión no hay historial")

    # RF-05..08 + R1, R2, R8
    s.iniciar_sesion("paulina@viajesaventura.cl", "ClaveAdmin2026")
    maipo = s.registrar_destino("Cajón del Maipo", "Región Metropolitana", "Montaña y río", 1, 45000)
    damas = s.registrar_destino("Isla Damas", "Región de Coquimbo", "Reserva marina", 1, 38000)
    elqui = s.registrar_destino("Valle del Elqui", "Región de Coquimbo", "Cielos y pisco", 2, 120000)
    suelto = s.registrar_destino("Destino de prueba", "Zona", "Sin paquetes", 1, 1000)
    assert falla_con(ValueError, s.registrar_destino, "cajón del maipo", "RM", "Repetido", 1, 1000)
    assert falla_con(ValueError, s.registrar_destino, "Gratis", "RM", "Costo cero", 1, 0)
    ok("RF-05 destino con nombre único y costo > 0")

    # RF-09/10 + R3, R5, R6
    salida, regreso = hoy + timedelta(days=30), hoy + timedelta(days=32)
    assert falla_con(ValueError, s.crear_paquete, "Uno solo", salida, regreso, 10, 0.2, [maipo.id])
    assert falla_con(ValueError, s.crear_paquete, "Repetido", salida, regreso, 10, 0.2, [maipo.id, maipo.id])
    assert falla_con(ValueError, s.crear_paquete, "Fechas", salida, salida, 10, 0.2, [maipo.id, damas.id])
    assert falla_con(ValueError, s.crear_paquete, "Margen", salida, regreso, 10, -0.1, [maipo.id, damas.id])
    escapada = s.crear_paquete("Escapada de fin de semana", salida, regreso, 3, 0.20, [maipo.id, damas.id])
    assert escapada.precio_por_persona == 99600
    ok("RF-09/10 paquete de 2 a 5 destinos; precio 83.000 + 20 % = 99.600")

    # R7: cambiar un costo no altera el precio publicado
    s.modificar_destino(maipo.id, "Cajón del Maipo", "Región Metropolitana", "Montaña y río", 1, 50000)
    precio = [p for p, _ in s.listar_paquetes_disponibles() if p.id == escapada.id][0].precio_por_persona
    assert precio == 99600
    ok("RF-06 / R7 modificar un costo no cambia el precio ya publicado")

    # R8
    assert s.eliminar_destino(suelto.id) == "eliminado"
    assert s.eliminar_destino(elqui.id) == "eliminado"
    assert s.eliminar_destino(maipo.id) == "no disponible"
    assert falla_con(ValueError, s.crear_paquete, "Nuevo", salida, regreso, 5, 0.2, [maipo.id, damas.id])
    ok("RF-07 / R8 eliminar si no está en paquetes; si está, queda no disponible")
    s.cerrar_sesion()

    # RF-11..15 + R13..R16 + S1 + S6
    s.iniciar_sesion("carolina@correo.cl", "Carolina2026")
    assert falla_con(ValueError, s.reservar, escapada.id, 0)
    assert falla_con(ValueError, s.reservar, escapada.id, 4)
    reserva = s.reservar(escapada.id, 2)
    assert reserva.total == 199200
    assert falla_con(ValueError, s.reservar, escapada.id, 1)
    ok("RF-12/13 reserva valida personas >= 1, cupo y duplicado; total 2 × 99.600")

    libre = [l for p, l in s.listar_paquetes_disponibles() if p.id == escapada.id][0]
    assert libre == 1
    s.cancelar_reserva(reserva.id)
    libre = [l for p, l in s.listar_paquetes_disponibles() if p.id == escapada.id][0]
    assert libre == 3
    assert [r.estado for r in s.historial()] == ["cancelada"]
    ok("RF-14/15 historial propio; cancelar no borra y libera el cupo")

    # R15: paquete con salida vencida (se simula una temporada pasada)
    with s._bd.conectar() as con:
        cur = con.execute(
            "INSERT INTO paquetes (nombre, fecha_salida, fecha_regreso, cupo_maximo, margen, precio_por_persona) "
            "VALUES ('Temporada pasada', ?, ?, 10, 0.2, 1000)",
            ((hoy - timedelta(days=10)).isoformat(), (hoy - timedelta(days=5)).isoformat()))
        vencido = cur.lastrowid
        con.executemany("INSERT INTO paquete_destino VALUES (?, ?)", [(vencido, maipo.id), (vencido, damas.id)])
    assert vencido not in [p.id for p, _ in s.listar_paquetes_disponibles()]
    assert falla_con(ValueError, s.reservar, vencido, 1)
    ok("RF-11 / R15 un paquete vencido no se lista ni se puede reservar")

    # R17
    cli = s._sesion
    assert "345" not in cli.rut_enmascarado() and cli.telefono_enmascarado().endswith("5678")
    ok("R17 RUT y teléfono enmascarados")

    # RNF-08: la base rechaza datos inválidos aunque se salten las clases
    with s._bd.conectar() as con:
        try:
            con.execute("INSERT INTO destinos (nombre, zona, descripcion, duracion_dias, costo_base) "
                        "VALUES ('Malo', 'Z', 'D', 1, -5)")
            raise AssertionError("la base aceptó un costo negativo")
        except sqlite3.IntegrityError:
            pass
    ok("RNF-08 la base rechaza un costo negativo (CHECK)")

    print(f"\nTODAS LAS PRUEBAS OK ({len(resultados)} de {len(resultados)})")


if __name__ == "__main__":
    _pruebas()
