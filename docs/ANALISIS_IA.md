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

## Resumen

| Decisión | Cantidad | Qué demuestra |
|---|---|---|
| Adoptar | 2 | La sugerencia era correcta y se verificó contra el caso |
| Modificar | 3 | La idea servía, pero se ajustó a la rúbrica, al idioma o al formato pedido |
| Descartar | 2 | La IA se equivocó y se detectó revisando la evidencia real |

> Las filas del código (Paso 5) y de la auditoría de seguridad (Paso 6) se agregan a medida que se trabaja.
