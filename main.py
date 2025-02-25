import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import yaml
import os


def create_form():
    # Create the main window
    root = tk.Tk()
    root.title("Medical Form")

    root.minsize(600, 400)

    medications = []

    def clean_lines():
        entry_name.delete(0, 'end')
        entry_orvi.delete(0, 'end')
        for med in medications:
            med[0].delete(0, 'end')
            med[1].set('')
            med[2].set('')

    def save_to_yaml():
        fio = entry_name.get()
        data = {
            fio: {
                'Дата записи': str(time.strftime("%d.%m.%Y", time.localtime(time.time()))),
                'Заболевание': entry_orvi.get(),
                'Лекарства': [{'Название': med[0].get(), 'Кол-во': med[1].get(), 'Как долго принимать': med[2].get()} for med in medications],
                'Отчёты': [{'Дата': str(time.strftime("%d.%m.%Y", time.localtime(time.time()))), 'Состояние здоровья': ''}]
            }
        }
        clean_lines()
        try:
            if os.path.exists('data.yaml'):
                with open('data.yaml', 'r', encoding='utf-8') as file:
                    try:
                        existing_data = yaml.safe_load(file) or {}
                    except yaml.YAMLError:
                        existing_data = {}
            else:
                existing_data = {}

            if fio in existing_data:
                existing_data[fio]['Заболевание'] = data[fio]['Заболевание']
                existing_data[fio]['Лекарства'] = data[fio]['Лекарства']
                existing_data[fio]['Отчёты'].append(data[fio]['Отчёты'][0])
            else:
                existing_data.update(data)

            with open('data.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(existing_data, file, allow_unicode=True)

            medication_row[0] += 2
            print(f"Данные для ФИО '{fio}' успешно сохранены в файле data.yaml.")
        except Exception as exc:
            tk.messagebox.showerror("Ошибка", f"Ошибка записи данных в файл data.yaml:\n{exc}")

    def add_medication():
        if len(medications) >= 10:
            return
        frame = tk.Frame(root)
        frame.grid(row=medication_row[0], column=0, columnspan=4, padx=5, pady=5)
        lbl_medication_text = ttk.Label(frame, text="Название")
        lbl_medication_text.grid(row=0, column=0, padx=5, pady=5)
        entry_medication_text = ttk.Entry(frame)
        entry_medication_text.grid(row=0, column=1, padx=5, pady=5)
        lbl_medication_time_dose = ttk.Label(frame, text="Кол-во")
        lbl_medication_time_dose.grid(row=0, column=2, padx=5, pady=5)
        medication_time_dose_combobox = ttk.Combobox(frame, values=[
            "1 раз в день", "2 раза в день", "3 раза в день", "4 раза в день"
        ])
        medication_time_dose_combobox.grid(row=0, column=3, padx=5, pady=5)
        lbl_medication_course = ttk.Label(frame, text="Как долго принимать")
        lbl_medication_course.grid(row=0, column=4, padx=5, pady=5)
        medication_course_combobox = ttk.Combobox(frame, values=["3 дня", "7 дней", "14 дней"])
        medication_course_combobox.grid(row=0, column=5, padx=5, pady=5)
        medications.append((entry_medication_text, medication_time_dose_combobox, medication_course_combobox))
        medication_row[0] += 1
        add_medication_button.grid(row=medication_row[0] + 1, column=0, columnspan=4, pady=10)
        save_button.grid(row=medication_row[0] + 2, column=0, columnspan=4, pady=10)
        show_table_button.grid(row=medication_row[0] + 3, column=0, columnspan=4, pady=10)

    def show_table():
        search_name = entry_name.get()
        table_window = tk.Toplevel(root)
        table_window.title(f"Таблица для записи с ФИО '{search_name}'")
        table_window.minsize(800, 400)
        tree = ttk.Treeview(table_window, columns=('Лекарство', 'Кол-во', "Как долго принимать", "Дата", "Состояние здоровья"), show='headings')

        table_window.minsize(800, 400)

        tree.heading('Лекарство', text='Лекарство')
        tree.heading('Кол-во', text='Кол-во')
        tree.heading('Как долго принимать', text='Как долго принимать')
        tree.heading('Дата', text='Дата')
        tree.heading('Состояние здоровья', text='Состояние здоровья')

        tree.column('Лекарство', width=150, anchor='center')
        tree.column('Кол-во', width=100, anchor='center')
        tree.column('Как долго принимать', width=100, anchor='center')
        tree.column('Дата', width=100, anchor='center')
        tree.column('Состояние здоровья', width=200, anchor='center')

        tree.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", wraplength=150)

        try:
            if os.path.exists('data.yaml'):
                with open('data.yaml', 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
            else:
                data = None

            found = False
            if data:
                for fio, info in data.items():
                    if fio == search_name:
                        for med in info.get('Лекарства', []):
                            tree.insert('', 'end', values=(med['Название'], med['Кол-во'], med['Как долго принимать'], '', ''))
                        for report in info.get('Отчёты', []):
                            tree.insert('', 'end', values=('', '', '', report['Дата'], report['Состояние здоровья']))
                        found = True
                        break
            if not found:
                print(f"Запись с ФИО '{search_name}' не найдена.")
                messagebox.showinfo("Информация", f"Запись с ФИО '{search_name}' не найдена.")
                table_window.destroy()
            if not data:
                print("Файл data.yaml пуст.")
                messagebox.showinfo("Информация", "Файл data.yaml пуст.")
                table_window.destroy()
        except yaml.YAMLError as exc:
            print(f"Ошибка чтения файла data.yaml:\n{exc}")
            messagebox.showerror("Ошибка", f"Ошибка чтения файла data.yaml:\n{exc}")
            table_window.destroy()

    medication_row = [5]
    lbl_name = ttk.Label(root, text="ФИО")
    lbl_name.grid(row=0, column=0, padx=5, pady=5)
    entry_name = ttk.Entry(root)
    entry_name.grid(row=1, column=0, padx=5, pady=5)
    lbl_orvi = ttk.Label(root, text="Диагноз")
    lbl_orvi.grid(row=0, column=1, padx=5, pady=5)
    entry_orvi = ttk.Entry(root)
    entry_orvi.grid(row=1, column=1, padx=5, pady=5)

    add_medication_button = ttk.Button(root, text="Добавить лекарство", command=add_medication)
    add_medication_button.grid(row=medication_row[0]+1, column=0, columnspan=4, pady=10)

    save_button = ttk.Button(root, text="Сохранить", command=save_to_yaml)
    save_button.grid(row=medication_row[0] + 2, column=0, columnspan=4, pady=10)

    show_table_button = ttk.Button(root, text="Показать таблицу по ФИО", command=show_table)
    show_table_button.grid(row=medication_row[0] + 3, column=0, columnspan=4, pady=10)

    root.mainloop()


create_form()
