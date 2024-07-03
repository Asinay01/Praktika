import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import yaml

def create_form():
    # Create the main window
    root = tk.Tk()
    root.title("Medical Form")

    medications = []

    def clean_lines():
        entry_name.delete(0, 'end')
        entry_orvi.delete(0, 'end')
        for med in medications:
            med[0].delete(0, 'end')
            med[1].set('')  # Сбрасываем комбобокс
            
    def save_to_yaml():
        fio = entry_name.get()
        data = {
            fio: {
                'Заболевание': entry_orvi.get(),
                'Лекарства': [{'Текст': med[0].get(), 'Время и доза': med[1].get()} for med in medications]
            }
        }

        clean_lines()

        with open('data.yaml', 'r+', encoding='utf-8') as file:
            try:
                existing_data = yaml.safe_load(file)
                if existing_data and fio in existing_data:
                    # Полностью заменяем данные о лекарствах
                    existing_data[fio]['Заболевание'] = data[fio]['Заболевание']
                    existing_data[fio]['Лекарства'] = data[fio]['Лекарства']
                    file.seek(0)
                    yaml.dump(existing_data, file, allow_unicode=True)
                else:
                    file.seek(0, 2)
                    yaml.dump(data, file, allow_unicode=True)
                    file.write('\n')
                medication_row[0]+=2
                print(f"Данные для ФИО '{fio}' успешно сохранены в файле data.yaml.")
            except yaml.YAMLError as exc:
                tk.messagebox.showerror("Ошибка", f"Ошибка записи данных в файл data.yaml:\n{exc}")



    def add_medication():
        if len(medications) >= 10:
            return
        
        frame = tk.Frame(root)
        frame.grid(row=medication_row[0], column=0, columnspan=4, padx=5, pady=5)
        
        lbl_medication_text = ttk.Label(frame, text="Текст")
        lbl_medication_text.grid(row=0, column=0, padx=5, pady=5)
        entry_medication_text = ttk.Entry(frame)
        entry_medication_text.grid(row=0, column=1, padx=5, pady=5)

        lbl_medication_time_dose = ttk.Label(frame, text="Время и доза")
        lbl_medication_time_dose.grid(row=0, column=2, padx=5, pady=5)
        medication_time_dose_combobox = ttk.Combobox(frame, values=["1", "2", "4"])
        medication_time_dose_combobox.grid(row=0, column=3, padx=5, pady=5)

        medications.append((entry_medication_text, medication_time_dose_combobox))
        medication_row[0] += 1

        add_medication_button.grid(row=medication_row[0] + 1, column=0, columnspan=4, pady=10)
        save_button.grid(row=medication_row[0] + 2, column=0, columnspan=4, pady=10)
        show_table_button.grid(row=medication_row[0] + 3, column=0, columnspan=4, pady=10)


    def show_table():
        search_name = entry_name.get()
        table_window = tk.Toplevel(root)
        table_window.title(f"Таблица для записи с ФИО '{search_name}'")

        tree = ttk.Treeview(table_window, columns=('Лекарство', 'Время и доза'), show='headings')
        tree.heading('Лекарство', text='Лекарство')
        tree.heading('Время и доза', text='Время и доза')
        tree.pack()

        with open('data.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            found = False
            if data:
                medication_row[0]+=1
                for fio, info in data.items():
                    if fio == search_name:
                        for med in info['Лекарства']:
                            tree.insert('', 'end', values=(med['Текст'], med['Время и доза']))
                        found = True
                        break
            if not found:
                # Вместо messagebox можно использовать простой вывод в консоль или в окно информации
                print(f"Запись с ФИО '{search_name}' не найдена.")
                table_window.destroy()

        # Если файл data.yaml пуст
        if not data:
            # Вместо messagebox можно использовать простой вывод в консоль или в окно информации
            print("Файл data.yaml пуст.")
            table_window.destroy()

        # Обработка ошибки чтения YAML файла
        try:
            yaml.safe_load(file)
        except yaml.YAMLError as exc:
            # Вместо messagebox можно использовать простой вывод в консоль или в окно информации
            print(f"Ошибка чтения файла data.yaml:\n{exc}")
            table_window.destroy()

    # Define labels and entry fields based on the image structure
    medication_row = [5]  # track the current row for medication inputs

    # Row 1: ФИО, ОРВИ
    lbl_name = ttk.Label(root, text="ФИО")
    lbl_name.grid(row=0, column=0, padx=5, pady=5)
    entry_name = ttk.Entry(root)
    entry_name.grid(row=1, column=0, padx=5, pady=5)

    lbl_orvi = ttk.Label(root, text="Диагноз")
    lbl_orvi.grid(row=0, column=1, padx=5, pady=5)
    entry_orvi = ttk.Entry(root)
    entry_orvi.grid(row=1, column=1, padx=5, pady=5)


    # Add medication button
    add_medication_button = ttk.Button(root, text="Добавить лекарство", command=add_medication)
    add_medication_button.grid(row=medication_row[0]+1, column=0, columnspan=4, pady=10)

    # Save button
    save_button = ttk.Button(root, text="Сохранить", command=save_to_yaml)
    save_button.grid(row=medication_row[0] + 2, column=0, columnspan=4, pady=10)

    show_table_button = ttk.Button(root, text="Показать таблицу по ФИО", command=show_table)
    show_table_button.grid(row=medication_row[0] + 3, column=0, columnspan=4, pady=10)

    # Run the application
    root.mainloop()

# Call the function to create the form
create_form()
