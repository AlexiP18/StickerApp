

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from tkinter import filedialog, messagebox, colorchooser
import os
import datetime
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from PIL import Image
import pandas as pd
import json

# --- Paleta de colores dinámica ---
RUTA_PALETA = os.path.join(os.path.dirname(__file__), 'colores.json')
def cargar_paleta_colores():
    if not os.path.exists(RUTA_PALETA):
        return {}
    with open(RUTA_PALETA, 'r', encoding='utf-8') as f:
        return json.load(f)
def guardar_paleta_colores(paleta):
    with open(RUTA_PALETA, 'w', encoding='utf-8') as f:
        json.dump(paleta, f, indent=2, ensure_ascii=False)

def generar_pdf_caja(data, ruta_pdf=None, mostrar_mensaje=True):
    # ...existing code...
    def definir_colores_nuevos(colores_nuevos, paleta):
        import tkinter as tk
        from definir_colores_window import DefinirColoresWindow
        root = None
        try:
            root = tk._default_root
        except Exception:
            pass
        if not root:
            root = tk.Tk()
            root.withdraw()
        resultado = {}
        def on_guardar_colores(res):
            resultado.update(res)
            paleta.update(res)
            guardar_paleta_colores(paleta)
        win = DefinirColoresWindow(root, colores_nuevos, on_guardar_colores)
        win.grab_set()
        root.wait_window(win)

    # Detectar colores en el Excel
    colores_en_excel = set()
    for row in data.itertuples():
        for c in str(getattr(row, 'COLOR', '')).split('/'):
            c = c.strip().upper()
            if c:
                colores_en_excel.add(c)
    paleta = cargar_paleta_colores()
    colores_nuevos = [c for c in colores_en_excel if c not in paleta]
    if colores_nuevos:
        definir_colores_nuevos(colores_nuevos, paleta)
        paleta = cargar_paleta_colores()
    if ruta_pdf is None:
        carpeta = filedialog.askdirectory(title='Selecciona carpeta para guardar el PDF')
        if not carpeta:
            return
        nombre_pdf = f"stickers_caja_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        ruta_pdf = f"{carpeta}/{nombre_pdf}"
    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    ancho, alto = A4
    x0, y0 = 5*mm, 5*mm
    stickers_por_fila = 3
    stickers_por_col = 7
    sticker_w = (ancho - 2*x0) / stickers_por_fila
    sticker_h = (alto - 2*y0) / stickers_por_col
    if sticker_w <= 0 or sticker_h <= 0:
        messagebox.showwarning('Sticker demasiado grande', 'El tamaño del sticker de caja es demasiado grande para la hoja. Reduce el tamaño del sticker.')
        return
    count = 0
    fila = col = 0
    for idx, row in data.iterrows():
        for talla in [str(n) for n in range(21,44)]:
            cantidad = row.get(talla, 0)
            if pd.isna(cantidad) or int(cantidad) == 0:
                continue
            for _ in range(int(cantidad)):
                x = x0 + (col * sticker_w)
                y = alto - y0 - ((fila + 1) * sticker_h)
                dibujar_sticker_caja(c, x, y, row, talla, sticker_w, sticker_h)
                count += 1
                col += 1
                if col >= stickers_por_fila:
                    col = 0
                    fila += 1
                    if fila >= stickers_por_col:
                        c.showPage()
                        fila = 0
                        col = 0
    if count == 0:
        if mostrar_mensaje:
            messagebox.showwarning('Sin stickers', 'No se generó ningún sticker de caja. Verifica los datos de tallas en el Excel y el tamaño del sticker.')
        return
    c.save()
    if mostrar_mensaje:
        messagebox.showinfo('PDF generado', f'Se generaron {count} stickers de caja en:\n{ruta_pdf}')

def dibujar_sticker_caja(c, x, y, row, talla, sticker_w, sticker_h):
    # --- Proporciones de filas ---
    header_h = sticker_h * 0.26
    code_h = sticker_h * 0.16
    middle_h = sticker_h * 0.50
    footer_h = sticker_h - (header_h + code_h + middle_h)
    c.setStrokeColorRGB(0,0,0)
    c.setLineWidth(1)

    # --- Encabezado negro y logo ---
    c.setFillColorRGB(0,0,0)
    c.rect(x, y+sticker_h-header_h, sticker_w, header_h, fill=1, stroke=1)
    marca = str(row.get('MARCA', '')).strip().upper()
    ruta_assets = os.path.join(os.path.dirname(__file__), 'assets')
    logo_base = 'DEFAULT'
    if 'WORLD' in marca:
        logo_base = 'WORLD'
    elif 'BUSCAPIES' in marca:
        logo_base = 'BUSCAPIES'
    logo_svg = os.path.join(ruta_assets, f'{logo_base}.svg')
    logo_img = None
    for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
        posible = os.path.join(ruta_assets, f'{logo_base}{ext}')
        if os.path.exists(posible):
            logo_img = posible
            break
    logo_max_h = header_h * 0.92
    logo_max_w = sticker_w * 0.96
    if os.path.exists(logo_svg):
        drawing = svg2rlg(logo_svg)
        scale = min(logo_max_w / drawing.width, logo_max_h / drawing.height)
        draw_w = drawing.width * scale
        draw_h = drawing.height * scale
        draw_x = x + (sticker_w - draw_w) / 2
        draw_y = y + sticker_h - header_h + (header_h - draw_h) / 2
        for el in drawing.contents:
            el.scale(scale, scale)
        renderPDF.draw(drawing, c, draw_x, draw_y)
    elif logo_img and os.path.exists(logo_img):
        im = Image.open(logo_img)
        iw, ih = im.size
        scale = min(logo_max_w/iw, logo_max_h/ih)
        draw_w = iw * scale
        draw_h = ih * scale
        draw_x = x + (sticker_w - draw_w) / 2
        draw_y = y + sticker_h - header_h + (header_h - draw_h) / 2
        c.drawImage(logo_img, draw_x, draw_y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')

    # --- Código modelo centrado ---
    c.setFillColorRGB(0,0,0)
    c.rect(x, y+sticker_h-header_h-code_h, sticker_w, code_h, fill=0, stroke=1)
    code_text = str(row.get('CÓDIGO', ''))
    font_name = 'Helvetica-Bold'
    code_font_size = int(code_h * 0.9)
    c.setFont(font_name, code_font_size)
    code_ascent = pdfmetrics.getAscent(font_name) / 1000 * code_font_size
    code_descent = abs(pdfmetrics.getDescent(font_name) / 1000 * code_font_size)
    code_height = code_ascent + code_descent
    code_y = y+sticker_h-header_h-code_h + (code_h - code_height)/2 + code_descent
    code_y -= 2
    c.drawCentredString(x+sticker_w/2, code_y, code_text)

    # --- Tres celdas horizontales ---
    y_middle = y+footer_h
    c.rect(x, y_middle, sticker_w, middle_h, fill=0, stroke=1)
    c.line(x+sticker_w/3, y_middle, x+sticker_w/3, y_middle+middle_h)
    c.line(x+2*sticker_w/3, y_middle, x+2*sticker_w/3, y_middle+middle_h)

    # --- Foto (izquierda, centrada) ---
    ruta_img = os.path.join(os.path.dirname(__file__), 'images')
    img_modelo = None
    for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
        posible = os.path.join(ruta_img, f"{row.get('CÓDIGO','')}{ext}")
        if os.path.exists(posible):
            img_modelo = posible
            break
    foto_cx = x
    foto_cy = y_middle
    foto_w = sticker_w/3
    foto_h = middle_h
    if img_modelo:
        max_w = foto_w * 0.85
        max_h = foto_h * 0.85
        try:
            im = Image.open(img_modelo)
            iw, ih = im.size
            scale = min(max_w/iw, max_h/ih)
            draw_w = iw*scale
            draw_h = ih*scale
        except Exception:
            draw_w = max_w
            draw_h = max_h
        draw_x = foto_cx + (foto_w - draw_w)/2
        draw_y = foto_cy + (foto_h - draw_h)/2
        c.drawImage(img_modelo, draw_x, draw_y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')

    # --- Colores (centro) ---
    paleta = cargar_paleta_colores()
    colores = str(row.get('COLOR','')).split('/')
    color_radius = min(3.2*mm, middle_h*0.13, sticker_w*0.04)
    color_gap = color_radius*2 + 1*mm
    total_height = len(colores)*color_gap
    centro_cx = x+sticker_w/3
    centro_cy = y_middle
    centro_w = sticker_w/3
    centro_h = middle_h
    y_start = centro_cy + (centro_h - total_height)/2 + color_gap/2
    color_font_size = int(middle_h*0.17)
    c.setFont('Helvetica-Bold', color_font_size)
    for i, color in enumerate(colores):
        color = color.strip().upper()
        y_color = y_start + (len(colores)-i-1)*color_gap
        circ_x = centro_cx + centro_w*0.13 + 1
        c.setFillColorRGB(0,0,0)
        c.circle(circ_x, y_color, color_radius, stroke=1, fill=0)
        hexcol = paleta.get(color, '#888888')
        try:
            r = int(hexcol[1:3],16)/255
            g = int(hexcol[3:5],16)/255
            b = int(hexcol[5:7],16)/255
            c.setFillColorRGB(r,g,b)
            c.circle(circ_x, y_color, color_radius-1, stroke=0, fill=1)
        except:
            pass
        c.setFillColorRGB(0,0,0)
        text = color.capitalize()
        text_x = circ_x + color_radius + 2*mm
        c.drawString(text_x, y_color-(color_font_size*0.35), text)

    # --- Talla grande alineada a la derecha y centrada verticalmente ---
    derecha_cx = x+2*sticker_w/3
    derecha_cy = y_middle
    derecha_w = sticker_w/3
    derecha_h = middle_h
    c.setLineWidth(1.2)
    c.rect(derecha_cx, derecha_cy, derecha_w, derecha_h, fill=0, stroke=1)
    c.setLineWidth(0.8)
    talla_text = str(talla)
    margen_derecho = derecha_w * 0.08
    margen_superior = derecha_h * 0.10
    max_w = derecha_w - margen_derecho - derecha_w*0.05
    max_h = derecha_h - 2*margen_superior
    font_name = 'Helvetica-Bold'
    talla_font_size = int(max_h)
    c.setFont(font_name, talla_font_size)
    # Ajustar el tamaño de fuente para que quepa en el ancho
    while c.stringWidth(talla_text, font_name, talla_font_size) > max_w and talla_font_size > 5:
        talla_font_size -= 1
        c.setFont(font_name, talla_font_size)
    # Ajustar el tamaño de fuente para que quepa en la altura
    while talla_font_size > max_h and talla_font_size > 5:
        talla_font_size -= 1
        c.setFont(font_name, talla_font_size)
        c.setFont(font_name, talla_font_size)
    talla_ascent = pdfmetrics.getAscent(font_name) / 1000 * talla_font_size
    talla_descent = abs(pdfmetrics.getDescent(font_name) / 1000 * talla_font_size)
    talla_height = talla_ascent + talla_descent
    centro_y = derecha_cy + derecha_h/2
    y_talla = centro_y - (talla_height/2) + talla_ascent
    y_talla -= 28 # Bajar 28 puntos (puedes ajustar este valor)
    x_talla = derecha_cx + derecha_w - margen_derecho
    c.setFillColorRGB(0,0,0)
    c.drawRightString(x_talla, y_talla, talla_text)

    # --- Footer ---
    c.rect(x, y, sticker_w, footer_h, fill=0, stroke=1)
    n_orden = str(row.get('N° ORDEN', ''))
    cliente = str(row.get('CLIENTE', ''))
    fecha = datetime.datetime.now().strftime('%d%m%y')
    cliente_code = (cliente[:2] + cliente[-2:]).upper() if len(cliente) >= 4 else cliente.upper()
    codigo_final = f"{n_orden.replace('-','')}-{fecha}-{cliente_code}"
    footer_font_size = int(footer_h*0.9)
    c.setFont('Helvetica', footer_font_size)
    footer_ascent = pdfmetrics.getAscent('Helvetica') / 1000 * footer_font_size
    footer_descent = abs(pdfmetrics.getDescent('Helvetica') / 1000 * footer_font_size)
    footer_height = footer_ascent + footer_descent
    footer_y = y + (footer_h - footer_height)/2 + footer_descent
    footer_y -= 1
    c.setFillColorRGB(0,0,0)
    c.drawCentredString(x+sticker_w/2, footer_y, codigo_final)

def generar_pdf_etiquetado(data, ruta_pdf=None, mostrar_mensaje=True):
    if ruta_pdf is None:
        carpeta = filedialog.askdirectory(title='Selecciona carpeta para guardar el PDF')
        if not carpeta:
            return
        nombre_pdf = f"etiquetado_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        ruta_pdf = f"{carpeta}/{nombre_pdf}"
    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    ancho, alto = A4
    margen = 5*mm
    etiqueta_w = 25*mm
    etiqueta_h = 31*mm
    etiquetas_por_fila = int((ancho - 2*margen) // etiqueta_w)
    etiquetas_por_col = int((alto - 2*margen) // etiqueta_h)
    etiquetas_por_pagina = etiquetas_por_fila * etiquetas_por_col
    x0, y0 = margen, margen
    count = 0
    # Construir una lista de (row, talla, cantidad) para todos los modelos y tallas presentes
    etiquetas = []
    for idx, row in data.iterrows():
        for talla in [str(n) for n in range(21,44)]:
            cantidad = row.get(talla, 0)
            if pd.isna(cantidad) or int(cantidad) == 0:
                continue
            etiquetas.extend([(row, talla)] * (int(cantidad) * 2))

    # Ordenar la lista de etiquetas primero por talla (como número), luego por modelo (opcional)
    etiquetas.sort(key=lambda x: int(x[1]))

    fila = col = 0
    for etiqueta in etiquetas:
        row, talla = etiqueta
        x = x0 + (col * etiqueta_w)
        y = alto - y0 - ((fila + 1) * etiqueta_h)
        dibujar_etiqueta_material(c, x, y, row, talla, etiqueta_w, etiqueta_h)
        count += 1
        col += 1
        if col >= etiquetas_por_fila:
            col = 0
            fila += 1
            if fila >= etiquetas_por_col:
                c.showPage()
                fila = 0
                col = 0
    if count == 0:
        if mostrar_mensaje:
            messagebox.showwarning('Sin etiquetas', 'No se generó ninguna etiqueta. Verifica los datos de tallas en el Excel y el tamaño de la etiqueta.')
        return
    c.save()
    if mostrar_mensaje:
        messagebox.showinfo('PDF generado', f'Se generaron {count} etiquetas en:\n{ruta_pdf}')

def dibujar_etiqueta_material(c, x, y, row, talla, w, h):
    """Dibuja una etiqueta individual con información del calzado"""
    # Margen interno
    m = 1.4*mm
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.8)
    
    # Marco principal
    c.rect(x, y, w, h, fill=0, stroke=1)
    
    # Esquinas de corte
    corte = 1*mm
    c.setLineWidth(0.5)
    # Superior izquierda
    c.line(x, y+h, x+corte, y+h)
    c.line(x, y+h, x, y+h-corte)
    # Superior derecha
    c.line(x+w-corte, y+h, x+w, y+h)
    c.line(x+w, y+h, x+w, y+h-corte)
    # Inferior izquierda
    c.line(x, y, x+corte, y)
    c.line(x, y, x, y+corte)
    # Inferior derecha
    c.line(x+w-corte, y, x+w, y)
    c.line(x+w, y, x+w, y+corte)
    
    c.setLineWidth(0.8)
    
    # Fuentes
    font_bold = 'Helvetica-Bold'
    font = 'Helvetica'
    
# --- TALLA con caja cuadrada y centrado perfecto ---
    talla_box_size = 5*mm  # Lado del cuadrado
    talla_font_size = 11

    # Posición del texto TALLA
    c.setFont(font_bold, 7)
    talla_y = y + h - m - 4*mm + 4
    c.drawString(x + m, talla_y, 'TALLA:')

    # Caja cuadrada alineada a la derecha con espaciado igual
    box_x = x + w - talla_box_size - m
    box_y = y + h - talla_box_size - m - 1*mm + 4
    c.rect(box_x, box_y, talla_box_size, talla_box_size, fill=0, stroke=1)

    # Número de talla perfectamente centrado en la caja
    c.setFont(font_bold, talla_font_size)
    # Centrado vertical preciso usando métricas de fuente
    ascent = pdfmetrics.getAscent(font_bold) / 1000 * talla_font_size
    descent = abs(pdfmetrics.getDescent(font_bold) / 1000 * talla_font_size)
    text_height = ascent + descent
    center_y = box_y + talla_box_size / 2
    y_num = center_y - (text_height / 2) + descent
    c.drawCentredString(box_x + talla_box_size / 2, y_num, str(talla))

    # --- Iconos y materiales alineados como en la imagen de referencia ---
    iconos = [
        ('CAPELLADA', 'icon-capellada.svg', str(row.get('CAPELLADA','')).upper()),
        ('FORRO', 'icon-forro.svg', 'TEXTIL'),
        ('PLANTILLA', 'icon-plantilla.svg', 'TEXTIL'),
        ('SUELA', 'icon-suela.svg', 'SINTETICO'),
    ]
    # Configuración de posiciones
    nombre_font_size = 4.1
    material_font_size = 4.1
    icon_size = 2.4*mm  # Ajusta este valor según el tamaño deseado
    icon_h = icon_size
    icon_w = icon_size
    line_spacing = 4.2*mm
    # Márgenes laterales
    nombre_x = x + m
    icon_x = x + w/2 - icon_w/2 - 0.5
    material_x = x + w - m
    # Posición inicial debajo de TALLA
    start_y = box_y - 2.2*mm - 5
    for i, (nombre, icon_file, material) in enumerate(iconos):
        y_pos = start_y - i * line_spacing
        # Nombre alineado a la izquierda
        c.setFont(font_bold, nombre_font_size)
        c.drawString(nombre_x, y_pos, nombre)
        # Icono SVG perfectamente alineado en la misma línea
        ruta_icon = os.path.join(os.path.dirname(__file__), 'assets', icon_file)
        icon_centro_y = y_pos + nombre_font_size*0.35  # centra el icono respecto a la línea de texto
        if os.path.exists(ruta_icon):
            try:
                drawing = svg2rlg(ruta_icon)
                if drawing and drawing.height > 0:
                    scale = icon_h/drawing.height
                    for el in drawing.contents:
                        if hasattr(el, 'scale'):
                            el.scale(scale, scale)
                    # Centrar icono verticalmente respecto a la línea base
                    icon_y = icon_centro_y - (drawing.height*scale)/2 - 20
                    renderPDF.draw(drawing, c, icon_x, icon_y, showBoundary=False)
            except:
                c.rect(icon_x, icon_centro_y - icon_h/2, icon_w, icon_h, fill=0, stroke=1)
        else:
            c.rect(icon_x, icon_centro_y - icon_h/2, icon_w, icon_h, fill=0, stroke=1)
        # Material alineado a la derecha
        c.setFont(font_bold if i in (0,3) else font, material_font_size)
        mat_text = material
        mat_w = c.stringWidth(mat_text, font_bold if i in (0,3) else font, material_font_size)
        c.drawRightString(material_x, y_pos, mat_text)
    
    # --- Pie de etiqueta con fuente más pequeña ---
    pie_font_size_bold = 4.1
    pie_font_size = 3.8
    c.setFont(font_bold, pie_font_size_bold)
    c.drawCentredString(x+w/2, y + 5.1*mm, 'HECHO EN ECUADOR')
    c.setFont(font, pie_font_size)
    c.drawCentredString(x+w/2, y + 3.2*mm, 'Elaborado por:  Alex  Poaquiza')
    c.setFont(font_bold, pie_font_size_bold)
    c.drawCentredString(x+w/2, y + 1.3*mm, 'RUC: 1802830636001')
