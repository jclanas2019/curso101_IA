# Curso 101 de LangChain en español

Esta versión reemplaza la anterior con un proyecto más serio y completamente en español.

## Qué incluye

- Un único `main.py`
- Curso completo en español
- Menú interactivo por terminal
- Explicación teórica y demos prácticas
- RAG básico con `FAISS`
- Secciones sobre `prompt`, `LCEL`, `parsers`, `memory`, `tools`, `agentes` y producción

## Archivos

- `main.py`
- `requirements.txt`
- `.env.example`
- `README.md`

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

En Windows:

```bash
venv\Scripts\activate
pip install -r requirements.txt
```

## Variables de entorno

Copia `.env.example` a `.env` y ajusta:

```bash
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-4.1-mini
```

## Ejecución

```bash
python main.py
```

## Notas

- Sin `OPENAI_API_KEY`, el curso sigue funcionando en modo teórico/local.
- Las demos reales con embeddings o LLM se omiten limpiamente si falta configuración.
