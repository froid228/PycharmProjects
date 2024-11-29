
# Config Translator

## Общее описание

Этот проект представляет собой инструмент для трансляции конфигурационных данных, представленных в формате XML, в структуру, используемую в учебных конфигурационных языках. Программа позволяет обрабатывать элементы конфигурации с типами данных: строки, числа и словари. Тестируются различные конфигурации, в том числе с ошибками в формате XML.

## Функциональность

Программа выполняет следующие задачи:
- Парсит XML-файлы с конфигурацией.
- Преобразует значения в соответствующие типы данных (строки, числа, словари).
- Отображает обработанные данные в виде конфигурационного списка.
- Проверяет корректность XML и выводит ошибки в случае некорректных данных.
- Проводит тесты с разными конфигурациями, включая валидные и некорректные XML.

## Структура файлов

```
.
├── translator.py        # Главный скрипт для трансляции XML в конфигурацию
├── test_script.py       # Скрипт для тестирования программы
├── test1.xml            # Пример XML для теста 1 (веб-сервер)
├── test2.xml            # Пример XML для теста 2 (умный дом)
├── test_invalid.xml     # Пример некорректного XML
└── README.md            # Этот файл с описанием
```

## Пример XML

### Пример 1: Веб-сервер

```xml
<dictionary>
    <entry>
        <name>host</name>
        <value type="string">localhost</value>
    </entry>
    <entry>
        <name>port</name>
        <value type="number">8080</value>
    </entry>
    <entry>
        <name>routes</name>
        <value type="dictionary">{'home': '/', 'about': '/about'}</value>
    </entry>
</dictionary>
```

### Пример 2: Умный дом

```xml
<dictionary>
    <entry>
        <name>temperature</name>
        <value type="number">22</value>
    </entry>
    <entry>
        <name>lighting</name>
        <value type="dictionary">{'living_room': 'on', 'bedroom': 'off'}</value>
    </entry>
    <entry>
        <name>security</name>
        <value type="dictionary">{'alarm': 'armed', 'cameras': 'active'}</value>
    </entry>
</dictionary>
```

### Пример 3: Некорректный XML

```xml
<dictionary>
    <entry>
        <name>invalid</name>
        <value>missing type attribute</value>
    </entry>
</dictionary>
```

## Запуск программы

1. Убедитесь, что у вас установлен Python 3.x.
2. Сохраните файлы в одну директорию.
3. Запустите скрипт для тестирования с помощью команды:

   ```bash
   python test_script.py
   ```

## Результаты тестирования

После выполнения программы вы увидите результаты тестов, например:

```plaintext
=== Тест 1: Веб-сервер ===
Результат:
 [
  host => localhost,
  port => 8080,
  routes => {'home': '/', 'about': '/about'},
]

=== Тест 2: Умный дом ===
Результат:
 [
  temperature => 22,
  lighting => {'living_room': 'on', 'bedroom': 'off'},
  security => {'alarm': 'armed', 'cameras': 'active'},
]

=== Тест 3: Некорректный XML ===
Ошибка:
 Отсутствует атрибут 'type' у элемента <value> для invalid.
```

