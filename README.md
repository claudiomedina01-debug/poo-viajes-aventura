# Viajes Aventura — Sistema de destinos, paquetes y reservas

Evaluación Sumativa 4 · Programación Orientada a Objeto Seguro (TI3021) · INACAP Valparaíso

Autor: Claudio Medina M. · Trabajo individual · Octubre de 2026

Sistema de terminal en Python para la agencia **Viajes Aventura**. Los socios administran destinos y arman paquetes de 2 a 5 destinos. El sistema calcula el precio, y los clientes se registran, reservan, ven su historial y cancelan. Todo queda guardado en SQLite, con contraseñas protegidas y datos personales ocultos.

## 1. Para evaluar

**Requisitos:** Python 3.11 o superior (probado en 3.11 y 3.13). No hay que instalar nada más: solo se usa la librería estándar.

| Paso | Windows (PowerShell) | Linux / Mac |
|---|---|---|
| 1. Pruebas automáticas | `python viajes.py` | `python3 viajes.py` |
| 2. Abrir el sistema | `python main.py` | `python3 main.py` |

- Las pruebas deben terminar en **`TODAS LAS PRUEBAS OK (15 de 15)`**. Usan una base temporal, así que no ensucian la real.
- **Primer uso:** como la base está vacía, el sistema pide crear la cuenta del **administrador** antes de mostrar el menú. Después, cualquier persona puede registrarse como cliente (opción 2).
- **Opcional:** para usar otro archivo de base de datos, definir la variable `DB_PATH` (ver `.env.example`). Ejemplo en PowerShell: `$env:DB_PATH="prueba.db"`.

Las instrucciones paso a paso, con datos de prueba, están en [`ENTREGA.md`](ENTREGA.md).

## 2. Qué hay en el repositorio

| Archivo / carpeta | Qué es |
|---|---|
| `viajes.py` | Las 8 clases del diagrama UML, la base de datos SQLite, el CRUD, el login y 15 pruebas automáticas |
| `main.py` | El menú de terminal. Solo pide y muestra datos: **no tiene SQL** |
| `requirements.txt` | Sin dependencias externas (solo librería estándar) |
| `.env.example` | Configuración opcional, sin secretos |
| `.gitignore` | Impide subir la base de datos (`*.db`), `.env` y archivos temporales |
| `ENTREGA.md` | Cómo ejecutar y probar el sistema |
| `diagramas/` | Casos de uso, 2 BPMN y diagrama de clases (`.png` claro/oscuro y `.drawio` editable) |
| `diagramas/historico/` | Versión 1 del diagrama de clases, antes de programar |
| `docs/REQUERIMIENTOS.md` | Supuestos S1–S6, problemas P1–P8, 15 RF, 12 RNF, prioridad y verificación |
| `docs/TRAZABILIDAD.md` | Cada requerimiento: problema → regla → caso de uso → BPMN → clase → evidencia |
| `docs/PLANIFICACION_AGIL.md` | Scrum: roles, 13 historias de usuario, 5 sprints, Definition of Done |
| `docs/SALIDA_TERMINAL.md` | Evidencia de ejecuciones reales, incluidos errores provocados a propósito |
| `docs/AUDITORIA.md` | Auditoría de seguridad: 14 controles, 4 hallazgos y riesgos que quedan |
| `docs/ANALISIS_IA.md` | 12 decisiones sobre lo que propuso la IA: adoptar, modificar o descartar |

## 3. Cómo está construida

**Programación orientada a objetos** según el diagrama `diagramas/Clases_ViajesAventura.png`:

| Clase | Qué representa | Tabla en la base |
|---|---|---|
| `Usuario` (abstracta) | Cualquier persona con cuenta: nombre, correo, clave protegida e intentos fallidos | `usuarios` |
| `Cliente` (hereda de Usuario) | Quien reserva. RUT y teléfono son privados y se muestran enmascarados | `usuarios` (rol `cliente`) |
| `Administrador` (hereda de Usuario) | Socio que gestiona destinos y paquetes | `usuarios` (rol `admin`) |
| `Destino` | Lugar con zona, duración y costo base; puede quedar "no disponible" | `destinos` |
| `Paquete` | Combina de 2 a 5 destinos (agregación), con fechas, cupo y precio fijo | `paquetes` + `paquete_destino` |
| `Reserva` | Un cliente reserva un paquete para N personas con un total fijo | `reservas` |
| `BaseDatos` | Abre la conexión, maneja transacciones y crea las tablas | — |
| `SistemaViajes` | Coordina todo: sesión, permisos por rol y operaciones | — |

**Conceptos de POO aplicados:**

- **Herencia y polimorfismo:** `Cliente` y `Administrador` heredan de `Usuario`, y cada uno responde distinto a `es_admin()`.
- **Clase abstracta:** no se puede crear un `Usuario` "a secas".
- **Encapsulamiento:** `_hash_clave`, `_sal`, `_rut` y `_telefono` son privados.
- **Composición:** `SistemaViajes` crea y contiene su `BaseDatos`.
- **Agregación:** `Paquete` agrupa `Destino` que existen por sí solos.

**Validación en 3 capas:** el menú revisa el formato → las clases revisan las reglas del negocio → la base revisa `NOT NULL`, `UNIQUE`, `CHECK` y claves foráneas.

**Precio (R6):** suma de costos × (1 + margen). Ejemplo: (45.000 + 38.000) × 1,20 = **$99.600** por persona. Queda fijo al publicar (R7).

## 4. Seguridad

| Protección | Cómo |
|---|---|
| Contraseñas | Hash **scrypt** con sal aleatoria; nunca se guardan legibles. Comparación en tiempo constante |
| Fuerza bruta | La cuenta se **bloquea** tras 3 intentos fallidos |
| Mensajes de login | Siempre "Correo o contraseña incorrectos": no revela qué correos existen |
| Inyección SQL | Todas las consultas usan parámetros `?` |
| Permisos | El rol se revisa **dentro de las clases** (un cliente no puede gestionar el catálogo ni ver reservas ajenas) |
| Datos personales (R17) | RUT y teléfono se muestran enmascarados (`12.***.***-*`); la base no se sube a GitHub |
| Errores | El programa no se cae y no muestra rutas ni trazas técnicas |
| Reservas simultáneas | Transacción `BEGIN IMMEDIATE`: dos reservas a la vez no pueden superar el cupo |

La auditoría encontró 4 hallazgos con pruebas reales. **3 se corrigieron**: nombre solo con números, "Cajón" y "Cajon" como destinos distintos, y RUT inválido avisado tarde. Detalle en [`docs/AUDITORIA.md`](docs/AUDITORIA.md).

## 5. Uso de inteligencia artificial

Herramientas: **Claude** (tutor y apoyo de diseño), **Claude Code** (revisión de carpetas) y **GitHub Copilot** (mensajes de commit). Cada sugerencia se comprobó contra el caso, la rúbrica o las pruebas antes de usarla.

| Decisión | Cantidad | Ejemplo |
|---|---|---|
| Adoptar | 4 | Las correcciones de H1–H3, comprobadas con 15 pruebas y una demostración manual |
| Modificar | 6 | El código del bloqueo deshacía el contador de intentos; la prueba lo detectó y se corrigió |
| Descartar | 2 | Claude Code marcó como "faltantes" archivos que existían con otro nombre |

Registro completo: [`docs/ANALISIS_IA.md`](docs/ANALISIS_IA.md).

## 6. Qué quedó fuera

Con honestidad, esto **no** está en esta entrega:

- **Pagos:** el caso menciona estados "Pagado / Pendiente", pero el pago queda fuera del alcance (supuesto S4). Las reservas solo están "confirmada" o "cancelada".
- **Desbloquear cuentas:** una cuenta bloqueada no se puede desbloquear desde el menú.
- **Cifrado de la base:** el RUT y el teléfono se guardan sin cifrar en el archivo local (se muestran enmascarados y el archivo no se sube).
- **Bitácora:** no se registra quién hizo cada acción.
- **Hallazgo H4:** el nombre inválido se avisa al final del registro (igual se rechaza).
- **Lo que el caso deja fuera del alcance:** facturación (SII), app móvil, integraciones, correos automáticos, informes y contabilidad.
- **Interfaz gráfica o web:** el sistema es de terminal, como pide la guía.

## 7. El menú

```
1. Iniciar sesión
2. Registrarme como cliente
0. Salir
```

| Administrador | Cliente |
|---|---|
| 1. Registrar destino | 1. Ver paquetes disponibles |
| 2. Modificar destino | 2. Reservar paquete |
| 3. Eliminar / desactivar destino | 3. Mi historial de reservas |
| 4. Listar destinos | 4. Cancelar una reserva |
| 5. Crear paquete | 0. Cerrar sesión |
| 6. Ver paquetes disponibles | |
| 0. Cerrar sesión | |
