# TODO:
- Пропадают теги (Synt. structure of anchor, co)
- пропадают картинки (перехардкодить base\_url)

- get_search_info
{
    'semantic_roles': [{'label': 'Acc', 'id': 2}, ...]
    'semantic_roles': {'Acc': 2},
}

- sqlmodel + alembic
- tag name length = 160
- trailing slashes
- sqlite alter example
- add item + tag example

+ auto crud
+ json schema test
+ __tablename__
+ less

ИНСТРУКЦИЯ КАК ЗАПУСТИТЬ ФРОНТ
Если используется докер контейнер:
```bash
$ make ui_build
$ make ui_bash
$ yarn
$ yarn serve
```

Если не используется докер контейнер необходимо поставить yarn
```bash
$ cd ui
$ yarn
$ yarn serve
```

