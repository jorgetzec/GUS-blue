# Cuantificación de Píxeles GUS-blue

<p align="center">
  <img src="https://raw.githubusercontent.com/jorgetzec/GUS-blue/main/gus_blue_logo.png" width="300">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-brightgreen?style=flat-square&logo=python" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License: MIT">
  <a href="https://doi.org/10.5281/zenodo.18726152"><img src="https://zenodo.org/badge/1163053683.svg" alt="DOI"></a>
  <img src="https://img.shields.io/badge/Status-Active-success?style=flat-square" alt="Status">
</p>

Este proyecto proporciona herramientas automatizadas para la cuantificación de tinción azul (GUS) en raíces de *Arabidopsis* mediante procesamiento de imágenes con OpenCV.

## Requisitos y Configuración

Utilizamos `uv` para la gestión de dependencias y entornos virtuales.

```bash
# 1. Inicializar ambiente con uv
uv init --app

# 2. Añadir dependencias necesarias
uv add opencv-python numpy matplotlib pandas ipykernel streamlit
```

---

## Formas de Uso (Las 3 Versiones)

### 1. Aplicación Web (Streamlit)
Ideal para usuarios que buscan una interfaz visual sin tocar código o para despliegue en la nube.
Visita https://gus-blue.streamlit.app/ para usar la aplicación.

- **Archivo:** `gus_blue_app.py`
- **Uso:** 
  ```bash
  streamlit run gus_blue_app.py
  ```
- **Características:** Subida de múltiples fotos, sliders interactivos para ajustar colores y descarga de resultados en CSV.

### 2. Herramienta de Línea de Comandos (CLI)
Ideal para procesamiento por lotes, automatización y rapidez extrema.

- **Archivo:** `gus-blue_quantification.py`
- **Comando básico:**

```bash
# Procesar todas las imágenes en la carpeta 'plant_photos'
python gus-blue_quantification.py

# Guardar los gráficos de validación automáticamente en la carpeta 'results/'
  python gus-blue_quantification.py --save-plots

# Especificar entrada, salida y personalizar el rango de azul (HSV)
python gus-blue_quantification.py -i mis_imagenes -o reporte_final.csv --hsv-lower 95 45 45
```

---

## Parámetros Principales

| Parámetro | CLI Flag | Descripción | Default |
| :--- | :--- | :--- | :--- |
| Entrada | `-i`, `--input` | Carpeta con fotos (`.jpg`, `.png`, etc.) | `plant_photos` |
| Salida | `-o`, `--output` | Nombre del archivo CSV de resultados | `resultados_gus.csv` |
| Plots | `--save-plots` | Guarda las comparaciones visuales en disco | `False` |
| HSV Lower | `--hsv-lower` | Límite inferior H S V para detección de azul | `90 40 40` |
| HSV Upper | `--hsv-upper` | Límite superior H S V para detección de azul | `140 255 255` |
| Root S | `--root-s` | Umbral de saturación mínima para la raíz | `20` |
| Root V | `--root-v` | Brillo máximo para excluir el fondo de la raíz | `240` |

---

## Detección de tonos azules con HSV

- **H (Hue / Matiz):** controla el rango de color. Para el azul suele estar entre 90–140.
- **S (Saturation / Saturación):** controla qué tan “puro” es el color. Valores bajos permiten captar colores deslavados o mezclados con blanco.
- **V (Value / Brillo):** controla la luminosidad. Valores bajos permiten incluir píxeles más oscuros.

### Estrategia de ajuste

1.  **Expandir el rango de saturación (S):**
    - Si los azules tenues no se capturan, probablemente su saturación es baja.
    - Ejemplo: cambiar el límite inferior de `S` de **40 → 20**.
    - Esto permitirá incluir píxeles azulados más deslavados.

2.  **Ajustar el rango de brillo (V):**
    - Si hay zonas azul oscuro que quieres mantener, asegúrate de que el límite inferior de `V` no sea demasiado alto.
    - Ejemplo: bajar `V` de **40 → 20** para incluir tonos más apagados.

3.  **Mantener el rango de H estable:**
    - El azul intenso y tenue suele caer dentro de 90–140.
    - Puedes probar ampliar un poco, por ejemplo 85–145, si notas que ciertos tonos se quedan fuera.

### Ejemplo de parámetros

```bash
# Ajuste de parámetros. Para detectar tonos azules más claros y tenues
python gus-blue_quantification.py --save-plots --hsv-lower 85 20 20 --hsv-upper 145 255 255

# Ajuste de parámetros. Estos parámetros detectan tonos azules aún más claros y tenues
python gus-blue_quantification.py --save-plots --hsv-lower 80 15 15 --hsv-upper 150 255 255 
```

### Consejos prácticos

- **Itera con muestras representativas:** prueba con varias imágenes para evitar sobreajustar a un solo caso.
- **Usa `--save-plots`:** así puedes visualizar qué píxeles se están capturando y ajustar con retroalimentación inmediata.
- **Evita rangos demasiado amplios:** si bajas demasiado `S` y `V`, corres el riesgo de incluir ruido (zonas grises o sombras).

## Lógica de Cuantificación (Protocolo)

El algoritmo asegura precisión normalizando los resultados por el tamaño de la muestra:

1.  **Segmentación de Raíz:** El algoritmo identifica el área total de la raíz (`root_area`) ignorando el fondo.
2.  **Detección Selectiva:** Solo se contabilizan los píxeles azules que se encuentran **dentro** de la raíz.
3.  **Normalización:** 
    `Porcentaje_Azul = (Píxeles_Azules_en_Raíz / Total_Píxeles_Raíz) * 100`

---

## Resultados

Ambas herramientas generan un informe detallado con:

- Pixeles totales de la raíz.
- Pixeles teñidos de azul.
- **Porcentaje de tinción (%)** normalizado por área.

## Despliegue

Este repositorio está listo para ser conectado a **Streamlit Cloud**:
1. Sube este código a un repositorio de GitHub.
2. Conecta el repositorio en [streamlit.io/cloud](https://streamlit.io/cloud).
3. Selecciona `gus_blue_app.py` como punto de entrada.

---

## Citación

Si utilizas esta herramienta en tu investigación, por favor cítala como:

> jorgetzec. (2026). jorgetzec/GUS-blue: GUS-Blue_v1.0.0 (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.18726152