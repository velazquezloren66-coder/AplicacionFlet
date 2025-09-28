import sqlite3 as sqlite
import flet as ft
from datetime import datetime


#Base de datos (SQLite3)
class Database:
    def __init__(self):
        self.db = None

    def connect_to_db(self):
        try:
            self.db = sqlite.connect("todo.db")
            c = self.db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id   INTEGER PRIMARY KEY AUTOINCREMENT,
                    task VARCHAR(255) NOT NULL,
                    date VARCHAR(50)  NOT NULL
                )
                """
            )
            self.db.commit()
        except sqlite.DatabaseError as e:
            print("Error connecting to database:", e)

    def read_db(self):
        c = self.db.cursor()
        c.execute("SELECT task, date FROM tasks ORDER BY id ASC")
        return c.fetchall()

    def insert_db(self, values):
        c = self.db.cursor()
        c.execute("INSERT INTO tasks (task, date) VALUES (?, ?)", values)
        self.db.commit()

    def delete_db(self, value):
        c = self.db.cursor()
        c.execute("DELETE FROM tasks WHERE task=?", value)
        self.db.commit()

    def update_db(self, value):
        c = self.db.cursor()
        c.execute("UPDATE tasks SET task=? WHERE task=?", value)
        self.db.commit()

    def close_db(self):
        if self.db:
            self.db.close()


#mi formulario para crear/editar
class FormContainer(ft.Container):
    def __init__(self, func):
        self.func = func
        super().__init__()

        self.text_field = ft.TextField(
            label="✍️ Escribe una nueva tarea...",
            height=60,
            width=360, #ancho de input donde agregar tareas
            border_radius=12,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_GREY_800,
            border_color=ft.Colors.BLUE_200,
            hint_style=ft.TextStyle(color=ft.Colors.BLUE_GREY_200, size=12),
        )

        self.add_button = ft.ElevatedButton(
            "➕ Agregar Tarea",
            width=200,
            height=46,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_400,
                color=ft.Colors.BLACK,
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=5,
            ),
            on_click=self.func,
        )

        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[self.text_field, self.add_button],
        )

        self.width = 420 #ancho de contenedor de opcion que aparece cuando quiero agregar nuevas tareas
        self.height = 80
        self.bgcolor = ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY_700)
        self.border_radius = ft.border_radius.all(20)
        self.opacity = 0
        self.animate = ft.Animation(400, ft.AnimationCurve.DECELERATE)
        self.animate_opacity = 300
        self.padding = 20
        self.shadow = ft.BoxShadow(
            spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK)
        )



#Ítem de tarea
class CreateTask(ft.Container):
    def __init__(self, task: str, date: str, func_delete, func_edit):
        self.task = task
        self.date = date
        self.func_delete = func_delete
        self.func_edit = func_edit
        super().__init__()

        self.width = 480 #ancho de mis campos de tareas al ser guardados
        self.height = 70
        self.bgcolor = ft.Colors.BLUE_GREY_800
        self.border_radius = ft.border_radius.all(12)
        self.shadow = ft.BoxShadow(blur_radius=6, color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK))
        self.padding = ft.padding.symmetric(horizontal=15, vertical=8)

        self.on_hover = self.hover_show_icon

        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(value=f"📌 {self.task}", size=13, weight=ft.FontWeight.BOLD),
                        ft.Text(value=f"⏳ {self.date}", size=10, color=ft.Colors.BLUE_200),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                    controls=[
                        self.task_button(ft.Icons.DELETE_FOREVER_ROUNDED, ft.Colors.RED_400, self.func_delete),
                        self.task_button(ft.Icons.CREATE_ROUNDED, ft.Colors.CYAN_300, self.func_edit),
                    ],
                ),
            ],
        )

    def task_button(self, icon, color, func):
        return ft.IconButton(
            icon=icon,
            icon_size=20,
            icon_color=color,
            opacity=0,
            animate_opacity=200,
            on_click=lambda e: func(self),
        )

    def hover_show_icon(self, e):
        show = e.data == "true"
        row_icons = e.control.content.controls[1]
        for btn in row_icons.controls:
            btn.opacity = 1 if show else 0
        e.control.content.update()



#App principal
def main(page: ft.Page):
    page.title = "🚀 Mis Pendientes"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_maximized = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30
    page.bgcolor = ft.Colors.BLUE_GREY_50


    #Mi conexión a mi DB
    db = Database()
    db.connect_to_db()

    def toggle_form_open(e=None):
        if form.height != 200:
            form.height, form.opacity = 200, 1
        else:
            form.height, form.opacity = 80, 0
            form.text_field.value = None
            form.add_button.text = "➕ Agregar Tarea"
            form.add_button.on_click = add_task_to_screen
        form.update()

    def add_task_to_screen(e):
        task_value = form.text_field.value
        if not task_value:
            return
        task_created_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        db.insert_db((task_value, task_created_date))
        main_column.controls.append(CreateTask(task_value, task_created_date, delete_task, edit_task))
        main_column.update()
        toggle_form_open()

    def delete_task(item: CreateTask):
        db.delete_db((item.task,))
        main_column.controls.remove(item)
        main_column.update()

    def edit_task(item: CreateTask):
        form.height, form.opacity = 200, 1
        form.text_field.value = item.task
        form.add_button.text = "✏️ Actualizar"

        def do_update(_=None):
            finalize_update(item)

        form.add_button.on_click = do_update
        form.update()

    def finalize_update(item: CreateTask):
        new_task = form.text_field.value or item.task
        old_task = item.task
        new_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        db.update_db((new_task, old_task))
        item.task = new_task
        item.date = new_date
        item.content.controls[0].controls[0].value = f"📌 {item.task}"
        item.content.controls[0].controls[1].value = f"⏳ {item.date}"
        item.content.update()
        form.text_field.value = None
        form.add_button.text = "➕ Agregar Tarea"
        form.add_button.on_click = add_task_to_screen
        toggle_form_open()

    #UI principal
    main_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
        spacing=15,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("🚀 Mis Pendientes", color=ft.Colors.CYAN_300, size=22, weight=ft.FontWeight.BOLD),
                    ft.IconButton(icon=ft.Icons.ADD_TASK_ROUNDED, icon_size=26, icon_color=ft.Colors.CYAN_400, on_click=toggle_form_open),
                ],
            ),
            ft.Divider(height=8, color=ft.Colors.BLUE_GREY_600),
        ],
    )

    form = FormContainer(add_task_to_screen)

    root = ft.Container(
        expand=True,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=440, #ancho de mi contenedor de aplicación
                    height=650,
                    bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.BLUE_GREY_900),
                    border_radius=30,
                    shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)),
                    padding=20,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.START,
                        expand=True,
                        spacing=20,
                        controls=[main_column, form],
                    ),
                )
            ],
        ),
    )

    page.add(root)

    #Acá voy a cargar mis tareas existentes
    for task, date in db.read_db():
        main_column.controls.append(CreateTask(task, date, delete_task, edit_task))
    main_column.update()

    def on_close(e):
        db.close_db()
    page.on_disconnect = on_close


if __name__ == "__main__":
    ft.app(target=main, port=8000)
