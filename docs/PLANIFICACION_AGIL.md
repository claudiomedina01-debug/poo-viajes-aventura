# Planificación ágil (Scrum) — Viajes Aventura

Criterio de la rúbrica: **4.1.3** (roles, Product Backlog, Sprint Backlog, tiempos y entregables).
Período: **30 de septiembre al 5 de octubre de 2026** · Entrega: **lunes 5 de octubre, 23:00 (AAI)**.

## 1. Roles y responsabilidades

El trabajo es **individual**, por lo que una misma persona cumple los tres roles de Scrum. Para no mezclarlos, cada rol tiene su momento y su artefacto.

| Rol Scrum | Quién | Responsabilidades | Artefacto que cuida |
|---|---|---|---|
| **Product Owner** | Claudio Medina (representa a los socios de Viajes Aventura) | Traducir las necesidades de Paulina, Matías e Ignacio en requerimientos; decidir prioridades; aceptar o rechazar cada entrega | Product Backlog · `docs/REQUERIMIENTOS.md` |
| **Scrum Master / Líder de proyecto** | Claudio Medina | Planificar los sprints, cuidar los plazos, eliminar bloqueos, registrar avances y retrospectivas | Sprint Backlog · `Avance_Viajes_Aventura.md` |
| **Equipo de desarrollo** | Claudio Medina | Diseñar, programar, probar y documentar | Código, diagramas y `docs/` |

**Partes interesadas (stakeholders):** Paulina Ovalle (catálogo y paquetes), Matías Bórquez (atención y reservas), Ignacio Salas (administración y datos). Sus entrevistas son la fuente de las historias de usuario.

**Herramientas de IA:** se usan como **apoyo** (explicaciones, borradores, revisión), no como miembro del equipo. Toda sugerencia se revisa y se registra en `docs/ANALISIS_IA.md` con la decisión Adoptar / Modificar / Descartar.

**Por qué este reparto es razonable:** en un equipo de una persona el riesgo es que "programar" se coma a "planificar" y a "revisar". Separar los roles por momento (planificación → construcción → revisión) obliga a detenerse, priorizar y aceptar cada entrega antes de avanzar.

## 2. Product Backlog

Formato de historia de usuario: *"Como **rol**, quiero **acción**, para **beneficio**"*.
Prioridad tomada de `REQUERIMIENTOS.md` (sección 5). Esfuerzo en **puntos de historia** (escala 1, 2, 3, 5): 1 = muy simple, 5 = complejo.

| ID | Historia de usuario | Requerimientos | Prioridad | Puntos |
|---|---|---|---|---|
| HU-01 | Como **socio**, quiero crear el primer administrador al usar el sistema por primera vez, para que solo él gestione el catálogo | RF-04 | Alta | 2 |
| HU-02 | Como **usuario**, quiero iniciar y cerrar sesión de forma segura, para que nadie más use mi cuenta | RF-02, RF-03, RNF-01, RNF-02, RNF-03, RNF-04 | Alta | 5 |
| HU-03 | Como **cliente**, quiero registrarme con mis datos, para poder reservar | RF-01, RNF-05, RNF-07 | Alta | 3 |
| HU-04 | Como **administrador**, quiero registrar y modificar destinos, para mantener el catálogo al día sin duplicados | RF-05, RF-06 | Alta | 3 |
| HU-05 | Como **administrador**, quiero eliminar un destino o dejarlo "no disponible", para que no se ofrezca lo que ya no operamos | RF-07 | Alta | 2 |
| HU-06 | Como **administrador**, quiero listar los destinos, para ver el estado del catálogo | RF-08 | Media | 1 |
| HU-07 | Como **administrador**, quiero armar un paquete con 2 a 5 destinos y que el precio se calcule solo, para no equivocarme en la suma | RF-09, RF-10 | Alta | 5 |
| HU-08 | Como **cliente**, quiero ver solo los paquetes vigentes y con cupo, para no elegir uno que no puedo comprar | RF-11 | Alta | 3 |
| HU-09 | Como **cliente**, quiero reservar indicando cuántas personas viajan, para asegurar mi lugar | RF-12, RF-13 | Alta | 5 |
| HU-10 | Como **cliente**, quiero ver el historial de mis reservas, para no tener que preguntar a la agencia | RF-14 | Alta | 2 |
| HU-11 | Como **cliente**, quiero cancelar mi reserva antes de la salida, para liberar el cupo si no puedo viajar | RF-15 | Media | 2 |
| HU-12 | Como **socio**, quiero que el sistema valide los datos y nunca se caiga, para confiar en la información | RNF-07 a RNF-12 | Alta | 3 |
| HU-13 | Como **equipo**, quiero auditar la seguridad y documentar el uso de IA, para demostrar que el código es confiable | RNF-01 a RNF-09 · ANALISIS_IA · AUDITORIA | Alta | 3 |

**Total:** 13 historias · 39 puntos · 11 Alta, 2 Media.

## 3. Sprint Backlog

Sprints cortos (1 a 2 días) porque el plazo total es de 6 días. Cada sprint termina con un **commit en GitHub** como evidencia.

| Sprint | Fechas | Objetivo | Contenido | Entregable | Estado |
|---|---|---|---|---|---|
| **0 · Análisis** | 30 sep – 1 oct | Entender el caso y definir qué construir | Leer pauta y rúbrica · crear repositorio · requerimientos, supuestos y prioridad | Repositorio + `docs/REQUERIMIENTOS.md` | ✅ Terminado |
| **1 · Diseño** | 1 – 2 oct | Modelar la solución | Casos de uso · BPMN reservar y armar paquete · diagrama de clases · trazabilidad · esta planificación | `diagramas/` + `docs/TRAZABILIDAD.md` + `docs/PLANIFICACION_AGIL.md` | ✅ Terminado |
| **2 · Catálogo** | 2 – 3 oct | Construir la base y el lado del administrador | Base de datos SQLite · HU-01, HU-04, HU-05, HU-06, HU-07, HU-12 | `viajes.py` (clases + BD + CRUD) · `main.py` (menú admin) | Pendiente |
| **3 · Clientes y seguridad** | 3 – 4 oct | Construir el lado del cliente y asegurar el sistema | HU-02, HU-03, HU-08, HU-09, HU-10, HU-11, HU-13 | Login seguro · reservas · `docs/AUDITORIA.md` · `docs/SALIDA_TERMINAL.md` · `docs/ANALISIS_IA.md` | Pendiente |
| **4 · Cierre** | 4 – 5 oct | Entregar y preparar la defensa | README final · informe Word (plantilla INACAP) · revisión contra la rúbrica · guion de defensa | Informe + repositorio subidos al AAI **antes de las 23:00** | Pendiente |

**Puntos por sprint:** Sprint 2 = 16 puntos (HU-01 2 + HU-04 3 + HU-05 2 + HU-06 1 + HU-07 5 + HU-12 3) · Sprint 3 = 23 puntos (HU-02 5 + HU-03 3 + HU-08 3 + HU-09 5 + HU-10 2 + HU-11 2 + HU-13 3).

## 4. Ceremonias (adaptadas a trabajo individual)

| Ceremonia | Cómo se hace | Duración |
|---|---|---|
| **Sprint Planning** | Al inicio de cada sprint: elegir las historias del backlog según prioridad | 15 min |
| **Daily** | Revisar `Avance_Viajes_Aventura.md`: qué hice, qué haré, qué me bloquea | 5 min |
| **Sprint Review** | Mostrar el resultado funcionando (captura o ejecución) y hacer el commit | 10 min |
| **Retrospectiva** | Tres preguntas: ¿qué salió bien?, ¿qué mejorar?, ¿qué cambio aplico? | 5 min |

## 5. Definición de "Terminado" (Definition of Done)

Una historia está terminada solo si:

1. Cumple sus criterios de aceptación (`REQUERIMIENTOS.md`).
2. El código coincide con el diagrama de clases.
3. Se probó y la ejecución quedó en `docs/SALIDA_TERMINAL.md`, incluidos los errores provocados.
4. El uso de IA quedó registrado en `docs/ANALISIS_IA.md`.
5. Está subida a GitHub con un commit en español que dice qué cambió.

## 6. Retrospectivas registradas

| Sprint | ¿Qué salió bien? | ¿Qué mejorar? | Cambio aplicado |
|---|---|---|---|
| 0 · Análisis | Reusar la estructura del proyecto EcoTech ahorró tiempo; los supuestos quedaron justificados | Al subir por arrastre, GitHub omitió los archivos que empiezan con punto (`.gitignore`, `.env.example`) | Revisar la lista de archivos antes de cada commit |
| 1 · Diseño | La trazabilidad confirmó que no faltaba ningún requerimiento | Una subida quedó en la carpeta equivocada (`historico`) y la traducción automática del navegador cambió nombres de carpetas | Revisar la ruta antes de confirmar y desactivar la traducción en GitHub |

## 7. Cronograma de entregables

| Fecha | Entregable | Criterio |
|---|---|---|
| Jue 1 oct | Requerimientos completos | 4.1.1 |
| Vie 2 oct | Diagramas, trazabilidad y planificación | 4.1.2 · 4.1.3 |
| Sáb 3 oct | Código con base de datos y CRUD | 4.1.4 |
| Dom 4 oct | Seguridad, auditoría, evidencias e informe | 4.1.5 |
| Lun 5 oct | Entrega en el AAI (antes de las 23:00) y guion de defensa | Todos |
