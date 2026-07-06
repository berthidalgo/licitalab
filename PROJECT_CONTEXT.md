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

## 4. Estado Actual
- Día 1 completado (replicado + commiteado).
- Día 2 en progreso / implementado:
  - Sistema de ingesta OCDS robusto (downloader + processor + pipeline)
  - Usa Polars (rápido) + httpx (streaming + retries)
  - Archivos: backend/app/ingest/{downloader.py, processor.py, pipeline.py, run_ingest.py}
  - data/raw/ y data/processed/ preparados
- Git inicializado y conectado a: https://github.com/berthidalgo/licitalab.git
- Estructura de carpetas completa.
- Próximo: Probar con URL real + integración con Supabase.

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

## 7. Próximo Paso Inmediato
Día 2 base completado (ingesta). 
Siguientes pasos recomendados:
- Probar la ingesta con una URL real del portal
- Guardar datos en Supabase (loader)
- Mejorar extracción de campos (awards, suppliers, etc.)
- Añadir scheduler / tarea diaria
- Documentar en README cómo correr la ingesta
