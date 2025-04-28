import flet as ft
import sqlite3
import hashlib
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='medical.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=(), fetch_one=False, fetch_all=False, commit=False):
        self.cursor.execute(query, params)
        if commit:
            self.conn.commit()
            return self.cursor.lastrowid if "INSERT" in query.upper() else None
        if fetch_one:
            return self.cursor.fetchone()
        if fetch_all:
            return self.cursor.fetchall()
        return None

    def table_exists(self, table_name):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute_query(query, (table_name,), fetch_one=True)
        return result is not None

    def create_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'nurse', 'patient'))
            )""",
            """CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT CHECK(gender IN ('М', 'Ж')),
                admission_date TEXT,
                treatment_type TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS treatment_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                session_date TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS session_procedures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                procedure_name TEXT NOT NULL,
                parameters TEXT,
                FOREIGN KEY (session_id) REFERENCES treatment_sessions(id) ON DELETE CASCADE
            )"""
        ]
        for table in tables:
            self.execute_query(table, commit=True)

    def add_default_users(self):
        if not self.table_exists('users'):
            return
        users = [
            ('admin', 'admin123', 'admin'),
            ('doctor', 'doctor123', 'doctor'),
            ('nurse', 'nurse123', 'nurse'),
            ('patient', 'patient123', 'patient')
        ]
        for username, password, role in users:
            user_exists = self.execute_query("SELECT 1 FROM users WHERE username = ?", (username,), fetch_one=True)
            if not user_exists:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                self.execute_query(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, hashed_password, role),
                    commit=True
                )

    def add_sample_data(self):
        if not self.table_exists('patients'):
            return
        if self.execute_query("SELECT COUNT(*) FROM patients", fetch_one=True)[0] == 0:
            patients = [
                ("Иванов Иван", 45, "М", "2023-01-10", "Терапия"),
                ("Петрова Анна", 32, "Ж", "2023-01-15", "Хирургия"),
                ("Сидоров Владимир", 28, "М", "2023-02-05", "Диагностика")
            ]
            for p in patients:
                self.execute_query(
                    "INSERT INTO patients (name, age, gender, admission_date, treatment_type) VALUES (?, ?, ?, ?, ?)",
                    p, commit=True
                )

        patient_ids = [row[0] for row in self.execute_query("SELECT id FROM patients ORDER BY id", fetch_all=True)]
        if self.execute_query("SELECT COUNT(*) FROM treatment_sessions", fetch_one=True)[0] == 0 and patient_ids:
            sessions = [
                (patient_ids[0], "2023-01-12 10:00", "Гипертония"),
                (patient_ids[1], "2023-01-16 11:00", "Аппендицит"),
                (patient_ids[2], "2023-02-06 09:30", "Обследование")
            ]
            for s in sessions:
                self.execute_query(
                    "INSERT INTO treatment_sessions (patient_id, session_date, diagnosis) VALUES (?, ?, ?)",
                    s, commit=True
                )

        session_ids = [row[0] for row in self.execute_query("SELECT id FROM treatment_sessions ORDER BY id", fetch_all=True)]
        if self.execute_query("SELECT COUNT(*) FROM session_procedures", fetch_one=True)[0] == 0 and session_ids:
            procedures = [
                (session_ids[0], "УЗИ брюшной полости", "Область: печень"),
                (session_ids[0], "Электрокардиография", "Давление: 120/80"),
                (session_ids[1], "МРТ", "Область: брюшная полость"),
                (session_ids[2], "Физиотерапия", "Курс: 10 сеансов")
            ]
            for proc in procedures:
                self.execute_query(
                    "INSERT INTO session_procedures (session_id, procedure_name, parameters) VALUES (?, ?, ?)",
                    proc, commit=True
                )

def main(page: ft.Page):
    page.title = "Медицинская информационная система"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    db_manager = DatabaseManager()
    db_manager.connect()
    db_manager.create_tables()
    db_manager.add_default_users()
    db_manager.add_sample_data()

    app_state = {"user_role": None, "user_id": None}

    # Вкладка "Пациенты"
    selected_patient_id = None  # Переменная для хранения ID выбранного пациента

    patients_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("ФИО")),
            ft.DataColumn(ft.Text("Возраст")),
            ft.DataColumn(ft.Text("Пол")),
            ft.DataColumn(ft.Text("Дата поступления")),
            ft.DataColumn(ft.Text("Тип лечения"))
        ],
        rows=[],
    )
    patients_table_container = ft.Column([patients_table], scroll=ft.ScrollMode.AUTO, expand=True)

    def update_patients_list():
        nonlocal selected_patient_id
        # Не сбрасываем selected_patient_id, чтобы сохранить выбор
        patients_data = db_manager.execute_query(
            "SELECT id, name, age, gender, admission_date, treatment_type FROM patients ORDER BY id",
            fetch_all=True
        )
        if patients_data is None:
            patients_data = []
        patients_table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(cell), color=ft.colors.BLUE if selected_patient_id == row[0] else None))
                    for cell in row
                ],
                data=row[0],
                on_select_changed=lambda e, row_id=row[0]: handle_row_selection(row_id),
            ) for row in patients_data
        ]
        page.update()
        print("Patients list updated")

    def handle_row_selection(row_id):
        nonlocal selected_patient_id
        selected_patient_id = row_id
        print(f"Row selected: {selected_patient_id}")
        update_patients_list()  # Обновляем таблицу для отображения выделения

    # Панель для добавления пациента
    add_patient_name = ft.TextField(label="ФИО", width=300)
    add_patient_age = ft.TextField(label="Возраст", width=300, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"))
    add_patient_gender = ft.Dropdown(label="Пол", width=300, options=[ft.dropdown.Option("М"), ft.dropdown.Option("Ж")])
    add_patient_admission_date = ft.TextField(label="Дата поступления", width=300, value=datetime.now().strftime("%Y-%m-%d"))
    add_patient_treatment_type = ft.Dropdown(
        label="Тип лечения", width=300,
        options=[ft.dropdown.Option("Терапия"), ft.dropdown.Option("Хирургия"), ft.dropdown.Option("Диагностика")]
    )
    add_patient_panel = ft.Column(
        [
            ft.Text("Добавить пациента", weight=ft.FontWeight.BOLD),
            add_patient_name,
            add_patient_age,
            add_patient_gender,
            add_patient_admission_date,
            add_patient_treatment_type,
            ft.Row([
                ft.ElevatedButton("Сохранить", on_click=lambda e: add_patient_action()),
                ft.ElevatedButton("Отмена", on_click=lambda e: toggle_add_patient_panel(None))
            ])
        ],
        visible=False,
        spacing=10
    )

    def toggle_add_patient_panel(e):
        add_patient_panel.visible = not add_patient_panel.visible
        if not add_patient_panel.visible:
            # Очищаем поля при закрытии
            add_patient_name.value = ""
            add_patient_age.value = ""
            add_patient_gender.value = None
            add_patient_admission_date.value = datetime.now().strftime("%Y-%m-%d")
            add_patient_treatment_type.value = None
        page.update()
        print("Add patient panel toggled:", add_patient_panel.visible)

    def add_patient_action():
        print("Adding patient")
        name = add_patient_name.value
        age = add_patient_age.value
        gender = add_patient_gender.value
        admission_date = add_patient_admission_date.value
        treatment_type = add_patient_treatment_type.value
        if not name or not age or not gender or not admission_date or not treatment_type:
            error_text.value = "Заполните все поля"
            page.update()
            return
        try:
            age = int(age)
            db_manager.execute_query(
                "INSERT INTO patients (name, age, gender, admission_date, treatment_type) VALUES (?, ?, ?, ?, ?)",
                (name, age, gender, admission_date, treatment_type),
                commit=True
            )
            error_text.value = "Пациент успешно добавлен"
            update_patients_list()
            toggle_add_patient_panel(None)  # Закрываем панель
            print("Patient added successfully")
        except ValueError:
            error_text.value = "Возраст должен быть числом"
        except Exception as ex:
            error_text.value = f"Ошибка при добавлении пациента: {str(ex)}"
        page.update()

    # Панель для удаления пациента
    delete_confirm_panel = ft.Column(
        [
            ft.Text("Подтверждение удаления", weight=ft.FontWeight.BOLD),
            ft.Text(""),
            ft.Row([
                ft.ElevatedButton("Да", on_click=lambda e: confirm_delete()),
                ft.ElevatedButton("Нет", on_click=lambda e: toggle_delete_confirm_panel(None))
            ])
        ],
        visible=False,
        spacing=10
    )

    def toggle_delete_confirm_panel(e):
        if selected_patient_id:
            delete_confirm_panel.controls[1] = ft.Text(f"Вы уверены, что хотите удалить пациента с ID {selected_patient_id}?")
            delete_confirm_panel.visible = not delete_confirm_panel.visible
        else:
            error_text.value = "Выберите пациента для удаления"
        page.update()
        print("Delete confirm panel toggled:", delete_confirm_panel.visible)

    def confirm_delete():
        nonlocal selected_patient_id  # Переместили nonlocal в начало функции
        print(f"Confirming deletion of patient ID {selected_patient_id}")
        db_manager.execute_query("DELETE FROM patients WHERE id = ?", (selected_patient_id,), commit=True)
        error_text.value = "Пациент удален"
        selected_patient_id = None
        update_patients_list()
        toggle_delete_confirm_panel(None)
        page.update()

    # Текст для отображения сообщений
    error_text = ft.Text("", color=ft.colors.RED)

    patients_tab_content = ft.Column(
        [
            ft.Row([
                ft.ElevatedButton("Добавить", icon=ft.Icons.ADD, on_click=toggle_add_patient_panel),
                ft.ElevatedButton("Удалить", icon=ft.Icons.DELETE, on_click=toggle_delete_confirm_panel),
                ft.ElevatedButton("Обновить", icon=ft.Icons.REFRESH, on_click=lambda e: update_patients_list())
            ], alignment=ft.MainAxisAlignment.START),
            add_patient_panel,
            delete_confirm_panel,
            error_text,
            ft.Divider(),
            patients_table_container
        ],
        expand=True
    )

    # Вкладка "Лечебные процедуры"
    proc_patient_dropdown = ft.Dropdown(label="Пациент", options=[], width=250)
    proc_date_entry = ft.TextField(label="Дата и время", value=datetime.now().strftime("%Y-%m-%d %H:%M"), width=200)
    proc_diagnosis_entry = ft.TextField(label="Диагноз", width=250)
    proc_name_dropdown = ft.Dropdown(
        label="Процедура",
        width=250,
        options=[
            ft.dropdown.Option("УЗИ брюшной полости"),
            ft.dropdown.Option("Электрокардиография"),
            ft.dropdown.Option("МРТ"),
            ft.dropdown.Option("Физиотерапия"),
            ft.dropdown.Option("Лазерная терапия")
        ]
    )
    proc_params_entry = ft.TextField(label="Параметры", width=300)
    procedures_list_view = ft.ListView(expand=True, spacing=5)
    temp_procedures = []

    def update_patient_dropdown():
        patients = db_manager.execute_query("SELECT id, name FROM patients ORDER BY name", fetch_all=True)
        if patients is None:
            patients = []
        proc_patient_dropdown.options = [ft.dropdown.Option(key=str(p[0]), text=f"{p[0]} - {p[1]}") for p in patients]
        page.update()
        print("Patient dropdown updated")

    def add_procedure_to_temp_list(e):
        proc_name = proc_name_dropdown.value
        proc_params = proc_params_entry.value
        if not proc_name:
            error_text.value = "Выберите процедуру"
            page.update()
            return
        temp_procedures.append({"name": proc_name, "params": proc_params})
        procedures_list_view.controls.append(ft.Text(f"- {proc_name}: {proc_params}"))
        proc_name_dropdown.value = None
        proc_params_entry.value = ""
        page.update()
        print("Procedure added to temp list")

    def save_treatment_session(e):
        patient_id = proc_patient_dropdown.value
        session_date = proc_date_entry.value
        diagnosis = proc_diagnosis_entry.value
        if not patient_id or not session_date or not diagnosis or not temp_procedures:
            error_text.value = "Заполните все поля и добавьте хотя бы одну процедуру"
            page.update()
            return
        try:
            session_id = db_manager.execute_query(
                "INSERT INTO treatment_sessions (patient_id, session_date, diagnosis) VALUES (?, ?, ?)",
                (int(patient_id), session_date, diagnosis),
                commit=True
            )
            for proc in temp_procedures:
                db_manager.execute_query(
                    "INSERT INTO session_procedures (session_id, procedure_name, parameters) VALUES (?, ?, ?)",
                    (session_id, proc["name"], proc["params"]),
                    commit=True
                )
            error_text.value = "Сеанс сохранен"
            proc_patient_dropdown.value = None
            proc_date_entry.value = datetime.now().strftime("%Y-%m-%d %H:%M")
            proc_diagnosis_entry.value = ""
            proc_name_dropdown.value = None
            proc_params_entry.value = ""
            procedures_list_view.controls.clear()
            temp_procedures.clear()
            page.update()
            print("Treatment session saved")
        except Exception as ex:
            error_text.value = f"Ошибка при сохранении сеанса: {str(ex)}"
            page.update()

    procedures_tab_content = ft.Row(
        [
            ft.Column([
                ft.Text("Информация о сеансе", weight=ft.FontWeight.BOLD),
                proc_patient_dropdown,
                proc_date_entry,
                proc_diagnosis_entry,
                ft.ElevatedButton("Обновить список пациентов", on_click=lambda e: update_patient_dropdown())
            ], width=300),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("Процедуры сеанса", weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=procedures_list_view,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    padding=5,
                    expand=True
                ),
                ft.Text("Добавить процедуру", weight=ft.FontWeight.BOLD),
                ft.Row([proc_name_dropdown, proc_params_entry], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ElevatedButton("Добавить процедуру", icon=ft.Icons.ADD, on_click=add_procedure_to_temp_list),
                ft.ElevatedButton("Сохранить сеанс", icon=ft.Icons.SAVE, on_click=save_treatment_session)
            ], expand=True)
        ],
        expand=True
    )

    # Вкладка "Просмотр данных"
    view_data_type_dropdown = ft.Dropdown(
        label="Тип данных",
        value="Пациенты",
        width=200,
        options=[
            ft.dropdown.Option("Пациенты"),
            ft.dropdown.Option("Сеансы"),
            ft.dropdown.Option("Процедуры")
        ]
    )
    view_data_table = ft.DataTable(columns=[], rows=[])
    view_data_table_container = ft.Column([view_data_table], scroll=ft.ScrollMode.AUTO, expand=True)

    def update_data_view(e=None):
        data_type = view_data_type_dropdown.value
        view_data_table.columns = []
        view_data_table.rows = []
        if data_type == "Пациенты":
            view_data_table.columns = [
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("ФИО")),
                ft.DataColumn(ft.Text("Возраст")),
                ft.DataColumn(ft.Text("Пол")),
                ft.DataColumn(ft.Text("Дата поступления")),
                ft.DataColumn(ft.Text("Тип лечения"))
            ]
            data = db_manager.execute_query("SELECT * FROM patients ORDER BY id", fetch_all=True)
        elif data_type == "Сеансы":
            view_data_table.columns = [
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("ID пациента")),
                ft.DataColumn(ft.Text("Пациент")),
                ft.DataColumn(ft.Text("Дата сеанса")),
                ft.DataColumn(ft.Text("Диагноз"))
            ]
            data = db_manager.execute_query(
                "SELECT s.id, s.patient_id, p.name, s.session_date, s.diagnosis FROM treatment_sessions s JOIN patients p ON s.patient_id = p.id ORDER BY s.session_date DESC",
                fetch_all=True
            )
        elif data_type == "Процедуры":
            view_data_table.columns = [
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("ID сеанса")),
                ft.DataColumn(ft.Text("Дата сеанса")),
                ft.DataColumn(ft.Text("Процедура")),
                ft.DataColumn(ft.Text("Параметры"))
            ]
            data = db_manager.execute_query(
                "SELECT p.id, p.session_id, s.session_date, p.procedure_name, p.parameters FROM session_procedures p JOIN treatment_sessions s ON p.session_id = s.id ORDER BY p.id",
                fetch_all=True
            )
        else:
            data = []
        if data is None:
            data = []
        view_data_table.rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
            for row in data
        ]
        page.update()
        print("Data view updated")

    tabs_control = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Пациенты", content=patients_tab_content),
            ft.Tab(text="Лечебные процедуры", content=procedures_tab_content),
            ft.Tab(text="Просмотр данных", content=ft.Column([
                ft.Row([
                    view_data_type_dropdown,
                    ft.ElevatedButton("Обновить", icon=ft.Icons.REFRESH, on_click=update_data_view)
                ]),
                ft.Divider(),
                view_data_table_container
            ], expand=True))
        ],
        expand=1
    )

    def create_main_interface():
        print("Creating main interface")
        page.controls = [tabs_control]
        update_data_view()
        update_patients_list()
        update_patient_dropdown()
        page.update()
        print("Main interface created")

    login_field = ft.TextField(label="Логин", width=300)
    password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True, width=300)

    def authenticate(e):
        username = login_field.value.strip()
        password = password_field.value.strip()
        if not username or not password:
            error_text.value = "Введите логин и пароль"
            page.update()
            return
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user_data = db_manager.execute_query(
            "SELECT id, role FROM users WHERE username = ? AND password = ?",
            (username, hashed_password),
            fetch_one=True
        )
        if user_data:
            app_state["user_id"] = user_data[0]
            app_state["user_role"] = user_data[1]
            create_main_interface()
        else:
            error_text.value = "Неверный логин или пароль"
        page.update()
        print("Authentication attempted")

    login_view = ft.Column(
        [
            ft.Text("Авторизация", size=24, weight=ft.FontWeight.BOLD),
            login_field,
            password_field,
            ft.ElevatedButton("Войти", on_click=authenticate, width=300),
            error_text
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True
    )

    def window_event_handler(e):
        if e.data == "close":
            db_manager.close()
            page.window_destroy()

    page.window_prevent_close = True
    page.on_window_event = window_event_handler
    page.controls = [login_view]
    page.update()

if __name__ == "__main__":
    ft.app(target=main)