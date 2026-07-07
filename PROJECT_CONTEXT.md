# PROJECT_CONTEXT.md - LicitAI Perú

## 1. Visión General del Proyecto
LicitAI Perú es un SaaS B2B robusto de monitoreo inteligente de licitaciones públicas del Estado Peruano (SEACE / OECE). 

Objetivo principal: Ayudar a empresas peruanas a encontrar, priorizar y analizar licitaciones de forma mucho más inteligente que la competencia actual (LicitaWins y similares), usando Machine Learning y RAG de alta calidad.

Diferenciadores clave:
- Scoring predictivo de probabilidad de ganar (XGBoost)
- Sistema RAG avanzado para consultas en lenguaje natural
- Datos oficiales OCDS procesados y enriquecidos
- Arquitectura limpia y escalable

## 2. Stack Tecnológico (Definitivo)
- Backend: Python 3.11 + FastAPI
- Base de Datos: Supabase (PostgreSQL 16 + pgvector)
- Machine Learning: XGBoost + scikit-learn + sentence-transformers
- Ingesta de datos: Polars + httpx
- Repositorio: GitHub
- Despliegue Backend: Render (free tier)
- Frontend: Next.js 15 + TypeScript (Fase 2)
- Entrenamiento de modelos: Google Colab / Kaggle

## 3. Plan de 14 Días (MVP Robusto)

**Semana 1 – Backend + Data + ML**
- Día 1: Arquitectura, estructura del proyecto y documentación base (COMPLETADO)
- Día 2: Ingesta robusta y automática de datos OCDS del OECE
- Día 3: Modelado de base de datos + migraciones (SQLAlchemy + Alembic)
- Día 4: Backend FastAPI profesional + endpoints principales
- Día 5: Sistema de Scoring con Machine Learning (XGBoost)
- Día 6-7: Sistema RAG básico + pruebas

**Semana 2 – Inteligencia + Producto**
- Día 8-9: Sistema de alertas inteligentes + suscripciones
- Día 10-11: Frontend básico (Next.js)
- Día 12-14: Testing, documentación, optimizaciones y despliegue inicial

## 4. Estado Actual (Actualizado 2026-07-07)
- Día 1 completado.
- **Día 2 (Ingesta)**: Código robusto implementado + estrategia migrada a API oficial.

**Logros principales hasta hoy:**
- Backend **LIVE** en Render (https://licitai-peru-api.onrender.com)
- Nueva estrategia de ingesta: API oficial `https://contratacionesabiertas.oece.gob.pe/api/v1` (paginada + dataSegmentation) — mucho mejor que el bulk JSONL.
- Endpoints en producción:
  - `POST /ingest/run` (dispara ingesta en background usando API)
  - `GET /ingest/status`
  - `GET /db/table-status` (verifica tabla)
  - `GET /licitaciones` + `GET /licitaciones/{ocid}`
- Tabla `licitaciones` verificada vía API: **existe** y actualmente tiene **0 registros**.
- Pipeline actualizado para soportar ingesta vía API/v1 (paginación, dataSegmentation, etc.).
- Decisión ML: trabajo pesado (XGBoost + embeddings) se hará de forma externa (Kaggle/Colab/HF).

- Git: https://github.com/berthidalgo/licitalab
- Deploy: licitai-peru-api (Render free)

## 5. Instrucciones para Grok Build (IMPORTANTE)

Cuando empieces una sesión nueva en Grok Build, sigue siempre este orden:

1. Lee primero este archivo `PROJECT_CONTEXT.md`
2. Revisa qué día estamos y qué se debe hacer según el plan de 14 días
3. Pregunta al usuario si quiere continuar con el siguiente día o si hay cambios
4. Mantén siempre una arquitectura limpia, profesional y robusta (nivel Staff Engineer)
5. Documenta decisiones importantes dentro de los archivos o en este mismo contexto
6. No hagas soluciones "básicas". Todo debe ser de calidad production-ready desde el inicio.

## 6. Reglas de Trabajo
- Priorizar calidad y robustez sobre velocidad.
- Usar siempre las mejores prácticas (type hints, validación, logging, etc.).
- El código debe ser fácil de entender para otros desarrolladores.
- Todo debe poder desplegarse en free tier (Render + Supabase).
- Mantener el enfoque B2B y diferenciado de la competencia.

## 7. Estrategia de Machine Learning y RAG (Actualizado 2026-07-07)
**Decisión importante:** El trabajo pesado de ML (entrenamiento de XGBoost, generación de embeddings con sentence-transformers, etc.) se hará **principalmente de forma externa**.

Razones:
- Render free tier tiene limitaciones fuertes para builds pesados (torch + sentence-transformers).
- El entrenamiento y precomputo de embeddings/scores se hace mucho mejor en herramientas con GPU: **Kaggle, Google Colab, Hugging Face**.
- El backend en Render se enfocará en servir datos ya procesados.

Estrategia recomendada:
- Usar Kaggle/Colab/HF para entrenar modelos y generar embeddings.
- Guardar resultados (scores + embeddings vectoriales) directamente en Supabase (tabla licitaciones + posiblemente tabla embeddings con pgvector).
- El backend de FastAPI solo lee/expone los datos precomputados.
- Más adelante evaluar si se necesita un servicio separado para inferencia ligera.

Esto se activará cuando lleguemos a Día 5 (Scoring) y Días 6-7 (RAG).

## 8. Estado al Pausar - 2026-07-07 (Fin de sesión)

**Día actual: Día 2 (Ingesta) - Muy avanzado**

**Lo que está listo:**
- Backend completamente desplegado y vivo.
- Ingesta migrada a la API oficial `/api/v1/releases` (forense completo realizado).
- Soporte para paginación + `dataSegmentation` (ideal para cargas incrementales).
- Tabla verificada: existe y accesible.
- Endpoints de ingesta + consulta listos.
- Decisión ML externa documentada.

**Próxima sesión (cuando retomemos):**
1. Disparar ingesta real usando la API (recomendado con `dataSegmentation` actual o páginas recientes).
2. Verificar que los datos lleguen correctamente a Supabase.
3. Mejorar extracción de campos en el processor (awards, suppliers, etc.).
4. Cerrar oficialmente Día 2.
5. Pasar a Día 3 (schema + preparación para scoring).

**Comando útil para retomar:**
```bash
# Local
python -m app.ingest.run_ingest --use-api --data-segmentation 2026-07 --load-to-supabase

# O vía la API viva:
curl -X POST https://licitai-peru-api.onrender.com/ingest/run \
  -H "Content-Type: application/json" \
  -d '{"load_to_supabase": true}'
```

**Pausa solicitada por el usuario.** Todo limpio y listo para continuar.
