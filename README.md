# LicitAI Perú

Sistema inteligente de monitoreo y análisis de licitaciones públicas del Estado Peruano impulsado por Machine Learning y RAG.

## Objetivo del Proyecto
Plataforma B2B que permite a empresas peruanas detectar, priorizar y analizar licitaciones públicas de forma inteligente mediante:
- Scoring predictivo de probabilidad de ganar
- Consultas en lenguaje natural (RAG)
- Alertas inteligentes
- Análisis de competencia

## Stack Tecnológico
- **Backend**: Python 3.11 + FastAPI
- **Base de Datos**: Supabase (PostgreSQL + pgvector)
- **Machine Learning**: XGBoost + sentence-transformers
- **Ingesta de datos**: Polars + httpx (datos OCDS oficiales de Perú)
- **Despliegue**: Render (backend) + Vercel (frontend)
- **Repositorio**: GitHub

## Estructura del Proyecto
```
licitai-peru/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── ingest/
│   │   ├── ml/
│   │   ├── rag/
│   │   └── utils/
│   ├── main.py
│   ├── requirements.txt
│   └── alembic.ini
├── data/raw/
├── notebooks/
├── frontend/
├── .env.example
├── .gitignore
└── README.md
```

## Instalación Local (para desarrollo)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Estado actual:** Día 1 completado - Arquitectura base robusta

**Plan de 14 días:**
- Semana 1: Backend + Data + ML
- Semana 2: RAG + Alertas + Frontend + Despliegue

## Despliegue en Render (Backend)

1. Ve a [Render](https://dashboard.render.com) y conecta tu repo `berthidalgo/licitalab`.

2. Usa el archivo `render.yaml` que ya está en la raíz (Blueprint).

3. En el dashboard de Render, agrega las variables de entorno (NUNCA las subas al repo):
   - `SUPABASE_URL`
   - `SUPABASE_KEY` (usa la **service_role** key)
   - `DATABASE_URL`
   - `ENV=production`
   - `DEBUG=false`

4. El servicio se llamará `licitai-peru-api` por defecto.

### Comando manual (si no usas render.yaml)
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Health check
El endpoint `/health` ya está implementado.

## Variables de entorno importantes
Copia de `.env.example` y renómbralo a `.env` localmente.
Nunca subas `.env` ni archivos con tokens.

## Render API Key
Si guardaste tu Render API Key, úsala para automatizar despliegues futuros con el CLI de Render:
```bash
render deploy
```
o vía API. No la guardes en el código.

