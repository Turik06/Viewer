# Universal File Viewer

Универсальный просмотрщик файлов на PyQt6. Позволяет просматривать текстовые файлы, изображения, аудио/видео, документы (PDF, DOCX), таблицы (CSV, TSV, XLSX) и содержимое архивов (ZIP, TAR, GZ) — всё в одном окне.

## Системные требования

- **ОС:** Ubuntu LTS (20.04 / 22.04 / 24.04)
- **Python:** 3.10 или новее
- **Qt мультимедиа** (для воспроизведения аудио и видео):
  ```bash
  sudo apt update
  sudo apt install -y libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad gstreamer1.0-libav
  ```

## Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone <url-репозитория>
   cd project
   ```

2. **Создайте виртуальное окружение и активируйте его:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

## Запуск

```bash
python main.py
```

Приложение откроет окно с файловым деревом справа и панелью просмотра слева. Щёлкните по файлу в дереве, чтобы открыть его во встроенном вьюере.

## Поддерживаемые форматы

| Категория          | Расширения                                                                 |
|--------------------|---------------------------------------------------------------------------|
| Текст и код        | `.txt`, `.md`, `.py`, `.cpp`, `.h`, `.php`, `.sql`, `.sh`                 |
| Конфигурации       | `.json`, `.xml`, `.yaml`, `.yml`, `.ini`, `Dockerfile`, `Makefile`        |
| Изображения        | `.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.svg`, `.webp`, `.tiff`, `.ico` |
| Аудио / Видео      | `.mp4`, `.avi`, `.mkv`, `.mov`, `.mp3`, `.wav`, `.flac`, `.ogg`           |
| Документы Word     | `.docx`                                                                   |
| Документы PDF      | `.pdf`                                                                    |
| Таблицы            | `.csv`, `.tsv`, `.xlsx`                                                   |
| Архивы             | `.zip`, `.tar`, `.gz`, `.tar.gz`                                          |

## Структура проекта

```
project/
├── main.py              # Точка входа в приложение
├── main_window.py       # Главное окно (QMainWindow + QSplitter)
├── requirements.txt     # Зависимости Python
├── README.md            # Документация
└── viewers/             # Пакет вьюеров
    ├── __init__.py      # Экспорт модулей
    ├── base.py          # Абстрактный базовый класс BaseViewerWidget
    ├── factory.py       # Фабрика/реестр ViewerFactory
    ├── text.py          # Просмотр текстовых файлов и кода
    ├── image.py         # Просмотр изображений
    ├── media.py         # Воспроизведение аудио/видео
    ├── document.py      # Просмотр PDF и DOCX
    ├── tables.py        # Просмотр таблиц (CSV, TSV, XLSX)
    └── archives.py      # Просмотр содержимого архивов
```

## Архитектура

- **Layout:** Горизонтальный `QSplitter` — слева панель просмотра (`QStackedWidget`), справа файловое дерево (`QTreeView` + `QFileSystemModel` + `QSortFilterProxyModel`).
- **Паттерн Registry / Strategy:** `ViewerFactory` сопоставляет расширения файлов с классами-вьюерами. Все вьюеры наследуются от `BaseViewerWidget`.
- **Без внешних процессов:** Никаких вызовов `os.system()` или `subprocess`. Всё отображается строго внутри виджетов PyQt6.

## Лицензия

Учебный проект.
