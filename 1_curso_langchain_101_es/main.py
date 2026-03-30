#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Curso 101 de LangChain
Archivo único: main.py
"""

from __future__ import annotations

import os
import textwrap
from typing import List

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    LANGCHAIN_OK = True
except Exception as e:
    LANGCHAIN_OK = False
    LANGCHAIN_IMPORT_ERROR = str(e)

ANCHO = 92


def linea(char: str = "=") -> None:
    print(char * ANCHO)


def titulo(texto: str) -> None:
    linea("=")
    print(texto.center(ANCHO))
    linea("=")


def subtitulo(texto: str) -> None:
    print()
    print(texto)
    print("-" * len(texto))


def bloque(texto: str) -> None:
    print(textwrap.fill(texto.strip(), width=ANCHO))


def codigo(texto: str) -> None:
    print()
    print("```python")
    print(texto.strip("\n"))
    print("```")
    print()


def pausa() -> None:
    input("\nPresiona Enter para continuar...")


def limpiar() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def advertencia(texto: str) -> None:
    print(f"[ADVERTENCIA] {texto}")


def exito(texto: str) -> None:
    print(f"[OK] {texto}")


def obtener_modelo() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def hay_api_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


LECCIONES = [
    "01. Qué es LangChain y cuándo usarlo",
    "02. Modelos, prompts y parsers",
    "03. LCEL: encadenamiento moderno con |",
    "04. Prompt engineering estructurado",
    "05. RAG básico: troceado, embeddings y recuperación",
    "06. Memory: qué es y qué no es",
    "07. Diseño de tools y agentes",
    "08. Buenas prácticas para producción",
]

RESUMEN_CURSO = """
Este curso 101 está pensado para entender LangChain sin humo. El foco no es memorizar
clases sino construir el modelo mental correcto: LangChain no es la IA, es una capa de
orquestación para aplicaciones con LLMs.

Al terminar deberías poder:
1. Entender prompts, modelos, parsers y pipelines.
2. Construir una cadena simple usando LCEL.
3. Implementar un RAG mínimo con documentos locales.
4. Entender qué significa memoria en este contexto.
5. Diseñar una base razonable para tools y agentes.
6. Pasar de demo a estructura más seria.
""".strip()


def validar_entorno() -> None:
    titulo("ESTADO DEL ENTORNO")
    if LANGCHAIN_OK:
        exito("Las librerías principales de LangChain están disponibles.")
    else:
        advertencia("No se pudieron importar todos los paquetes de LangChain.")
        print("Detalle técnico:")
        print(LANGCHAIN_IMPORT_ERROR)

    if hay_api_key():
        exito("OPENAI_API_KEY está configurada.")
    else:
        advertencia("No se detectó OPENAI_API_KEY. Las demos remotas se omitirán.")

    print(f"Modelo configurado: {obtener_modelo()}")


def demo_1_teoria() -> None:
    titulo("LECCIÓN 1 — QUÉ ES LANGCHAIN")
    bloque("""
    LangChain es un framework de orquestación para aplicaciones basadas en modelos
    de lenguaje. Su valor aparece cuando necesitas combinar varias piezas:
    prompts, modelos, recuperación de contexto, tools, parsers, memoria o agentes.
    """)

    subtitulo("Modelo mental correcto")
    bloque("""
    LangChain no reemplaza al modelo ni corrige una mala arquitectura.
    Sirve para estructurar mejor la lógica alrededor del LLM.
    """)

    subtitulo("Cuándo sí aporta")
    print("• Chat con documentos")
    print("• Extracción estructurada")
    print("• Asistentes con tools")
    print("• Flujos de análisis multi-etapa")
    print("• Sistemas con retrieval")

    subtitulo("Cuándo no hace tanta falta")
    print("• Un script con una sola llamada al modelo")
    print("• Prototipos diminutos")
    print("• Automatizaciones sin razonamiento LLM")

    codigo("""
from openai import OpenAI

client = OpenAI()
resp = client.responses.create(
    model="gpt-4.1-mini",
    input="Resume LangChain en 5 líneas."
)
print(resp.output_text)
""")


def demo_2_prompts_y_parsers() -> None:
    titulo("LECCIÓN 2 — MODELOS, PROMPTS Y PARSERS")
    bloque("""
    Una aplicación simple en LangChain suele tener tres piezas:
    prompt template, modelo y output parser. El parser es importante porque
    normaliza la salida y evita acoplar la aplicación al texto bruto.
    """)

    codigo("""
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "Explica {tema} para un ingeniero senior en 6 líneas."
)

modelo = ChatOpenAI(model="gpt-4.1-mini")
parser = StrOutputParser()

chain = prompt | modelo | parser
resultado = chain.invoke({"tema": "LangChain"})
print(resultado)
""")

    if not (LANGCHAIN_OK and hay_api_key()):
        advertencia("Saltando demo ejecutable porque faltan librerías o API key.")
        return

    prompt = ChatPromptTemplate.from_template(
        "Explica {tema} en español técnico y sin marketing, en máximo 8 líneas."
    )
    modelo = ChatOpenAI(model=obtener_modelo(), temperature=0)
    parser = StrOutputParser()
    chain = prompt | modelo | parser
    salida = chain.invoke({"tema": "el rol de LangChain en una arquitectura LLM"})
    print(salida)


def demo_3_lcel() -> None:
    titulo("LECCIÓN 3 — LCEL")
    bloque("""
    LCEL significa LangChain Expression Language. Permite componer piezas con el
    operador | para formar pipelines declarativos y más legibles.
    """)

    codigo("""
chain = prompt | modelo | parser
resultado = chain.invoke({"tema": "RAG"})
""")

    subtitulo("Qué ganas con LCEL")
    bloque("""
    Ganas legibilidad, composición y reemplazo limpio de componentes.
    También separas mejor responsabilidades: prompt formula, modelo genera
    y parser normaliza.
    """)


def demo_4_prompt_engineering() -> None:
    titulo("LECCIÓN 4 — PROMPT ENGINEERING")
    bloque("""
    Un prompt útil no es más largo por defecto. Es más claro, más delimitado
    y más alineado con la salida que necesitas.
    """)

    codigo("""
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un analista técnico riguroso. Responde en español."),
    ("human", """
Analiza el siguiente incidente.

Contexto:
{contexto}

Objetivo:
1. Identificar causa probable
2. Proponer siguientes pasos
3. Responder en formato:
   - Hallazgo
   - Riesgo
   - Acción
""")
])
""")

    subtitulo("Errores frecuentes")
    print("• Pedir demasiadas cosas en una sola llamada")
    print("• No definir formato de salida")
    print("• No separar contexto de instrucciones")
    print("• Usar prompts ambiguos")


def construir_documentos_demo() -> List[str]:
    return [
        "LangChain es un framework para construir aplicaciones con modelos de lenguaje. Permite combinar prompts, modelos, recuperación de contexto y herramientas externas.",
        "RAG significa Retrieval-Augmented Generation. La idea es recuperar documentos relevantes antes de generar la respuesta.",
        "Un vector store permite indexar embeddings y luego buscar similitud semántica. FAISS es una opción popular para prototipos locales.",
        "La memoria en asistentes no debe confundirse con una base de conocimiento completa. Suele servir para continuidad conversacional o preferencias del usuario."
    ]


def demo_5_rag() -> None:
    titulo("LECCIÓN 5 — RAG BÁSICO")
    bloque("""
    RAG tiene una idea central: antes de responder, recuperas contexto relevante.
    Esto mejora grounding y reduce alucinación.
    """)

    codigo("""
documentos = [...]
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.create_documents(documentos)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

docs = retriever.invoke("¿Qué es RAG?")
""")

    textos = construir_documentos_demo()
    subtitulo("Corpus local")
    for i, t in enumerate(textos, start=1):
        print(f"[Doc {i}] {textwrap.shorten(t, width=110, placeholder='...')}")

    if not LANGCHAIN_OK:
        advertencia("No se puede ejecutar la demo real de RAG porque faltan librerías.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=180, chunk_overlap=30)
    docs = splitter.create_documents(textos)

    subtitulo("Chunking")
    print(f"Cantidad de chunks: {len(docs)}")
    for i, d in enumerate(docs[:4], start=1):
        print(f"Chunk {i}: {textwrap.shorten(d.page_content, width=100, placeholder='...')}")

    if not hay_api_key():
        advertencia("Sin OPENAI_API_KEY no se crearán embeddings reales. Se muestra sólo la estructura.")
        return

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    encontrados = retriever.invoke("¿Cuál es la idea principal de RAG?")

    subtitulo("Documentos recuperados")
    for i, doc in enumerate(encontrados, start=1):
        print(f"\n[{i}] {doc.page_content}")

    prompt = ChatPromptTemplate.from_template("""
Responde sólo con base en el contexto entregado.

Contexto:
{contexto}

Pregunta:
{pregunta}

Respuesta en español técnico:
""")
    llm = ChatOpenAI(model=obtener_modelo(), temperature=0)
    parser = StrOutputParser()
    chain = prompt | llm | parser

    contexto = "\n\n".join(d.page_content for d in encontrados)
    respuesta = chain.invoke({
        "contexto": contexto,
        "pregunta": "Explica RAG de forma breve pero precisa."
    })
    print("\nRespuesta final:")
    print(respuesta)


def demo_6_memory() -> None:
    titulo("LECCIÓN 6 — MEMORY")
    bloque("""
    Conviene separar tres cosas:
    1. Historial conversacional
    2. Memoria persistente de usuario
    3. Base de conocimiento / RAG

    No son lo mismo y no deberían diseñarse igual.
    """)

    codigo("""
# Mala práctica:
# meter manuales completos en el historial de chat

# Mejor práctica:
# - historial corto para continuidad
# - vector DB para conocimiento
# - store estructurado para preferencias o estado
""")


def demo_7_tools_y_agentes() -> None:
    titulo("LECCIÓN 7 — TOOLS Y AGENTES")
    bloque("""
    Una tool es una capacidad externa que el modelo puede invocar: buscar datos,
    calcular, consultar una API o leer archivos. Un agente decide cuándo usar
    una tool y cuál usar.
    """)

    subtitulo("Diseño sano")
    print("• Empieza con chains antes de saltar a agentes")
    print("• Limita el número de tools")
    print("• Define entradas y salidas con precisión")
    print("• Registra trazas y errores")

    codigo("""
def calcular_margen(ventas, costos):
    return (ventas - costos) / ventas
""")


def demo_8_produccion() -> None:
    titulo("LECCIÓN 8 — PRODUCCIÓN")
    bloque("""
    La mayoría de los proyectos falla no por el modelo, sino por falta de disciplina
    de ingeniería. Un prototipo bonito no equivale a un sistema robusto.
    """)

    subtitulo("Lista mínima")
    print("• Configuración por variables de entorno")
    print("• Logs y trazabilidad")
    print("• Timeouts y reintentos")
    print("• Evaluaciones")
    print("• Métricas de costo, latencia y calidad")
    print("• Versionado de prompts")


def laboratorio_final() -> None:
    titulo("LABORATORIO FINAL — MINI PROYECTO 101")
    bloque("""
    Tu primer proyecto razonable con LangChain no debería ser un super agente.
    Debería ser algo pequeño pero limpio, por ejemplo:
    un asistente técnico que responde sobre un conjunto de documentos internos.
    """)

    subtitulo("Arquitectura mínima")
    print("1. Cargar documentos")
    print("2. Dividir en chunks")
    print("3. Generar embeddings")
    print("4. Indexar en FAISS")
    print("5. Recuperar top-k chunks")
    print("6. Construir prompt con contexto")
    print("7. Responder y registrar la traza")


OPCIONES = {
    "1": ("Ver introducción del curso", lambda: (titulo("CURSO 101 DE LANGCHAIN"), bloque(RESUMEN_CURSO))),
    "2": ("Validar entorno", validar_entorno),
    "3": ("Lección 1: qué es LangChain", demo_1_teoria),
    "4": ("Lección 2: modelos, prompts y parsers", demo_2_prompts_y_parsers),
    "5": ("Lección 3: LCEL", demo_3_lcel),
    "6": ("Lección 4: prompt engineering", demo_4_prompt_engineering),
    "7": ("Lección 5: RAG básico", demo_5_rag),
    "8": ("Lección 6: memory", demo_6_memory),
    "9": ("Lección 7: tools y agentes", demo_7_tools_y_agentes),
    "10": ("Lección 8: producción", demo_8_produccion),
    "11": ("Laboratorio final", laboratorio_final),
    "12": ("Ejecutar curso completo", None),
    "0": ("Salir", None),
}


def ejecutar_curso_completo() -> None:
    limpiar()
    titulo("CURSO 101 DE LANGCHAIN — RECORRIDO COMPLETO")
    bloque(RESUMEN_CURSO)
    print()
    print("Temario:")
    for item in LECCIONES:
        print(f"• {item}")
    pausa()

    for fn in [
        validar_entorno,
        demo_1_teoria,
        demo_2_prompts_y_parsers,
        demo_3_lcel,
        demo_4_prompt_engineering,
        demo_5_rag,
        demo_6_memory,
        demo_7_tools_y_agentes,
        demo_8_produccion,
        laboratorio_final,
    ]:
        limpiar()
        fn()
        pausa()

    limpiar()
    titulo("FIN DEL CURSO")
    bloque("""
    Ya tienes una base sólida para dejar de ver LangChain como una caja negra.
    El siguiente paso correcto es construir un caso pequeño, medirlo y endurecerlo.
    """)


def imprimir_menu() -> None:
    titulo("LANGCHAIN 101 — CURSO EN ESPAÑOL")
    print("Selecciona una opción:\n")
    for k, (nombre, _) in OPCIONES.items():
        print(f" {k.rjust(2)}. {nombre}")
    print()


def main() -> None:
    while True:
        limpiar()
        imprimir_menu()
        opcion = input("Opción: ").strip()

        if opcion == "0":
            print("Saliendo del curso.")
            break

        if opcion == "12":
            ejecutar_curso_completo()
            continue

        item = OPCIONES.get(opcion)
        if not item:
            print("Opción no válida.")
            pausa()
            continue

        _, funcion = item
        limpiar()
        funcion()
        pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
