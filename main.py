"""
Universidad de Buenos Aires (UBA)
Facultad de Ciencias Exactas y Naturales (FCEyN)
Laboratorio de Datos
Trabajo Práctico 01
Curso de Verano - 2026

-- Nombre de grupo: {Las Nulls}
-- Integrante_1: {1189/24 ; Tamara Diana Argañaraz; tamaradiana.ar@gmail.com}
-- Integrante_2: {151/15 ; Yamila Daniela Burrafato; yamilab8.yb@gmail.com}
-- Integrante_3: {572/23 ; Carolina Belén Fonseca ; carolina.fonseca.uba@gmail.com}
"""

#%% Importamos bibliotecas
import pandas as pd
import duckdb as dd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

#%%============================
# Funciones para leer los datos
#==============================

def leer_censo(path, anio, total = False):

    df_raw = pd.read_excel(path, skiprows=range(0, 14), header=None)

    # Elimino la primera columna que no tiene informacion 
    df_raw.drop(df_raw.columns[0], axis=1, inplace=True)
    
    datos_procesados = []

    # Recorro fila por fila
    for i, fila in df_raw.iterrows():
        columnb = str(fila[1]).strip()
        columnc = str(fila[2]).strip()
        
        if columnb == 'RESUMEN':
            break
        
        if "AREA #" in columnb:
            id_prov = str(fila[1]).replace("AREA #", "")
            id_prov = int(id_prov.strip())
            prov = str(fila[2]).strip()
            continue
        
        if columnb != 'nan' and columnc == 'nan':
            if "Cobertura" not in columnb:
                cobertura = columnb
                for numcol, value in fila.items():
                    value = str(value)
                    if 'Mujer' in value:
                        colmujer = numcol
                    elif 'Var' in value:
                        colvaron = numcol
            continue
        
        if columnc.isdigit():
            edad = int(columnc)
            mujeres = pd.to_numeric(fila[colmujer], errors='coerce')
            varones = pd.to_numeric(fila[colvaron], errors='coerce')
            
            datos_procesados.append([id_prov, prov, cobertura, edad, 'Femenino', mujeres])
            datos_procesados.append([id_prov, prov, cobertura, edad, 'Masculino', varones])

    cobertura_por_genero_edad = pd.DataFrame(datos_procesados, columns=['Id_Provincia', 'Provincia', 'Cobertura_de_Salud', 'Edad', 'Sexo', 'Cantidad'])
    cobertura_por_genero_edad['Anio'] = anio

    total_por_genero_edad = cobertura_por_genero_edad[cobertura_por_genero_edad['Cobertura_de_Salud']== 'Total']
    if total:
        return total_por_genero_edad.reset_index(drop=True)
    else:
        cobertura_por_genero_edad = cobertura_por_genero_edad.drop(total_por_genero_edad.index)
        return cobertura_por_genero_edad.reset_index(drop=True)

#%%===========================================================================
# Importamos los datasets que vamos a utilizar en este programa
#=============================================================================

carpeta = "Tablas Originales/"

censo2010 = carpeta + "censo2010.xlsX"
censo2022 = carpeta + "censo2022.xlsX"

censo2010_datos = leer_censo(censo2010, 2010)
censo2022_datos = leer_censo(censo2022, 2022)

defunciones = pd.read_csv(carpeta + "defunciones.csv")
instituciones_de_salud = pd.read_excel(carpeta + "instituciones_de_salud.xlsx")

#%%====================================================
# Ejercicios: Procesamiento de Datos - Calidad de Datos
#======================================================

provincias_unicas = dd.query("""
      SELECT DISTINCT provincia_nombre
      FROM instituciones_de_salud
      ORDER BY provincia_nombre
""").df()

provincias_con_id_repetido = dd.query("""
      SELECT 
            provincia_nombre,
            COUNT(DISTINCT provincia_id) AS cantidad_ids_distintos
        FROM instituciones_de_salud
        GROUP BY provincia_nombre
        HAVING COUNT(DISTINCT provincia_id) > 1
""").df()

total = len(provincias_unicas) 
repetidos = len(provincias_con_id_repetido)
Metrica = repetidos / total
print(f"Metrica de provincias con IDs duplicados: {Metrica:.2%}")

#%%==========================================

tipologias_con_multiples_id = dd.query("""
      SELECT 
            tipologia_nombre,
            COUNT(DISTINCT tipologia_id) AS cantidad_ids_distintos
        FROM instituciones_de_salud
        GROUP BY tipologia_nombre
        HAVING COUNT(DISTINCT tipologia_id) > 1
""").df()

id_con_multiples_tipologias = dd.query("""
      SELECT 
            tipologia_id,
            COUNT(DISTINCT tipologia_nombre) AS cantidad_ids_distintos
        FROM instituciones_de_salud
        GROUP BY tipologia_id
        HAVING COUNT(DISTINCT tipologia_nombre) > 1
""").df()

total_tipologias = dd.query("""
      SELECT DISTINCT tipologia_nombre 
        FROM instituciones_de_salud
""").df()
total = len(total_tipologias)
duplicadas = len(tipologias_con_multiples_id)

Metrica = duplicadas / total
print(f"Metrica de tipologías con múltiples IDs: {Metrica:.2%}")

#%%==========================================

id_con_multiples_departamentos = dd.query("""
      SELECT 
            departamento_id,
            COUNT(DISTINCT departamento_nombre) AS cantidad_Name_distintos
        FROM instituciones_de_salud
        GROUP BY departamento_id
        ORDER BY cantidad_Name_distintos DESC, departamento_id ASC
""").df()

#%%========================================================================

total_registros = dd.query("""
      SELECT COUNT(Cantidad) AS Cantidad
        FROM defunciones
""").df()

clasificacion_sexo_no_Definido = dd.query("""
      SELECT COUNT(Cantidad) AS Cantidad
        FROM defunciones
        WHERE Sexo = 'desconocido' OR Sexo = 'indeterminado';
""").df()

total = total_registros['Cantidad'][0]
no_definido = clasificacion_sexo_no_Definido['Cantidad'][0]

Metrica = no_definido / total
print(f"Metrica de Sexo indefinido: {Metrica:.2%}")

#%%===============================

Metrica_Def_Prov = dd.query("""
      SELECT DISTINCT jurisdiccion_de_residencia_id, jurisdicion_residencia_nombre
      FROM defunciones
      ORDER BY jurisdiccion_de_residencia_id
""").df()

#%%===============================

Metrica_Def_Edad = dd.query("""
      SELECT DISTINCT grupo_edad
      FROM defunciones
""").df()

#%%=====================================================================================
# LIMPIAMOS LAS TABLAS DE LOS ARCHIVOS PARA REPRESENTAR CADA ESQUEMA DEL MODELO RACIONAL
#=======================================================================================

Provincia = dd.query("""
                SELECT DISTINCT
                    jurisdiccion_de_residencia_id AS Id_Provincia,
                    jurisdicion_residencia_nombre AS Provincia
                FROM defunciones
                WHERE NOT (jurisdiccion_de_residencia_id = 98 OR jurisdiccion_de_residencia_id = 99)
                ORDER BY Id_Provincia
""").df()

#%%===========================

Departamentos = dd.query("""
                SELECT DISTINCT
                    departamento_id,
                    departamento_nombre,
                    provincia_id,
                    provincia_nombre
                FROM instituciones_de_salud;
""").df()

Departamentos = dd.query("""
                SELECT DISTINCT
                    departamento_id,
                    departamento_nombre,
                    (CASE WHEN provincia_nombre='CHACO' 
                        THEN 22 
                        ELSE provincia_id
                    END) AS provincia_id,
                    provincia_nombre
                FROM Departamentos;
""").df()

Departamentos = dd.query("""
                SELECT DISTINCT
                    departamento_id,
                    departamento_nombre,
                    (CASE WHEN provincia_nombre='CHUBUT' 
                        THEN 26 
                        ELSE provincia_id
                    END) AS provincia_id,
                    provincia_nombre
                FROM Departamentos;
""").df()

Departamentos = dd.query("""
                SELECT DISTINCT
                    departamento_id,
                    departamento_nombre,
                    (CASE WHEN provincia_nombre='CÓRDOBA' 
                        THEN 14 
                        ELSE provincia_id
                    END) AS provincia_id,
                    provincia_nombre
                FROM Departamentos;
""").df()

Departamentos = dd.query("""
                SELECT DISTINCT
                    departamento_id,
                    departamento_nombre,
                    (CASE WHEN provincia_nombre='RÍO NEGRO' 
                        THEN 62 
                        ELSE provincia_id
                    END) AS provincia_id,
                    provincia_nombre
                FROM Departamentos;
""").df()

Departamentos = dd.query("""
                SELECT DISTINCT
                    departamento_id,
                    departamento_nombre,
                    (CASE WHEN provincia_nombre='SAN LUIS' 
                        THEN 74 
                        ELSE provincia_id
                    END) AS provincia_id
                FROM Departamentos
                ORDER BY provincia_id, departamento_id;
""").df()

Departamentos = dd.query("""
                SELECT DISTINCT
                    ROW_NUMBER() OVER (ORDER BY provincia_id, departamento_nombre) AS departamento_id,
                    departamento_nombre,
                    provincia_id
                FROM Departamentos
                GROUP BY provincia_id, departamento_nombre
                ORDER BY provincia_id, departamento_id
""").df()

#%%========================

Tipologia = dd.query("""
                SELECT DISTINCT
                    'TIP-' || LPAD(ROW_NUMBER() OVER (ORDER BY tipologia_nombre)::TEXT, 2, '0') AS Id_Tipologia,
                    tipologia_nombre AS Tipologia_Nombre
                FROM instituciones_de_salud
                GROUP BY Tipologia_Nombre
                ORDER BY Id_Tipologia;
""").df()

#%%===============================

Origen_Financiero = dd.query("""
                SELECT DISTINCT
                    'OF-' || LPAD(ROW_NUMBER() OVER (ORDER BY origen_financiamiento)::TEXT, 2, '0') AS Id_Origen_Financiamiento,
                    origen_financiamiento AS Origen_Financiamiento
                FROM instituciones_de_salud
                GROUP BY Origen_Financiamiento
                ORDER BY Id_Origen_Financiamiento;
""").df()

#%%=======================================

Establecimientos_de_Salud = dd.query("""
                SELECT DISTINCT
                    establecimiento_id AS Id_Establecimiento,
                    establecimiento_nombre AS Nombre_Establecimiento,
                    tipologia_nombre,
                    origen_financiamiento,
                    departamento_nombre AS Nam_Dep,
                    provincia_id AS Id_Provincia
                FROM instituciones_de_salud;
""").df()

Establecimientos_de_Salud = dd.query("""
                SELECT
                    ES.Id_Establecimiento,
                    ES.Nombre_Establecimiento,
                    T.Id_Tipologia,
                    ES.origen_financiamiento,
                    ES.Nam_Dep,
                    ES.Id_Provincia
                FROM Establecimientos_de_Salud AS ES
                INNER JOIN Tipologia AS T
                ON ES.tipologia_nombre = T.Tipologia_Nombre;
""").df()

Establecimientos_de_Salud = dd.query("""
                SELECT
                    ES.Id_Establecimiento,
                    ES.Nombre_Establecimiento,
                    ES.Id_Tipologia,
                    OF.Id_Origen_Financiamiento,
                    ES.Nam_Dep,
                    ES.Id_Provincia
                FROM Establecimientos_de_Salud AS ES
                INNER JOIN Origen_Financiero AS OF
                ON ES.origen_financiamiento = OF.Origen_Financiamiento
                ORDER BY Id_Provincia, OF.Id_Origen_Financiamiento, ES.Id_Establecimiento;
""").df()

Establecimientos_de_Salud = dd.query("""
                SELECT
                    ES.Id_Establecimiento,
                    ES.Nombre_Establecimiento,
                    ES.Id_Tipologia,
                    ES.Id_Origen_Financiamiento,
                    DEP.departamento_id AS Id_Departamento
                FROM Establecimientos_de_Salud AS ES
                INNER JOIN Departamentos AS DEP
                ON ES.Id_Provincia = DEP.provincia_id AND
                   ES.Nam_Dep = DEP.departamento_nombre
                ORDER BY DEP.departamento_id, ES.Id_Establecimiento;
""").df()

#%%===================

Censos = dd.query("""
                 SELECT DISTINCT 
                     '2010' AS Año,
                     'Obra social o prepaga (incluye PAMI)' AS Cobertura_de_Salud,
                     Sexo, 
                     Edad
                 FROM censo2010_datos
                 WHERE Cobertura_de_Salud = 'Obra social (incluye PAMI)'
            UNION
                SELECT DISTINCT 
                    '2010' AS Año,
                    'No tiene obra social, prepaga ni plan estatal' AS Cobertura_de_Salud,
                    Sexo, 
                    Edad
                FROM censo2010_datos
                WHERE Cobertura_de_Salud = 'No tiene obra social, prepaga o plan estatal'
            UNION
                SELECT DISTINCT 
                    '2010' AS Año,
                    Cobertura_de_Salud,
                    Sexo, 
                    Edad
                FROM censo2010_datos
                WHERE Cobertura_de_Salud = 'Programas o planes estatales de salud'
            UNION
                SELECT DISTINCT 
                       '2022' AS Año,
                       Cobertura_de_Salud,
                       Sexo, 
                       Edad 
                FROM censo2022_datos
            ORDER BY Año, Cobertura_de_Salud, Edad
""").df()

#%%==========================

Defunciones = dd.query("""
                SELECT *
                FROM defunciones
                WHERE NOT (jurisdiccion_de_residencia_id = 98 OR jurisdiccion_de_residencia_id = 99)
""").df()

Defunciones = dd.query("""
                SELECT *
                FROM Defunciones
                WHERE NOT (Sexo = 'desconocido' OR Sexo = 'indeterminado')
""").df()

Defunciones = dd.query("""
                SELECT *
                FROM Defunciones
                WHERE NOT grupo_edad LIKE '%Sin especificar'
""").df()

defuncionesNOTNULL_and_U07 = dd.query("""
                SELECT jurisdiccion_de_residencia_id AS Id_provincia,
                      cie10_causa_id AS Id_causa,
                      (CASE WHEN cie10_clasificacion IS NULL          
                      THEN 'Sin definir'        
                      ELSE cie10_clasificacion       
                      END) AS Nombre_Causa_de_Muerte,
                    anio AS Año,
                    SUBSTRING(grupo_edad, 4, LEN(grupo_edad)) AS Grupo_Edad, 
                    Sexo,
                    cantidad AS Cantidad
                FROM Defunciones
                WHERE
                   (cie10_causa_id = UPPER(cie10_causa_id)
                    AND cie10_clasificacion IS NOT NULL)
                   OR
                   (cie10_causa_id = 'U07' 
                    AND cie10_clasificacion IS NULL)
""").df()

defuncionesMINUS_A_MAYUS = dd.query("""
                SELECT jurisdiccion_de_residencia_id AS Id_provincia,
                UPPER(cie10_causa_id) AS Id_causa,
                   cie10_clasificacion AS Nombre_Causa_de_Muerte,
                    anio AS Año,
                    SUBSTRING(grupo_edad, 4, LEN(grupo_edad)) AS Grupo_Edad, 
                    Sexo,
                    cantidad AS Cantidad
                FROM defunciones
                WHERE 
                    cie10_causa_id = LOWER(cie10_causa_id);
""").df()

defuncionesSINMINUS_NOMBRADOS = dd.query("""
               SELECT 
               Id_provincia,
               dm.Id_causa,
               dnl.Nombre_Causa_de_Muerte,
               dm.Año,
               dm.Grupo_Edad,
               dm.Sexo,
               Cantidad
               FROM defuncionesMINUS_A_MAYUS AS dm
               LEFT JOIN (
                   SELECT DISTINCT Id_causa, Nombre_Causa_de_Muerte
                   FROM defuncionesNOTNULL_and_U07
                   ) AS dnl
               ON dm.Id_causa = dnl.Id_causa;
""").df()

defuncionesLIMPIO = dd.query("""         
            SELECT *
            FROM defuncionesNOTNULL_and_U07 
            UNION ALL
            SELECT *
            FROM defuncionesSINMINUS_NOMBRADOS;
""").df()

Defunciones = dd.query("""         
            SELECT DISTINCT 
                Nombre_Causa_de_Muerte, 
                Grupo_Edad,
                Sexo,
                Año
            FROM defuncionesLIMPIO;
""").df()

#%%===========================

se_producen = dd.query("""
                SELECT DISTINCT
                  Id_provincia, 
                  Nombre_Causa_de_Muerte,
                  Año, 
                  Grupo_Edad, 
                  Sexo, 
                  SUM(Cantidad) AS Cantidad
                FROM defuncionesLIMPIO 
                GROUP BY Id_provincia, Nombre_Causa_de_Muerte, Año, Grupo_Edad, Sexo
                ORDER BY Id_provincia, Año, Grupo_Edad;
""").df()

#%%===========================

censo2010_ObraSocial = dd.query("""
                     SELECT DISTINCT 
                            Id_Provincia, 
                            '2010' AS Año,
                            'Obra social o prepaga (incluye PAMI)' AS Cobertura_de_Salud,
                            Sexo, 
                            Edad, 
                            SUM(Cantidad) AS Cantidad
                     FROM censo2010_datos
                     WHERE Cobertura_de_Salud = 'Prepaga sólo por contratación voluntaria'
                        OR Cobertura_de_Salud = 'Obra social (incluye PAMI)'
                        OR Cobertura_de_Salud = 'Prepaga a través de obra social'
                     GROUP BY Id_Provincia, Sexo, Edad
""").df()

censo2010_NoTieneObraSocial = dd.query("""
                     SELECT DISTINCT 
                           Id_Provincia, 
                           '2010' AS Año,
                           'No tiene obra social, prepaga ni plan estatal' AS Cobertura_de_Salud,
                           Sexo, 
                           Edad, 
                           Cantidad
                    FROM censo2010_datos
                    WHERE Cobertura_de_Salud = 'No tiene obra social, prepaga o plan estatal'
""").df()

censo2010_PlanesEstatales = dd.query("""
                     SELECT DISTINCT 
                          Id_Provincia, 
                          '2010' AS Año,
                          Cobertura_de_Salud,
                          Sexo, 
                          Edad, 
                          Cantidad
                   FROM censo2010_datos
                   WHERE Cobertura_de_Salud = 'Programas o planes estatales de salud'
""").df()

censo2022_Casos = dd.query("""
                    SELECT DISTINCT 
                           Id_Provincia,
                           '2022' AS Año,
                           Cobertura_de_Salud,
                           Sexo, 
                           Edad, 
                           Cantidad
                    FROM censo2022_datos
""").df()

se_realizan = dd.query("""
                    SELECT *
                    FROM censo2010_ObraSocial
                UNION
                    SELECT *
                    FROM censo2010_NoTieneObraSocial
                UNION
                    SELECT *
                    FROM censo2010_PlanesEstatales
                UNION
                    SELECT *
                    FROM censo2022_Casos
                ORDER BY Id_provincia, Año, Cobertura_de_Salud, Edad;
""").df()

se_realizan = dd.query("""
               SELECT DISTINCT 
                      Id_Provincia,
                      Año,
                      Cobertura_de_Salud,
                      Sexo, 
                      Edad, 
                      (CASE WHEN Cantidad IS NULL THEN 0 ELSE Cantidad END) AS Cantidad
               FROM se_realizan
               ORDER BY Id_provincia, Año, Cobertura_de_Salud, Edad;
""").df()

#%%===============================================================================
# Creamos las tablas pedidas en "Ejercicios: Analisis de Datos - Primera Consigna"
#=================================================================================

habitantes_sin_cobertura2010 = dd.query("""
                SELECT Id_provincia,
                CASE 
                WHEN Edad BETWEEN 0 AND 14 THEN 'De 0 a 14 anios'
                WHEN Edad BETWEEN 15 AND 34 THEN 'De 15 a 34 anios'
                WHEN Edad BETWEEN 35 AND 54 THEN 'De 35 a 54 anios'
                WHEN Edad BETWEEN 55 AND 74 THEN 'De 55 a 74 anios'
                WHEN Edad >= 75 THEN 'De 75 anios y mas'
                END AS Grupo_Edad,
                SUM (Cantidad) AS Cantidad
                FROM se_realizan
                WHERE Año = 2010 AND Cobertura_de_Salud = 'No tiene obra social, prepaga ni plan estatal'
                GROUP BY  
                    Id_provincia,
                    Grupo_Edad
                ORDER BY Id_provincia ASC, Grupo_Edad;
""").df()

habitantes_con_cobertura2010 = dd.query("""
                SELECT Id_provincia,
                CASE 
                WHEN Edad BETWEEN 0 AND 14 THEN 'De 0 a 14 anios'
                WHEN Edad BETWEEN 15 AND 34 THEN 'De 15 a 34 anios'
                WHEN Edad BETWEEN 35 AND 54 THEN 'De 35 a 54 anios'
                WHEN Edad BETWEEN 55 AND 74 THEN 'De 55 a 74 anios'
                WHEN Edad >= 75 THEN 'De 75 anios y mas'
                END AS Grupo_Edad,
                SUM (Cantidad) AS Cantidad
                FROM se_realizan
                WHERE Año = 2010 AND Cobertura_de_Salud <> 'No tiene obra social, prepaga ni plan estatal'
                GROUP BY  
                    Id_provincia,
                    Grupo_Edad
                ORDER BY Id_provincia ASC, Grupo_Edad;
""").df()

cobertura_en2010 = dd.query("""
                SELECT con.Id_provincia, 
                sin.Grupo_edad, 
                con.Cantidad AS 'Habitantes con cobertura en 2010',
                sin.Cantidad AS 'Habitantes sin cobertura en 2010'
                FROM habitantes_con_cobertura2010 AS con
                LEFT OUTER JOIN habitantes_sin_cobertura2010 AS sin
                ON sin.Grupo_Edad = con.Grupo_Edad AND
                sin.Id_provincia = con.Id_provincia
""").df()

habitantes_sin_cobertura2022 = dd.query("""
                SELECT Id_provincia,
                CASE 
                WHEN Edad BETWEEN 0 AND 14 THEN 'De 0 a 14 anios'
                WHEN Edad BETWEEN 15 AND 34 THEN 'De 15 a 34 anios'
                WHEN Edad BETWEEN 35 AND 54 THEN 'De 35 a 54 anios'
                WHEN Edad BETWEEN 55 AND 74 THEN 'De 55 a 74 anios'
                WHEN Edad >= 75 THEN 'De 75 anios y mas'
                END AS Grupo_Edad,
                SUM (Cantidad) AS Cantidad
                FROM se_realizan
                WHERE Año = 2022 AND Cobertura_de_Salud = 'No tiene obra social, prepaga ni plan estatal'
                GROUP BY  
                    Id_provincia,
                    Grupo_Edad
                ORDER BY Id_provincia ASC, Grupo_Edad;
""").df()

habitantes_con_cobertura2022 = dd.query("""
                SELECT Id_provincia,
                CASE 
                WHEN Edad BETWEEN 0 AND 14 THEN 'De 0 a 14 anios'
                WHEN Edad BETWEEN 15 AND 34 THEN 'De 15 a 34 anios'
                WHEN Edad BETWEEN 35 AND 54 THEN 'De 35 a 54 anios'
                WHEN Edad BETWEEN 55 AND 74 THEN 'De 55 a 74 anios'
                WHEN Edad >= 75 THEN 'De 75 anios y mas'
                END AS Grupo_Edad,
                SUM (Cantidad) AS Cantidad
                FROM se_realizan
                WHERE Año = 2022 AND Cobertura_de_Salud <> 'No tiene obra social, prepaga ni plan estatal'
                GROUP BY  
                    Id_provincia,
                    Grupo_Edad
                ORDER BY Id_provincia ASC, Grupo_Edad;
""").df()

cobertura_en2022 = dd.query("""
                SELECT con.Id_provincia, 
                sin.Grupo_edad, 
                con.Cantidad AS 'Habitantes con cobertura en 2022',
                sin.Cantidad AS 'Habitantes sin cobertura en 2022'
                FROM habitantes_con_cobertura2022 AS con
                LEFT OUTER JOIN habitantes_sin_cobertura2022 AS sin
                ON sin.Grupo_Edad = con.Grupo_Edad AND
                sin.Id_provincia = con.Id_provincia
""").df()

Cobertura_de_Salud = dd.query("""
                SELECT c10.Id_provincia,
                c10.Grupo_Edad,
                "Habitantes con cobertura en 2010",
                "Habitantes sin cobertura en 2010",
                "Habitantes con cobertura en 2022",
                "Habitantes sin cobertura en 2022"
                FROM cobertura_en2010 AS c10
                LEFT OUTER JOIN cobertura_en2022 AS c22
                ON c10.Id_provincia = c22.Id_provincia AND
                c10.Grupo_Edad = c22.Grupo_Edad
""").df()

Cobertura_de_Salud = dd.query("""
                SELECT p.Provincia,
                cs.Grupo_Edad,
                "Habitantes con cobertura en 2010",
                "Habitantes sin cobertura en 2010",
                "Habitantes con cobertura en 2022",
                "Habitantes sin cobertura en 2022"
                FROM Cobertura_de_Salud as cs
                INNER JOIN Provincia AS p
                ON cs.Id_provincia = p.Id_provincia
                ORDER BY p.Provincia ASC, Grupo_Edad ASC;
""").df()

#%%======================================================================

terapia_intensiva = dd.query("""
        SELECT Id_Tipologia
        FROM Tipologia
        WHERE Tipologia_Nombre LIKE '%terapia intensiva%'
""").df()

establecimiento_con_terapia_intensiva = dd.query("""
        SELECT 
            Id_Establecimiento,
            Id_Origen_Financiamiento,
            Id_Departamento
        FROM Establecimientos_de_Salud AS ES
        INNER JOIN terapia_intensiva AS TI
        ON ES.Id_Tipologia = TI.Id_Tipologia
""").df()

Estatal_Privado = dd.query("""
        SELECT Id_Origen_Financiamiento, Origen_Financiamiento
        FROM Origen_Financiero
        WHERE Origen_Financiamiento = 'Nacional'
            OR Origen_Financiamiento = 'Provincial'
            OR Origen_Financiamiento = 'Municipal'
            OR Origen_Financiamiento = 'Privado'
            OR Origen_Financiamiento = 'Mixta'
""").df()

establecimiento_Estatal_Privado = dd.query("""
        SELECT 
            Id_Establecimiento,
            Origen_Financiamiento,
            Id_Departamento
        FROM establecimiento_con_terapia_intensiva AS ES
        INNER JOIN Estatal_Privado AS EP
        ON ES.Id_Origen_Financiamiento = EP.Id_Origen_Financiamiento
""").df()

Prov_Dep = dd.query("""
        SELECT 
            D.departamento_id AS Id_Departamento,
            P.Provincia
        FROM Provincia AS P
        INNER JOIN Departamentos AS D
        ON P.Id_Provincia = D.provincia_id
""").df()

establecimiento_Provincia = dd.query("""
        SELECT 
            Id_Establecimiento,
            Origen_Financiamiento,
            PD.Provincia
        FROM establecimiento_Estatal_Privado AS ES
        INNER JOIN Prov_Dep AS PD
        ON ES.Id_Departamento = PD.Id_Departamento
""").df()

Establecimientos_de_Salud_con_Terapia_Intensiva = dd.query("""
        SELECT 
            Provincia,
            Origen_Financiamiento,
            COUNT(Id_Establecimiento) AS Cantidad
        FROM establecimiento_Provincia
        GROUP BY Provincia, Origen_Financiamiento
        ORDER BY Provincia ASC, Origen_Financiamiento ASC
""").df()

#%%========================================

Frecuencia_Causa_Muerte = dd.query("""
        SELECT 
            Grupo_Edad,
            Sexo,
            Nombre_Causa_de_Muerte,
            COUNT(Cantidad) AS Frecuencia
        FROM se_producen
        GROUP BY Grupo_Edad, Sexo, Nombre_Causa_de_Muerte
        ORDER BY Frecuencia DESC;
""").df()

Mayor_Frecuencia_Causa_Muerte = dd.query("""
        SELECT 
            t1.Grupo_Edad, 
            t1.Sexo, 
            t1.Nombre_Causa_de_Muerte
        FROM Frecuencia_Causa_Muerte AS t1
        WHERE (
            SELECT COUNT(*)
            FROM Frecuencia_Causa_Muerte AS t2
            WHERE t2.Grupo_Edad = t1.Grupo_Edad AND 
                  t2.Sexo = t1.Sexo AND ( 
                      t2.frecuencia > t1.frecuencia OR (
                          t2.frecuencia = t1.frecuencia AND 
                          t2.Nombre_Causa_de_Muerte < t1.Nombre_Causa_de_Muerte)
            )) < 5
        ORDER BY Grupo_Edad, Sexo;
""").df()

Menor_Frecuencia_Causa_Muerte = dd.query("""
        SELECT 
            t1.Grupo_Edad, 
            t1.Sexo, 
            t1.Nombre_Causa_de_Muerte
        FROM Frecuencia_Causa_Muerte AS t1
        WHERE (
            SELECT COUNT(*)
            FROM Frecuencia_Causa_Muerte AS t2
            WHERE t2.Grupo_Edad = t1.Grupo_Edad AND 
                  t2.Sexo = t1.Sexo AND ( 
                      t2.frecuencia < t1.frecuencia OR (
                          t2.frecuencia = t1.frecuencia AND 
                          t2.Nombre_Causa_de_Muerte < t1.Nombre_Causa_de_Muerte)
            )) < 5
        ORDER BY Grupo_Edad, Sexo;
""").df()

Causas_de_Muerte = dd.query("""
            SELECT *
            FROM Mayor_Frecuencia_Causa_Muerte 
        UNION
            SELECT *
            FROM Menor_Frecuencia_Causa_Muerte
        ORDER BY Grupo_Edad ASC, Sexo ASC;
""").df()

#%%=======================================================

Mortalidad_por_provincia_2022 = dd.query("""
        SELECT Grupo_Edad AS Grupo_Etario,
           SP.Id_provincia AS Id_Provincia,
           P.Provincia AS Provincia,
           SUM(Cantidad) AS Cantidad_Defunciones
        FROM se_producen AS SP
        JOIN Provincia AS P 
          ON SP.Id_provincia = P.Id_Provincia
        WHERE Año = 2022
        GROUP BY SP.Id_provincia, P.Provincia, Grupo_Edad
        ORDER BY SP.Id_provincia, Grupo_Edad;
""").df()

Cantidad_de_poblacion = dd.query("""
        SELECT SUM(Cantidad) AS Cantidad_2022,
               Id_provincia AS Id_Provincia
        FROM se_realizan
        WHERE Año = 2022
        GROUP BY Id_provincia
        ORDER BY Id_provincia;  
""").df()

Tasa_de_mortalidad_por_provincia_2022 = dd.query("""
        SELECT mpp.Provincia, mpp.Grupo_Etario,
            (mpp.Cantidad_Defunciones / cm.Cantidad_2022) * 1000 AS Tasa_Mortalidad
        FROM Mortalidad_por_provincia_2022 AS mpp 
        JOIN Cantidad_de_poblacion AS cm ON mpp.Id_Provincia = cm.Id_Provincia;
""").df()

#%%=========================================================

defunciones2010 = dd.query("""
                SELECT Nombre_Causa_de_Muerte,
                SUM(Cantidad) AS Cantidad
                FROM defuncionesLIMPIO
                WHERE Año = 2010
                GROUP BY Nombre_Causa_de_Muerte
                ORDER BY Nombre_Causa_de_Muerte;
""").df()

defunciones2022 = dd.query("""
                SELECT Nombre_Causa_de_Muerte,
                SUM(Cantidad) AS Cantidad
                FROM defuncionesLIMPIO
                WHERE Año = 2022
                GROUP BY Nombre_Causa_de_Muerte
                ORDER BY Nombre_Causa_de_Muerte;
""").df()

Cambios_en_Causa_Defuncion = dd.query("""
                SELECT d10.Nombre_Causa_de_Muerte, (d22.Cantidad - d10.Cantidad) AS Diferencia
                FROM defunciones2022 AS d22
                INNER JOIN defunciones2010 AS d10
                ON d10.Nombre_Causa_de_Muerte = d22.Nombre_Causa_de_Muerte
                ORDER BY Diferencia DESC;
""").df()

#%%=================================================================================
# Creamos las Graficos pedidos en "Ejercicios: Analisis de Datos - Segunda Consigna"
#===================================================================================

Cantidad_de_habitantes_por_Provincia = dd.query("""
            SELECT 
                Año,
                ID_Provincia, 
                SUM(Cantidad) AS "Cantidad de Habitantes"
            FROM se_realizan
            GROUP BY Año, ID_Provincia
            ORDER BY ID_Provincia ASC
""").df()

Cantidad_de_habitantes_por_Provincia = dd.query("""
            SELECT 
                CHP.Año,
                P.Provincia, 
                CHP."Cantidad de Habitantes"
            FROM Cantidad_de_habitantes_por_Provincia AS CHP
            INNER JOIN Provincia AS P
            ON CHP.ID_Provincia = P.ID_Provincia
""").df()

fig, ax = plt.subplots()
sns.barplot(data=Cantidad_de_habitantes_por_Provincia, x='Provincia', y='Cantidad de Habitantes',
             hue='Año', ax=ax)

Abreviaturas = {'Ciudad Autónoma de Buenos Aires':'CABA', 'Buenos Aires':'BA', 'Catamarca':'Ct',
       'Córdoba':'Cd', 'Corrientes':'Cr', 'Chaco':'Cc', 'Chubut':'Ch', 'Entre Ríos':'ER',
       'Formosa':'Fr', 'Jujuy':'Jj', 'La Pampa':'LP', 'La Rioja':'LR', 'Mendoza':'Md', 'Misiones':'Ms',
       'Neuquén':'Nq', 'Río Negro':'RN', 'Salta':'St', 'San Juan':'SJ', 'San Luis':'SL',
       'Santa Cruz':'SC', 'Santa Fe':'SF', 'Santiago del Estero':'SE', 'Tucumán':'Tc',
       'Tierra del Fuego, Antártida e Islas del Atlántico Sur':'TF'}

xtickslabels = [Abreviaturas[prov.get_text()] for prov in ax.get_xticklabels()]
plt.title('Cantidad de habitantes por provincia para 2010 y 2022')
plt.xlabel('Provincia')
plt.ylabel('Cantidad de Habitantes')
plt.xticks(ticks=range(len(xtickslabels)), 
           labels=xtickslabels, rotation=90)
plt.show()

#%%================================================================

datos_cie10 = [
    (1, "Ciertas enfermedades infecciosas y parasitarias", "A", 0, "B", 99),
    (2, "Tumores [neoplasias]", "C", 0, "D", 48),
    (3, "Enfermedades de la sangre y de los órganos hematopoyéticos, y ciertos trastornos que afectan el mecanismo de la inmunidad", "D", 50, "D", 89),
    (4, "Enfermedades endocrinas, nutricionales y metabólicas", "E", 0, "E", 90),
    (5, "Trastornos mentales y del comportamiento", "F", 0, "F", 99),
    (6, "Enfermedades del sistema nervioso", "G", 0, "G", 99),
    (7, "Enfermedades del ojo y sus anexos", "H", 0, "H", 59),
    (8, "Enfermedades del oído y de la apófisis mastoides", "H", 60, "H", 95),
    (9, "Enfermedades del sistema circulatorio", "I", 0, "I", 99),
    (10, "Enfermedades del sistema respiratorio", "J", 0, "J", 99),
    (11, "Enfermedades del sistema digestivo", "K", 0, "K", 99),
    (12, "Enfermedades de la piel y del tejido subcutáneo", "L", 0, "L", 99),
    (13, "Enfermedades del sistema osteomuscular y del tejido conectivo", "M", 0, "M", 99),
    (14, "Enfermedades del sistema genitourinario", "N", 0, "N", 99),
    (15, "Embarazo, parto y puerperio", "O", 0, "O", 99),
    (16, "Ciertas afecciones originadas en el período perinatal", "P", 0, "P", 96),
    (17, "Malformaciones congénitas, deformidades y anomalías cromosómicas", "Q", 0, "Q", 99),
    (18, "Síntomas, signos y hallazgos anormales de pruebas clínicas y de laboratorio, no clasificados en otra parte", "R", 0, "R", 99),
    (19, "Traumatismos, envenenamientos y algunas otras consecuencias de causas externas", "S", 0, "T", 98),
    (20, "Causas externas de morbilidad y de mortalidad", "V", 1, "Y", 98),
    (21, "Factores que influyen en el estado de salud y contacto con los servicios de salud", "Z", 0, "Z", 99),
    (22, "Códigos para situaciones especiales (Causas mal definidas)", "U", 0, "U", 99)
]

df_capitulos = pd.DataFrame(datos_cie10, columns=[
    'Nro_Capitulo', 'Capitulo', 'Letra_Inicio', 'Numero_Inicio', 'Letra_Fin', 'Numero_Fin'
])

categoria = dd.query("""
            SELECT DISTINCT
                    LEFT(cie10_causa_id, 1) AS Categoria,
                    SUBSTR(cie10_causa_id, 2) AS Subcategoria,
                    cie10_clasificacion AS Nombre_Causa_de_Muerte
                FROM defunciones 
                ORDER BY Categoria, Subcategoria;
            """).df()

categoria_final = dd.query("""
                        SELECT 
                            c.Nro_Capitulo,
                            c.Capitulo AS Nombre_Capitulo,
                            cat.Categoria,
                            cat.Subcategoria,
                            cat.Nombre_Causa_de_Muerte
                        FROM categoria AS cat
                        JOIN df_capitulos AS c 
                        ON (cat.Categoria, CAST(cat.Subcategoria AS FLOAT)) 
                            BETWEEN (c.Letra_Inicio, CAST(c.Numero_Inicio AS FLOAT)) 
                                AND (c.Letra_Fin, CAST(c.Numero_Fin AS FLOAT))
                        ORDER BY c.Nro_Capitulo, cat.Categoria, cat.Subcategoria;
""").df()

segundo_grafico = dd.query("""
        SELECT 
            c.Nro_Capitulo,
            Año,
            SUM(Cantidad) AS Cantidad_Defunciones
        FROM se_producen as sp
        JOIN categoria_final AS c ON sp.Nombre_Causa_de_Muerte = c.Nombre_Causa_de_Muerte
        GROUP BY c.Nro_Capitulo, Año 
        ORDER BY c.Nro_Capitulo, Año;      
""").df()

#%%

cantidad_categorias = segundo_grafico['Nro_Capitulo'].nunique()
print(f"Cantidad de categorías de muerte: {cantidad_categorias}")

colors = plt.get_cmap('viridis')(np.linspace(0, 1, cantidad_categorias))

sns.lineplot(data=segundo_grafico, x='Año', y='Cantidad_Defunciones',
              hue='Nro_Capitulo', palette=colors)
plt.title('Defunciones por categoría a lo largo del tiempo')
plt.xlabel('Año')
plt.legend(title='Capitulos según CIE10', bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2)
plt.ylabel('Cantidad de Defunciones')
plt.show()

#%%

fig, ax = plt.subplots(2, 1, figsize=(8, 10), sharex=True)
plt.subplots_adjust(hspace=0.1)

mascara0 = (segundo_grafico['Cantidad_Defunciones'] > 2.5e4) & (segundo_grafico['Año'] == 2022)
mayor_muertes = segundo_grafico[mascara0]['Nro_Capitulo'].unique()
mascara01 = segundo_grafico['Nro_Capitulo'].isin(mayor_muertes)
menor_muertes = segundo_grafico[~mascara01]['Nro_Capitulo'].unique()

colors = plt.get_cmap('viridis')(np.linspace(0.5, 1, len(mayor_muertes)))
colors2 = plt.get_cmap('plasma')(np.linspace(0, 1, len(menor_muertes)))

g1 = sns.lineplot(data=segundo_grafico[mascara01], x='Año', y='Cantidad_Defunciones',
                  hue='Nro_Capitulo', palette=colors, ax=ax[0], legend='brief')

g2 = sns.lineplot(data=segundo_grafico[~mascara01], x='Año', y='Cantidad_Defunciones',
                  hue='Nro_Capitulo', palette=colors2, ax=ax[1], legend='brief')

ax[0].set_ylabel('Cantidad de Defunciones \n (en unidades de miles)', fontsize=12)
ax[1].set_ylabel('Cantidad de Defunciones \n(en unidades de miles)', fontsize=12)
ax[1].set_xlabel('Año')

ax[0].legend(title='Capitulos según CIE10 \n mayor cantidad de muertes', bbox_to_anchor=(1.05, 1), 
             loc='upper left', ncol=2, fontsize=12)
ax[1].legend(title='Capitulos según CIE10', bbox_to_anchor=(1.05, 1),
              loc='upper left', ncol=2, fontsize=12)
year = range(2005, 2023, 2)  
plt.xticks(year)
ax[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x/1e3:.1f}"))
ax[1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x/1e3:.1f}"))
plt.show()

#%%

segundo_grafico_bis = dd.query("""
        SELECT 
            c.Nro_Capitulo,
            Año,
            AVG(sp.Cantidad) AS Cantidad_Defunciones
        FROM se_producen as sp
        INNER JOIN categoria_final AS c ON sp.Nombre_Causa_de_Muerte = c.Nombre_Causa_de_Muerte
        GROUP BY c.Nro_Capitulo, Año 
        ORDER BY c.Nro_Capitulo, Año;      
""").df()

cantidad_categorias = segundo_grafico_bis['Nro_Capitulo'].nunique()
print(f"Cantidad de categorías de muerte: {cantidad_categorias}")

colors = plt.get_cmap('viridis')(np.linspace(0, 1, cantidad_categorias))

sns.lineplot(data=segundo_grafico_bis, x='Año', y='Cantidad_Defunciones',
              hue='Nro_Capitulo', palette=colors)
plt.title('Promedio de defunciones por categoría entre 2005 y 2022')
plt.xlabel('Año')
plt.legend(title='Capitulos según CIE10', bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2)
plt.ylabel('Promedio de Defunciones')
year = range(2005, 2023, 2)  
plt.xticks(year)
plt.show()

#%%========================================================

Abreviaturas = {'Ciudad Autónoma de Buenos Aires':'CABA', 'Buenos Aires':'BA', 'Catamarca':'Ct',
       'Córdoba':'Cd', 'Corrientes':'Cr', 'Chaco':'Cc', 'Chubut':'Ch', 'Entre Ríos':'ER',
       'Formosa':'Fr', 'Jujuy':'Jj', 'La Pampa':'LP', 'La Rioja':'LR', 'Mendoza':'Md', 'Misiones':'Ms',
       'Neuquén':'Nq', 'Río Negro':'RN', 'Salta':'St', 'San Juan':'SJ', 'San Luis':'SL',
       'Santa Cruz':'SC', 'Santa Fe':'SF', 'Santiago del Estero':'SE', 'Tucumán':'Tc',
       'Tierra del Fuego, Antártida e Islas del Atlántico Sur':'TF'}

Mortalidad_por_provincia_2022 = dd.query("""
        SELECT
           SP.Id_provincia AS Id_Provincia,
           P.Provincia AS Provincia,
           SUM(Cantidad) AS Cantidad_Defunciones
    FROM se_producen AS SP
    JOIN Provincia AS P 
      ON SP.Id_provincia = P.Id_Provincia
    WHERE Año = 2022
    GROUP BY SP.Id_provincia, P.Provincia
    ORDER BY SP.Id_provincia;
""").df()

Cantidad_de_poblacion = dd.query("""
               SELECT SUM(Cantidad) AS Cantidad_2022,
                      Id_provincia AS Id_Provincia
               FROM se_realizan
               WHERE Año = 2022
               GROUP BY Id_provincia
               ORDER BY Id_provincia;  
""").df()

tercer_grafico = dd.query("""
            SELECT mpp.Provincia,
                (mpp.Cantidad_Defunciones / cm.Cantidad_2022) * 1000 AS Tasa_Mortalidad
            FROM Mortalidad_por_provincia_2022 AS mpp 
            JOIN Cantidad_de_poblacion AS cm ON mpp.Id_Provincia = cm.Id_Provincia
            ORDER BY Tasa_Mortalidad;
""").df()

mascara = tercer_grafico['Provincia'].isin(Abreviaturas.keys())

ax = sns.barplot(data=tercer_grafico[mascara], x='Provincia',
             y='Tasa_Mortalidad', ci=None)

xtickslabels = [Abreviaturas[prov.get_text()] for prov in ax.get_xticklabels()]
plt.xlabel('Provincia')
plt.ylabel('Tasa de Mortalidad (por cada 1000 habitantes)')
plt.xticks(ticks=range(len(xtickslabels)), 
           labels=xtickslabels, rotation=90)
plt.show()

#%%

Mortalidad_por_provincia_2022 = dd.query("""
        SELECT 
           SP.Id_provincia AS Id_Provincia,
           P.Provincia AS Provincia,
           CASE 
            WHEN Sexo IN ('femenino') THEN 'Femenino'
            WHEN Sexo IN ('masculino') THEN 'Masculino'
            END AS Sexo,
           SUM(Cantidad) AS Cantidad_Defunciones
    FROM se_producen AS SP
    JOIN Provincia AS P 
      ON SP.Id_provincia = P.Id_Provincia
    WHERE Año = 2022 
    GROUP BY SP.Id_provincia, P.Provincia, Sexo
    ORDER BY SP.Id_provincia;
""").df()

Cantidad_de_poblacion = dd.query("""
               SELECT SUM(Cantidad) AS Cantidad_2022,
                      Id_provincia AS Id_Provincia,
                      Sexo
               FROM se_realizan
               WHERE Año = 2022
               GROUP BY Id_provincia, Sexo
               ORDER BY Id_provincia;  
""").df()

tercer_grafico_bis = dd.query("""
            SELECT mpp.Provincia, mpp.Sexo,
                (mpp.Cantidad_Defunciones / cm.Cantidad_2022) * 1000 AS Tasa_Mortalidad
            FROM Mortalidad_por_provincia_2022 AS mpp 
            RIGHT JOIN Cantidad_de_poblacion AS cm 
            ON mpp.Id_Provincia = cm.Id_Provincia
            AND mpp.Sexo = cm.Sexo
            ORDER BY mpp.Sexo, Tasa_Mortalidad;
""").df()

mascara = tercer_grafico_bis['Provincia'].isin(Abreviaturas.keys())

ax = sns.barplot(data=tercer_grafico_bis[mascara], x='Provincia',
             y='Tasa_Mortalidad', hue='Sexo', ci=None)

xtickslabels = [Abreviaturas[prov.get_text()] for prov in ax.get_xticklabels()]
plt.title('Tasa de mortalidad por provincia en 2022')
plt.xlabel('Provincia')
plt.ylabel('Tasa de Mortalidad (por cada 1000 habitantes)')
plt.xticks(ticks=range(len(xtickslabels)), 
           labels=xtickslabels, rotation=90)
plt.show()

#%%===================================================

defunciones_por_Sexo_GrupoEtario = dd.query("""
                SELECT SUM(Cantidad) AS Cantidad, Sexo, Grupo_Edad
                FROM se_producen
                WHERE Año = 2022
                GROUP BY Grupo_Edad, Sexo
                ORDER BY Grupo_Edad;
""").df()

fig, ax = plt.subplots(figsize=(10,6))

sns.barplot(
    data=defunciones_por_Sexo_GrupoEtario,
    x='Grupo_Edad',
    y='Cantidad',
    hue='Sexo',
    order=['De a 0  a 14 anios','De 15 a 34 anios','De 35 a 54 anios','De 55 a 74 anios','De 75 anios y mas'],
    palette={
        'masculino': 'skyblue',
        'femenino': 'orange',
    },
    ax=ax
)

ax.set_title('Defunciones por sexo y grupo etario en 2022')
ax.set_xlabel('Grupo etario')
ax.set_ylabel('Cantidad de defunciones')

for container in ax.containers:
    ax.bar_label(container, fontsize=8)

plt.legend(title='Sexo')
plt.tight_layout()
plt.show()

#%%=========================================================

Cantidad_de_establecimientos_de_salud_por_Departamento = dd.query("""
        SELECT 
            D.departamento_id AS Id_Departamento,
            P.Provincia,
            D.departamento_nombre AS Departamento
        FROM Provincia AS P
        INNER JOIN Departamentos AS D
        ON P.Id_Provincia = D.provincia_id
""").df()

Cantidad_de_establecimientos_de_salud_por_Departamento = dd.query("""
        SELECT 
            PD.Provincia,
            PD.Departamento,
            ES.Id_Establecimiento
        FROM Establecimientos_de_Salud AS ES
        INNER JOIN Cantidad_de_establecimientos_de_salud_por_Departamento AS PD
        ON ES.Id_Departamento = PD.Id_Departamento;
""").df()

Cantidad_de_establecimientos_de_salud_por_Departamento = dd.query("""
        SELECT 
            Provincia,
            Departamento,
            COUNT(Id_Establecimiento) AS "Cantidad de Establecimientos de Salud"
        FROM Cantidad_de_establecimientos_de_salud_por_Departamento AS PD
        GROUP BY Provincia, Departamento
        ORDER BY Provincia, Departamento;
""").df()

prov_ordenas = Cantidad_de_establecimientos_de_salud_por_Departamento.groupby('Provincia')['Cantidad de Establecimientos de Salud'].median().sort_values().index

ax = sns.boxplot(
    data=Cantidad_de_establecimientos_de_salud_por_Departamento, 
    x="Provincia", 
    y="Cantidad de Establecimientos de Salud", 
    order=prov_ordenas,
    showfliers=True)

ax.set_title('Distribución de establecimientos de salud por departamento en cada provincia (con outliers)')
ax.set_xlabel('Provincia')
ax.set_ylabel('Cantidad de Establecimientos de Salud')

xtickslabels = [Abreviaturas[prov.get_text()] for prov in ax.get_xticklabels()]
plt.xticks(ticks=range(len(xtickslabels)), 
           labels=xtickslabels, rotation=90)
plt.show()

#%%

prov_ordenas = Cantidad_de_establecimientos_de_salud_por_Departamento.groupby('Provincia')['Cantidad de Establecimientos de Salud'].median().sort_values().index

ax = sns.boxplot(
    data=Cantidad_de_establecimientos_de_salud_por_Departamento, 
    x="Provincia", 
    y="Cantidad de Establecimientos de Salud", 
    order=prov_ordenas,
    showfliers=False)

ax.set_xlabel('Provincia')
ax.set_ylabel('Cantidad de Establecimientos de Salud')

xtickslabels = [Abreviaturas[prov.get_text()] for prov in ax.get_xticklabels()]
plt.xticks(ticks=range(len(xtickslabels)), 
           labels=xtickslabels, rotation=90)
plt.show()

#%%================================================================================

cantidad_total_habitantes_en_censos = dd.query("""                                 
                SELECT Año, SUM("Cantidad de Habitantes") AS "Cantidad Total"
                FROM Cantidad_de_habitantes_por_Provincia 
                GROUP BY Año
""").df()

defunciones_2010_2022 = dd.query("""
                SELECT Año, Grupo_Edad, SUM(Cantidad) AS Cantidad
                FROM se_producen AS sp
                WHERE (Año = 2010 OR Año = 2022) 
                GROUP BY Año, Grupo_Edad
                ORDER BY Año, Grupo_Edad;
""").df()

defunciones_2010_2022 = dd.query("""
                SELECT d.Año, Grupo_Edad, (Cantidad / "Cantidad Total") AS Total
                FROM defunciones_2010_2022 AS d
                INNER JOIN cantidad_total_habitantes_en_censos AS c
                ON d.Año = c.Año
                GROUP BY d.Año, Grupo_Edad, Total
""").df()

defunciones_2010_2022['Por_mil'] = defunciones_2010_2022['Total'] * 1000

fig, ax = plt.subplots(figsize=(10,6))

sns.barplot(
    data=defunciones_2010_2022,
    x='Grupo_Edad',
    y='Por_mil',
    hue='Año',
    order=['De a 0  a 14 anios','De 15 a 34 anios', 'De 35 a 54 anios', 'De 55 a 74 anios' ,'De 75 anios y mas'],
    palette={
        2010: 'skyblue',
        2022 : 'orange',
    },
    ax=ax
)

ax.set_title('Diferencia entre fallecidos en 2010 y 2022')
ax.set_xlabel('Grupo de edad')
ax.set_ylabel('Cantidad de defunciones')

for container in ax.containers:
    ax.bar_label(container, fontsize=12)

plt.tight_layout()
plt.show()

#%%

cobertura_por_provincia2010 = dd.query("""
                SELECT p.Provincia, Año, Cobertura_de_Salud, SUM(Cantidad) AS Cantidad
                FROM se_realizan AS s
                INNER JOIN Provincia AS p
                ON p.Id_Provincia = s.Id_Provincia
                WHERE (p.Provincia = 'Buenos Aires' 
                OR 
                p.Provincia = 'Ciudad Autónoma de Buenos Aires'
                OR
                p.Provincia = 'Santa Fe'
                OR 
                p.Provincia = 'Córdoba')
                AND 
                Año = 2010
                GROUP BY p.Provincia, Año, Cobertura_de_Salud;
""").df()

sns.set(style="whitegrid")

plt.figure(figsize=(12,6))

sns.barplot(
    data=cobertura_por_provincia2010,
    x="Provincia",
    y="Cantidad",
    hue="Cobertura_de_Salud",
    order=['Buenos Aires', 'Ciudad Autónoma de Buenos Aires', 'Córdoba', 'Santa Fe']
)

plt.title("Cobertura de Salud por Provincia (2010)")
plt.ylabel("Cantidad de habitantes")

plt.tight_layout()
plt.ticklabel_format(style='plain', axis='y')
plt.show()

#%%

cobertura_por_provincia2022 = dd.query("""
                SELECT p.Provincia, Año, Cobertura_de_Salud, SUM(Cantidad) AS Cantidad
                FROM se_realizan AS s
                INNER JOIN Provincia AS p
                ON p.Id_Provincia = s.Id_Provincia
                WHERE (p.Provincia = 'Buenos Aires' 
                OR 
                p.Provincia = 'Ciudad Autónoma de Buenos Aires'
                OR
                p.Provincia = 'Santa Fe'
                OR 
                p.Provincia = 'Córdoba')
                AND 
                Año = 2022
                GROUP BY p.Provincia, Año, Cobertura_de_Salud;
""").df()

sns.set(style="whitegrid")

plt.figure(figsize=(12,6))

sns.barplot(
    data=cobertura_por_provincia2022,
    x="Provincia",
    y="Cantidad",
    hue="Cobertura_de_Salud",
    order=['Buenos Aires', 'Ciudad Autónoma de Buenos Aires', 'Córdoba', 'Santa Fe']
)

plt.title("Cobertura de Salud por Provincia (2022)")
plt.ylabel("Cantidad de habitantes")

plt.tight_layout()
plt.ticklabel_format(style='plain', axis='y')
plt.show()