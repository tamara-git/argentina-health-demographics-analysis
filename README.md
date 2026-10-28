# Análisis de Salud Pública, Demografía y Mortalidad en Argentina (2005–2022)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow?logo=duckdb)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas)
![Seaborn](https://img.shields.io/badge/Seaborn-Data%20Viz-3776AB)

## - Descripción del Proyecto
Este proyecto de análisis de datos explora las relaciones entre las causas de mortalidad, las variables demográficas (edad y sexo registrado al nacer) y las condiciones de acceso a la salud (cobertura médica e infraestructura de establecimientos) en la República Argentina durante el período **2005–2022**.

Desarrollado en el marco de la materia **Laboratorio de Datos** (Facultad de Ciencias Exactas y Naturales - Universidad de Buenos Aires), el proyecto abarca desde el procesamiento masivo de microdatos censales y registros de defunciones, la evaluación de calidad bajo metodología **GQM** (*Goal, Question, Metric*), hasta la modelación en **Tercera Forma Normal (3FN)** y la consulta analítica intensiva mediante SQL (**DuckDB**).

---

## - Objetivos Principales
1. **Modelado y Limpieza de Datos:**
   - Diseñar un Diagrama Entidad-Relación (DER) óptimo.
   - Normalizar los esquemas relacionales a **3FN** (identificando PKs, FKs y Dependencias Funcionales).
   - Cuantificar problemas de calidad de datos (instancia y modelo) aplicando **GQM**.
2. **Análisis de Datos e Inferencia SQL:**
   - Evaluar la brecha de acceso a la salud (cobertura) entre los censos **2010** y **2022** por grupo etario y provincia.
   - Analizar la disponibilidad de camas de terapia intensiva según origen de financiamiento (público vs. privado).
   - Determinar las principales causas de muerte (CIE-10) por rango etario/sexo y su evolución temporal.
   - Calcular tasas de mortalidad específicas normalizadas por cada 1.000 habitantes en 2022.
3. **Visualización y Comunicación:**
   - Presentar patrones demográficos y de mortalidad mediante gráficos claros (*barplots*, *lineplots* y *boxplots*).

---

## - Fuentes de Datos
- **Censo Nacional de Población 2010 & 2022 (INDEC / Redatam):** Población por provincia, edad, sexo y cobertura de salud.
- **Defunciones Ocurridas y Registradas (Ministerio de Salud / Datos Abiertos 2005–2022):** Causas de muerte codificadas bajo la Clasificación Internacional de Enfermedades (CIE-10).
- **Registro Federal de Establecimientos de Salud (REFES 2022):** Distribución de centros de salud, tipologías y fuentes de financiamiento.

---

## - Arquitectura y Modelo Relacional
El modelo relacional fue diseñado en **3FN** priorizando la eliminación de redundancias y garantizando la integridad referencial. 

```
[Provincias] ──< [Departamentos] ──< [Establecimientos_de_Salud]
     │                                     │
     │                                     ├──> [Tipologias]
     │                                     └──> [Origen_Financiero]
     │
     ├───< [Se_Realizan] >─── [Censos]
     │
     └───< [Se_Producen] >─── [Defunciones]
```

---
### 🗄️ Esquema Relacional (3FN)

- **Provincias** (`Id-Provincia`, Nombre de Provincia)
- **Departamentos** (`Id-Departamento`, Nombre de Departamento, *Id-Provincia*)
- **Tipologias** (`Id-Tipología`, Nombre de la Tipología)
- **Origen_Financiero** (`Id-Origen-Financiero`, Nombres del Origen Financiero)
- **Establecimientos_de_Salud** (`Id-Establecimiento`, Nombres de los Establecimientos, *Id-Tipología*, *Id-Origen-Financiero*, *Id-Departamento*)
- **Censos** (`Año`, `Cobertura de Salud`, `Sexo`, `Edad`)
- **Defunciones** (`Nombre-Causa-Muerte`, `Año`, `Grupo de Edad`, `Sexo`)
- **Se_Realizan** (*Id-Provincia*, *Año*, *Cobertura de Salud*, *Sexo*, *Edad*, Cantidad)
- **Se_Producen** (*Id-Provincia*, *Nombre-Causa-Muerte*, *Año*, *Grupo de Edad*, *Sexo*, Cantidad de Casos)

## - Estructura del Repositorio

```text
├── TablasOriginales/         # Archivos fuente (.xlsx, .csv)
├── TablasModelo/             # Tablas normalizadas en CSV derivadas del proceso ETL (3FN)
├── Trabajo-Practico-01.py    # Script principal de Python (ETL, Queries SQL con DuckDB y Visualizaciones)
├── Informe.pdf               # Informe final con metodología, análisis GQM y conclusiones
└── README.md                 # Descripción del proyecto
```

---

## - Requisitos e Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/tu-repositorio.git
   cd tu-repositorio
   ```

2. **Instalar dependencias necesarias:**
   ```bash
   pip install pandas duckdb numpy matplotlib seaborn openpyxl
   ```

3. **Ejecutar el análisis:**
   ```bash
   python Trabajo-Practico-01.py
   ```

---

## - Principales Análisis y Visualizaciones
- **Evolución de Cobertura de Salud:** Comparativa 2010 vs. 2022 por provincia y franja etaria.
- **Tasa de Mortalidad 2022:** Tasas ajustadas por grupo etario e impacto por sexo.
- **Capacidad Instalada (Terapia Intensiva):** Proporción de financiamiento estatal vs. privado por jurisdicción.
- **Distribución de Centros de Salud:** Evaluación de dispersión de establecimientos por departamento utilizando *boxplots*.

---

## 👥 Autores
- **Tamara Diana Argañaraz**
- **Yamila Daniela Burrafato**
- **Carolina Belén Fonseca**

*Laboratorio de Datos — FCEyN, Universidad de Buenos Aires (UBA)*
