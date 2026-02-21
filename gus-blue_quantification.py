#!/usr/bin/env python3
"""
Protocolo de Cuantificación de Píxeles GUS-blue (Herramienta CLI)
----------------------------------------------------------------
Este script permite la cuantificación automatizada de tinción azul (GUS) 
en raíces de Arabidopsis desde la línea de comandos.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse
import sys

def process_gus_image(image_path, blue_lower, blue_upper, root_params):
    """
    Procesa una imagen para detectar la raíz y la tinción azul.
    """
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return None
    
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

def main():
    parser = argparse.ArgumentParser(description="Herramienta de cuantificación GUS-blue")
    
    # Argumentos de ruta
    parser.add_argument("-i", "--input", default="plant_photos", help="Directorio de entrada de imágenes")
    parser.add_argument("-o", "--output", default="resultados_gus.csv", help="Archivo CSV de salida")
    parser.add_argument("--save-plots", action="store_true", help="Guardar imágenes de validación en la carpeta 'results'")
    
    # Argumentos de filtrado (HSV)
    parser.add_argument("--hsv-lower", nargs=3, type=int, default=[90, 40, 40], metavar=('H', 'S', 'V'),
                        help="Límite inferior HSV para azul (default: 90 40 40)")
    parser.add_argument("--hsv-upper", nargs=3, type=int, default=[140, 255, 255], metavar=('H', 'S', 'V'),
                        help="Límite superior HSV para azul (default: 140 255 255)")
    
    # Argumentos de raíz
    parser.add_argument("--root-s", type=int, default=20, help="Saturación mínima para raíz (default: 20)")
    parser.add_argument("--root-v", type=int, default=240, help="Valor máximo para raíz (default: 240)")

    args = parser.parse_args()

    # Configuración de parámetros
    blue_lower = np.array(args.hsv_lower)
    blue_upper = np.array(args.hsv_upper)
    root_params = (args.root_s, args.root_v)

    # Buscar imágenes
    if not os.path.exists(args.input):
        print(f"Error: El directorio '{args.input}' no existe.")
        sys.exit(1)

    exts = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')
    image_paths = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.lower().endswith(exts)]

    if not image_paths:
        print(f"No se encontraron imágenes válidas en '{args.input}'.")
        sys.exit(0)

    print(f"--- Iniciando procesamiento de {len(image_paths)} imágenes ---")
    
    if args.save_plots:
        os.makedirs("results", exist_ok=True)

    all_results = []

    for path in image_paths:
        name = os.path.basename(path)
        print(f"Procesando: {name}...")
        
        data = process_gus_image(path, blue_lower, blue_upper, root_params)
        
        if data:
            metrics = data['metrics']
            metrics['Archivo'] = name
            all_results.append(metrics)
            
            # Generar visualización
            fig, axs = plt.subplots(1, 3, figsize=(15, 5))
            axs[0].imshow(data['original'])
            axs[0].set_title(f"Original: {name}")
            axs[1].imshow(data['root_mask'], cmap='gray')
            axs[1].set_title("Máscara de Raíz")
            axs[2].imshow(data['blue_mask'], cmap='Blues')
            axs[2].set_title(f"Azul: {metrics['percentage']}%")
            for ax in axs: ax.axis('off')
            
            if args.save_plots:
                plt.savefig(f"results/check_{name}")
                plt.close()
            else:
                plt.show()

    # Guardar CSV
    if all_results:
        df = pd.DataFrame(all_results)
        # Reordenar columnas para que 'Archivo' sea la primera
        cols = ['Archivo'] + [c for c in df.columns if c != 'Archivo']
        df = df[cols]
        df.to_csv(args.output, index=False)
        print(f"\n--- Análisis completado ---")
        print(f"Resultados guardados en: {args.output}")
        if args.save_plots:
            print("Visualizaciones guardadas en la carpeta 'results/'")
    else:
        print("No se pudieron procesar las imágenes.")

if __name__ == "__main__":
    main()