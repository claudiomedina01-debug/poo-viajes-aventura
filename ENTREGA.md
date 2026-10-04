# Instrucciones de entrega — Viajes Aventura

Pasos para ejecutar y probar el sistema en unos 10 minutos. No hay que instalar nada: solo **Python 3.11 o superior**.

> En Linux / Mac, cambiar `python` por `python3`.

## 1. Descargar

```
git clone https://github.com/claudiomedina01-debug/poo-viajes-aventura.git
cd poo-viajes-aventura
```

(O descargar el ZIP desde GitHub con **Code → Download ZIP** y abrir una terminal dentro de la carpeta.)

## 2. Pruebas automáticas

```
python viajes.py
```

Resultado esperado: 15 líneas `OK` y al final **`TODAS LAS PRUEBAS OK (15 de 15)`**.
Las pruebas usan una base temporal: no crean ni modifican `viajes_aventura.db`.

## 3. Probar el sistema a mano

```
python main.py
```

La primera vez se crea el archivo `viajes_aventura.db` y el sistema pide el **administrador**. Datos sugeridos (las contraseñas no se ven al escribirlas):

| Paso | Qué hacer | Qué debe pasar |
|---|---|---|
| 1 | Crear admin: `Paulina Ovalle` · `paulina@viajesaventura.cl` · clave `ClaveAdmin2026` (2 veces) | "Administrador creado" |
| 2 | Opción 1, iniciar sesión con ese correo y clave | Menú de administrador |
| 3 | Opción 1 (registrar destino): `Cajón del Maipo` · `Región Metropolitana` · `Montaña y río` · `1` · `45000` | Destino registrado |
| 4 | Opción 1 otra vez: `Isla Damas` · `Región de Coquimbo` · `Reserva marina` · `1` · `38000` | Destino registrado |
| 5 | **Error a propósito:** opción 1 con nombre `cajon del maipo` | "Ya existe un destino con ese nombre" (sin importar tildes ni mayúsculas) |
| 6 | Opción 5 (crear paquete): `Escapada` · salida y regreso en fechas futuras (`dd-mm-aaaa`) · cupo `3` · margen `20` · ids `1,2` | Precio por persona **$99.600** |
| 7 | Opción 0 (cerrar sesión) | Vuelve al menú inicial |
| 8 | **Error a propósito:** opción 2 (registrarse) con RUT `12345678-9` | Se rechaza **al instante**: dígito verificador inválido |
| 9 | Registrarse bien: `Carolina Reyes` · RUT `12345678-5` · `carolina@correo.cl` · `912345678` · clave `Carolina2026` | "Registro exitoso" |
| 10 | Iniciar sesión como Carolina | Menú de cliente |
| 11 | **Error a propósito:** opción 2 (reservar) paquete `1` para `5` personas | "No hay cupo suficiente. Lugares disponibles: 3" |
| 12 | Opción 2: paquete `1` para `2` personas | Reserva confirmada, total **$199.200** |
| 13 | Opción 3 (historial) | Muestra la reserva "confirmada" |
| 14 | Opción 4 (cancelar) la reserva | "Reserva cancelada. El cupo quedó liberado" |
| 15 | **Error a propósito:** cerrar sesión e intentar entrar 3 veces con clave incorrecta | Al 3.er intento: "Cuenta bloqueada…" |

## 4. Volver a empezar

Para partir con la base vacía, borrar el archivo `viajes_aventura.db` (o usar otro archivo con la variable `DB_PATH`, ver `.env.example`).

## 5. Dónde está cada evidencia

| Para revisar… | Ver |
|---|---|
| Requerimientos, supuestos y prioridad | `docs/REQUERIMIENTOS.md` |
| Diagramas UML y BPMN | `diagramas/` |
| Trazabilidad requerimiento → código → evidencia | `docs/TRAZABILIDAD.md` |
| Planificación ágil (Scrum) | `docs/PLANIFICACION_AGIL.md` |
| Ejecuciones reales y errores provocados | `docs/SALIDA_TERMINAL.md` |
| Seguridad | `docs/AUDITORIA.md` |
| Uso crítico de IA | `docs/ANALISIS_IA.md` |
