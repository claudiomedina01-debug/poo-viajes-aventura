# Requerimientos — Viajes Aventura

Criterio de la rúbrica: **4.1.1** (identificar, clasificar, priorizar y redactar requerimientos).
Fuente: caso "Viajes Aventura" (reglas R1–R17, entrevistas, cifras de la temporada y alcance).

> Una **regla de negocio** describe cómo funciona la agencia.
> Un **requerimiento** describe qué debe hacer el sistema. Este documento hace esa traducción.

## 1. Supuestos (vacíos del caso)

| ID | Vacío detectado | Supuesto adoptado | Fundamento |
|---|---|---|---|
| S1 | El caso no dice qué pasa si un cliente desiste de una reserva | El cliente puede cancelar **su propia** reserva mientras la fecha de salida no haya pasado. La reserva no se borra: pasa a estado "cancelada" y libera el cupo. La devolución del dinero queda fuera del sistema | Conserva el historial que hoy falta (31 consultas respondidas revisando el cuaderno) y el pago está fuera del alcance |
| S2 | El caso no dice qué pasa con un paquete cuando termina su temporada | Un paquete con fecha de salida vencida deja de mostrarse como disponible, pero no se borra | Evita las 3 reservas sobre fechas vencidas (R15) sin perder el historial |
| S3 | El caso no dice quién puede modificar el catálogo | Solo el rol **Administrador** gestiona destinos y paquetes. El Cliente consulta y reserva. El primer administrador se crea al usar el sistema por primera vez | Hoy los 3 socios editan la misma planilla, lo que generó destinos repetidos y precios mal calculados |
| S4 | El pago está fuera del alcance, pero el caso muestra estados "Pagado/Pendiente" | La reserva queda "confirmada" al registrarse. La transferencia la verifica un socio a mano, fuera del sistema | La pasarela de pago y la verificación automática están fuera del alcance |
| S5 | R7 habla de "publicar" un paquete, pero no dice cuándo ocurre | El paquete se publica en el momento en que el administrador lo crea, y ahí queda fijo su precio por persona | Solución simple que cumple R7: los paquetes publicados conservan su precio |
| S6 | El caso detectó 19 reservas duplicadas, pero no da una regla para evitarlas | Un cliente no puede tener 2 reservas activas del mismo paquete. Para cambiar la cantidad de personas, cancela y vuelve a reservar | Ataca directamente el problema de duplicados medido en la temporada |


## 2. Problemas del caso (punto de partida)

Cada requerimiento indica qué problema resuelve (columna **Problema**).

| ID | Problema detectado en el caso | Evidencia |
|---|---|---|
| P1 | Catálogo desordenado: destinos repetidos con nombres distintos y destinos que ya no se operan siguen visibles | Entrevista Paulina; 4 destinos no operados visibles |
| P2 | Precios mal calculados a mano y que cambian después de vender | Error "de un cero"; 4 paquetes con precio distinto al cobrado |
| P3 | Se venden más lugares que el cupo del paquete | 6 reservas sobre el cupo (entrevista Matías) |
| P4 | Se venden paquetes cuya fecha de salida ya pasó | 3 reservas sobre fechas vencidas |
| P5 | Reservas duplicadas, anotadas por socios distintos | 19 duplicadas al cierre |
| P6 | Datos sensibles (RUT, teléfono) en una planilla que circula por correo | Entrevista Ignacio |
| P7 | No hay historial: responder qué reservó un cliente obliga a revisar el cuaderno | 31 consultas respondidas a mano |
| P8 | No existe acceso controlado: cualquiera edita todo | 3 socios editan la misma planilla |

## 3. Requerimientos funcionales (RF)

Formato: "El sistema debe…". **Origen** = regla (R) o supuesto (S) que lo justifica.

### 3.1 Acceso y usuarios

| ID | Requerimiento | Actor | Origen | Problema | Criterio de aceptación |
|---|---|---|---|---|---|
| RF-01 | El sistema debe permitir que un cliente se registre con nombre, RUT, correo electrónico, teléfono y contraseña | Cliente | R9 | P6, P7 | Se rechaza un correo ya registrado; todos los campos son obligatorios |
| RF-02 | El sistema debe permitir iniciar sesión con correo y contraseña | Cliente, Administrador | R11 | P8 | Con datos correctos entra; con datos incorrectos muestra un mensaje genérico |
| RF-03 | El sistema debe permitir cerrar la sesión | Cliente, Administrador | R11 | P8 | Después de cerrar sesión no se puede reservar ni ver reservas |
| RF-04 | El sistema debe crear el primer administrador la primera vez que se ejecuta | Administrador | S3 | P8 | Si no existe ningún administrador, el sistema lo pide antes de mostrar el menú |

### 3.2 Destinos

| ID | Requerimiento | Actor | Origen | Problema | Criterio de aceptación |
|---|---|---|---|---|---|
| RF-05 | El sistema debe permitir registrar un destino con nombre, zona, descripción, duración en días y costo base por persona | Administrador | R1, R2 | P1 | Se rechaza un nombre repetido y un costo menor o igual a cero |
| RF-06 | El sistema debe permitir modificar los datos de un destino | Administrador | R1, R2, R7 | P1, P2 | Los cambios no alteran el precio de paquetes ya publicados |
| RF-07 | El sistema debe eliminar un destino que no está en ningún paquete, y marcar como "no disponible" uno que sí está | Administrador | R8 | P1 | Un destino no disponible no aparece al crear paquetes nuevos |
| RF-08 | El sistema debe listar los destinos del catálogo indicando si están disponibles | Administrador | R8 | P1 | El listado muestra nombre, zona, duración, costo y disponibilidad |

### 3.3 Paquetes

| ID | Requerimiento | Actor | Origen | Problema | Criterio de aceptación |
|---|---|---|---|---|---|
| RF-09 | El sistema debe permitir crear un paquete con nombre, fecha de salida, fecha de regreso, cupo máximo, margen y entre 2 y 5 destinos disponibles distintos | Administrador | R3, R4, R5, S3 | P1, P2 | Se rechaza: menos de 2 o más de 5 destinos, un destino repetido, regreso no posterior a la salida, cupo ≤ 0 |
| RF-10 | El sistema debe calcular el precio por persona como la suma de los costos base de los destinos más el margen, y fijarlo al publicar el paquete | Sistema | R6, R7, S5 | P2 | Ej.: 45.000 + 38.000 = 83.000 con 20 % → 99.600; el margen nunca es negativo |
| RF-11 | El sistema debe listar los paquetes disponibles mostrando destinos, fechas, precio por persona y cupo disponible | Cliente, Administrador | R14, R15, S2 | P3, P4 | No aparecen paquetes con fecha de salida vencida; cupo disponible = cupo máximo − personas reservadas |

### 3.4 Reservas

| ID | Requerimiento | Actor | Origen | Problema | Criterio de aceptación |
|---|---|---|---|---|---|
| RF-12 | El sistema debe permitir que un cliente autenticado reserve un paquete indicando la cantidad de personas | Cliente | R11, R12, R14, R15, R16, S6 | P3, P4, P5 | Se rechaza si: supera el cupo disponible, la salida ya pasó, personas < 1, o el cliente ya tiene una reserva activa de ese paquete |
| RF-13 | El sistema debe calcular el total de la reserva (precio × personas) al reservar y guardarlo sin cambios | Sistema | R13 | P2 | Si después cambia un costo de destino, el total guardado no cambia |
| RF-14 | El sistema debe mostrar al cliente el historial de **sus** reservas | Cliente | R11, R12 | P7 | Un cliente nunca ve reservas de otro cliente |
| RF-15 | El sistema debe permitir que un cliente cancele su propia reserva si la salida no ha pasado | Cliente | S1 | P3, P7 | La reserva queda "cancelada" y el cupo vuelve a estar disponible |

## 4. Requerimientos no funcionales (RNF)

Describen **cómo** debe comportarse el sistema (cualidades), no qué funciones ofrece.

| ID | Tipo | Requerimiento | Origen | Problema | Criterio de aceptación |
|---|---|---|---|---|---|
| RNF-01 | Seguridad | El sistema debe guardar las contraseñas como hash con sal usando `hashlib.scrypt` de la librería estándar de Python, nunca como texto | R10 | P6 | En la base no aparece ninguna contraseña legible; dos usuarios con la misma clave tienen hash distinto |
| RNF-02 | Seguridad | El sistema debe bloquear el inicio de sesión de una cuenta después de 3 intentos fallidos seguidos | R11 | P8 | Al 4.º intento el sistema rechaza el acceso aunque la clave sea correcta |
| RNF-03 | Seguridad | El sistema debe exigir contraseñas de al menos 8 caracteres y mostrar un mensaje genérico ante un login fallido, sin decir si el correo existe | R10, R11 | P8 | "Correo o contraseña incorrectos" en ambos casos |
| RNF-04 | Control de acceso | El sistema debe verificar el rol (Cliente o Administrador) antes de cada operación, tanto en el menú como en las clases | R11, S3 | P8 | Un cliente no puede crear destinos ni ver reservas ajenas, ni siquiera llamando directo a la clase |
| RNF-05 | Privacidad | El sistema no debe mostrar el RUT ni el teléfono en listados ni en mensajes de error | R17 | P6 | Ningún listado ni error del sistema muestra esos datos |
| RNF-06 | Privacidad | Los datos deben guardarse solo en la base local; el archivo de base de datos no se sube al repositorio | R17 | P6 | `*.db` está en `.gitignore` |
| RNF-07 | Validación | El sistema debe validar todo dato ingresado: formato de correo, RUT con dígito verificador, teléfono, fechas (dd-mm-aaaa) y números positivos | Alcance | P1, P5 | Un dato inválido se rechaza con un mensaje claro y se pide de nuevo |
| RNF-08 | Integridad | La base de datos debe reforzar las reglas con restricciones `NOT NULL`, `UNIQUE`, `CHECK` y claves foráneas | R1–R5, R9, R16 | P1, P5 | Un dato inválido que se salte el menú igual es rechazado por la base |
| RNF-09 | Seguridad | Todas las consultas SQL deben usar parámetros (`?`), nunca texto concatenado | Alcance | P6 | Escribir `' OR 1=1 --` como correo no permite entrar |
| RNF-10 | Confiabilidad | El programa no debe cerrarse ante un error: cada error se captura con `try/except` y se muestra un mensaje claro, sin rutas ni trazas técnicas | Alcance | — | Ninguna prueba de error provoca un cierre inesperado |
| RNF-11 | Usabilidad | El sistema debe funcionar con un menú de terminal en español, con opciones numeradas y mensajes de confirmación | — | — | Cada acción termina con un mensaje de éxito o de error |
| RNF-12 | Mantenibilidad | El sistema debe construirse en Python 3 con SQLite y solo la librería estándar, separando el dominio (`viajes.py`) del menú (`main.py`) | Guía U4 | — | `requirements.txt` sin dependencias externas; `main.py` no contiene SQL |

## 5. Priorización (Alta / Media / Baja)

**Criterios usados**

| Prioridad | Criterio | Pregunta clave |
|---|---|---|
| **Alta** | Lo exige una regla del caso (R1–R17) o el alcance mínimo, o resuelve un problema grave medido en la temporada (sobreventa, datos expuestos, precios) | ¿El sistema sirve a la agencia sin esto? → **No** |
| **Media** | Mejora importante, pero el sistema funciona sin ella; o nace de un supuesto propio | ¿Funciona sin esto? → Sí, pero peor |
| **Baja** | Comodidad o presentación | ¿Alguien lo extrañaría en la primera versión? → Poco |

Los requerimientos **Alta** se construyen primero (Sprint 1 y 2); los **Media** y **Baja**, después.

### 5.1 Funcionales

| ID | Requerimiento (resumen) | Prioridad | Justificación |
|---|---|---|---|
| RF-01 | Registrar cliente | **Alta** | R9; sin clientes registrados no hay reservas |
| RF-02 | Iniciar sesión | **Alta** | R11: solo un cliente autenticado reserva |
| RF-03 | Cerrar sesión | Media | Buena práctica de seguridad, pero el flujo principal funciona sin ella |
| RF-04 | Crear primer administrador | **Alta** | Sin administrador no se puede cargar el catálogo (S3) |
| RF-05 | Registrar destino | **Alta** | R1, R2; base de todo el catálogo |
| RF-06 | Modificar destino | Media | Necesario para actualizar costos, pero no bloquea vender |
| RF-07 | Eliminar / dejar no disponible | **Alta** | R8; resuelve P1 (4 destinos no operados visibles) |
| RF-08 | Listar destinos | Media | Apoya al administrador; el paquete puede crearse igual |
| RF-09 | Crear paquete | **Alta** | R3–R5; es el producto que vende la agencia |
| RF-10 | Calcular y fijar precio | **Alta** | R6, R7; resuelve P2 (error "de un cero", 4 precios distintos) |
| RF-11 | Listar paquetes disponibles | **Alta** | R14, R15; el cliente no puede reservar sin ver qué hay |
| RF-12 | Reservar paquete | **Alta** | R12, R14–R16; resuelve P3, P4 y P5 (6 + 3 + 19 casos) |
| RF-13 | Total fijo de la reserva | **Alta** | R13; resuelve P2 |
| RF-14 | Historial propio | **Alta** | Está en el alcance; resuelve P7 (31 consultas a mano) |
| RF-15 | Cancelar reserva | Media | Nace del supuesto S1, no de una regla explícita |

### 5.2 No funcionales

| ID | Requerimiento (resumen) | Prioridad | Justificación |
|---|---|---|---|
| RNF-01 | Contraseña con hash + sal | **Alta** | R10; indicador 4.1.5.G.17 |
| RNF-02 | Bloqueo tras 3 intentos | **Alta** | Indicador 4.1.5.G.18 (validar credenciales) |
| RNF-03 | Clave mínima 8 caracteres y mensaje genérico | Media | Refuerza RNF-01/02, pero no es una regla del caso |
| RNF-04 | Control de acceso por rol | **Alta** | R11 y S3; resuelve P8 |
| RNF-05 | RUT y teléfono ocultos | **Alta** | R17; resuelve P6; indicador 4.1.5.I.19 |
| RNF-06 | Base de datos fuera del repositorio | Media | Protege datos, pero es configuración (`.gitignore`) |
| RNF-07 | Validar todo dato ingresado | **Alta** | Está en el alcance ("validación de todo dato ingresado") |
| RNF-08 | Restricciones en la base de datos | Media | Segunda capa de defensa; la primera es RNF-07 |
| RNF-09 | Consultas parametrizadas | **Alta** | Evita inyección SQL; protege P6 |
| RNF-10 | El programa nunca se cae | **Alta** | Un sistema que se cierra pierde la reserva en curso |
| RNF-11 | Menú en español con mensajes claros | Baja | Presentación; no cambia lo que el sistema hace |
| RNF-12 | Python estándar y archivos separados | Media | Facilita mantener el sistema; no lo ve el usuario |

**Resumen:** 18 Alta · 8 Media · 1 Baja (27 requerimientos).

## 6. Verificación: ¿los requerimientos resuelven el problema del cliente?

Indicador **4.1.1.I.4**. Se revisa en tres direcciones: problemas, reglas y alcance.

### 6.1 Cada problema del caso queda resuelto

| Problema | Cifra del caso | Lo resuelven | Cómo |
|---|---|---|---|
| P1 Catálogo desordenado | 4 destinos no operados visibles | RF-05, RF-07, RF-08, RNF-08 | Nombre único; destino en uso pasa a "no disponible" y no se ofrece en paquetes nuevos |
| P2 Precios mal calculados | 4 paquetes con precio distinto al cobrado | RF-10, RF-13, RF-06 | El sistema calcula el precio, lo fija al publicar y el total de la reserva no cambia |
| P3 Sobreventa de cupos | 6 reservas sobre el cupo | RF-11, RF-12 | Cupo disponible calculado; se rechaza la reserva que lo supera |
| P4 Venta con fecha vencida | 3 reservas | RF-11, RF-12 | Paquete vencido no se lista ni se puede reservar (compara con la fecha de hoy) |
| P5 Reservas duplicadas | 19 duplicadas | RF-12, RNF-07 | Un cliente no puede tener 2 reservas activas del mismo paquete (S6) |
| P6 Datos sensibles expuestos | Planilla enviada por correo | RNF-01, RNF-05, RNF-06, RNF-09 | Clave con hash, RUT/teléfono ocultos, base fuera del repositorio, SQL parametrizado |
| P7 Sin historial | 31 consultas a mano | RF-01, RF-14, RF-15 | Cada cliente tiene cuenta y ve su historial; cancelar no borra |
| P8 Sin control de acceso | 3 socios editan todo | RF-02, RF-04, RNF-02, RNF-04 | Login, roles y bloqueo por intentos |

**Resultado:** los 8 problemas tienen al menos un requerimiento que los resuelve. ✅

### 6.2 Cada regla de negocio queda cubierta

| Regla | Requerimiento | Regla | Requerimiento |
|---|---|---|---|
| R1 datos del destino, nombre único | RF-05, RNF-08 | R10 contraseña no legible | RNF-01 |
| R2 costo > 0 | RF-05, RF-06 | R11 solo autenticado; cada uno ve lo suyo | RF-02, RF-14, RNF-04 |
| R3 2 a 5 destinos sin repetir | RF-09 | R12 datos de la reserva | RF-12 |
| R4 destino en varios paquetes | RF-09 | R13 total fijo | RF-13 |
| R5 fechas y cupo válidos | RF-09 | R14 no superar el cupo | RF-11, RF-12 |
| R6 precio = costos + margen | RF-10 | R15 no reservar vencidos | RF-11, RF-12 |
| R7 precio fijo al publicar | RF-10, RF-06 | R16 personas ≥ 1 | RF-12, RNF-08 |
| R8 eliminar o "no disponible" | RF-07 | R17 RUT y teléfono ocultos | RNF-05 |
| R9 datos del cliente, correo único | RF-01 | | |

**Resultado:** las 17 reglas están cubiertas. ✅

### 6.3 Cada punto del alcance tiene su requerimiento

| Alcance acordado por los socios | Requerimientos |
|---|---|
| Destinos: registrar, modificar, dejar no disponible, listar | RF-05, RF-06, RF-07, RF-08 |
| Paquetes: crear, fechas y cupo, calcular precio, consultar disponibilidad | RF-09, RF-10, RF-11 |
| Reservas: registro y autenticación, reservar, almacenar, historial | RF-01, RF-02, RF-12, RF-13, RF-14 |
| Seguridad: autenticación, validación de datos, protección de credenciales y datos sensibles | RNF-01 a RNF-09 |
| **Fuera del alcance** (pagos, SII, app móvil, integraciones, correos, informes, contabilidad) | Ningún requerimiento los incluye; el pago se trata en el supuesto S4 |

**Resultado:** todo el alcance está cubierto y no se agregó nada fuera de él. ✅
