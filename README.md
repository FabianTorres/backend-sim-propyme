# Documentación Maestra: Backend Simulador Asistente Propyme (SII)
 
## 1. Visión General del Proyecto
Este proyecto ("Proyecto 2") es un componente crítico del ecosistema de Certificación de Calidad para el Asistente Propyme del Servicio de Impuestos Internos (SII). Actúa como el **Motor de Reglas (Oráculo)** que reemplaza a un antiguo y complejo sistema basado en Excel.
 
*   **Objetivo Principal:** Recibir un set de datos de prueba, aplicar la lógica tributaria oficial del Asistente Propyme, y retornar los resultados esperados (Campos Calculados).
*   **Posición en el Flujo:** Se sitúa entre el Generador de Casos de Prueba (Proyecto 1) y el Automatizador Playwright (Proyecto 3).
*   **Alcance del Backend:** Este repositorio (`backend_sim_propyme`) no contiene interfaz gráfica. Es una API RESTful pura que procesa datos de manera rápida, determinista y estructurada.
---
 
## 2. Diccionario de Datos y Reglas de Negocio
Para mantener un lenguaje ubicuo entre el equipo de QA, desarrollo y automatización, se definen los siguientes conceptos fundamentales:
 
*   **AT (Año Tributario):** Variable principal de entrada. El sistema asume que las reglas de negocio, los parámetros e incluso la estructura del Asistente pueden cambiar dependiendo del AT (ej. AT 2024 vs AT 2025).
*   **Vectores (`Vx01xxxx`):** Variables internas del SII que representan el historial o "memoria" del contribuyente (ej. ingresos de años anteriores). Existen aproximadamente 2000 vectores. Su estructura consta del prefijo seguido de un identificador numérico.
*   **Parámetros (`Pxxx`):** Constantes macroeconómicas de la ley dictadas para cada AT (ej. valor UTM, IPC, topes legales). Existen alrededor de 700 parámetros. No son proporcionados por el usuario, sino que el sistema debe tenerlos precargados.
*   **Campos Digitados:** Inputs manuales del formulario web del SII que el usuario de QA inyecta en la simulación.
*   **Campos Calculados:** El resultado de salida. Son los valores que nuestra API calcula a partir de los Vectores, Parámetros y Campos Digitados, aplicando los algoritmos del negocio.
---
 
## 3. Arquitectura del Sistema
El sistema se diseña utilizando **Clean Architecture**, asegurando que la lógica del negocio esté aislada de las conexiones a bases de datos o de la red.
 
### 3.1. Patrón Orquestador (Pipeline Secuencial)
El Asistente Propyme original está compuesto por 8 "páginas" conectadas. Nuestro backend simulará este flujo como un Pipeline Secuencial.
*   **Mecánica:** Una solicitud de cálculo pasa por la Página 1, su resultado alimenta a la Página 2, y así sucesivamente.
*   **Excepciones Manejadas:** Se contemplan saltos lógicos asíncronos en el negocio. Por ejemplo, la Página 7 (Registro de Renta Empresarial - RRE) es la más compleja y su flujo puede inyectar datos retroactivamente en la Página 3, o devolver la ejecución a la Página 6.
*   **Salida (Output):** La API no devuelve resultados página por página, sino que procesa el pipeline completo y retorna un único y masivo objeto JSON estructurado por módulos (`{"pagina_1": {...}, "pagina_2": {...}}`) para que el Frontend lo renderice de una vez.
### 3.2. Estrategia de Persistencia (Mocks Temporales)
Durante las fases iniciales del desarrollo, **no se utilizará una base de datos real** para priorizar la construcción de la lógica del negocio.
*   Los Parámetros y Vectores se almacenarán en archivos `.json` locales (ej. `mock_parametros_at2026.json`).
*   A futuro, estas colecciones migrarán a Azure SQL Database sin necesidad de reescribir la lógica de cálculo, gracias al aislamiento en la capa de repositorios.
---
 
## 4. Stack Tecnológico
 
*   **Lenguaje:** Python 3.11+
*   **Framework API:** FastAPI (Alta velocidad y validación nativa).
*   **Servidor ASGI:** Uvicorn.
*   **Validación de Contratos:** Pydantic (Garantiza que los Vectores y Códigos que ingresan tengan el tipo de dato correcto).
*   **Procesamiento de Archivos:** `pandas` y `openpyxl` (Para la importación/exportación de casos en Excel, cuando se implemente).
---
 
## 5. Estructura de Directorios
```text
backend_sim_propyme/
├── app/
│   ├── api/            # Controladores/Endpoints (Rutas de FastAPI)
│   ├── core/           # Configuraciones generales (.env, variables de entorno)
│   ├── db/             # Manejo de Mocks locales (y a futuro Azure SQL)
│   ├── models/         # Modelos de datos (Entidades)
│   ├── schemas/        # Validadores de Pydantic (Input/Output del API)
│   ├── services/       # NÚCLEO: Algoritmos de las 8 Páginas del SII
│   └── utils/          # Herramientas de soporte (Lectura de Excel, formateo)
├── tests/              # Pruebas automatizadas de los algoritmos
├── venv/               # Entorno virtual aislado
├── .env                # Variables de entorno locales
├── .gitignore          # Exclusión de archivos para Git
├── requirements.txt    # Dependencias de Python
└── main.py             # Punto de entrada de Uvicorn/FastAPI
```
 
---
 
## 6. Historial de Trabajo y Estado Actual
 
*   [Completado] Definición de la estrategia general (Separación Frontend React / Backend Python).
*   [Completado] Configuración inicial del repositorio backend.
*   [Completado] Creación del entorno virtual (venv) y manejo de errores de compilación (pip upgrade).
*   [Completado] Instalación de librerías base (FastAPI, Pandas).
*   [Completado] Implementación de main.py y validación del servidor en el puerto 8001 (/health).
---
 
## 7. Hoja de Ruta (Siguientes Pasos)
 
*   Construcción de Estructuras Base: Diseñar los esquemas JSON (schemas) que representen los Vectores (Vx01xxxx), Parámetros (Pxxx) y el concepto de Año Tributario (AT).
*   Sistema de Mocks: Crear los archivos JSON locales para poblar los Parámetros y Vectores de prueba.
*   Desarrollo Página 1: Recibir la documentación de negocio para la Página 1 e implementar el primer módulo de cálculo en services/.
*   Desarrollo Páginas 2 a 8: Continuar el pipeline respetando dependencias (especial énfasis técnico en la Página 7 - RRE).
*   Integración Frontend: Ajustar el JSON de salida según las necesidades del equipo de UI.
*   Módulo Excel: Implementar el parser para generar el Excel de salida que consumirá Playwright.