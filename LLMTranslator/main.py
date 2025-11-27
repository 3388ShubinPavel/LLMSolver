import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from config import UI_MESSAGES
from modules.formalizer import Formalizer
from modules.resolution_engine import ResolutionEngine
from modules.explainer import Explainer

class LogicProverSystem:
    """
    ГЛАВНАЯ СИСТЕМА: Объединяет все три модуля согласно архитектуре из задания
    """

    def __init__(self, root):
        self.root = root
        self.setup_gui()

        # Инициализация модулей ТОЧНО как в задании
        self.formalizer = Formalizer()      # Модуль 1: LLM-формализатор
        self.prover = ResolutionEngine()    # Модуль 2: Движок резолюций
        self.explainer = Explainer()        # Модуль 3: LLM-объяснятор

        self.is_processing = False

    def setup_gui(self):
        """Настраивает графический интерфейс"""
        self.root.title(UI_MESSAGES["title"])
        self.root.geometry("900x700")

        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Заголовок и описание архитектуры
        ttk.Label(main_frame, text=UI_MESSAGES["title"],
                  font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        desc_text = scrolledtext.ScrolledText(main_frame, width=100, height=4, wrap=tk.WORD)
        desc_text.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        desc_text.insert(tk.END, UI_MESSAGES["description"])
        desc_text.config(state=tk.DISABLED)

        # Поле ввода
        ttk.Label(main_frame, text=UI_MESSAGES["input_label"],
                  font=("Arial", 11, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))

        self.input_text = scrolledtext.ScrolledText(main_frame, width=100, height=5, wrap=tk.WORD)
        self.input_text.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        self.input_text.insert(tk.END, UI_MESSAGES["examples"][0])

        # Быстрые примеры из задания
        example_frame = ttk.LabelFrame(main_frame, text="📋 Примеры из задания", padding="5")
        example_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        for i, example in enumerate(UI_MESSAGES["examples"]):
            btn = ttk.Button(example_frame, text=f"Пример {i+1}",
                             command=lambda e=example: self.load_example(e))
            btn.grid(row=0, column=i, padx=5)

        # Кнопка доказательства
        self.prove_btn = ttk.Button(main_frame, text="🧠 Начать логическое доказательство",
                                    command=self.start_proof_process)
        self.prove_btn.grid(row=5, column=0, columnspan=2, pady=15)

        # Прогресс
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов к работе")
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)

        # Вкладки результатов для каждого модуля
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Вкладка Модуля 1
        formalize_frame = ttk.Frame(notebook, padding="10")
        self.formalize_text = scrolledtext.ScrolledText(formalize_frame, width=100, height=8, wrap=tk.WORD)
        self.formalize_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(formalize_frame, text="🔍 Модуль 1: Формализация")

        # Вкладка Модуля 2
        proof_frame = ttk.Frame(notebook, padding="10")
        self.proof_text = scrolledtext.ScrolledText(proof_frame, width=100, height=8, wrap=tk.WORD)
        self.proof_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(proof_frame, text="⚡ Модуль 2: Доказательство")

        # Вкладка Модуля 3
        explain_frame = ttk.Frame(notebook, padding="10")
        self.explain_text = scrolledtext.ScrolledText(explain_frame, width=100, height=10, wrap=tk.WORD)
        self.explain_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(explain_frame, text="🎓 Модуль 3: Объяснение")

        # Настройка расширения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)

    def load_example(self, example):
        """Загружает пример из задания в поле ввода"""
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(tk.END, example)

    def start_proof_process(self):
        """Запускает процесс доказательства в отдельном потоке"""
        if self.is_processing:
            return

        self.is_processing = True
        self.prove_btn.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="Начинаю процесс доказательства...")

        # Очистка предыдущих результатов
        for widget in [self.formalize_text, self.proof_text, self.explain_text]:
            widget.delete(1.0, tk.END)

        thread = threading.Thread(target=self.run_proof_process)
        thread.daemon = True
        thread.start()

    def run_proof_process(self):
        """Запускает полный процесс трех модулей согласно архитектуре из задания"""
        try:
            input_text = self.input_text.get(1.0, tk.END).strip()

            # === МОДУЛЬ 1: LLM-формализатор ===
            self.update_status("🔍 Модуль 1: Преобразую естественный язык в логику...")
            formulas = self.formalizer.formalize(input_text)
            self.update_text(self.formalize_text,
                         "🤖 LLM-ФОРМАЛИЗАТОР: Перевод с русского на язык логики\n\n"
                         f"ВХОД: {input_text}\n\n"
                         "ВЫХОД (формальный язык):\n" +
                         "\n".join(f"• {formula}" for formula in formulas))
            time.sleep(1)

            # === МОДУЛЬ 2: Движок резолюций ===
            self.update_status("⚡ Модуль 2: Выполняю строгое доказательство...")
            proved, proof_steps = self.prover.prove(formulas)

            proof_result = "✅ ДОКАЗАТЕЛЬСТВО УСПЕШНО" if proved else "❌ ДОКАЗАТЕЛЬСТВО НЕ НАЙДЕНО"
            proof_content = f"🧮 ДВИЖОК РЕЗОЛЮЦИЙ: Строгое доказательство\n\n"
            proof_content += f"РЕЗУЛЬТАТ: {proof_result}\n\n"
            proof_content += "ШАГИ ДОКАЗАТЕЛЬСТВА:\n" + "\n".join(f"• {step}" for step in proof_steps)

            self.update_text(self.proof_text, proof_content)
            time.sleep(1)

            # === МОДУЛЬ 3: LLM-объяснятор ===
            self.update_status("🎓 Модуль 3: Объясняю доказательство на естественном языке...")
            explanation = self.explainer.explain_proof(proof_steps, input_text, proved)

            explain_content = f"🎓 LLM-ОБЪЯСНЯТОР: Перевод с языка логики на русский\n\n"
            explain_content += explanation

            self.update_text(self.explain_text, explain_content)

            self.update_status("✅ Процесс завершен! Все модули отработали согласно архитектуре")

        except Exception as e:
            self.update_status(f"❌ Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

        finally:
            self.complete_process()

    def update_status(self, message):
        """Обновляет статус из основного потока"""
        def update():
            self.status_label.config(text=message)
            print(message)
        self.root.after(0, update)

    def update_text(self, text_widget, content):
        """Обновляет текстовый виджет из основного потока"""
        def update():
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, content)
        self.root.after(0, update)

    def complete_process(self):
        """Завершает процесс"""
        def update():
            self.is_processing = False
            self.prove_btn.config(state='normal')
            self.progress.stop()
        self.root.after(0, update)

def main():
    root = tk.Tk()
    app = LogicProverSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()