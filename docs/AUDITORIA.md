# Auditoría de seguridad — Viajes Aventura

Indicadores **4.1.5.G.17** (proteger credenciales), **4.1.5.G.18** (validar credenciales), **4.1.5.I.19** (proteger datos personales) y **4.1.5.I.20** (evaluar la seguridad del sistema con apoyo de IA).

- **Fecha:** 3 de octubre de 2026
- **Qué se revisó:** `viajes.py` (clases y base de datos), `main.py` (menú) y `.gitignore`
- **Cómo se revisó:**
  1. Revisión del código, línea por línea, contra los RNF de seguridad (`docs/REQUERIMIENTOS.md`).
  2. Pruebas automáticas (`python viajes.py`).
  3. Demostración manual como un usuario real, provocando errores a propósito (`docs/SALIDA_TERMINAL.md`, bloque 2).
  4. Corrección de lo encontrado y una nueva demostración para comprobarlo (bloque 5).

**Escala de severidad**

| Nivel | Significado |
|---|---|
| Alta | Permite entrar sin permiso, ver datos ajenos o perder información |
| Media | Deja guardar datos incorrectos o hace volver un problema del caso |
| Baja | Molesta al usuario, pero no pone en riesgo datos ni reglas |

## 1. Controles de seguridad verificados

Cada control se buscó en el código y se comprobó con una prueba o con la demostración.

| # | Control | Qué amenaza evita | Dónde está en el código | Evidencia | Resultado |
|---|---|---|---|---|---|
| C1 | Contraseña guardada como **hash scrypt con sal** de 16 bytes (RNF-01, R10) | Que alguien que copie la base lea las contraseñas | `Usuario.generar_hash()` | Prueba RNF-01: la clave no aparece dentro del hash | ✅ Cumple |
| C2 | Comparación del hash en **tiempo constante** (`secrets.compare_digest`) | Adivinar la clave midiendo cuánto tarda la respuesta | `Usuario.verificar_clave()` | Revisión de código | ✅ Cumple |
| C3 | **Bloqueo** tras 3 intentos fallidos (RNF-02) | Probar claves una tras otra (fuerza bruta) | `Usuario.esta_bloqueado()` · `SistemaViajes.iniciar_sesion()` | Prueba RNF-02: al 4.º intento rechaza incluso la clave correcta | ✅ Cumple |
| C4 | **Mensaje genérico** "Correo o contraseña incorrectos" (RNF-03) | Descubrir qué correos están registrados | `SistemaViajes.iniciar_sesion()` | Prueba RNF-03 | ✅ Cumple |
| C5 | Clave de **mínimo 8 caracteres** (RNF-03) | Claves fáciles de adivinar | `Usuario.__init__()` | Prueba RF-01 (clave "corta" rechazada) | ✅ Cumple |
| C6 | La clave **no se ve** al escribirla (`getpass`) | Que otra persona la lea en la pantalla o quede en la evidencia | `main.pedir_clave()` | `SALIDA_TERMINAL.md` 2.1 y 5.1 | ✅ Cumple |
| C7 | **Consultas parametrizadas** `?` (RNF-09) | Inyección SQL | Todas las consultas de `viajes.py` | Prueba RNF-09: `' OR 1=1 --` no permite entrar | ✅ Cumple |
| C8 | **Control de acceso por rol** dentro de las clases (RNF-04, R11) | Que un cliente gestione el catálogo o vea reservas ajenas | `_exigir_admin()` · `_exigir_cliente()` | Prueba RNF-04 | ✅ Cumple |
| C9 | **RUT y teléfono enmascarados** (RNF-05, R17) | Exponer datos personales en pantalla | `Cliente.rut_enmascarado()` · `telefono_enmascarado()` | Prueba R17 | ✅ Cumple |
| C10 | La **base de datos no se sube** al repositorio (RNF-06) | Publicar datos personales en GitHub | `.gitignore` (`*.db`, `.env`) | El repositorio no tiene archivos `.db` | ✅ Cumple |
| C11 | **Validación en 3 capas**: menú → clases → base (RNF-07, RNF-08) | Datos inválidos que se salten una sola revisión | `main.py` · `validar()` · `CHECK`, `UNIQUE`, claves foráneas | Prueba RNF-08: la base rechaza un costo negativo | ✅ Cumple |
| C12 | **Transacciones** (`BEGIN IMMEDIATE` y `ROLLBACK` ante error) | Reservas a medias o dos reservas que superen el cupo al mismo tiempo | `BaseDatos.conectar()` | Prueba RF-12/13 (cupo y duplicado) | ✅ Cumple |
| C13 | **Errores sin rutas ni trazas** técnicas (RNF-10) | Mostrar información interna a un atacante | `main.py` (`try/except` en el menú y al final del programa) | Demostración: ningún error cerró el programa | ✅ Cumple |
| C14 | Solo **librería estándar** de Python (RNF-12) | Dependencias externas con fallas de seguridad | `requirements.txt` sin paquetes | Revisión de código | ✅ Cumple |

## 2. Hallazgos

Los hallazgos H1 a H3 aparecieron en la demostración manual del 2 de octubre: **las pruebas automáticas no los detectaban**. H4 se detectó al revisar la demostración de verificación.

| # | Severidad | Qué se observó | Causa | Corrección | Evidencia | Estado |
|---|---|---|---|---|---|---|
| H1 | Media | El nombre aceptó `12345678-5`, un RUT sin letras | Solo se revisaba que el nombre no estuviera vacío | Patrón `PATRON_NOMBRE`: solo letras (con tildes y ñ), espacios, guion y apóstrofo, de 2 a 60 caracteres. Está en `Usuario`, así que vale para Cliente y Administrador (herencia) | Prueba H1 · `SALIDA_TERMINAL.md` 5.1 | ✅ Corregido |
| H2 | Media | "Cajon del Maipo" y "Cajón del Maipo" se guardaban como destinos distintos: **vuelve el problema P1** | `COLLATE NOCASE` ignora mayúsculas, pero no tildes | `Destino.normalizar()` quita tildes, mayúsculas y espacios dobles; `_exigir_nombre_libre()` compara con los destinos existentes dentro de la misma transacción | Prueba H2 · `SALIDA_TERMINAL.md` 5.2 | ✅ Corregido |
| H3 | Baja | El RUT inválido se avisaba al final del registro, después de pedir todo lo demás | El RUT solo se revisaba al crear el objeto `Cliente` (capa 2) | `main.pedir_rut()` lo revisa apenas se escribe (capa 1), con el mismo `Cliente.validar_rut()` | `SALIDA_TERMINAL.md` 5.1 | ✅ Corregido |
| H4 | Baja | Después de corregir H1, el nombre inválido también se avisa al final del registro | Igual que H3: el nombre solo se revisa en la capa 2 | Agregar `pedir_nombre()` en `main.py`, igual que `pedir_rut()` | `SALIDA_TERMINAL.md` 5.1 | ⏳ Pendiente (mejora) |

> H4 no pone en riesgo los datos: el nombre inválido **igual se rechaza** y el cliente no queda registrado. Solo obliga a escribir de nuevo. Se dejó pendiente para no cambiar el código cerca de la entrega.

## 3. Detalle de las correcciones

### H1 — `viajes.py`

```python
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]{2,60}$")

# dentro de Usuario.__init__
if not PATRON_NOMBRE.match(nombre):
    raise ValueError("El nombre solo puede tener letras y espacios (2 a 60 caracteres).")
```

### H2 — `viajes.py`

```python
@staticmethod
def normalizar(nombre):                      # Destino
    sin_tildes = unicodedata.normalize("NFD", nombre or "")
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().split())
```

`"Cajón  del Maipo"` → `"cajon del maipo"`. `registrar_destino()` y `modificar_destino()` llaman a `_exigir_nombre_libre()` antes de guardar. Al modificar, el destino no se compara consigo mismo.

### H3 — `main.py`

```python
def pedir_rut(mensaje="RUT (12345678-5): "):
    while True:
        rut = pedir_texto(mensaje)
        if Cliente.validar_rut(rut):
            return rut
        print("  ✗ RUT inválido: revise el dígito verificador (ejemplo: 12345678-5).")
```

**Resultado:** las pruebas automáticas pasaron de **13 a 15** (se agregaron las de H1 y H2) y todas terminan en OK.

## 4. Riesgos que quedan y mejoras futuras

Ningún sistema queda "100 % seguro". Estos riesgos se conocen y se aceptan para el alcance de esta entrega:

| # | Riesgo | Por qué se acepta ahora | Mejora propuesta |
|---|---|---|---|
| RR1 | El RUT y el teléfono se guardan **sin cifrar** dentro del archivo `.db` | La base es local, no se sube a GitHub (C10) y los datos se muestran enmascarados (C9) | Cifrar esas columnas, o proteger el archivo con permisos del sistema operativo |
| RR2 | Una cuenta bloqueada **no se puede desbloquear** desde el menú | Es más seguro que desbloquear sin control; el caso no lo pide | Opción del administrador para desbloquear, dejando registro de quién lo hizo |
| RR3 | No hay **bitácora** (registro) de quién hizo cada acción | No está en el alcance del caso | Tabla `bitacora` con fecha, usuario y acción |
| RR4 | La clave solo exige 8 caracteres, sin pedir números ni símbolos | Lo que exige el RNF-03 | Exigir mezcla de letras y números |
| RR5 | H4: el nombre inválido se avisa al final del registro | No afecta la seguridad (ver hallazgo H4) | `pedir_nombre()` en `main.py` |

## 5. Uso de IA en la auditoría

- Claude (Anthropic) apoyó la revisión del código y propuso las correcciones de H1, H2 y H3.
- **Cada propuesta se comprobó:** primero con las pruebas automáticas en el PC del estudiante (15 de 15) y después repitiendo a mano los errores de la demostración original.
- H4 se encontró al **revisar críticamente** el resultado de la corrección de H1, no porque la IA lo avisara antes.
- El detalle de lo que se adoptó, modificó o descartó está en `docs/ANALISIS_IA.md`.

## 6. Conclusión

- Los **14 controles** revisados cumplen.
- De **4 hallazgos**, **3 se corrigieron** y se comprobaron con evidencia real. El cuarto (H4, severidad baja) queda documentado como mejora.
- La lección principal: **las pruebas automáticas no bastan**. Probar el sistema como lo usaría una persona real encontró problemas que las pruebas no veían, y uno de ellos (H2) hacía volver el problema P1 del caso: destinos duplicados.
