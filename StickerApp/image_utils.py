import os
from tkinter import filedialog, messagebox
import shutil

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

def asociar_imagen(data, parent):
    ruta_img = os.path.join(os.path.dirname(__file__), 'images')
    codigos = []
    # Si hay DataFrame válido, usarlo; si no, detectar modelos por archivos en la carpeta de imágenes
    if data is not None and hasattr(data, '__getitem__') and 'CÓDIGO' in data:
        codigos = sorted(set(str(c).upper() for c in data['CÓDIGO']))
    else:
        # Buscar modelos por archivos en la carpeta de imágenes
        if os.path.exists(ruta_img):
            archivos = os.listdir(ruta_img)
            codigos_detectados = set()
            for fname in archivos:
                base, ext = os.path.splitext(fname)
                if ext.lower() in ('.png', '.jpg', '.jpeg', '.bmp'):
                    codigos_detectados.add(base.upper())
            codigos = sorted(codigos_detectados)
    import tkinter as tk
    from PIL import Image, ImageTk

    # --- Detectar modelos sin imagen y mostrar mensaje si hay nuevos ---
    modelos_sin_imagen = []
    for cod in codigos:
        tiene_imagen = False
        for ext in ('.png', '.jpg', '.jpeg', '.bmp'):
            if os.path.exists(os.path.join(ruta_img, f'{cod}{ext}')):
                tiene_imagen = True
                break
        if not tiene_imagen:
            modelos_sin_imagen.append(cod)
    if modelos_sin_imagen:
        modelos_str = ', '.join(modelos_sin_imagen)
        messagebox.showinfo(
            "Nuevos modelos encontrados",
            f"Se han encontrado los siguientes nuevos modelos: {modelos_str}. Por favor, asígneles una imagen."
        )

    win = tk.Toplevel(parent)
    win.withdraw()
    win.title('Asociar imágenes a modelos')
    win.geometry('700x370')
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()
    # Icono de ventana
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'favicon.ico')
        if os.path.exists(icon_path):
            win.iconbitmap(icon_path)
    except Exception:
        pass

    # Layout principal: lista a la izquierda, panel derecho expandido a la derecha
    main_frame = tk.Frame(win)
    main_frame.pack(expand=True, fill='both', padx=10, pady=10)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)

    # --- Centrar y mostrar la ventana solo después de construir widgets ---
    win.update_idletasks()
    centrar_ventana(win, parent)
    win.deiconify()

    # Columna izquierda: buscador y listado juntos arriba, listado ocupa todo el alto
    left_col = tk.Frame(main_frame)
    left_col.grid(row=0, column=0, sticky='ns', rowspan=4)
    left_col.grid_rowconfigure(1, weight=1)
    left_col.grid_columnconfigure(0, weight=1)
    # Buscador
    search_frame = tk.Frame(left_col)
    search_frame.grid(row=0, column=0, sticky='ew', pady=(0,2))
    search_icon = tk.Label(search_frame, text='🔍', font=('Arial', 11))
    search_icon.pack(side='left', padx=(0,2))
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=18, font=('Arial', 11))
    search_entry.pack(side='left', fill='x', expand=True)
    # Listado
    listbox_frame = tk.Frame(left_col)
    listbox_frame.grid(row=1, column=0, sticky='nsew')
    listbox_frame.grid_rowconfigure(0, weight=1)
    listbox_frame.grid_columnconfigure(0, weight=1)
    listbox = tk.Listbox(listbox_frame, width=22, font=('Arial', 11), exportselection=False)
    scrollbar = tk.Scrollbar(listbox_frame, orient='vertical', command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)
    listbox.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')
    for cod in codigos:
        listbox.insert('end', cod)

    # Botón Agregar modelo debajo del listado
    # Cargar iconos (asegurar icon_dir está definido antes de cualquier uso)
    icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
    icon_agregar = None
    icon_agregar_path = os.path.join(icon_dir, 'agregar.png')
    if os.path.exists(icon_agregar_path):
        try:
            img = Image.open(icon_agregar_path)
            img = img.resize((18, 18), Image.LANCZOS)
            icon_agregar = ImageTk.PhotoImage(img)
        except Exception:
            icon_agregar = None

    def agregar_modelo():
        # Diálogo simple para ingresar el nombre
        def on_ok():
            nombre = entry.get().strip().upper()
            if not nombre:
                messagebox.showwarning('Nombre requerido', 'Debes ingresar un nombre para el modelo.')
                return
            if nombre in codigos:
                messagebox.showwarning('Ya existe', 'Ese modelo ya existe.')
                return
            codigos.append(nombre)
            codigos.sort()
            listbox.delete(0, 'end')
            for cod in codigos:
                listbox.insert('end', cod)
            resaltar_modelos()
            # Seleccionar el nuevo modelo
            idx = codigos.index(nombre)
            listbox.selection_clear(0, 'end')
            listbox.selection_set(idx)
            mostrar(idx)
            top.destroy()

        top = tk.Toplevel(win)
        top.withdraw()
        top.title('Agregar modelo')
        top.geometry('320x120')
        top.resizable(False, False)
        top.transient(win)
        top.grab_set()
        # Icono de ventana
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'favicon.ico')
            if os.path.exists(icon_path):
                top.iconbitmap(icon_path)
        except Exception:
            pass
        label = tk.Label(top, text='Nombre del nuevo modelo:', font=('Arial', 11))
        label.pack(pady=(18,4))
        entry = tk.Entry(top, font=('Arial', 12))
        entry.pack(pady=4, padx=16)
        entry.focus_set()
        btn_ok = tk.Button(top, text='Agregar', width=12, command=on_ok)
        btn_ok.pack(pady=8)
        top.bind('<Return>', lambda e: on_ok())
        top.update_idletasks()
        centrar_ventana(top, win)
        top.deiconify()

    btn_agregar = tk.Button(left_col, text='Agregar modelo', image=icon_agregar, compound='left', padx=8, font=('Arial', 11), command=agregar_modelo)
    btn_agregar.grid(row=2, column=0, pady=(8,0), sticky='ew')
    # Mantener referencia al icono
    btn_agregar._icon_ref = icon_agregar

    # --- Resaltar modelos sin imagen ---
    def resaltar_modelos():
        for idx, cod in enumerate(codigos):
            tiene_imagen = False
            for ext in ('.png', '.jpg', '.jpeg', '.bmp'):
                if os.path.exists(os.path.join(ruta_img, f'{cod}{ext}')):
                    tiene_imagen = True
                    break
            if not tiene_imagen:
                listbox.itemconfig(idx, {'bg': '#fff7b2'})  # Amarillo claro
            else:
                listbox.itemconfig(idx, {'bg': 'white'})

    # --- Panel derecho expandido y centrado ---
    panel_container = tk.Frame(main_frame)
    panel_container.grid(row=0, column=1, rowspan=4, sticky='nsew', padx=(24,0))
    panel_container.grid_rowconfigure(0, weight=1)
    panel_container.grid_columnconfigure(0, weight=1)
    # Panel interno centrado en el contenedor expandido
    panel = tk.Frame(panel_container)
    panel.place(relx=0.5, rely=0.5, anchor='center')
    # Header
    lbl_modelo = tk.Label(panel, text='', font=('Arial', 14, 'bold'))
    lbl_modelo.pack(pady=(0,8))
    # Body
    img_frame = tk.Frame(panel, width=320, height=200)
    img_frame.pack()
    canvas = tk.Canvas(img_frame, width=320, height=200, bg='#eee', highlightthickness=1, highlightbackground='#aaa')
    canvas.pack()
    lbl_img = tk.Label(panel, text='', fg='gray')
    lbl_img.pack(pady=(8,0))
    # Footer
    # Cargar iconos
    icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
    icon_reemplazar = None
    icon_eliminar = None
    try:
        icon_reemplazar_path = os.path.join(icon_dir, 'reemplazar.png')
        if os.path.exists(icon_reemplazar_path):
            img = Image.open(icon_reemplazar_path)
            img = img.resize((18, 18), Image.LANCZOS)
            icon_reemplazar = ImageTk.PhotoImage(img)
        icon_eliminar_path = os.path.join(icon_dir, 'eliminar.png')
        if os.path.exists(icon_eliminar_path):
            img = Image.open(icon_eliminar_path)
            img = img.resize((18, 18), Image.LANCZOS)
            icon_eliminar = ImageTk.PhotoImage(img)
    except Exception:
        pass
    # --- Botones en línea ---
    botones_frame = tk.Frame(panel)
    botones_frame.pack(pady=10)
    btn_asociar = tk.Button(botones_frame, text='Asociar/Cambiar', width=120, image=icon_reemplazar, compound='left', padx=16)
    btn_asociar.pack(side='left', padx=(0,20))

    # Botón eliminar modelo
    def eliminar_modelo():
        sel = listbox.curselection()
        if not sel:
            show_modal_message('Selecciona', 'Selecciona un modelo para eliminar.', 'warning')
            return
        idx = sel[0]
        codigo = codigos[idx]
        if messagebox.askyesno('Eliminar modelo', f'¿Eliminar el modelo "{codigo}" y todas sus imágenes asociadas?'):
            # Eliminar imágenes asociadas
            for ext in ('.png', '.jpg', '.jpeg', '.bmp'):
                path = os.path.join(ruta_img, f'{codigo}{ext}')
                if os.path.exists(path):
                    os.remove(path)
            # Eliminar del listado y actualizar
            codigos.pop(idx)
            listbox.delete(idx)
            lbl_modelo.config(text='')
            canvas.delete('all')
            lbl_img.config(text='')
            resaltar_modelos()

    btn_eliminar = tk.Button(botones_frame, text='Eliminar modelo', image=icon_eliminar, compound='left', padx=8, command=eliminar_modelo)
    btn_eliminar.pack(side='left')
    # Mantener referencias a los iconos
    panel._icon_refs = (icon_reemplazar, icon_eliminar)

    # --- Funciones de lógica ---
    def mostrar(idx):
        codigo = codigos[idx]
        lbl_modelo.config(text=f'{codigo}')
        # Buscar imagen asociada
        img_file = None
        for ext in ('.png', '.jpg', '.jpeg', '.bmp'):
            path = os.path.join(ruta_img, f'{codigo}{ext}')
            if os.path.exists(path):
                img_file = path
                break
        canvas.delete('all')
        if img_file:
            try:
                img = Image.open(img_file)
                img.thumbnail((300, 180), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(img)
                canvas.create_image(160, 100, image=imgtk, anchor='center')
                canvas.imgtk = imgtk
                lbl_img.config(text=os.path.basename(img_file))
            except Exception as e:
                lbl_img.config(text='No se pudo cargar la imagen')
        else:
            lbl_img.config(text='Sin imagen asociada')
            canvas.imgtk = None

    def show_modal_message(title, msg, kind='info'):
        modal = tk.Toplevel(win)
        modal.withdraw()
        modal.title(title)
        modal.geometry('340x120')
        modal.resizable(False, False)
        modal.transient(win)
        modal.grab_set()
        # Icono de ventana
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'favicon.ico')
            if os.path.exists(icon_path):
                modal.iconbitmap(icon_path)
        except Exception:
            pass
        lbl = tk.Label(modal, text=msg, font=('Arial', 11), wraplength=320)
        lbl.pack(pady=18, padx=10)
        btn = tk.Button(modal, text='Cerrar', command=modal.destroy, width=12)
        btn.pack(pady=8)
        modal.update_idletasks()
        centrar_ventana(modal, win)
        modal.deiconify()
        modal.wait_window()

    def asociar_o_cambiar():
        sel = listbox.curselection()
        if not sel:
            show_modal_message('Selecciona', 'Selecciona un modelo de la lista.', 'warning')
            return
        idx = sel[0]
        codigo = codigos[idx]
        img_path = filedialog.askopenfilename(title=f'Selecciona imagen para {codigo}', filetypes=[('Imágenes', '*.png *.jpg *.jpeg *.bmp')])
        if not img_path:
            return
        ext = os.path.splitext(img_path)[1]
        destino = os.path.join(ruta_img, f'{codigo}{ext}')
        # Eliminar otras imágenes previas de ese código
        for ext_old in ('.png', '.jpg', '.jpeg', '.bmp'):
            path_old = os.path.join(ruta_img, f'{codigo}{ext_old}')
            if os.path.exists(path_old):
                os.remove(path_old)
        shutil.copy(img_path, destino)
        show_modal_message('Imagen asociada', f'Imagen asociada a {codigo}.', 'info')
        mostrar(idx)
        resaltar_modelos()

    btn_asociar.config(command=asociar_o_cambiar)

    def on_select(event):
        sel = listbox.curselection()
        if sel:
            mostrar(sel[0])

    listbox.bind('<<ListboxSelect>>', on_select)

    # --- Buscador ---
    def filtrar_lista(*args):
        filtro = search_var.get().strip().lower()
        listbox.delete(0, 'end')
        indices = []
        for cod in codigos:
            if filtro in cod.lower():
                indices.append(cod)
                listbox.insert('end', cod)
        # Resaltar modelos sin imagen en el filtrado
        for idx, cod in enumerate(indices):
            tiene_imagen = False
            for ext in ('.png', '.jpg', '.jpeg', '.bmp'):
                if os.path.exists(os.path.join(ruta_img, f'{cod}{ext}')):
                    tiene_imagen = True
                    break
            if not tiene_imagen:
                listbox.itemconfig(idx, {'bg': '#fff7b2'})
            else:
                listbox.itemconfig(idx, {'bg': 'white'})
        # Seleccionar el primero si hay resultados
        if listbox.size() > 0:
            listbox.selection_set(0)
            mostrar(codigos.index(listbox.get(0)))
        else:
            lbl_modelo.config(text='')
            canvas.delete('all')
            lbl_img.config(text='')

    search_var.trace_add('write', filtrar_lista)

    # --- No permitir cerrar hasta asociar todas las imágenes ---
    def puede_cerrar():
        for cod in codigos:
            tiene_imagen = False
            for ext in ('.png', '.jpg', '.jpeg', '.bmp'):
                if os.path.exists(os.path.join(ruta_img, f'{cod}{ext}')):
                    tiene_imagen = True
                    break
            if not tiene_imagen:
                messagebox.showwarning(
                    "Faltan imágenes",
                    "Debes asociar una imagen a todos los modelos antes de cerrar esta ventana."
                )
                return
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", puede_cerrar)

    # Seleccionar el primero por defecto y resaltar modelos sin imagen
    if codigos:
        listbox.selection_set(0)
        mostrar(0)
        resaltar_modelos()
