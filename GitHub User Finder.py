import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Файл для сохранения избранных
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Загрузка избранных в список
        self.refresh_favorites_list()
    
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Поле поиска
        ttk.Label(main_frame, text="Поиск пользователя GitHub:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.search_entry = ttk.Entry(main_frame, width=40, font=("Arial", 10))
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_user())
        
        # Кнопка поиска
        self.search_button = ttk.Button(main_frame, text="Поиск", command=self.search_user)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Панель вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Вкладка результатов поиска
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Результаты поиска")
        
        # Список результатов поиска
        search_scroll = ttk.Scrollbar(self.search_frame)
        search_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.search_listbox = tk.Listbox(self.search_frame, yscrollcommand=search_scroll.set, font=("Arial", 9))
        self.search_listbox.pack(fill=tk.BOTH, expand=True)
        search_scroll.config(command=self.search_listbox.yview)
        
        # Контекстное меню для результатов поиска
        self.search_menu = tk.Menu(self.search_listbox, tearoff=0)
        self.search_menu.add_command(label="Добавить в избранное", command=self.add_to_favorites_from_search)
        self.search_menu.add_command(label="Показать профиль", command=self.show_user_profile)
        self.search_listbox.bind("<Button-3>", self.show_search_menu)
        
        # Вкладка избранного
        self.favorites_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.favorites_frame, text="Избранное")
        
        # Список избранного
        fav_scroll = ttk.Scrollbar(self.favorites_frame)
        fav_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.favorites_listbox = tk.Listbox(self.favorites_frame, yscrollcommand=fav_scroll.set, font=("Arial", 9))
        self.favorites_listbox.pack(fill=tk.BOTH, expand=True)
        fav_scroll.config(command=self.favorites_listbox.yview)
        
        # Контекстное меню для избранного
        self.fav_menu = tk.Menu(self.favorites_listbox, tearoff=0)
        self.fav_menu.add_command(label="Удалить из избранного", command=self.remove_from_favorites)
        self.fav_menu.add_command(label="Показать профиль", command=self.show_user_profile_fav)
        self.favorites_listbox.bind("<Button-3>", self.show_fav_menu)
        
        # Кнопки управления избранным
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Обновить избранное", command=self.refresh_favorites_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить всё избранное", command=self.clear_all_favorites).pack(side=tk.LEFT, padx=5)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
    
    def load_favorites(self):
        """Загрузка избранных пользователей из JSON файла"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_favorites(self):
        """Сохранение избранных пользователей в JSON файл"""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
    
    def search_user(self):
        """Поиск пользователя на GitHub"""
        username = self.search_entry.get().strip()
        
        # Проверка на пустое поле
        if not username:
            messagebox.showwarning("Ошибка", "Поле поиска не должно быть пустым!")
            return
        
        self.status_var.set(f"Поиск пользователя: {username}...")
        self.search_button.config(state=tk.DISABLED)
        
        try:
            # Запрос к GitHub API
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url)
            
            if response.status_code == 200:
                user_data = response.json()
                self.display_search_results([user_data])
                self.status_var.set(f"Найден пользователь: {user_data['login']}")
            elif response.status_code == 404:
                messagebox.showinfo("Не найдено", f"Пользователь '{username}' не найден")
                self.status_var.set("Пользователь не найден")
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
                self.status_var.set(f"Ошибка: {response.status_code}")
        
        except requests.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к GitHub API: {str(e)}")
            self.status_var.set("Ошибка соединения")
        
        finally:
            self.search_button.config(state=tk.NORMAL)
    
    def display_search_results(self, users):
        """Отображение результатов поиска в списке"""
        self.search_listbox.delete(0, tk.END)
        
        for user in users:
            # Форматирование информации о пользователе
            user_info = f"@{user['login']} | Имя: {user.get('name', 'Не указано')} | Репозитории: {user['public_repos']} | Подписчики: {user['followers']}"
            self.search_listbox.insert(tk.END, user_info)
            # Сохраняем данные пользователя в атрибуты элемента списка
            self.search_listbox.itemconfig(tk.END, user_data=user)
    
    def add_to_favorites_from_search(self):
        """Добавление выбранного пользователя из результатов поиска в избранное"""
        selection = self.search_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для добавления в избранное")
            return
        
        user_data = self.search_listbox.itemconfig(selection[0], 'user_data')[4]
        
        # Проверка, не добавлен ли уже пользователь
        if any(fav['login'] == user_data['login'] for fav in self.favorites):
            messagebox.showinfo("Информация", f"Пользователь {user_data['login']} уже в избранном")
            return
        
        # Сохранение в избранное
        favorite_user = {
            'login': user_data['login'],
            'name': user_data.get('name', 'Не указано'),
            'html_url': user_data['html_url'],
            'avatar_url': user_data['avatar_url'],
            'public_repos': user_data['public_repos'],
            'followers': user_data['followers'],
            'following': user_data['following'],
            'added_date': datetime.now().isoformat()
        }
        
        self.favorites.append(favorite_user)
        self.save_favorites()
        self.refresh_favorites_list()
        self.status_var.set(f"Пользователь {user_data['login']} добавлен в избранное")
    
    def refresh_favorites_list(self):
        """Обновление списка избранного"""
        self.favorites_listbox.delete(0, tk.END)
        
        for user in self.favorites:
            user_info = f"@{user['login']} | {user.get('name', 'Не указано')} | Репозитории: {user.get('public_repos', 0)}"
            self.favorites_listbox.insert(tk.END, user_info)
            self.favorites_listbox.itemconfig(tk.END, user_data=user)
        
        self.status_var.set(f"В избранном: {len(self.favorites)} пользователей")
    
    def remove_from_favorites(self):
        """Удаление выбранного пользователя из избранного"""
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return
        
        user_data = self.favorites_listbox.itemconfig(selection[0], 'user_data')[4]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {user_data['login']} из избранного?"):
            self.favorites = [user for user in self.favorites if user['login'] != user_data['login']]
            self.save_favorites()
            self.refresh_favorites_list()
            self.status_var.set(f"Пользователь {user_data['login']} удален из избранного")
    
    def clear_all_favorites(self):
        """Очистка всего избранного"""
        if self.favorites and messagebox.askyesno("Подтверждение", "Очистить весь список избранного?"):
            self.favorites = []
            self.save_favorites()
            self.refresh_favorites_list()
            self.status_var.set("Избранное очищено")
    
    def show_user_profile(self):
        """Показ профиля выбранного пользователя из результатов поиска"""
        selection = self.search_listbox.curselection()
        if not selection:
            return
        
        user_data = self.search_listbox.itemconfig(selection[0], 'user_data')[4]
        self.show_profile_window(user_data)
    
    def show_user_profile_fav(self):
        """Показ профиля выбранного пользователя из избранного"""
        selection = self.favorites_listbox.curselection()
        if not selection:
            return
        
        user_data = self.favorites_listbox.itemconfig(selection[0], 'user_data')[4]
        self.show_profile_window(user_data)
    
    def show_profile_window(self, user_data):
        """Отображение окна с подробной информацией о пользователе"""
        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"Профиль: {user_data['login']}")
        profile_window.geometry("400x500")
        
        # Информация о пользователе
        info_text = f"""
Логин: {user_data['login']}
Имя: {user_data.get('name', 'Не указано')}
Компания: {user_data.get('company', 'Не указано')}
Местоположение: {user_data.get('location', 'Не указано')}
Email: {user_data.get('email', 'Не указано')}
Био: {user_data.get('bio', 'Не указано')}
Публичные репозитории: {user_data.get('public_repos', 0)}
Подписчики: {user_data.get('followers', 0)}
Подписки: {user_data.get('following', 0)}
Дата регистрации: {user_data.get('created_at', 'Не указано')[:10]}
URL профиля: {user_data.get('html_url', 'Не указано')}
        """
        
        text_widget = tk.Text(profile_window, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
        
        # Кнопка открытия в браузере
        if 'html_url' in user_data:
            ttk.Button(profile_window, text="Открыть в браузере", 
                      command=lambda: self.open_browser(user_data['html_url'])).pack(pady=10)
    
    def open_browser(self, url):
        """Открытие URL в браузере"""
        import webbrowser
        webbrowser.open(url)
    
    def show_search_menu(self, event):
        """Показ контекстного меню для результатов поиска"""
        if self.search_listbox.curselection():
            self.search_menu.post(event.x_root, event.y_root)
    
    def show_fav_menu(self, event):
        """Показ контекстного меню для избранного"""
        if self.favorites_listbox.curselection():
            self.fav_menu.post(event.x_root, event.y_root)

def main():
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()