# Salida de terminal — Viajes Aventura

Evidencia de **ejecuciones reales** del sistema, incluidos los **errores provocados a propósito**.
Cada bloque indica qué requerimiento y qué indicador de la rúbrica demuestra.

- Equipo: Windows 11 · Python 3.13 · SQLite (librería estándar)
- Carpeta de trabajo: `04_Codigo` (la ruta personal del equipo se reemplazó por `...`)

## 1. Pruebas automáticas — `python viajes.py` (3 de octubre de 2026, después del Paso 6)

Indicadores: **4.1.4.G.13** (código respeta el UML), **4.1.4.G.14** (persistencia), **4.1.4.G.15** (CRUD), **4.1.5.G.17/18** (autenticación).

```
Pruebas de viajes.py
  OK  RF-04 primer administrador (y solo uno)
  OK  RF-01 registro con RUT válido, correo único y clave mínima
  OK  H1 un nombre con solo números se rechaza
  OK  RNF-01/02/03/09 hash, bloqueo a los 3 intentos, mensaje genérico, inyección SQL
  OK  RNF-04 un cliente no puede gestionar el catálogo; sin sesión no hay historial
  OK  RF-05 destino con nombre único y costo > 0
  OK  H2 'Cajon' y 'Cajón' se detectan como el mismo destino
  OK  RF-09/10 paquete de 2 a 5 destinos; precio 83.000 + 20 % = 99.600
  OK  RF-06 / R7 modificar un costo no cambia el precio ya publicado
  OK  RF-07 / R8 eliminar si no está en paquetes; si está, queda no disponible
  OK  RF-12/13 reserva valida personas >= 1, cupo y duplicado; total 2 × 99.600
  OK  RF-14/15 historial propio; cancelar no borra y libera el cupo
  OK  RF-11 / R15 un paquete vencido no se lista ni se puede reservar
  OK  R17 RUT y teléfono enmascarados
  OK  RNF-08 la base rechaza un costo negativo (CHECK)

TODAS LAS PRUEBAS OK (15 de 15)
```

Cada línea "OK" prueba una regla del caso (R), un requerimiento (RF/RNF) o la corrección de un hallazgo (H). Antes del Paso 6 eran 13 pruebas; se agregaron 2 para H1 y H2. Las pruebas usan una base de datos temporal, así que no ensucian la base real.

## 2. Demostración manual — `python main.py` (2 de octubre de 2026)

### 2.1 Primer uso: se crea el administrador (RF-04, S3)

```
PS ...\04_Codigo> python main.py
============================================
   VIAJES AVENTURA · Sistema de reservas
============================================

Primera vez: cree la cuenta del administrador.
Nombre: Paulina Ovalle
Correo: paulina@viajesaventura.cl
Contraseña:
Repita la contraseña:
  ✓ Administrador creado. Ya puede iniciar sesión.

1. Iniciar sesión
2. Registrarme como cliente
0. Salir
Opción: 1
Correo: paulina@viajesaventura.cl
Contraseña:
  ✓ Bienvenido/a, Paulina Ovalle.
```

- La contraseña **no aparece en pantalla** al escribirla (`getpass`) y por eso tampoco queda en esta evidencia (RNF-01, RNF-05).
- El sistema exige crear el administrador antes de mostrar el menú (RF-04).

### 2.2 Administrador registra destinos (RF-05, R1, R2)

```
Opción: 1
Nombre: Cajon del Maipo
Zona: metropolitana
Descripción: montaña y rio
Duración en días: 1
Costo base por persona: 45000
  ✓ Destino registrado con id 1.

=== Administrador ===
  1. Registrar destino
  2. Modificar destino
  3. Eliminar / desactivar destino
  4. Listar destinos
  5. Crear paquete
  6. Ver paquetes disponibles
  0. Cerrar sesión
Opción: 1
Nombre: Islas Damas
Zona: Region de Coquimbo
Descripción: Reserva Marina
Duración en días: 1
Costo base por persona: 38000
  ✓ Destino registrado con id 2.
```

### 2.3 Error provocado: datos inválidos de un destino (RNF-07, capa 1 de validación)

```
Opción: 1
Nombre: gratis
Zona:
  ✗ Este dato es obligatorio.
Zona:
  ✗ Este dato es obligatorio.
Zona: costo cero
Descripción: cero
Duración en días: 2
Costo base por persona: 0
  ✗ Ingrese un número entero mayor o igual a 1.
Costo base por persona: 0
  ✗ Ingrese un número entero mayor o igual a 1.
Costo base por persona: 6
  ✓ Destino registrado con id 3.
```

- El menú **no acepta campos vacíos** ni un **costo 0** (R2). Recién con un costo mayor que cero el destino se registra.
- Indicador **4.1.4.G.15** (CRUD con validación).

### 2.4 Crear paquete: el sistema calcula el precio (RF-09, RF-10, R3, R5, R6)

```
Opción: 5

Destinos:
  [1] Cajon del Maipo · metropolitana · 1 día(s) · $45.000 · disponible
  [3] gratis · costo cero · 2 día(s) · $6 · disponible
  [2] Islas Damas · Region de Coquimbo · 1 día(s) · $38.000 · disponible
Nombre del paquete: Escapada fin de semana
Fecha de salida (dd-mm-aaaa):
  ✗ Use el formato dd-mm-aaaa (ejemplo: 15-12-2026).
Fecha de salida (dd-mm-aaaa): 15-12-2026
Fecha de regreso (dd-mm-aaaa): 17-12
  ✗ Use el formato dd-mm-aaaa (ejemplo: 15-12-2026).
Fecha de regreso (dd-mm-aaaa): 17-12-2026
Cupo máximo de personas: 3
Margen en % (habitual 20): 20
Ids de 2 a 5 destinos separados por coma: 1,2
  ✓ Paquete publicado con id 1. Precio por persona: $99.600
```

- Fechas con formato incorrecto se rechazan y se piden de nuevo (RNF-07).
- Precio calculado por el sistema: (45.000 + 38.000) × 1,20 = **$99.600** por persona → resuelve el error "de un cero" de Paulina (P2).

### 2.5 Error provocado: RUT inválido (RF-01, RNF-07, R9)

```
1. Iniciar sesión
2. Registrarme como cliente
0. Salir
Opción: 2

— Registro de cliente —
Nombre completo: 12345678-5
RUT (12345678-5): 12345678-9
Correo: prueba@correo.cl
Teléfono: 912345678
Contraseña (mínimo 8 caracteres):
Repita la contraseña:
  ✗ El RUT no es válido (revise el dígito verificador).
```

- El dígito verificador se valida con el algoritmo **módulo 11**: `12345678-9` es rechazado.

### 2.6 Registro correcto e inicio de sesión del cliente (RF-01, RF-02)

```
1. Iniciar sesión
2. Registrarme como cliente
0. Salir
Opción: 2

— Registro de cliente —
Nombre completo: Carolina Reyes
RUT (12345678-5): 12.345.678-5
Correo: carolina@correo.cl
Teléfono: 912345678
Contraseña (mínimo 8 caracteres):
Repita la contraseña:
  ✓ Registro exitoso. Ya puede iniciar sesión.

1. Iniciar sesión
2. Registrarme como cliente
0. Salir
Opción: 1
Correo: carolina@correo.cl
Contraseña:
  ✓ Bienvenido/a, Carolina Reyes.
```

### 2.7 Error provocado: reservar más personas que el cupo (RF-12, R14)

```
Opción: 2
  [1] Escapada fin de semana: Cajon del Maipo · Islas Damas
       15-12-2026 → 17-12-2026 · $99.600 por persona · cupo disponible: 3
Id del paquete: 1
Cantidad de personas: 5
  ✗ No hay cupo suficiente. Lugares disponibles: 3.
```

- Resuelve el problema de Matías: **vender 14 lugares en un paquete de 12** (P3, 6 reservas sobre el cupo).

### 2.8 Reserva correcta e historial (RF-12, RF-13, RF-14, R13)

```
Opción: 2
  [1] Escapada fin de semana: Cajon del Maipo · Islas Damas
       15-12-2026 → 17-12-2026 · $99.600 por persona · cupo disponible: 3
Id del paquete: 1
Cantidad de personas: 2
  ✓ Reserva n.º 1 confirmada. Total: $199.200

=== Cliente: Carolina Reyes ===
  1. Ver paquetes disponibles
  2. Reservar paquete
  3. Mi historial de reservas
  4. Cancelar una reserva
  0. Cerrar sesión
Opción: 3
  [1] Escapada fin de semana · 02-10-2026 · 2 persona(s) · $199.200 · confirmada
```

- Total calculado al reservar: 2 × $99.600 = **$199.200** (R13). El historial muestra solo las reservas de Carolina (R11).

### 2.9 Cierre de sesión y salida (RF-03)

```
Opción: 0
  ✓ Sesión cerrada.

1. Iniciar sesión
2. Registrarme como cliente
0. Salir
Opción: 0
Hasta pronto.
PS ...\04_Codigo> 
```

## 3. Hallazgos detectados durante la demostración

Probar el sistema como lo usaría una persona real reveló detalles que las pruebas automáticas no cubrían. Se registran en `docs/AUDITORIA.md`; los tres quedaron **corregidos** el 3 de octubre (ver bloque 5):

| # | Qué se observó | Dónde (bloque) | Riesgo | Estado |
|---|---|---|---|---|
| H1 | El campo **nombre** aceptó `12345678-5` (un RUT, sin letras) | 2.5 | Datos de baja calidad; el RUT podría quedar visible como nombre (R17) | ✅ Corregido (5.1) |
| H2 | Se registró **"Cajon del Maipo"** sin tilde: si otro socio escribe "Cajón del Maipo", el sistema los considera **distintos** | 2.2 | Vuelve el problema P1: destinos repetidos con nombres distintos | ✅ Corregido (5.2) |
| H3 | En el registro, el RUT inválido se avisa **al final**, después de pedir correo, teléfono y contraseña | 2.5 | Mala experiencia: hay que escribir todo de nuevo | ✅ Corregido (5.1) |

## 4. Resumen de cobertura

| Requerimiento | Demostrado en |
|---|---|
| RF-01 Registrar cliente | 2.5 (error) · 2.6 (correcto) · prueba automática |
| RF-02 / RF-03 Sesión | 2.1 · 2.6 · 2.9 |
| RF-04 Primer administrador | 2.1 |
| RF-05 Registrar destino | 2.2 · 2.3 |
| RF-09 / RF-10 Paquete y precio | 2.4 |
| RF-11 Paquetes disponibles | 2.7 · 2.8 |
| RF-12 / RF-13 Reservar y total | 2.7 (error) · 2.8 (correcto) |
| RF-14 Historial | 2.8 |
| RF-06, RF-07, RF-08, RF-15, RNF-02, R15, R17 | Pruebas automáticas (bloque 1) |
| H1, H2, H3 corregidos | Bloque 5 · pruebas automáticas H1 y H2 |

## 5. Verificación de las correcciones — `python main.py` (3 de octubre de 2026)

Indicador: **4.1.5.I.20** (evaluar la seguridad y corregir lo detectado). Se repitió a propósito lo que falló en la demostración del bloque 2.

### 5.1 H3 y H1: el RUT se revisa al escribirlo y el nombre debe tener letras

```
PS ...\04_Codigo> python main.py
============================================
   VIAJES AVENTURA · Sistema de reservas
============================================

1. Iniciar sesión
2. Registrarme como cliente
0. Salir
Opción: 2

— Registro de cliente —
Nombre completo: 12345678
RUT (12345678-5): 11111111-2
  ✗ RUT inválido: revise el dígito verificador (ejemplo: 12345678-5).
RUT (12345678-5): 11111111-1
Correo: prueba.h1@correo.cl
Teléfono: 912345678
Contraseña (mínimo 8 caracteres):
Repita la contraseña:
  ✗ El nombre solo puede tener letras y espacios (2 a 60 caracteres).
```

- **H3 corregido:** el RUT `11111111-2` se rechazó **en el mismo momento**, sin pedir el resto de los datos.
- **H1 corregido:** el nombre `12345678` ya no se acepta y el cliente **no** quedó registrado.
- La contraseña no se ve al escribirla (`getpass`, RNF-01).

### 5.2 H2: el mismo destino con y sin tilde

```
Opción: 1
Correo: Paulina@viajesaventura.cl
Contraseña:
  ✓ Bienvenido/a, Paulina Ovalle.

=== Administrador ===
Opción: 1
Nombre: cajón del Maipo
Zona: santiago
Descripción: valle
Duración en días: 2
Costo base por persona: 99000
  ✗ Ya existe un destino con ese nombre: Cajon del Maipo.

=== Administrador ===
Opción: 0
  ✓ Sesión cerrada.

1. Iniciar sesión
2. Registrarme como cliente
0. Salir
Opción: 0
Hasta pronto.
```

- **H2 corregido:** "cajón del Maipo" (con tilde y minúscula) se reconoció como el mismo destino "Cajon del Maipo" guardado el 2 de octubre. El problema P1 no vuelve a aparecer.
- El correo escrito con mayúscula (`Paulina@...`) igual funcionó: el sistema lo pasa a minúsculas antes de buscarlo.
