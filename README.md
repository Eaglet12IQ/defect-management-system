# defect-management-system
Это веб-приложение для управления дефектами на строительных объектах. Оно состоит из бэкенда на FastAPI и фронтенда на Vue.js.

## Предварительные требования
- Python 3.8 или выше
- Node.js 16 или выше
- PostgreSQL (установленный и запущенный)

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd defect-management-system
```

### 2. Настройка базы данных
- Установите PostgreSQL и создайте базу данных `defect`.
- По умолчанию используется подключение: `postgresql://postgres:12345@localhost:5432/defect`

### 3. Настройка бэкенда
```bash
cd backend
pip install -r req.txt
alembic upgrade head
```

### 4. Настройка фронтенда
```bash
cd ../frontend
npm install
```

### 5. Запуск приложения
Запустите бэкенд и фронтенд в отдельных терминалах.

#### Бэкенд:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Бэкенд будет доступен по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

#### Фронтенд:
```bash
cd frontend
npm run dev
```
Фронтенд будет доступен по адресу: http://localhost:5173

## Структура проекта
- `backend/` - Бэкенд на FastAPI
- `frontend/` - Фронтенд на Vue.js
- `backend/app/models/` - Модели базы данных
- `backend/app/api/endpoints/` - API эндпоинты
- `frontend/src/views/` - Страницы фронтенда
- `frontend/src/components/` - Компоненты Vue.js
