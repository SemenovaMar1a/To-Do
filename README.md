# 📝 To-Do App на FastAPI

Это простой To-Do веб-приложение с возможностью регистрации, авторизации и управления задачами. Приложение разработано на **FastAPI** с использованием **SQLite** и поддерживает как **HTML-интерфейс**, так и **JSON-API** (доступен через Swagger UI).

## 🔧 Стек технологий

- **FastAPI** — backend-фреймворк
- **SQLModel** — ORM и база данных SQLite
- **Jinja2** — шаблонизатор для HTML
- **OAuth2** — аутентификация с использованием токенов и поддержки куки
- **Swagger UI** — автоматическая документация API

## 📌 Функциональность

- Вход по имени пользователя и паролю
- Регистрация по имени, емайлу и паролю
- Изменение данных пользователя
- Удаление пользователя
- Получение токена доступа через OAuth2 (в заголовке или куках)
- Просмотр и управление задачами:
  - создание
  - удаление
  - пометка как завершённой
  - редактирование
- HTML-страницы для входа, регистрации и просмотра задач
- JSON-эндпоинты, полностью совместимые с OpenAPI

## 📁 Структура проекта

```bash
.
├── app/
│   ├── main.py                # Точка входа
│   ├── models/                # SQLModel модели User и Task
│   ├── routers/               # Роуты приложения
│   ├── services/              # Бизнес-логика (например, authenticate_user)
│   ├── core/                  # Настройки и утилиты безопасности
│   ├── templates/             # HTML-шаблоны
├── database.py                # Подключение к SQLite
├── requirements.txt
└── README.md
```

## 📄 Примеры моделей

**Task**
```python
class TaskBase(SQLModel):
    """Базовая модель задачи"""
    title: str = Field(max_length=100, index=True)
    description: str | None = Field(default=None)

class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
```

**User**
```python
class UserBase(SQLModel):
    """Базовая модель пользователя"""
    username: str = Field(max_length=50, index=True, unique=True)
    email: str = Field(max_length=100, unique=True)
    role: Role = Field(default=Role.USER)

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
```

## 🔐 Аутентификация

- Токен можно получить через `/token` (OAuth2PasswordRequestForm).
- Также реализована авторизация через HTML-форму (`/login`), с сохранением токена в **HTTP-only куки**.
- Поддерживается получение токена как из заголовка `Authorization`, так и из куки.

Пример запроса на получение токена:

```bash
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=&username=yourname&password=yourpass&scope=&client_id=&client_secret=
```

## 🚀 Запуск проекта

1. Клонируй репозиторий:

```bash
git clone https://github.com/SemenovaMar1a/To-Do
cd To-Do
```

2. Установи зависимости:

```bash
pip install -r requirements.txt
```

3. Запусти приложение:

```bash
uvicorn app.main:app --reload
```

4. Перейди в браузере по адресу:  
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)  
   - HTML-интерфейс: [http://localhost:8000/login](http://localhost:8000/login)

## 📌 Примечания

- Все задачи привязаны к пользователям (по `user_id`).
- Удаление пользователя приведёт к каскадному удалению всех его задач.
- Без авторизации доступ к задачам будет ограничен.

## ✅ Планы по доработке

- Добавить пагинацию и фильтрацию задач
- Подключить фронтенд-фреймворк (например, Vue или React)
