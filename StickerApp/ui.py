import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from excel_utils import cargar_excel
from pdf_templates import generar_pdf_caja, generar_pdf_etiquetado
from image_utils import asociar_imagen

class StickerApp:
    def vista_previa_pdf(self):
        import tempfile, os, sys
        from pdf_templates import generar_pdf_caja, generar_pdf_etiquetado
        from tkinter import PhotoImage
        from PIL import Image, ImageTk
        try:
            from pdf2image import convert_from_path
        except ImportError:
            messagebox.showerror('Falta dependencia', 'Debes instalar pdf2image y poppler para la vista previa.\nEjecuta: pip install pdf2image')
            return

        if self.data is None:
            messagebox.showwarning('Advertencia', 'Primero debes cargar un archivo Excel.')
            return
        tipo = self.tipo_sticker.get()
        # 1. Generar PDF temporal
        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp_pdf.close()
        try:
            if tipo == 'etiquetado':
                generar_pdf_etiquetado(self.data, ruta_pdf=tmp_pdf.name, mostrar_mensaje=False)
            else:
                generar_pdf_caja(self.data, ruta_pdf=tmp_pdf.name, mostrar_mensaje=False)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo generar el PDF temporal.\n{e}')
            os.unlink(tmp_pdf.name)
            return

        # --- VENTANA DE VISTA PREVIA ---
        preview = tk.Toplevel(self.root)
        preview.title('Vista previa del PDF')
        preview.geometry('700x600')
        preview.resizable(False, False)
        # Modalidad y centrado igual que asociar modelos
        def center_modal(child, parent):
            child.update_idletasks()
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_w = parent.winfo_width()
            parent_h = parent.winfo_height()
            win_w = child.winfo_width()
            win_h = child.winfo_height()
            x = parent_x + (parent_w // 2) - (win_w // 2)
            y = parent_y + (parent_h // 2) - (win_h // 2)
            child.geometry(f'+{x}+{y}')
        preview.transient(self.root)
        preview.grab_set()
        center_modal(preview, self.root)

        def show_modal_message(title, msg):
            modal = tk.Toplevel(preview)
            modal.title(title)
            modal.geometry('340x120')
            modal.resizable(False, False)
            modal.transient(preview)
            modal.grab_set()
            center_modal(modal, preview)
            lbl = tk.Label(modal, text=msg, font=('Arial', 11), wraplength=320)
            lbl.pack(pady=18, padx=10)
            btn = tk.Button(modal, text='Cerrar', command=modal.destroy, width=12)
            btn.pack(pady=8)
            modal.wait_window()

        # --- CARGA DE ICONOS (usa PNGs en assets/icons/) ---
        icon_path = lambda name: os.path.join(os.path.dirname(__file__), 'assets', 'icons', name)
        def load_icon(name):
            try:
                return PhotoImage(file=icon_path(name))
            except:
                return None
        # Guardar referencias a los iconos en el objeto preview para evitar garbage collection
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
            # Redimensionar según zoom
            w, h = img.size
            factor = zoom_state['zoom']
            new_w, new_h = max(1, int(w * factor)), max(1, int(h * factor))
            if new_w < 1 or new_h < 1:
                return
            img_resized = img.resize((new_w, new_h), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(img_resized)
            canvas.delete('all')
            # Calcular offset para centrar la imagen
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
            # Solo redimensionar la imagen ya cargada en memoria
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
        btn_next = tk.Button(footer, image=icon_next, text=' Siguiente', compound='left', command=siguiente, width=90)
        btn_next.image = icon_next
        btn_next.pack(side='left', padx=5)

        # Instrucción
        lbl_info = tk.Label(preview, text='Vista previa interna. Usa los botones para navegar y hacer zoom. "Abrir PDF" lo abre en el visor externo.')
        lbl_info.pack(pady=5)

        # Redibujar imagen al cambiar tamaño ventana
        def on_resize(event):
            # No redimensionar la imagen, solo ajustar el scroll
            pass
        canvas.bind('<Configure>', on_resize)

        mostrar_pagina()

    def __init__(self, root):
        self.root = root
        self.root.title('StickerApp - Generador de Stickers para Zapatos')
        self.root.geometry('1000x600')
        self.data = None

        self.btn_cargar = tk.Button(root, text='Cargar archivo Excel', command=self.cargar_excel)
        self.btn_cargar.pack(pady=10)

        # --- Definir columnas por defecto usando el header del CSV proporcionado ---
        default_columns = [
            'N° ORDEN', 'CLIENTE', 'CÓDIGO', 'COLOR', 'MARCA', 'CAPELLADA', 'FORRO', 'SUELA',
            '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', 'TOTAL'
        ]
        self.tree = ttk.Treeview(root, columns=default_columns, show='headings')
        # Asignar ancho menor y estilo a las columnas numéricas
        small_width = 40
        normal_width = 80
        numeric_cols = {'33','34','35','36','37','38','39','40','41','42'}
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background='#e0e0e0', foreground='#222')

        for col in default_columns:
            if col in numeric_cols:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=small_width, anchor='center')
            else:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=normal_width, anchor='center')
        self.tree.pack(expand=True, fill='both')

        self.btn_asociar_img = tk.Button(root, text='Asociar imágenes a modelos', command=self.abrir_ventana_asociar_imagen)
        self.btn_asociar_img.pack(pady=5)

        self.tipo_sticker = tk.StringVar(value='etiquetado')
        frame_tipo = tk.Frame(root)
        frame_tipo.pack(pady=5)
        tk.Label(frame_tipo, text='Tipo de sticker:').pack(side='left')
        tk.Radiobutton(frame_tipo, text='Etiquetado (interior)', variable=self.tipo_sticker, value='etiquetado').pack(side='left')
        tk.Radiobutton(frame_tipo, text='Caja', variable=self.tipo_sticker, value='caja').pack(side='left')

        self.btn_generar_pdf = tk.Button(root, text='Generar stickers en PDF', command=self.generar_pdf)
        self.btn_generar_pdf.pack(pady=10)

        self.btn_previsualizar = tk.Button(root, text='Vista previa e imprimir', command=self.vista_previa_pdf)
        self.btn_previsualizar.pack(pady=5)

    def cargar_excel(self):
        file_path = filedialog.askopenfilename(
            title='Selecciona un archivo Excel',
            filetypes=[('Archivos Excel', '*.xlsx *.xls')]
        )
        if not file_path:
            return
        try:
            df = cargar_excel(file_path)
            self.data = df
            self.mostrar_datos(df)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo leer el archivo Excel.\n{e}')

    def generar_pdf(self):
        if self.data is None:
            messagebox.showwarning('Advertencia', 'Primero debes cargar un archivo Excel.')
            return
        tipo = self.tipo_sticker.get()
        if tipo == 'etiquetado':
            generar_pdf_etiquetado(self.data)
        else:
            generar_pdf_caja(self.data)

    def mostrar_datos(self, df):
        # Limpiar filas
        self.tree.delete(*self.tree.get_children())
        # Actualizar columnas y mantener estilos
        numeric_cols = {'33','34','35','36','37','38','39','40','41','42'}
        small_width = 40
        normal_width = 80
        self.tree['columns'] = list(df.columns)
        self.tree['show'] = 'headings'
        for col in df.columns:
            if col in numeric_cols:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=small_width, anchor='center')
            else:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=normal_width, anchor='center')
        for _, row in df.iterrows():
            self.tree.insert('', 'end', values=list(row))

    def abrir_ventana_asociar_imagen(self):
        if self.data is None:
            messagebox.showwarning('Advertencia', 'Primero debes cargar un archivo Excel.')
            return
        asociar_imagen(self.data, self.root)
