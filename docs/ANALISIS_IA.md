# Análisis del uso de IA — Viajes Aventura

Indicador **4.1.4.I.16** (usar, analizar y mejorar críticamente lo generado por IA) y **4.1.5.I.20** (evaluar la seguridad con apoyo de IA).

**Herramientas usadas:** Claude (Anthropic) como tutor y asistente de diseño · Claude Code para revisar carpetas · GitHub Copilot (sugerencias de mensajes de commit).
**Regla:** cada vez que la IA propone algo se anota una fila **en el momento**, no al final. Ninguna sugerencia se usa sin revisarla contra el caso, la rúbrica o el código.

## Registro

| # | Fecha | Etapa | Herramienta | Qué propuso la IA | Problema detectado | Decisión | Fundamento técnico |
|---|---|---|---|---|---|---|---|
| 1 | 30-09-2026 | Repositorio | GitHub Copilot | Mensaje del commit que crea `diagramas/historico/.gitkeep` | Ninguno: describe con precisión el cambio | **Adoptar** | Mensaje corto, en imperativo, dice qué archivo y para qué |
| 2 | 01-10-2026 | Requerimientos | Claude | Seis supuestos (S1–S6): tres vacíos que nombra el caso y tres detectados al analizarlo | Se verificó que S4–S6 tuvieran evidencia en el caso (estados "Pagado/Pendiente", R7 "publicar", 19 reservas duplicadas) | **Adoptar** | Cada supuesto quedó con vacío, decisión y fundamento, como exige el caso |
| 3 | 01-10-2026 | Requerimientos | Claude | Priorizar con el método MoSCoW | La guía de la carpeta del proyecto pedía Alta / Media / Baja, más simple de justificar | **Modificar** | Se usaron 3 niveles con un criterio escrito para cada uno (pregunta clave) |
| 4 | 01-10-2026 | Requerimientos | Claude | Tabla de requerimientos funcionales con origen y criterio de aceptación | Faltaba mostrar qué problema del cliente resuelve cada uno (indicador 4.1.1.I.4) | **Modificar** | Se agregaron los problemas P1–P8 con su evidencia y una columna "Problema" en cada requerimiento |
| 5 | 01-10-2026 | Requerimientos | GitHub Copilot | Descripción del commit de `REQUERIMIENTOS.md` | Estaba en inglés; el proyecto se documenta en español | **Modificar** | Se reescribió el mensaje en español y se quitó la descripción larga |
| 6 | 02-10-2026 | Organización | Claude Code | Informe de estructura: marcó como "faltantes" la guía y la rúbrica del AAI | Falso positivo: los archivos existían con otro nombre (`instrucciones_eva_4.pdf`, `rubrica_eva_4.xlsx`) | **Descartar** | Se comprobó a mano que eran los mismos documentos; el informe comparaba nombres, no contenido |
| 7 | 02-10-2026 | Organización | Claude Code | Afirmó que `06_Uso_IA/ANALISIS_IA.md` tenía "la tabla de registro llena" | Al abrirlo, solo tenía la plantilla con una fila vacía | **Descartar** | Se verificó el contenido real antes de unirlo con este registro |
| 8 | 02-10-2026 | Código | Claude | Código de `iniciar_sesion()` que avisaba el error de clave **dentro** de la transacción | La prueba de bloqueo falló: el `ROLLBACK` deshacía el contador de intentos y la cuenta nunca se bloqueaba | **Modificar** | Primero se guarda el contador y el error se avisa **después** de cerrar la transacción; la prueba RNF-02 pasa |
| 9 | 02-10-2026 | Código / Diagramas | Claude | Diagrama de clases v1, hecho antes de programar | Al programar cambiaron algunos métodos y atributos; el diagrama ya no coincidía con el código | **Modificar** | Se actualizó el diagrama para que coincida con el código (4.1.4.G.13); la v1 se guardó en `diagramas/historico` como evidencia del cambio |
| 10 | 03-10-2026 | Seguridad | Claude | Correcciones de los hallazgos H1, H2 y H3 de la demostración | Se comprobaron en el PC del estudiante: 15 de 15 pruebas y una nueva demostración manual | **Adoptar** | Evidencia en `SALIDA_TERMINAL.md` (bloques 1 y 5) y `AUDITORIA.md` |
| 11 | 03-10-2026 | Seguridad | Claude | Validar el nombre (H1) solo dentro de la clase `Usuario` | Al revisar la demostración, el nombre inválido se avisa recién al final del registro (el mismo problema que H3) | **Adoptar** | El dato inválido igual se rechaza; la mejora se registró como hallazgo H4 (pendiente) en `AUDITORIA.md` |
| 12 | 03-10-2026 | Seguridad | GitHub Copilot | Mensaje y descripción del commit de `AUDITORIA.md`: "Revise y actualice…", "se mejoró la estructura" | Mal redactado y no era cierto: el documento estaba vacío, no se "mejoró" | **Modificar** | Se reemplazó por "Auditoría de seguridad (Paso 6)" con una descripción exacta |

## Resumen

| Decisión | Cantidad | Qué demuestra |
|---|---|---|
| Adoptar | 4 | La sugerencia era correcta y se verificó contra el caso |
| Modificar | 6 | La idea servía, pero hubo que corregirla o ajustarla (código, diagrama, rúbrica, idioma o formato) |
| Descartar | 2 | La IA se equivocó y se detectó revisando la evidencia real |

> **Total: 12 registros.** La IA acertó en 4 casos, en 6 hubo que ajustar lo que propuso y en 2 se equivocó. Ninguna sugerencia se usó sin comprobarla.
