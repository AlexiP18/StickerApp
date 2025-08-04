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
        self.preview_label = tk.Label(content_frame, bg='white')
        self.preview_label.pack(side='left', fill='both', expand=True)

        btns = tk.Frame(self, bg='white')
        btns.pack(pady=(5,0))
        # Cargar iconos para los botones
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
        # Centrar botones horizontal y verticalmente
        btns.grid_rowconfigure(0, weight=0)
        btns.grid_columnconfigure((0,1,2), weight=1)
        tk.Button(btns, text='Agregar LOGO', image=icon_agregar, compound='left', command=self._add_logo, padx=10).grid(row=0, column=0, padx=10, pady=2, sticky='ew')
        tk.Button(btns, text='Eliminar LOGO', image=icon_eliminar, compound='left', command=self._delete_logo, padx=10).grid(row=0, column=1, padx=10, pady=2, sticky='ew')
        tk.Button(btns, text='Reemplazar LOGO', image=icon_reemplazar, compound='left', command=self._replace_logo, padx=10).grid(row=0, column=2, padx=10, pady=2, sticky='ew')
        # Botón de cerrar eliminado

        self._all_logos = []  # Para mantener la lista completa

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
        # No agregar mensaje especial para SVG
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
