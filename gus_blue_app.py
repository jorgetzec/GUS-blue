import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io

def process_gus_image(img_bgr, blue_lower, blue_upper, root_params):
    """
    Procesa una imagen BGR para detectar la raíz y la tinción azul.
    """
    # 1. Preprocesamiento: Desenfoque Gaussiano
    blurred = cv2.GaussianBlur(img_bgr, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # 2. Segmentación de la Raíz
    root_s_threshold, root_v_max = root_params
    root_mask = cv2.inRange(hsv, np.array([0, root_s_threshold, 0]), np.array([179, 255, root_v_max]))
    
    # 3. Detección de Azul
    blue_mask_raw = cv2.inRange(hsv, blue_lower, blue_upper)
    blue_mask_in_root = cv2.bitwise_and(blue_mask_raw, root_mask)
    
    # 4. Limpieza Morfológica
    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], np.uint8)
    blue_mask_clean = cv2.morphologyEx(blue_mask_in_root, cv2.MORPH_OPEN, kernel)
    
    # Cuantificación
    root_area = np.sum(root_mask > 0)
    blue_area = np.sum(blue_mask_clean > 0)
    percentage = (blue_area / root_area * 100) if root_area > 0 else 0
    
    return {
        'original': cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB),
        'root_mask': root_mask,
        'blue_mask': blue_mask_clean,
        'metrics': {
            'root_pixels': int(root_area),
            'blue_pixels': int(blue_area),
            'percentage': round(percentage, 2)
        }
    }

st.set_page_config(page_title="GUS-blue Quantifier", layout="wide")

# --- Logo Centrado ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("gus_blue_logo.png", use_column_width=True)

st.title("Cuantificación de Tinción GUS-blue")
st.markdown("Carga tus fotos de raíces de Arabidopsis para calcular automáticamente el porcentaje de tinción azul.")

# --- Barra Lateral de Parámetros ---
st.sidebar.header("Parámetros de Ajuste")

st.sidebar.subheader("Rango de Color Azul (HSV)")
h_range = st.sidebar.slider("H (Hue)", 0, 179, (90, 140))
s_range = st.sidebar.slider("S (Saturation)", 0, 255, (40, 255))
v_range = st.sidebar.slider("V (Value)", 0, 255, (40, 255))

st.sidebar.subheader("Detección de Raíz")
root_s = st.sidebar.slider("Umbral Sat. Raíz", 0, 100, 20)
root_v = st.sidebar.slider("Valor Máx Raíz (Brillo)", 100, 255, 240)

blue_lower = np.array([h_range[0], s_range[0], v_range[0]])
blue_upper = np.array([h_range[1], s_range[1], v_range[1]])
root_params = (root_s, root_v)

# --- Carga de Archivos ---
uploaded_files = st.file_uploader("Sube una o varias imágenes (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    results = []
    
    for uploaded_file in uploaded_files:
        # Leer imagen
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        
        # Convertir RGB a BGR para OpenCV
        if img_array.shape[2] == 4: # Manejar RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Procesar
        data = process_gus_image(img_bgr, blue_lower, blue_upper, root_params)
        
        if data:
            metrics = data['metrics']
            metrics['Archivo'] = uploaded_file.name
            results.append(metrics)
            
            with st.expander(f"Ver Análisis: {uploaded_file.name}"):
                col1, col2, col3 = st.columns(3)
                col1.image(data['original'], caption="Original", use_column_width=True)
                col2.image(data['root_mask'], caption="Máscara de Raíz", use_column_width=True)
                col3.image(data['blue_mask'], caption=f"Tinción Detectada: {metrics['percentage']}%", use_column_width=True)

    # --- Resultados Globales ---
    if results:
        st.markdown("---")
        st.subheader("Resultados Finales")
        df = pd.DataFrame(results)
        cols = ['Archivo', 'percentage', 'blue_pixels', 'root_pixels']
        df = df[cols].rename(columns={'percentage': 'Porcentaje Azul (%)', 'blue_pixels': 'Píxeles Azules', 'root_pixels': 'Total Píxeles Raíz'})
        
        st.dataframe(df)
        
        # Botón de Descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Resultados (CSV)",
            data=csv,
            file_name="resultados_gus_streamlit.csv",
            mime="text/csv",
        )
else:
    st.info("Por favor, sube una imagen en el panel central para comenzar.")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**DOI:** [![DOI](https://zenodo.org/badge/1163053683.svg)](https://doi.org/10.5281/zenodo.18726152)")

st.sidebar.info("""
**Instrucciones:**
1. Ajusta los **rangos HSV** si no se capta el azul correctamente.
2. Amplía el rango de **Saturation (S)** y baja el **Value (V)** para tonos más tenues.
3. El porcentaje se calcula **respecto al área de la raíz**, no de la foto.

**Cómo citar:**
jorgetzec. (2026). jorgetzec/GUS-blue: GUS-Blue_v1.0.0 (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.18726152
""")
