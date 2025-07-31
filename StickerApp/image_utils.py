import os
from tkinter import filedialog, messagebox
import shutil

def asociar_imagen(data, parent):
    codigos = sorted(list(data['CÓDIGO']))
    ruta_img = os.path.join(os.path.dirname(__file__), 'images')
    import tkinter as tk
    from PIL import Image, ImageTk

    win = tk.Toplevel(parent)
    win.title('Asociar imágenes a modelos')
    win.geometry('700x370')
    win.resizable(False, False)
    # Modalidad y centrado respecto al padre
    win.transient(parent)
    win.grab_set()
    win.update_idletasks()
    # Centrar sobre el padre
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    win_w = win.winfo_width()
    win_h = win.winfo_height()
    x = parent_x + (parent_w // 2) - (win_w // 2)
    y = parent_y + (parent_h // 2) - (win_h // 2)
    win.geometry(f'+{x}+{y}')

    # Layout principal: lista a la izquierda, panel derecho expandido a la derecha
    main_frame = tk.Frame(win)
    main_frame.pack(expand=True, fill='both', padx=10, pady=10)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)

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
    btn_asociar = tk.Button(panel, text='Asociar/Cambiar imagen', width=22)
    btn_asociar.pack(pady=16)

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
        modal.title(title)
        modal.geometry('340x120')
        modal.resizable(False, False)
        modal.transient(win)
        modal.grab_set()
        modal.update_idletasks()
        # Centrar sobre la ventana padre (win)
        parent_x = win.winfo_rootx()
        parent_y = win.winfo_rooty()
        parent_w = win.winfo_width()
        parent_h = win.winfo_height()
        win_w = modal.winfo_width()
        win_h = modal.winfo_height()
        x = parent_x + (parent_w // 2) - (win_w // 2)
        y = parent_y + (parent_h // 2) - (win_h // 2)
        modal.geometry(f'+{x}+{y}')
        lbl = tk.Label(modal, text=msg, font=('Arial', 11), wraplength=320)
        lbl.pack(pady=18, padx=10)
        btn = tk.Button(modal, text='Cerrar', command=modal.destroy, width=12)
        btn.pack(pady=8)
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
        for cod in codigos:
            if filtro in cod.lower():
                listbox.insert('end', cod)
        # Seleccionar el primero si hay resultados
        if listbox.size() > 0:
            listbox.selection_set(0)
            mostrar(codigos.index(listbox.get(0)))
        else:
            lbl_modelo.config(text='')
            canvas.delete('all')
            lbl_img.config(text='')

    search_var.trace_add('write', filtrar_lista)

    # Seleccionar el primero por defecto
    if codigos:
        listbox.selection_set(0)
        mostrar(0)
