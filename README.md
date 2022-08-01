# Yatube, блог-платформа, финальная версия

## Это блог-платформа для публикации постов, сгруппированных по темам и комментариев к ним

### Как запустить проект:

Достаточно выполнить команду

```
docker-compose up
```

из директории /infra

Есть более сложный путь.

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/robky/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Загрузить данные из файлов csv в базу данных:

```
python manage.py filldb
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

## Стек технологий

- python 3.7
- django
