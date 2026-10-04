# Matriz de trazabilidad — Viajes Aventura

Indicador **4.1.2.I.8**: coherencia y trazabilidad entre requerimientos, procesos y diseño UML.

> Cómo leerla: cada fila sigue un requerimiento desde el **problema del caso** hasta la **clase y método** que lo cumplen.
> La columna **Evidencia** muestra dónde se comprobó cada requerimiento con una ejecución real:
> - **ST 2.5** = bloque 2.5 de `docs/SALIDA_TERMINAL.md` (demostración manual).
> - **Prueba RF-01** = línea "OK RF-01…" de las pruebas automáticas (`python viajes.py`, 15 de 15).

**Diagramas:** casos de uso (`diagramas/CasosDeUso_ViajesAventura.png`) · BPMN reservar (`diagramas/BPMN_ReservarPaquete.png`) · BPMN armar paquete (`diagramas/BPMN_ArmarPaquete.png`) · clases (`diagramas/Clases_ViajesAventura.png`).

## 1. Requerimientos funcionales

| RF | Problema | Regla / Supuesto | Caso de uso | Paso BPMN | Clase · método | Evidencia |
|---|---|---|---|---|---|---|
| RF-01 Registrar cliente | P6, P7 | R9 | CU-01 | — | `SistemaViajes.registrar_cliente()` · `Cliente.__init__()` · `Cliente.validar_rut()` · `main.pedir_rut()` (H3) | ST 2.5 (error) · ST 2.6 · ST 5.1 · Prueba RF-01 · Prueba H1 |
| RF-02 Iniciar sesión | P8 | R11 | CU-02 | Reservar: "Iniciar sesión" → "Validar credenciales" → ◆ · Armar: "Validar credenciales y rol" | `SistemaViajes.iniciar_sesion()` · `Usuario.verificar_clave()` | ST 2.1 · ST 2.6 · Prueba RNF-01/02/03/09 |
| RF-03 Cerrar sesión | P8 | R11 | CU-03 | — | `SistemaViajes.cerrar_sesion()` | ST 2.9 · ST 5.2 |
| RF-04 Crear primer administrador | P8 | S3 | CU-08 | — | `SistemaViajes.existe_admin()` · `crear_admin_inicial()` · `Administrador` | ST 2.1 · Prueba RF-04 |
| RF-05 Registrar destino | P1 | R1, R2 | CU-09 | — | `SistemaViajes.registrar_destino()` · `Destino.validar()` · `Destino.normalizar()` (H2) | ST 2.2 · ST 2.3 · ST 5.2 · Prueba RF-05 · Prueba H2 |
| RF-06 Modificar destino | P1, P2 | R1, R2, R7 | CU-10 | — | `SistemaViajes.modificar_destino()` · `Destino.validar()` | Prueba RF-06 / R7 |
| RF-07 Eliminar / no disponible | P1 | R8 | CU-11 | — | `SistemaViajes.eliminar_destino()` · `Destino.marcar_no_disponible()` | Prueba RF-07 / R8 |
| RF-08 Listar destinos | P1 | R8 | CU-12 | Armar: "Listar destinos disponibles" | `SistemaViajes.listar_destinos()` | ST 2.4 (listado antes de armar el paquete) |
| RF-09 Crear paquete | P1, P2 | R3, R4, R5, S3 | CU-13 | Armar: "Ingresar datos…" → "Validar datos" → ◆ | `SistemaViajes.crear_paquete()` · `Paquete.validar()` | ST 2.4 · Prueba RF-09/10 |
| RF-10 Calcular y fijar precio | P2 | R6, R7, S5 | CU-14 («include» de CU-13) | Armar: "Calcular precio" → "Publicar y fijar precio" | `Paquete.calcular_precio()` · atributo `precio_por_persona` | ST 2.4 ($99.600) · Prueba RF-09/10 · Prueba RF-06 / R7 |
| RF-11 Listar paquetes disponibles | P3, P4 | R14, R15, S2 | CU-04 | Reservar: "Listar paquetes vigentes con cupo" | `SistemaViajes.listar_paquetes_disponibles()` · `Paquete.esta_vigente()` · `Paquete.cupo_disponible()` | ST 2.7 · ST 2.8 · Prueba RF-11 / R15 |
| RF-12 Reservar paquete | P3, P4, P5 | R11, R12, R14–R16, S6 | CU-05 + CU-15 («include») | Reservar: "Elegir paquete" → "Verificar fecha, cupo, personas y duplicado" → ◆ | `SistemaViajes.reservar()` · `Paquete.esta_vigente()` · `Paquete.cupo_disponible()` | ST 2.7 (error de cupo) · ST 2.8 · Prueba RF-12/13 |
| RF-13 Total fijo de la reserva | P2 | R13 | CU-05 | Reservar: "Calcular total" → "Guardar reserva" | `Reserva.calcular_total()` · atributo `total` | ST 2.8 ($199.200) · Prueba RF-12/13 |
| RF-14 Historial propio | P7 | R11, R12 | CU-06 | — | `SistemaViajes.historial()` · `SistemaViajes._exigir_cliente()` | ST 2.8 · Prueba RF-14/15 · Prueba RNF-04 |
| RF-15 Cancelar reserva | P3, P7 | S1 | CU-07 | — | `SistemaViajes.cancelar_reserva()` · `Reserva.cancelar()` · `Reserva.esta_activa()` | Prueba RF-14/15 |

## 2. Requerimientos no funcionales

| RNF | Regla | Dónde se cumple en el diseño | Evidencia |
|---|---|---|---|
| RNF-01 Hash + sal | R10 | `Usuario.generar_hash()` · `verificar_clave()` · atributos privados `_hash_clave`, `_sal` | Prueba RNF-01/02/03/09 · ST 2.1 (la clave no se ve) |
| RNF-02 Bloqueo tras 3 intentos | R11 | `Usuario.MAX_INTENTOS` · `registrar_intento_fallido()` · `esta_bloqueado()` · BPMN Reservar (nota del ◆ credenciales) | Prueba RNF-01/02/03/09 |
| RNF-03 Clave mínima y mensaje genérico | R10, R11 | `SistemaViajes.registrar_cliente()` · `iniciar_sesion()` | Prueba RNF-01/02/03/09 · Prueba RF-01 (clave corta) |
| RNF-04 Control de acceso por rol | R11, S3 | `SistemaViajes._exigir_admin()` · `_exigir_cliente()` · `Usuario.es_admin()` (abstracto, polimorfismo) | Prueba RNF-04 |
| RNF-05 RUT y teléfono ocultos | R17 | Atributos privados `Cliente._rut`, `_telefono` · `rut_enmascarado()` · `telefono_enmascarado()` | Prueba R17 |
| RNF-06 Base fuera del repositorio | R17 | `.gitignore` (`*.db`) | ✅ ya está en el repositorio |
| RNF-07 Validar todo dato | Alcance | `Cliente.validar_rut()` · `Destino.validar()` · `Paquete.validar()` · menú en `main.py` | ST 2.3 · ST 2.4 · ST 2.5 · ST 5.1 · Prueba RF-01 · Prueba H1 |
| RNF-08 Restricciones en la base | R1–R5, R9, R16 | `BaseDatos.crear_tablas()` (`NOT NULL`, `UNIQUE`, `CHECK`, claves foráneas) | Prueba RNF-08 |
| RNF-09 Consultas parametrizadas | Alcance | Todas las consultas de `SistemaViajes` usan `?` | Prueba RNF-01/02/03/09 (`' OR 1=1 --` no entra) |
| RNF-10 Nunca se cae | Alcance | `main.py` (`try/except` por tipo de error) | ST bloques 2 y 5: ningún error provocado cerró el programa |
| RNF-11 Menú en español | — | `main.py` | ST bloques 2 y 5 |
| RNF-12 Python estándar, archivos separados | Guía U4 | `viajes.py` (clases) · `main.py` (menú) · `requirements.txt` | `requirements.txt` sin paquetes · `main.py` sin SQL · `AUDITORIA.md` C14 |

## 3. Verificación de coherencia

| Revisión | Resultado |
|---|---|
| ¿Todo RF tiene un caso de uso? | ✅ 15 de 15 |
| ¿Todo caso de uso viene de un RF? | ✅ 15 de 15 (CU-14 y CU-15 son «include» de RF-10 y RF-12) |
| ¿Los 2 procesos BPMN usan solo pasos que existen como RF? | ✅ Sí |
| ¿Toda clase del diagrama participa en algún requerimiento? | ✅ 8 de 8 |
| ¿Toda regla R1–R17 llega hasta una clase? | ✅ Sí (ver columna "Regla") |
| ¿El código respeta el diagrama, miembro por miembro? | ✅ Sí. El diagrama se actualizó al programar (la v1 quedó en `diagramas/historico`, ver `ANALISIS_IA.md` #9). Diferencias menores que se conocen: `Destino.normalizar()` y `SistemaViajes._exigir_nombre_libre()` se agregaron en el Paso 6, y los métodos privados de apoyo (`_buscar_destino()`) no se dibujaron |
| ¿Todo requerimiento tiene evidencia de ejecución? | ✅ 15 de 15 RF y 12 de 12 RNF |
