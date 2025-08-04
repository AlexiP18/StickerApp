import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class LogosManagerWindow(tk.Toplevel):
    def __init__(self, parent, logos_dir, on_update=None):
        super().__init__(parent)
        self.title('Gestor de Logos Disponibles')
        self.geometry('600x400')
        self.logos_dir = logos_dir
        self.on_update = on_update
        self.selected_logo = None
        self.logo_images = {}
        self.configure(bg='white')
        self._build_ui()
        self._load_logos()
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        # Centrar ventana
        def centrar_ventana(ventana):
            ventana.update_idletasks()
            w = ventana.winfo_width()
            h = ventana.winfo_height()
            x = (ventana.winfo_screenwidth() // 2) - (w // 2)
            y = (ventana.winfo_screenheight() // 2) - (h // 2)
            ventana.geometry(f'+{x}+{y}')
        centrar_ventana(self)

    def _build_ui(self):
        frame = tk.Frame(self, bg='white')
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Buscador con icono
        search_frame = tk.Frame(frame, bg='white')
        search_frame.pack(fill='x', padx=0, pady=(0,5))
        import os
        from PIL import Image, ImageTk
        icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
        icon_search = None
        icon_path = os.path.join(icon_dir, 'search.png')
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            img = img.resize((18, 18), Image.LANCZOS)
            icon_search = ImageTk.PhotoImage(img)
        if icon_search:
            icon_label = tk.Label(search_frame, image=icon_search, bg='white')
            icon_label.image = icon_search  # Referencia para evitar garbage collection
            icon_label.pack(side='left', padx=(0,3))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=(0,0))
        self.search_var.trace_add('write', lambda *args: self._filter_logos())

        # Listado y preview con scrollbar
        content_frame = tk.Frame(frame, bg='white')
        content_frame.pack(fill='both', expand=True)
        listbox_frame = tk.Frame(content_frame, bg='white')
        listbox_frame.pack(side='left', fill='y', padx=(0,10))
        self.listbox = tk.Listbox(listbox_frame, width=30)
        self.listbox.pack(side='left', fill='y', expand=True)
        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.bind('<<ListboxSelect>>', self._on_select_logo)
        preview_panel = tk.Frame(content_frame, bg='white')
        preview_panel.pack(side='left', fill='both', expand=True)
        self.preview_label = tk.Label(preview_panel, bg='white')
        self.preview_label.pack(fill='both', expand=True)
        # Selector de color de fondo para el header del sticker de caja (botón que abre un selector avanzado)
        # Centrado vertical y horizontal del apartado de color
        color_frame = tk.Frame(preview_panel, bg='white')
        color_frame.pack(fill='both', expand=True, pady=(8,0))
        color_inner = tk.Frame(color_frame, bg='white')
        color_inner.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(color_inner, text='Color HEADER:', bg='white').pack(side='left', padx=(0,4))
        self.color_var = tk.StringVar()
        self.color_preview = tk.Label(color_inner, text='', width=10, bg='white', relief='groove')
        self.color_preview.pack(side='left', padx=(0,4))
        # Botón solo con icono pincel.png
        icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
        icon_pincel = None
        icon_pincel_path = os.path.join(icon_dir, 'pincel.png')
        if os.path.exists(icon_pincel_path):
            try:
                img = Image.open(icon_pincel_path)
                img = img.resize((20, 20), Image.LANCZOS)
                icon_pincel = ImageTk.PhotoImage(img)
            except Exception:
                icon_pincel = None
        self.btn_color_selector = tk.Button(color_inner, image=icon_pincel, command=self._open_color_selector, padx=2, pady=2, relief='flat', bg='white', borderwidth=0, width=26, height=26)
        self.btn_color_selector.image = icon_pincel  # Referencia para evitar garbage collection
        self.btn_color_selector.pack(side='left')
        self._logo_color_map = self._load_logo_colors()

        # Listbox de colores debajo de la previsualización (se crea dinámicamente)
        self._color_selector_win = None

        # --- Botones de footer: Agregar, Eliminar, Reemplazar LOGO ---
        btns = tk.Frame(self, bg='white')
        btns.pack(pady=(5,0))
        icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
        icon_agregar = None
        icon_eliminar = None
        icon_reemplazar = None
        try:
            icon_agregar_path = os.path.join(icon_dir, 'agregar.png')
            if os.path.exists(icon_agregar_path):
                img = Image.open(icon_agregar_path)
                img = img.resize((18, 18), Image.LANCZOS)
                icon_agregar = ImageTk.PhotoImage(img)
            icon_eliminar_path = os.path.join(icon_dir, 'eliminar.png')
            if os.path.exists(icon_eliminar_path):
                img = Image.open(icon_eliminar_path)
                img = img.resize((18, 18), Image.LANCZOS)
                icon_eliminar = ImageTk.PhotoImage(img)
            icon_reemplazar_path = os.path.join(icon_dir, 'reemplazar.png')
            if os.path.exists(icon_reemplazar_path):
                img = Image.open(icon_reemplazar_path)
                img = img.resize((18, 18), Image.LANCZOS)
                icon_reemplazar = ImageTk.PhotoImage(img)
        except Exception:
            pass
        self._icon_refs_btns = (icon_agregar, icon_eliminar, icon_reemplazar)
        btns.grid_rowconfigure(0, weight=0)
        btns.grid_columnconfigure((0,1,2), weight=1)
        tk.Button(btns, text='Agregar LOGO', image=icon_agregar, compound='left', command=self._add_logo, padx=10).grid(row=0, column=0, padx=10, pady=2, sticky='ew')
        tk.Button(btns, text='Eliminar LOGO', image=icon_eliminar, compound='left', command=self._delete_logo, padx=10).grid(row=0, column=1, padx=10, pady=2, sticky='ew')
        tk.Button(btns, text='Reemplazar LOGO', image=icon_reemplazar, compound='left', command=self._replace_logo, padx=10).grid(row=0, column=2, padx=10, pady=2, sticky='ew')
    def _load_logo_colors(self):
        """Carga el mapeo de color de header para cada logo desde un archivo JSON."""
        import json
        path = os.path.join(self.logos_dir, '_logo_header_colors.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_logo_colors(self):
        import json
        path = os.path.join(self.logos_dir, '_logo_header_colors.json')
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._logo_color_map, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _save_logo_color(self, color):
        sel = self.listbox.curselection()
        if not sel or not hasattr(self, '_filtered_bases'):
            return
        idx = sel[0]
        base = self._filtered_bases[idx]
        if color:
            self._logo_color_map[base] = color
            self._save_logo_colors()

    def _load_logos(self):
        self.logo_images.clear()
        if not os.path.exists(self.logos_dir):
            os.makedirs(self.logos_dir)
        # Agrupar por nombre base (sin extensión)
        files = [fname for fname in os.listdir(self.logos_dir)
                 if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.svg'))]
        self._logo_map = {}
        for fname in files:
            base, ext = os.path.splitext(fname)
            if base not in self._logo_map:
                self._logo_map[base] = []
            self._logo_map[base].append(ext.lower())
        self._all_logos = list(self._logo_map.keys())
        self._filter_logos()

    def _filter_logos(self):
        filtro = self.search_var.get().lower() if hasattr(self, 'search_var') else ''
        self.listbox.delete(0, 'end')
        self._filtered_bases = []
        for base in self._all_logos:
            if filtro in base.lower():
                self.listbox.insert('end', base)
                self._filtered_bases.append(base)

    def _on_select_logo(self, event=None):
        sel = self.listbox.curselection()
        if not sel or not hasattr(self, '_filtered_bases'):
            self.preview_label.config(image='', text='')
            self.color_var.set('')
            self.color_preview.config(bg='white', text='')
            return
        idx = sel[0]
        base = self._filtered_bases[idx]
        exts = self._logo_map.get(base, [])
        # Preferencia de preview: png, jpg, jpeg, bmp, gif
        preview_ext = None
        for ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
            if ext in exts:
                preview_ext = ext
                break
        info_lines = []
        for ext in exts:
            info_lines.append(f'{base}{ext} ({ext[1:].upper()})')
        info = '\n'.join(info_lines)
        if preview_ext:
            fname = f'{base}{preview_ext}'
            path = os.path.join(self.logos_dir, fname)
            try:
                img = Image.open(path)
                img.thumbnail((200,200))
                tkimg = ImageTk.PhotoImage(img)
                self.logo_images[fname] = tkimg
                self.preview_label.config(image=tkimg, text=info, compound='bottom', font=(None, 10))
            except Exception as e:
                self.preview_label.config(image='', text=f'No se pudo cargar la imagen\n{fname}\n{e}\n{info}', compound='bottom', font=(None, 10))
        else:
            self.preview_label.config(image='', text=info, compound='bottom', font=(None, 10))

        # Actualizar color de preview según color guardado
        colores = self._get_colores_definidos()
        color_sel = self._logo_color_map.get(base, '')
        color_hex = self._get_color_hex(color_sel) if color_sel else None
        if color_sel and color_sel in colores and color_hex:
            self.color_var.set(color_sel)
            self.color_preview.config(bg=color_hex, text=color_sel)
        elif colores:
            self.color_var.set(colores[0])
            color_hex = self._get_color_hex(colores[0])
            self.color_preview.config(bg=color_hex if color_hex else 'white', text=colores[0])
        else:
            self.color_var.set('')
            self.color_preview.config(bg='white', text='')

    def _get_color_hex(self, color_name):
        # Devuelve el valor hexadecimal del color desde colores.json
        import json
        ruta = os.path.join(os.path.dirname(__file__), 'colores.json')
        if os.path.exists(ruta):
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    paleta = json.load(f)
                return paleta.get(color_name, None)
            except Exception:
                return None
        return None

    def _open_color_selector(self):
        if self._color_selector_win and tk.Toplevel.winfo_exists(self._color_selector_win):
            self._color_selector_win.lift()
            return
        sel = self.listbox.curselection()
        if not sel or not hasattr(self, '_filtered_bases'):
            return
        idx = sel[0]
        base = self._filtered_bases[idx]
        colores = self._get_colores_definidos()
        if not colores:
            messagebox.showwarning('Sin colores', 'No hay colores definidos en colores.json')
            return
        # Cargar mapa nombre->hex
        import json
        ruta = os.path.join(os.path.dirname(__file__), 'colores.json')
        paleta = {}
        if os.path.exists(ruta):
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    paleta = json.load(f)
            except Exception:
                paleta = {}

        win = tk.Toplevel(self)
        win.title('Seleccionar color de header')
        win.geometry('320x400')
        win.transient(self)
        win.grab_set()
        win.focus_set()
        # Centrar
        win.update_idletasks()
        w, h = win.winfo_width(), win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (w // 2)
        y = (win.winfo_screenheight() // 2) - (h // 2)
        win.geometry(f'+{x}+{y}')
        self._color_selector_win = win

        # Header: buscador con icono y entry expandible
        header = tk.Frame(win)
        header.pack(fill='x', padx=10, pady=(10,2))
        # Icono de búsqueda
        icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
        icon_search = None
        icon_path = os.path.join(icon_dir, 'search.png')
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            img = img.resize((18, 18), Image.LANCZOS)
            icon_search = ImageTk.PhotoImage(img)
        if icon_search:
            icon_label = tk.Label(header, image=icon_search, bg='white')
            icon_label.image = icon_search
            icon_label.pack(side='left', padx=(0,6))
        search_var = tk.StringVar()
        search_entry = tk.Entry(header, textvariable=search_var)
        search_entry.pack(side='left', fill='x', expand=True)

        # Body: scrollable frame con radiobuttons, nombre y cuadrado, scroll siempre visible y funcional
        body = tk.Frame(win)
        body.pack(fill='both', expand=True, padx=10, pady=(2,2))
        canvas = tk.Canvas(body, borderwidth=0, bg='white', highlightthickness=0)
        scroll = tk.Scrollbar(body, orient='vertical', command=canvas.yview)
        scroll.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        frame = tk.Frame(canvas, bg='white')
        frame_id = canvas.create_window((0,0), window=frame, anchor='nw')
        canvas.config(yscrollcommand=scroll.set)
        # Forzar ancho del frame igual al canvas
        def resize_frame(event):
            canvas.itemconfig(frame_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', resize_frame)

        # Permitir scroll con la rueda del mouse en el canvas, de forma robusta
        def _on_mousewheel(event):
            # Solo hacer scroll si el mouse está sobre el canvas
            if event.widget == canvas or str(event.widget).startswith(str(canvas)):
                if os.name == 'nt':
                    canvas.yview_scroll(-1 * int(event.delta / 120), 'units')
                else:
                    canvas.yview_scroll(-1 * int(event.delta), 'units')
        # Bind a la ventana toplevel para que siempre funcione el scroll sobre el canvas
        win.bind_all('<MouseWheel>', _on_mousewheel)
        win.bind_all('<Button-4>', lambda e: canvas.yview_scroll(-1, 'units'))  # Linux scroll up
        win.bind_all('<Button-5>', lambda e: canvas.yview_scroll(1, 'units'))   # Linux scroll down
        # Limpiar el binding al cerrar la ventana
        def cleanup_mousewheel():
            win.unbind_all('<MouseWheel>')
            win.unbind_all('<Button-4>')
            win.unbind_all('<Button-5>')
        win.protocol('WM_DELETE_WINDOW', lambda: (cleanup_mousewheel(), win.destroy()))

        # Variable para radiobuttons
        radio_var = tk.StringVar(value=self.color_var.get())

        # Función para poblar los colores filtrados
        def render_colores(filtrado):
            for w in frame.winfo_children():
                w.destroy()
            for i, color in enumerate(filtrado):
                color_hex = paleta.get(color, '#FFFFFF')
                row = tk.Frame(frame, bg='white')
                row.pack(fill='x', pady=2)
                rb = tk.Radiobutton(row, variable=radio_var, value=color, bg='white', highlightthickness=0)
                rb.pack(side='left', padx=(0,6))
                tk.Label(row, text=color, bg='white', width=14, anchor='w').pack(side='left')
                swatch = tk.Label(row, bg=color_hex, width=4, height=1, relief='groove')
                swatch.pack(side='left', padx=(8,0))
        # Inicial
        colores_filtrados = list(colores)
        render_colores(colores_filtrados)

        def on_search(*args):
            filtro = search_var.get().strip().lower()
            if not filtro:
                filtrados = list(colores)
            else:
                filtrados = [c for c in colores if filtro in c.lower()]
            render_colores(filtrados)
            # Ajustar scroll region
            frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox('all'))
        search_var.trace_add('write', on_search)

        # Ajustar scroll region al cambiar tamaño
        def on_configure(event):
            canvas.config(scrollregion=canvas.bbox('all'))
        frame.bind('<Configure>', on_configure)

        # Footer: preview y botón guardar (solo icono save.png), centrados
        footer = tk.Frame(win, bg='white')
        footer.pack(fill='x', pady=(8,8), padx=10)
        footer_inner = tk.Frame(footer, bg='white')
        footer_inner.pack(expand=True)
        swatch = tk.Label(footer_inner, text='', width=16, height=2, relief='groove', bg='white', font=(None, 10))
        swatch.grid(row=0, column=0, sticky='nsew')
        # Icono guardar
        icon_save = None
        icon_save_path = os.path.join(icon_dir, 'save.png')
        if os.path.exists(icon_save_path):
            img = Image.open(icon_save_path)
            img = img.resize((24, 24), Image.LANCZOS)
            icon_save = ImageTk.PhotoImage(img)
        def update_swatch(*args):
            color = radio_var.get()
            color_hex = paleta.get(color, '#FFFFFF')
            swatch.config(bg=color_hex, text=color)
        radio_var.trace_add('write', update_swatch)
        update_swatch()
        def guardar():
            color = radio_var.get()
            color_hex = paleta.get(color, '#FFFFFF')
            if not color:
                return
            self.color_var.set(color)
            self.color_preview.config(bg=color_hex, text=color)
            self._save_logo_color(color)
            win.destroy()
        btn = tk.Button(footer_inner, image=icon_save, command=guardar, relief='flat', bg='white', borderwidth=0, width=28, height=28)
        btn.image = icon_save
        btn.grid(row=0, column=1, padx=(12,0), sticky='nsew')
        footer_inner.grid_columnconfigure(0, weight=1)
        footer_inner.grid_columnconfigure(1, weight=1)
        footer_inner.grid_rowconfigure(0, weight=1)
        win.protocol('WM_DELETE_WINDOW', win.destroy)

    def _get_colores_definidos(self):
        # Lee los colores definidos en colores.json
        import json
        ruta = os.path.join(os.path.dirname(__file__), 'colores.json')
        if os.path.exists(ruta):
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    paleta = json.load(f)
                return list(paleta.keys())
            except Exception:
                return []
        return []

    def _update_color_menu(self, colores):
        menu = self.color_menu['menu']
        menu.delete(0, 'end')
        for color in colores:
            menu.add_command(label=color, command=lambda v=color: self.color_var.set(v))

    def _add_logo(self):
        file_path = filedialog.askopenfilename(
            title='Selecciona una imagen de logo',
            filetypes=[('Imágenes', '*.png *.jpg *.jpeg *.bmp *.gif *.svg')]
        )
        if not file_path:
            return
        fname = os.path.basename(file_path)
        dest = os.path.join(self.logos_dir, fname)
        base, _ = os.path.splitext(fname)
        if os.path.exists(dest):
            messagebox.showwarning('Ya existe', 'Ya existe un logo con ese nombre.')
            return
        try:
            with open(file_path, 'rb') as src, open(dest, 'wb') as dst:
                dst.write(src.read())
            # Guardar color por defecto 'NEGRO' para el nuevo logo
            self._logo_color_map[base] = 'NEGRO'
            self._save_logo_colors()
            self._load_logos()
            # Seleccionar y previsualizar el logo recién agregado
            if hasattr(self, '_filtered_bases') and base in self._filtered_bases:
                idx = self._filtered_bases.index(base)
                self.listbox.selection_clear(0, 'end')
                self.listbox.selection_set(idx)
                self.listbox.activate(idx)
                self._on_select_logo()
            if self.on_update:
                self.on_update()
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo agregar el logo.\n{e}')

    def _delete_logo(self):
        sel = self.listbox.curselection()
        if not sel or not hasattr(self, '_filtered_bases'):
            return
        idx = sel[0]
        base = self._filtered_bases[idx]
        exts = self._logo_map.get(base, [])
        files_to_delete = [os.path.join(self.logos_dir, f'{base}{ext}') for ext in exts]
        if messagebox.askyesno('Eliminar', f'¿Eliminar todos los archivos del logo "{base}"?'):
            errores = []
            for path in files_to_delete:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    errores.append(f'{os.path.basename(path)}: {e}')
            # Eliminar el color asociado a este logo si existe
            if base in self._logo_color_map:
                del self._logo_color_map[base]
                self._save_logo_colors()
            self._load_logos()
            self.preview_label.config(image='', text='')
            if self.on_update:
                self.on_update()
            if errores:
                messagebox.showerror('Error', 'No se pudieron eliminar algunos archivos:\n' + '\n'.join(errores))

    def _replace_logo(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        fname = self.listbox.get(sel[0])
        path = os.path.join(self.logos_dir, fname)
        file_path = filedialog.askopenfilename(
            title='Selecciona la nueva imagen',
            filetypes=[('Imágenes', '*.png *.jpg *.jpeg *.bmp *.gif *.svg')]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'rb') as src, open(path, 'wb') as dst:
                dst.write(src.read())
            self._load_logos()
            if self.on_update:
                self.on_update()
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo reemplazar el logo.\n{e}')
