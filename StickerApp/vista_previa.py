import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os, sys, tempfile

def centrar_ventana(win, parent=None):
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    if parent and parent.winfo_ismapped():
        x = parent.winfo_rootx() + (parent.winfo_width()//2) - (w//2)
        y = parent.winfo_rooty() + (parent.winfo_height()//2) - (h//2)
    else:
        x = win.winfo_screenwidth()//2 - w//2
        y = win.winfo_screenheight()//2 - h//2
    win.geometry(f'+{x}+{y}')

def mostrar_vista_previa_pdf(parent, data, tipo_sticker, generar_pdf_caja, generar_pdf_etiquetado):
    # ...código previo...
    try:
        from pdf2image import convert_from_path
    except ImportError:
        messagebox.showerror('Falta dependencia', 'Debes instalar pdf2image y poppler para la vista previa.\nEjecuta: pip install pdf2image')
        return

    if data is None:
        messagebox.showwarning('Advertencia', 'Primero debes cargar un archivo Excel.')
        return
    tipo = tipo_sticker.get() if hasattr(tipo_sticker, 'get') else tipo_sticker
    # 1. Generar PDF temporal
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp_pdf.close()
    colores_validados = {'ok': True}

    def show_modal_message(title, msg, allow_save=False, on_save=None):
        modal = tk.Toplevel(parent)
        modal.title(title)
        modal.geometry('340x160')
        modal.resizable(False, False)
        modal.transient(parent)
        modal.grab_set()
        centrar_ventana(modal, parent)
        lbl = tk.Label(modal, text=msg, font=('Arial', 11), wraplength=320)
        lbl.pack(pady=(18,10), padx=10)
        btn_frame = tk.Frame(modal)
        btn_frame.pack(fill='x', padx=10, pady=(0,8))
        if allow_save:
            btn_save = tk.Button(btn_frame, text='Guardar', command=lambda: (on_save() if on_save else None, modal.destroy()), bg='#4caf50', fg='white', font=('Arial', 11, 'bold'))
            btn_save.pack(side='left', fill='x', expand=True, padx=(0,6))
        btn = tk.Button(btn_frame, text='Cerrar', command=modal.destroy, width=12)
        btn.pack(side='left', fill='x', expand=True)
        modal.wait_window()

    def validar_colores_faltantes():
        # Detectar colores faltantes en la paleta
        from pdf_templates import cargar_paleta_colores
        paleta = cargar_paleta_colores()
        colores_en_excel = set()
        for row in data.itertuples():
            for c in str(getattr(row, 'COLOR', '')).split('/'):
                c = c.strip().upper()
                if c:
                    colores_en_excel.add(c)
        faltantes = [c for c in colores_en_excel if c not in paleta or not paleta[c]]
        return faltantes
    faltantes = validar_colores_faltantes()
    if faltantes:
        # Mostrar ventana de edición de colores faltantes
        from definir_colores_window import DefinirColoresWindow
        from pdf_templates import cargar_paleta_colores, guardar_paleta_colores
        paleta = cargar_paleta_colores()
        root = parent if isinstance(parent, tk.Tk) else parent.winfo_toplevel()
        def guardar_callback(nuevos_colores):
            paleta.update(nuevos_colores)
            guardar_paleta_colores(paleta)
        win = DefinirColoresWindow(root, faltantes, guardar_callback)
        win.wait_window()
        # Revalidar después de editar
        if validar_colores_faltantes():
            messagebox.showwarning('Colores incompletos', 'No se puede establecer la vista previa hasta especificar los colores faltantes.')
            os.unlink(tmp_pdf.name)
            return
    try:
        if tipo == 'etiquetado':
            generar_pdf_etiquetado(data, ruta_pdf=tmp_pdf.name, mostrar_mensaje=False)
        else:
            generar_pdf_caja(data, ruta_pdf=tmp_pdf.name, mostrar_mensaje=False)
    except Exception as e:
        messagebox.showerror('Error', f'No se pudo generar el PDF temporal.\n{e}')
        os.unlink(tmp_pdf.name)
        return

    # --- VENTANA DE VISTA PREVIA ---
    preview = tk.Toplevel(parent)
    preview.title('Vista previa del PDF')
    preview.geometry('700x600')
    preview.resizable(False, False)
    centrar_ventana(preview, parent)
    preview.transient(parent)
    preview.grab_set()

    def show_modal_message(title, msg, allow_save=False, on_save=None):
        modal = tk.Toplevel(preview)
        modal.title(title)
        modal.geometry('340x160')
        modal.resizable(False, False)
        modal.transient(preview)
        modal.grab_set()
        centrar_ventana(modal, preview)
        lbl = tk.Label(modal, text=msg, font=('Arial', 11), wraplength=320)
        lbl.pack(pady=(18,10), padx=10)
        btn_frame = tk.Frame(modal)
        btn_frame.pack(fill='x', padx=10, pady=(0,8))
        if allow_save:
            btn_save = tk.Button(btn_frame, text='Guardar', command=lambda: (on_save() if on_save else None, modal.destroy()), bg='#4caf50', fg='white', font=('Arial', 11, 'bold'))
            btn_save.pack(side='left', fill='x', expand=True, padx=(0,6))
        btn = tk.Button(btn_frame, text='Cerrar', command=modal.destroy, width=12)
        btn.pack(side='left', fill='x', expand=True)
        modal.wait_window()

    # --- CARGA DE ICONOS (usa PNGs en assets/icons/) ---
    icon_path = lambda name: os.path.join(os.path.dirname(__file__), 'assets', 'icons', name)
    def load_icon(name):
        try:
            return tk.PhotoImage(file=icon_path(name))
        except:
            return None
    preview._icon_refs = {}
    icon_open = load_icon('open.png')
    icon_download = load_icon('download.png')
    icon_zoom_in = load_icon('zoom_in.png')
    icon_zoom_out = load_icon('zoom_out.png')
    icon_prev = load_icon('prev.png')
    icon_next = load_icon('next.png')
    preview._icon_refs['open'] = icon_open
    preview._icon_refs['download'] = icon_download
    preview._icon_refs['zoom_in'] = icon_zoom_in
    preview._icon_refs['zoom_out'] = icon_zoom_out
    preview._icon_refs['prev'] = icon_prev
    preview._icon_refs['next'] = icon_next

    # --- Convertir PDF a imágenes (una sola vez, DPI fijo) ---
    dpi_base = 120
    zoom_state = {'zoom': 0.75}  # Zoom inicial al 75%
    try:
        images = convert_from_path(tmp_pdf.name, dpi=dpi_base, fmt='png')
    except Exception as e:
        show_modal_message('Error', f'No se pudo convertir el PDF a imágenes.\nAsegúrate de tener poppler instalado.\n{e}')
        preview.destroy()
        os.unlink(tmp_pdf.name)
        return
    total_paginas = len(images)
    pagina = {'idx': 0}

    # --- HEADER: botones principales ---
    header = tk.Frame(preview)
    header.pack(pady=10)
    def abrir_pdf():
        try:
            if sys.platform.startswith('win'):
                os.startfile(tmp_pdf.name)
            elif sys.platform == 'darwin':
                os.system(f'open "{tmp_pdf.name}"')
            else:
                os.system(f'xdg-open "{tmp_pdf.name}"')
        except Exception as e:
            show_modal_message('Error', f'No se pudo abrir el PDF.\n{e}')
    def descargar():
        ruta = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF','*.pdf')], title='Guardar PDF')
        if ruta:
            try:
                with open(tmp_pdf.name, 'rb') as fsrc, open(ruta, 'wb') as fdst:
                    fdst.write(fsrc.read())
                show_modal_message('Guardado', f'PDF guardado en:\n{ruta}')
            except Exception as e:
                show_modal_message('Error', f'No se pudo guardar el PDF.\n{e}')
    def zoom_mas():
        if zoom_state['zoom'] < 2.5:
            zoom_state['zoom'] += 0.15
            recargar_imagen()
    def zoom_menos():
        if zoom_state['zoom'] > 0.3:
            zoom_state['zoom'] -= 0.15
            recargar_imagen()
    tk.Button(header, image=icon_open, text=' Abrir PDF', compound='left', command=abrir_pdf, width=90).pack(side='left', padx=5)
    tk.Button(header, image=icon_download, text=' Descargar', compound='left', command=descargar, width=100).pack(side='left', padx=5)
    tk.Button(header, image=icon_zoom_in, text=' Zoom +', compound='left', command=zoom_mas, width=90).pack(side='left', padx=5)
    tk.Button(header, image=icon_zoom_out, text=' Zoom -', compound='left', command=zoom_menos, width=90).pack(side='left', padx=5)

    # --- CANVAS con scrollbars para mostrar la imagen ---
    canvas_frame = tk.Frame(preview)
    canvas_frame.pack(expand=True, fill='both', padx=10, pady=10)
    canvas = tk.Canvas(canvas_frame, bg='#222', highlightthickness=0)
    # Permitir scroll vertical con la rueda del mouse en el canvas
    def _on_mousewheel(event):
        # Windows y Mac
        if hasattr(event, 'delta'):
            if event.delta < 0:
                canvas.yview_scroll(1, 'units')
            elif event.delta > 0:
                canvas.yview_scroll(-1, 'units')
        # Linux (event.num)
        elif hasattr(event, 'num'):
            if event.num == 5:
                canvas.yview_scroll(1, 'units')
            elif event.num == 4:
                canvas.yview_scroll(-1, 'units')
    canvas.bind('<MouseWheel>', _on_mousewheel)
    canvas.bind('<Button-4>', _on_mousewheel)    # Linux scroll up
    canvas.bind('<Button-5>', _on_mousewheel)    # Linux scroll down

    v_scroll = tk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
    h_scroll = tk.Scrollbar(canvas_frame, orient='horizontal', command=canvas.xview)
    canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    canvas.grid(row=0, column=0, sticky='nsew')
    v_scroll.grid(row=0, column=1, sticky='ns')
    h_scroll.grid(row=1, column=0, sticky='ew')
    canvas_frame.rowconfigure(0, weight=1)
    canvas_frame.columnconfigure(0, weight=1)
    img_on_canvas = {'imgtk': None, 'img_id': None}

    def mostrar_pagina():
        img = images[pagina['idx']]
        w, h = img.size
        factor = zoom_state['zoom']
        new_w, new_h = max(1, int(w * factor)), max(1, int(h * factor))
        if new_w < 1 or new_h < 1:
            return
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img_resized)
        canvas.delete('all')
        c_w = canvas.winfo_width()
        c_h = canvas.winfo_height()
        x0 = max((c_w - new_w) // 2, 0)
        y0 = max((c_h - new_h) // 2, 0)
        img_id = canvas.create_image(x0, y0, image=imgtk, anchor='nw')
        canvas.config(scrollregion=(0, 0, max(new_w, c_w), max(new_h, c_h)))
        img_on_canvas['imgtk'] = imgtk
        img_on_canvas['img_id'] = img_id
        lbl_pagina.config(text=f'Página {pagina["idx"]+1} de {total_paginas}')
        btn_prev.config(state='normal' if pagina['idx'] > 0 else 'disabled')
        btn_next.config(state='normal' if pagina['idx'] < total_paginas-1 else 'disabled')

    def recargar_imagen():
        mostrar_pagina()

    # --- FOOTER: navegación de páginas ---
    footer = tk.Frame(preview)
    footer.pack(pady=10)
    def anterior():
        if pagina['idx'] > 0:
            pagina['idx'] -= 1
            mostrar_pagina()
    def siguiente():
        if pagina['idx'] < total_paginas-1:
            pagina['idx'] += 1
            mostrar_pagina()
    btn_prev = tk.Button(footer, image=icon_prev, text=' Anterior', compound='left', command=anterior, width=90)
    btn_prev.image = icon_prev
    btn_prev.pack(side='left', padx=5)
    lbl_pagina = tk.Label(footer, text=f'Página 1 de {total_paginas}')
    lbl_pagina.pack(side='left', padx=10)
    btn_next = tk.Button(footer, image=icon_next, text='Siguiente ', compound='right', command=siguiente, width=90)
    btn_next.image = icon_next
    btn_next.pack(side='left', padx=5)

    lbl_info = tk.Label(preview, text='Vista previa interna. Usa los botones para navegar y hacer zoom. "Abrir PDF" lo abre en el visor externo.')
    lbl_info.pack(pady=5)

    def on_resize(event):
        pass
    canvas.bind('<Configure>', on_resize)

    mostrar_pagina()
