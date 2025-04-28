import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import hashlib
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Медицинская информационная система")
        self.root.geometry("1200x800")
        
        # Инициализация базы данных
        self.conn = sqlite3.connect('medical.db')
        self.cursor = self.conn.cursor()
        
        # Создание таблиц
        self.create_tables()
        self.add_default_users()
        self.add_sample_data()
        
        # Текущий пользователь
        self.current_user = None
        
        # Создание интерфейса
        self.create_login_screen()

    def create_tables(self):
        """Создание таблиц в базе данных"""
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
                age INTEGER CHECK(age > 0 AND age < 120),
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
            try:
                self.cursor.execute(table)
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка БД", f"Ошибка создания таблицы: {str(e)}")
                raise
        self.conn.commit()

    def add_default_users(self):
        """Добавление тестовых пользователей"""
        users = [
            ('admin', 'admin123', 'admin'),
            ('doctor', 'doctor123', 'doctor'),
            ('nurse', 'nurse123', 'nurse'),
            ('patient', 'patient123', 'patient')
        ]
        
        for username, password, role in users:
            try:
                self.cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
                if not self.cursor.fetchone():
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    self.cursor.execute(
                        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        (username, hashed_password, role)
                    )
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка БД", f"Ошибка добавления пользователя: {str(e)}")
                raise
        self.conn.commit()

    def add_sample_data(self):
        """Добавление тестовых данных"""
        try:
            # Добавляем пациентов, если их нет
            self.cursor.execute("SELECT COUNT(*) FROM patients")
            if self.cursor.fetchone()[0] == 0:
                patients = [
                    ("Иванов Иван", 45, "М", "2023-01-10", "Терапия"),
                    ("Петрова Анна", 32, "Ж", "2023-01-15", "Хирургия"),
                    ("Сидоров Владимир", 28, "М", "2023-02-05", "Диагностика")
                ]
                self.cursor.executemany(
                    "INSERT INTO patients (name, age, gender, admission_date, treatment_type) VALUES (?, ?, ?, ?, ?)",
                    patients
                )
                self.conn.commit()

            # Получаем ID всех пациентов
            self.cursor.execute("SELECT id FROM patients ORDER BY id")
            patient_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Добавляем тестовые сеансы, если их нет
            self.cursor.execute("SELECT COUNT(*) FROM treatment_sessions")
            if self.cursor.fetchone()[0] == 0 and patient_ids:
                sessions = []
                if len(patient_ids) >= 1:
                    sessions.append((patient_ids[0], "2023-01-12 10:00", "Гипертония"))
                if len(patient_ids) >= 2:
                    sessions.append((patient_ids[1], "2023-01-16 11:00", "Аппендицит"))
                if len(patient_ids) >= 3:
                    sessions.append((patient_ids[2], "2023-02-06 09:30", "Обследование"))
                
                if sessions:
                    self.cursor.executemany(
                        "INSERT INTO treatment_sessions (patient_id, session_date, diagnosis) VALUES (?, ?, ?)",
                        sessions
                    )
                    self.conn.commit()

            # Получаем ID всех сеансов
            self.cursor.execute("SELECT id FROM treatment_sessions ORDER BY id")
            session_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Добавляем тестовые процедуры, если их нет
            self.cursor.execute("SELECT COUNT(*) FROM session_procedures")
            if self.cursor.fetchone()[0] == 0 and session_ids:
                procedures = []
                if len(session_ids) >= 1:
                    procedures.extend([
                        (session_ids[0], "УЗИ брюшной полости", "Область: печень, параметры: норма"),
                        (session_ids[0], "Электрокардиография", "Давление: 120/80")
                    ])
                if len(session_ids) >= 2:
                    procedures.append((session_ids[1], "МРТ", "Область: брюшная полость"))
                if len(session_ids) >= 3:
                    procedures.append((session_ids[2], "Физиотерапия", "Курс: 10 сеансов"))
                
                if procedures:
                    self.cursor.executemany(
                        "INSERT INTO session_procedures (session_id, procedure_name, parameters) VALUES (?, ?, ?)",
                        procedures
                    )
                    self.conn.commit()

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка добавления тестовых данных: {str(e)}")
            raise

    def create_login_screen(self):
        """Создание экрана авторизации"""
        self.clear_window()
        
        login_frame = ttk.LabelFrame(self.root, text="Авторизация")
        login_frame.pack(pady=50, padx=50, fill="both", expand=True)
        
        ttk.Label(login_frame, text="Логин:").grid(row=0, column=0, padx=5, pady=5)
        self.login_entry = ttk.Entry(login_frame)
        self.login_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(login_frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        login_btn = ttk.Button(login_frame, text="Войти", command=self.authenticate)
        login_btn.grid(row=2, columnspan=2, pady=10)

    def authenticate(self):
        """Аутентификация пользователя"""
        username = self.login_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            self.cursor.execute(
                "SELECT id, role FROM users WHERE username = ? AND password = ?",
                (username, hashed_password)
            )
            user = self.cursor.fetchone()
            
            if user:
                self.current_user = {'id': user[0], 'role': user[1]}
                self.create_main_interface()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка аутентификации: {str(e)}")

    def create_main_interface(self):
        """Создание основного интерфейса"""
        self.clear_window()
        
        # Создание панели вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # Добавление вкладок в зависимости от роли
        if self.current_user['role'] != 'patient':
            self.create_patients_tab()
            self.create_procedures_tab()
            self.create_view_data_tab()
        
        if self.current_user['role'] in ['admin', 'doctor']:
            self.create_stats_tab()
        
        # Кнопка выхода
        logout_btn = ttk.Button(self.root, text="Выйти", command=self.create_login_screen)
        logout_btn.pack(pady=10)

    def create_patients_tab(self):
        """Вкладка работы с пациентами"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Пациенты")
        
        # Таблица пациентов
        self.patients_tree = ttk.Treeview(tab, columns=("id", "name", "age", "gender", "admission_date"), show="headings")
        self.patients_tree.heading("id", text="ID")
        self.patients_tree.heading("name", text="ФИО")
        self.patients_tree.heading("age", text="Возраст")
        self.patients_tree.heading("gender", text="Пол")
        self.patients_tree.heading("admission_date", text="Дата поступления")
        
        self.patients_tree.column("id", width=50)
        self.patients_tree.column("name", width=200)
        self.patients_tree.column("age", width=50)
        self.patients_tree.column("gender", width=50)
        self.patients_tree.column("admission_date", width=100)
        
        self.patients_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.patients_tree.yview)
        self.patients_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Панель кнопок
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Добавить", command=self.show_add_patient_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_patient).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_patients_list).pack(side="left", padx=5)
        
        # Первоначальная загрузка данных
        self.update_patients_list()

    def show_add_patient_dialog(self):
        """Диалог добавления нового пациента"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить пациента")
        dialog.geometry("400x300")
        
        fields = [
            ("ФИО:", ttk.Entry(dialog)),
            ("Возраст:", ttk.Entry(dialog)),
            ("Пол:", ttk.Combobox(dialog, values=["М", "Ж"], state="readonly")),
            ("Дата поступления:", ttk.Entry(dialog)),
            ("Тип лечения:", ttk.Combobox(dialog, values=["Терапия", "Хирургия", "Диагностика"], state="readonly"))
        ]
        
        for i, (label, widget) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            widget.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            if label == "Дата поступления:":
                widget.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(dialog, text="Добавить", command=lambda: self.add_patient(
            fields[0][1].get(),  # name
            fields[1][1].get(),  # age
            fields[2][1].get(),  # gender
            fields[3][1].get(),  # admission_date
            fields[4][1].get()   # treatment_type
        )).grid(row=len(fields), columnspan=2, pady=10)

    def add_patient(self, name, age, gender, admission_date, treatment_type):
        """Добавление нового пациента в БД"""
        try:
            if not name or not age or not gender:
                raise ValueError("Заполните обязательные поля")
            
            self.cursor.execute(
                "INSERT INTO patients (name, age, gender, admission_date, treatment_type) VALUES (?, ?, ?, ?, ?)",
                (name, age, gender, admission_date, treatment_type)
            )
            self.conn.commit()
            messagebox.showinfo("Успех", "Пациент добавлен")
            self.update_patients_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка добавления пациента: {str(e)}")

    def update_patients_list(self):
        """Обновление списка пациентов"""
        for item in self.patients_tree.get_children():
            self.patients_tree.delete(item)
        
        try:
            self.cursor.execute("SELECT id, name, age, gender, admission_date FROM patients ORDER BY id")  # Сортируем по ID
            for row in self.cursor.fetchall():
                self.patients_tree.insert("", "end", values=row)  # Добавляем в конец списка
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки пациентов: {str(e)}")

    def delete_patient(self):
        """Удаление выбранного пациента"""
        selected = self.patients_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пациента для удаления")
            return
        
        patient_id = self.patients_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Удалить этого пациента и все связанные данные?"):
            try:
                self.cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
                self.conn.commit()
                self.update_patients_list()
                messagebox.showinfo("Успех", "Пациент удален")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить пациента: {str(e)}")
                self.conn.rollback()

    def create_procedures_tab(self):
        """Вкладка лечебных процедур"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Лечебные процедуры")
        
        # Основной контейнер
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Левая панель - информация о сеансе
        left_frame = ttk.LabelFrame(main_frame, text="Информация о сеансе")
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        # Выбор пациента
        ttk.Label(left_frame, text="Пациент:").pack(anchor="w")
        self.patient_combobox = ttk.Combobox(left_frame, state="readonly")
        self.patient_combobox.pack(fill="x", pady=2)
        
        # Дата сеанса
        ttk.Label(left_frame, text="Дата и время:").pack(anchor="w")
        self.session_date_entry = ttk.Entry(left_frame)
        self.session_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.session_date_entry.pack(fill="x", pady=2)
        
        # Диагноз
        ttk.Label(left_frame, text="Диагноз:").pack(anchor="w")
        self.diagnosis_entry = ttk.Entry(left_frame)
        self.diagnosis_entry.pack(fill="x", pady=2)
        
        # Кнопка обновления списка пациентов
        ttk.Button(left_frame, text="Обновить список", command=self.update_patient_combobox).pack(pady=5)
        
        # Правая панель - процедуры
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Таблица процедур
        self.procedures_tree = ttk.Treeview(right_frame, columns=("procedure", "params"), show="headings")
        self.procedures_tree.heading("procedure", text="Процедура")
        self.procedures_tree.heading("params", text="Параметры")
        self.procedures_tree.column("procedure", width=200)
        self.procedures_tree.column("params", width=300)
        self.procedures_tree.pack(fill="both", expand=True)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.procedures_tree.yview)
        self.procedures_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Панель добавления процедуры
        add_frame = ttk.LabelFrame(right_frame, text="Добавить процедуру")
        add_frame.pack(fill="x", pady=5)
        
        ttk.Label(add_frame, text="Процедура:").grid(row=0, column=0, padx=2)
        self.procedure_name_combobox = ttk.Combobox(add_frame, state="readonly")
        self.procedure_name_combobox['values'] = [
            "УЗИ брюшной полости",
            "Электрокардиография",
            "МРТ",
            "Физиотерапия",
            "Лазерная терапия"
        ]
        self.procedure_name_combobox.grid(row=0, column=1, padx=2, sticky="ew")
        
        ttk.Label(add_frame, text="Параметры:").grid(row=1, column=0, padx=2)
        self.procedure_params_entry = ttk.Entry(add_frame)
        self.procedure_params_entry.grid(row=1, column=1, padx=2, sticky="ew")
        
        ttk.Button(add_frame, text="Добавить", command=self.add_procedure_to_list).grid(row=2, columnspan=2, pady=5)
        
        # Кнопка сохранения сеанса
        ttk.Button(right_frame, text="Сохранить сеанс", command=self.save_treatment_session).pack(pady=5)
        
        # Обновление списка пациентов
        self.update_patient_combobox()

    def update_patient_combobox(self):
        """Обновление списка пациентов в combobox"""
        try:
            self.cursor.execute("SELECT id, name FROM patients ORDER BY name")
            patients = [f"{row[0]} - {row[1]}" for row in self.cursor.fetchall()]
            self.patient_combobox['values'] = patients
            if patients:
                self.patient_combobox.current(0)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки пациентов: {str(e)}")

    def add_procedure_to_list(self):
        """Добавление процедуры в список"""
        procedure = self.procedure_name_combobox.get()
        params = self.procedure_params_entry.get()
        
        if not procedure:
            messagebox.showwarning("Ошибка", "Выберите процедуру")
            return
        
        self.procedures_tree.insert("", "end", values=(procedure, params))
        self.procedure_name_combobox.set('')
        self.procedure_params_entry.delete(0, tk.END)

    def save_treatment_session(self):
        """Сохранение лечебного сеанса"""
        try:
            # Проверка данных
            if not self.patient_combobox.get():
                raise ValueError("Выберите пациента")
            
            patient_id = int(self.patient_combobox.get().split(" - ")[0])
            session_date = self.session_date_entry.get()
            diagnosis = self.diagnosis_entry.get()
            
            if not session_date:
                raise ValueError("Введите дату сеанса")
            if not diagnosis:
                raise ValueError("Введите диагноз")
            if not self.procedures_tree.get_children():
                raise ValueError("Добавьте хотя бы одну процедуру")
            
            # Сохранение сеанса
            self.cursor.execute(
                "INSERT INTO treatment_sessions (patient_id, session_date, diagnosis) VALUES (?, ?, ?)",
                (patient_id, session_date, diagnosis)
            )
            session_id = self.cursor.lastrowid
            
            # Сохранение процедур
            for item in self.procedures_tree.get_children():
                procedure = self.procedures_tree.item(item)['values']
                self.cursor.execute(
                    "INSERT INTO session_procedures (session_id, procedure_name, parameters) VALUES (?, ?, ?)",
                    (session_id, procedure[0], procedure[1])
                )
            
            self.conn.commit()
            messagebox.showinfo("Успех", "Сеанс сохранен")
            
            # Очистка формы
            self.session_date_entry.delete(0, tk.END)
            self.session_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
            self.diagnosis_entry.delete(0, tk.END)
            self.procedures_tree.delete(*self.procedures_tree.get_children())
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения сеанса: {str(e)}")
            self.conn.rollback()

    def create_view_data_tab(self):
        """Вкладка просмотра данных"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Просмотр данных")
        
        # Панель фильтров
        filter_frame = ttk.LabelFrame(tab, text="Фильтры")
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Тип данных:").grid(row=0, column=0, padx=5)
        self.data_type_combobox = ttk.Combobox(filter_frame, values=["Пациенты", "Сеансы", "Процедуры"], state="readonly")
        self.data_type_combobox.current(0)
        self.data_type_combobox.grid(row=0, column=1, padx=5)
        
        ttk.Button(filter_frame, text="Обновить", command=self.update_data_view).grid(row=0, column=2, padx=5)
        
        # Таблица данных
        self.data_tree = ttk.Treeview(tab)
        self.data_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Первоначальная загрузка
        self.update_data_view()

    def update_data_view(self):
        """Обновление данных в таблице"""
        data_type = self.data_type_combobox.get()
        self.data_tree.delete(*self.data_tree.get_children())
        self.data_tree["columns"] = []
        
        if data_type == "Пациенты":
            self.show_patients_data()
        elif data_type == "Сеансы":
            self.show_sessions_data()
        elif data_type == "Процедуры":
            self.show_procedures_data()

    def show_patients_data(self):
        """Отображение данных о пациентах"""
        columns = ("ID", "ФИО", "Возраст", "Пол", "Дата поступления", "Тип лечения")
        self.data_tree["columns"] = columns
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100)
        
        try:
            self.cursor.execute("SELECT * FROM patients ORDER BY id")  # Сортируем по ID
            for row in self.cursor.fetchall():
                self.data_tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки пациентов: {str(e)}")

    def show_sessions_data(self):
        """Отображение данных о сеансах"""
        columns = ("ID", "ID пациента", "Пациент", "Дата сеанса", "Диагноз")
        self.data_tree["columns"] = columns
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100)
        
        try:
            self.cursor.execute("""
                SELECT s.id, s.patient_id, p.name, s.session_date, s.diagnosis 
                FROM treatment_sessions s
                JOIN patients p ON s.patient_id = p.id
                ORDER BY s.session_date DESC
            """)
            for row in self.cursor.fetchall():
                self.data_tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки сеансов: {str(e)}")

    def show_procedures_data(self):
        """Отображение данных о процедурах"""
        columns = ("ID", "ID сеанса", "Дата сеанса", "Процедура", "Параметры")
        self.data_tree["columns"] = columns
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100)
        
        try:
            self.cursor.execute("""
                SELECT p.id, p.session_id, s.session_date, p.procedure_name, p.parameters
                FROM session_procedures p
                JOIN treatment_sessions s ON p.session_id = s.id
                ORDER BY p.id
            """)
            for row in self.cursor.fetchall():
                self.data_tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки процедур: {str(e)}")

    def create_stats_tab(self):
        """Вкладка статистики"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Статистика")
        
        # Контейнер с прокруткой
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Статистика по возрастам
        age_frame = ttk.LabelFrame(scrollable_frame, text="Распределение по возрастам")
        age_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Кнопка обновления статистики
        ttk.Button(age_frame, text="Обновить статистику", command=self.update_age_stats).pack(pady=5)
        
        # Контейнер для графика
        self.age_stats_container = ttk.Frame(age_frame)
        self.age_stats_container.pack(fill="both", expand=True)
        
        # Первоначальная загрузка статистики
        self.update_age_stats()

    def update_age_stats(self):
        """Обновление статистики по возрастам"""
        # Очищаем контейнер
        for widget in self.age_stats_container.winfo_children():
            widget.destroy()
        
        try:
            self.cursor.execute("SELECT age FROM patients WHERE age IS NOT NULL")
            ages = [row[0] for row in self.cursor.fetchall()]
            
            if ages:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.hist(ages, bins=range(0, 101, 10), edgecolor='black')
                ax.set_xlabel('Возраст')
                ax.set_ylabel('Количество пациентов')
                ax.set_title('Распределение пациентов по возрастам')
                
                canvas = FigureCanvasTkAgg(fig, master=self.age_stats_container)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            else:
                ttk.Label(self.age_stats_container, text="Нет данных для отображения").pack()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки статистики: {str(e)}")
            ttk.Label(self.age_stats_container, text="Ошибка загрузки данных").pack()

    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def __del__(self):
        """Закрытие соединения с БД"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalApp(root)
    root.mainloop()