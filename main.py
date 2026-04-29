import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Хранилище фильмов
        self.movies = []
        self.filtered_movies = []

        # Путь к файлу JSON
        self.json_file = "movies.json"

        # Загрузка данных из файла при запуске
        self.load_from_json(silent=True)

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы
        self.refresh_table()

    # ------------------ Вспомогательные методы проверки ------------------
    def validate_year(self, year_str):
        """Проверяет, что год — целое число и не отрицательное (разумный диапазон)."""
        try:
            year = int(year_str)
            return 1900 <= year <= 2026  # разумный диапазон
        except ValueError:
            return False

    def validate_rating(self, rating_str):
        """Проверяет, что рейтинг — число от 0 до 10 (возможны дробные)."""
        try:
            rating = float(rating_str)
            return 0.0 <= rating <= 10.0
        except ValueError:
            return False

    # ------------------ Работа с JSON ------------------
    def save_to_json(self):
        """Сохраняет текущий список фильмов в JSON-файл."""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Фильмы сохранены в {self.json_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_from_json(self, silent=False):
        """Загружает фильмы из JSON-файла (если файл существует)."""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.movies = json.load(f)
                if not silent:
                    messagebox.showinfo("Успех", f"Данные загружены из {self.json_file}")
            except Exception as e:
                if not silent:
                    messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        else:
            if not silent:
                messagebox.showinfo("Информация", "Файл не найден. Будет создан новый.")

    # ------------------ Добавление фильма ------------------
    def add_movie(self):
        """Получает данные из полей ввода, проверяет и добавляет фильм."""
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get().strip()
        year_str = self.entry_year.get().strip()
        rating_str = self.entry_rating.get().strip()

        if not title or not genre:
            messagebox.showerror("Ошибка", "Название и жанр не могут быть пустыми.")
            return

        if not self.validate_year(year_str):
            messagebox.showerror("Ошибка", "Год должен быть целым числом от 1900 до 2026.")
            return

        if not self.validate_rating(rating_str):
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом от 0 до 10.")
            return

        movie = {
            "название": title,
            "жанр": genre,
            "год": int(year_str),
            "рейтинг": float(rating_str)
        }
        self.movies.append(movie)
        # Очистить поля ввода
        self.entry_title.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_rating.delete(0, tk.END)

        self.refresh_table()
        messagebox.showinfo("Успех", f"Фильм '{title}' добавлен.")

    # ------------------ Удаление фильма ------------------
    def delete_movie(self):
        """Удаляет выбранный в таблице фильм."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите фильм для удаления.")
            return
        # Получаем название фильма из выделенной строки
        item = selected[0]
        title = self.tree.item(item, "values")[0]
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Удалить фильм '{title}'?"):
            # Удаляем из self.movies по совпадению (по названию + жанру + году)
            # Более надёжно: найти индекс по всем полям
            values = self.tree.item(item, "values")
            for i, m in enumerate(self.movies):
                if (m["название"] == values[0] and
                    m["жанр"] == values[1] and
                    str(m["год"]) == values[2] and
                    str(m["рейтинг"]) == values[3]):
                    del self.movies[i]
                    break
            self.refresh_table()

    # ------------------ Фильтрация ------------------
    def filter_movies(self):
        """Фильтрует фильмы по жанру и/или году (введённым в поля фильтрации)."""
        filter_genre = self.filter_genre_entry.get().strip().lower()
        filter_year = self.filter_year_entry.get().strip()
        # Сброс фильтрованных списка
        self.filtered_movies.clear()

        for movie in self.movies:
            match = True
            if filter_genre and movie["жанр"].lower() != filter_genre:
                match = False
            if filter_year:
                if not filter_year.isdigit():
                    messagebox.showerror("Ошибка", "Год в фильтре должен быть числом.")
                    return
                if movie["год"] != int(filter_year):
                    match = False
            if match:
                self.filtered_movies.append(movie)

        self.refresh_table(filtered=True)

    def clear_filters(self):
        """Очищает поля фильтрации и показывает все фильмы."""
        self.filter_genre_entry.delete(0, tk.END)
        self.filter_year_entry.delete(0, tk.END)
        self.filtered_movies.clear()
        self.refresh_table(filtered=False)

    # ------------------ Отображение таблицы ------------------
    def refresh_table(self, filtered=False):
        """Обновляет таблицу на основе текущего списка (фильтрованного или общего)."""
        # Очистить таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        data_to_show = self.filtered_movies if filtered else self.movies
        for movie in data_to_show:
            self.tree.insert("", tk.END, values=(
                movie["название"],
                movie["жанр"],
                movie["год"],
                f"{movie['рейтинг']:.1f}" if isinstance(movie['рейтинг'], float) else str(movie['рейтинг'])
            ))

    # ------------------ Создание интерфейса ------------------
    def create_widgets(self):
        # --- Рамка для ввода нового фильма ---
        input_frame = ttk.LabelFrame(self.root, text="Добавление фильма", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_title = ttk.Entry(input_frame, width=25)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_genre = ttk.Entry(input_frame, width=20)
        self.entry_genre.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Год выпуска:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_year = ttk.Entry(input_frame, width=10)
        self.entry_year.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_rating = ttk.Entry(input_frame, width=10)
        self.entry_rating.grid(row=1, column=3, padx=5, pady=5)

        btn_add = ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie)
        btn_add.grid(row=2, column=0, columnspan=4, pady=10)

        # --- Рамка для фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_genre_entry = ttk.Entry(filter_frame, width=20)
        self.filter_genre_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Год выпуска:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_year_entry = ttk.Entry(filter_frame, width=10)
        self.filter_year_entry.grid(row=0, column=3, padx=5, pady=5)

        btn_filter = ttk.Button(filter_frame, text="Фильтровать", command=self.filter_movies)
        btn_filter.grid(row=0, column=4, padx=5, pady=5)

        btn_clear = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filters)
        btn_clear.grid(row=0, column=5, padx=5, pady=5)

        # --- Кнопки сохранения/загрузки и удаления ---
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=5)

        btn_save = ttk.Button(action_frame, text="Сохранить в JSON", command=self.save_to_json)
        btn_save.pack(side="left", padx=5)

        btn_load = ttk.Button(action_frame, text="Загрузить из JSON", command=lambda: self.load_from_json(silent=False))
        btn_load.pack(side="left", padx=5)

        btn_delete = ttk.Button(action_frame, text="Удалить выбранный фильм", command=self.delete_movie)
        btn_delete.pack(side="left", padx=5)

        # --- Таблица (Treeview) ---
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("название", "жанр", "год", "рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("название", text="Название")
        self.tree.heading("жанр", text="Жанр")
        self.tree.heading("год", text="Год")
        self.tree.heading("рейтинг", text="Рейтинг")
        self.tree.column("название", width=250)
        self.tree.column("жанр", width=150)
        self.tree.column("год", width=80)
        self.tree.column("рейтинг", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()