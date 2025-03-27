import json
import random
from tkinter import *
from tkinter import messagebox, ttk
from tkinter import ttk


class VocabularyApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Учим английские слова")
        self.master.geometry("400x300")
        # показывать перевод да/нет
        self.show_translation = True

        # Загрузка словаря
        self.words = self.load_words()
        self.selected_words = []

        # Создание GUI элементов
        self.create_widgets()

    def create_widgets(self):
        # Поля для ввода слов
        Label(self.master, text="Английское слово:").pack(pady=5)
        self.eng_entry = Entry(self.master, width=30)
        self.eng_entry.pack()

        Label(self.master, text="Русский перевод:").pack(pady=5)
        self.ru_entry = Entry(self.master, width=30)
        self.ru_entry.pack()

        # Добавляем обработчики горячих клавиш для полей ввода
        self.setup_clipboard_shortcuts(self.eng_entry)
        self.setup_clipboard_shortcuts(self.ru_entry)


        # Кнопка добавления
        Button(self.master, text="Добавить слово", command=self.add_word).pack(pady=10)

        # Кнопки для других функций
        Button(self.master, text="Просмотр слов", command=self.show_words_window).pack(pady=5)
        Button(self.master, text="Учить слова", command=self.start_learning).pack(pady=5)

    def setup_clipboard_shortcuts(self, widget):
        # Привязка горячих клавиш для копирования/вставки
        widget.bind("<Control-KeyPress>", self.handle_ctrl_shortcut)

    def handle_ctrl_shortcut(self, event):
        # Проверяем код физической клавиши и состояние Ctrl
        if event.state & 0x0004:  # Проверка что Ctrl нажат
            if event.keycode == 86:  # Физическая клавиша V (английская) / М (русская)
                self.paste_text(event)
                return "break"
            elif event.keycode == 67:  # Физическая клавиша C (английская) / С (русская)
                self.copy_text(event)
                return "break"


    def copy_text(self, event):
        event.widget.event_generate("<<Copy>>")

    def paste_text(self, event):
        event.widget.event_generate("<<Paste>>")


    def load_words(self):
        try:
            with open('words.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_words(self):
        with open('words.json', 'w') as f:
            json.dump(self.words, f, ensure_ascii=False)

    def add_word(self):
        eng = self.eng_entry.get().strip().lower()
        ru = self.ru_entry.get().strip().lower()

        if eng and ru:
            self.words[eng] = ru
            self.save_words()
            self.eng_entry.delete(0, END)
            self.ru_entry.delete(0, END)
            messagebox.showinfo("Успех", "Слово добавлено!")
        else:
            messagebox.showerror("Ошибка", "Заполните оба поля!")

    def show_words_window(self):
        words_window = Toplevel(self.master)
        words_window.title("Выбор слов для изучения")

        # Основной контейнер
        main_frame = Frame(words_window)
        main_frame.pack(padx=10, pady=10, fill=BOTH, expand=True)

        # Создаем Canvas и Scrollbar
        canvas = Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)

        # Настройка прокрутки
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

        # Привязка колеса мыши ко всему окну
        def on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                # Для Linux
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")

        # Привязка событий для разных платформ
        words_window.bind("<MouseWheel>", on_mousewheel)
        words_window.bind("<Button-4>", on_mousewheel)
        words_window.bind("<Button-5>", on_mousewheel)

        # Добавление чекбоксов
        self.check_vars = {}
        self.check_widgets = []
        for eng, ru in self.words.items():
            var = BooleanVar()
            text = f"{eng} - {ru}" if self.show_translation else f"{eng} - ****"
            cb = Checkbutton(scrollable_frame,
                             text=text,
                             variable=var,
                             anchor="w",
                             width=30)
            cb.pack(fill="x", pady=2)
            self.check_widgets.append((cb, eng, ru))
            self.check_vars[eng] = var

        # Фрейм для кнопок
        button_frame = Frame(words_window)
        button_frame.pack(pady=10)

        Button(button_frame,
               text="👁️",
               command=lambda: self.toggle_translation(words_window),
               width=5).pack(side=LEFT, padx=5)

        Button(button_frame,
               text="Сохранить",
               command=lambda: self.save_selection(words_window)).pack(side=LEFT, padx=5)

    def toggle_translation(self, window):
        self.show_translation = not self.show_translation
        for cb, eng, ru in self.check_widgets:
            new_text = f"{eng} - {ru}" if self.show_translation else f"{eng} - ****"
            cb.config(text=new_text)
        window.update()


    def save_selection(self, window):
        self.selected_words = [
            eng for eng, var in self.check_vars.items() if var.get()
        ]
        window.destroy()
        self.check_widgets = []  # Очищаем список виджетов
        messagebox.showinfo("Выбор сохранен", f"Выбрано слов: {len(self.selected_words)}")


    def start_learning(self):
        if not self.selected_words:
            messagebox.showerror("Ошибка", "Сначала выберите слова для изучения!")
            return

        # Создаем окно обучения
        learn_window = Toplevel(self.master)
        learn_window.title("Режим обучения")

        self.current_word = None
        self.correct_answer = None
        self.buttons = []

        # Элементы интерфейса
        self.word_label = Label(learn_window, text="", font=('Arial', 14))
        self.word_label.pack(pady=20)

        buttons_frame = Frame(learn_window)
        buttons_frame.pack()

        # Создаем 6 кнопок в два столбца
        for i in range(6):
            btn = Button(buttons_frame, text="", width=20,
                         command=lambda idx=i: self.check_answer(idx))
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5)
            self.buttons.append(btn)

        self.next_word(learn_window)

    def next_word(self, window):
        if not self.selected_words:
            messagebox.showinfo("Конец", "Вы изучили все выбранные слова!")
            window.destroy()
            return

        self.current_word = random.choice(self.selected_words)
        self.selected_words.remove(self.current_word)
        self.word_label.config(text=self.current_word)

        # Генерируем варианты ответов
        correct = self.words[self.current_word]
        wrongs = [v for k, v in self.words.items()
                  if k != self.current_word and v != correct]
        random.shuffle(wrongs)

        answers = [correct] + wrongs[:5]
        random.shuffle(answers)
        self.correct_answer = answers.index(correct)

        # Обновляем текст кнопок
        for i, btn in enumerate(self.buttons):
            btn.config(text=answers[i] if i < len(answers) else "", bg='SystemButtonFace')

    def check_answer(self, button_idx):
        if button_idx == self.correct_answer:
            self.buttons[button_idx].config(bg='green')
            self.master.after(1000, self.next_word, self.master.winfo_children()[-1])
        else:
            self.buttons[button_idx].config(bg='red')


if __name__ == "__main__":
    root = Tk()
    app = VocabularyApp(root)
    root.mainloop()