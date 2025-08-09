from drf_spectacular.utils import OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

POST_VIEW_SET_DOCS = {
  "tags": ["Посты"],
  "description": (
    "Пост - Основной контент.\n\n"
  )
}

LIST_POSTS_DOCS = {
  "summary":"Получить список постов",
  "description":(
      "- Для этого метода включена пагинация (`PostPagination`).\n"
      "- Получаем все субпосты"
  ),
  "responses":{
      200: OpenApiResponse(description="Список постов с пагинацией"),
  },
  "tags":["Посты"]
}

RETRIEVE_POST_DOCS = {
  "summary": "Получить детали поста",
  "description": (
    "Возвращает данные одного поста по его ID.\n\n"
    "Если субпост с указанным идентификатором не найден - будет возвращена ошибка 404."
  ),
  "responses": {
    200: OpenApiResponse(
      description="Субпост успешно найден",
      examples=[
        OpenApiExample(
          "Пример успешного ответа",
          value={
            "id": 1,
            "post": 10,
            "content": "Текст субпоста",
            "created_at": "2025-08-09T10:15:00Z"
          },
          media_type="application/json",
        )
      ],
    ),
    404: OpenApiResponse(
      description="Субпост не найден",
      examples=[
        OpenApiExample(
          "Пример ошибки 404",
          value={"detail": "Страница не найдена."},
          media_type="application/json",
        )
      ],
    ),
  }
}


CREATE_POST_DOCS = {
  "summary": "Создать один или несколько постов",
  "description": (
    "Метод создаёт новый пост или несколько постов за один запрос.\n\n"
    "- Если передаётся список объектов - происходит массовое создание.\n"
    "- Если объект содержит поле `subposts` (список), создаётся пост с вложенными субпостами в одной транзакции.\n\n"
    "Если данные некорректны - возвращается 400 с деталями ошибок."
  ),
  "request": {"application/json": OpenApiTypes.ANY},
  "examples": [
    OpenApiExample(
      "Одиночный пост",
      value={"title": "Новый пост", "content": "Текст"},
      description="Пример одиночного объекта",
      media_type="application/json",
    ),
    OpenApiExample(
      "Массовое создание постов",
      value=[
        {"title": "Пост 1", "content": "Текст 1"},
        {"title": "Пост 2", "content": "Текст 2"},
      ],
      description="Пример списка объектов для массового создания",
      media_type="application/json",
    ),
    OpenApiExample(
      "С одним субпостом",
      value={
        "title": "Пост с субпостами",
        "content": "Текст",
        "subposts": [{"title": "Субпост 1", "content": "..."}],
      },
      description="Пример объекта с одним вложенным субпостом",
      media_type="application/json",
    ),
    OpenApiExample(
      "С несколькими субпостами",
      value={
        "title": "Пост с субпостами",
        "content": "Текст",
        "subposts": [
          {"title": "Субпост 1", "content": "..."},
          {"title": "Субпост 2", "content": "..."},
        ],
      },
      description="Пример объекта с несколькими вложенными субпостами",
      media_type="application/json",
    ),
  ],
  "responses": {
    201: OpenApiResponse(description="Возвращает созданный объект(объекты)"),
    400: OpenApiResponse(
      description="Ошибка валидации данных",
      examples=[
        OpenApiExample(
          "Ошибка валидации",
          value={"subposts": ["subposts ожидается type: list"]},
          media_type="application/json",
        )
      ],
    ),
  },
  "tags": ["Посты"]
}


UPDATE_POST_DOCS = {
  "summary": "Обновить пост и его субпосты",
  "description": (
    "Метод обновляет существующий пост.\n\n"
    "- Если передан параметр `subposts` (список), можно одновременно "
    "создавать, обновлять и удалять вложенные субпосты в одной транзакции.\n"
    "- Для обновления субпоста необходимо передать его `id` и новые поля.\n"
    "- Для создания субпоста указывать `id` не нужно.\n"
    "- Субпосты, которые не переданы в списке `subposts`, будут удалены.\n\n"
    "**Правила:**\n"
    "- Обновлять и удалять можно только свои посты.\n"
    "- Если указаны `id` субпостов, которые не принадлежат данному посту, вернётся ошибка 403.\n"
    "- Если `subposts` не является списком - ошибка 400."
  ),
  "request": {"application/json": OpenApiTypes.ANY},
  "examples": [
    OpenApiExample(
      "Обновление поста без субпостов",
      value={"title": "Обновлённый заголовок", "content": "Обновлённый текст"},
      description="Пример частичного обновления только полей поста",
      media_type="application/json",
    ),
    OpenApiExample(
      "Обновление поста и добавление нового субпоста",
      value={
        "title": "Пост с новым субпостом",
        "subposts": [
          {"title": "Новый субпост", "content": "Текст субпоста"}
        ]
      },
      description="Создание нового субпоста при обновлении поста",
      media_type="application/json",
    ),
    OpenApiExample(
      "Обновление поста и существующего субпоста",
      value={
        "title": "Пост с обновлённым субпостом",
        "subposts": [
          {"id": 5, "title": "Новое название субпоста", "content": "Обновлённый текст"}
        ]
      },
      description="Обновление уже существующего субпоста по его id",
      media_type="application/json",
    ),
    OpenApiExample(
      "Одновременное обновление, добавление и удаление субпостов",
      value={
        "title": "Комплексное обновление",
        "subposts": [
          {"id": 5, "title": "Обновлённый субпост"},
          {"title": "Новый субпост"}
        ]
      },
      description=(
        "Субпост с id=5 будет обновлён, второй - создан, "
        "а все остальные, не указанные в списке, будут удалены."
      ),
      media_type="application/json",
    ),
  ],
  "responses": {
    200: OpenApiResponse(description="Возвращает обновлённый пост с данными"),
    400: OpenApiResponse(
      description="Ошибка валидации данных",
      examples=[
        OpenApiExample(
          "Некорректный тип поля subposts",
          value={"subposts": ["subposts ожидается type: list"]},
          media_type="application/json",
        )
      ],
    ),
    403: OpenApiResponse(
      description="Доступ запрещён",
      examples=[
        OpenApiExample(
          "Субпост не принадлежит посту",
          value={"detail": "Субпост(ы): (id){7} Не принадлежат посту: 3."},
          media_type="application/json",
        )
      ],
    ),
  },
  "tags": ["Посты"]
}


PARTIAL_UPDATE_POST_DOCS = {
  "summary": "Частично обновить пост и его субпосты",
  "description": (
    "Метод выполняет частичное обновление существующего поста.\n\n"
    "- Если передан параметр `subposts` (список), можно одновременно "
    "создавать, обновлять и удалять вложенные субпосты в одной транзакции.\n"
    "- Для обновления субпоста необходимо передать его `id` и новые поля.\n"
    "- Для создания субпоста указывать `id` не нужно.\n"
    "- Субпосты, которые не переданы в списке `subposts`, будут удалены.\n\n"
    "**Правила:**\n"
    "- Обновлять и удалять можно только свои посты.\n"
    "- Если указаны `id` субпостов, которые не принадлежат данному посту, вернётся ошибка 403.\n"
    "- Если `subposts` не является списком — ошибка 400.\n\n"
    "**Отличие от PUT:**\n"
    "- PATCH позволяет передавать только те поля, которые нужно изменить, "
    "а остальные данные поста и субпостов сохраняются без изменений."
  ),
  "request": {"application/json": OpenApiTypes.ANY},
  "examples": [
    OpenApiExample(
      "Частичное обновление поста без субпостов",
      value={"title": "Обновлённый заголовок"},
      description="Меняем только заголовок поста",
      media_type="application/json",
    ),
    OpenApiExample(
      "Частичное обновление поста и добавление нового субпоста",
      value={
        "subposts": [
          {"title": "Новый субпост", "content": "Текст субпоста"}
        ]
      },
      description="Добавляем новый субпост, не меняя остальные поля поста",
      media_type="application/json",
    ),
    OpenApiExample(
      "Частичное обновление существующего субпоста",
      value={
        "subposts": [
          {"id": 5, "title": "Новое название субпоста"}
        ]
      },
      description="Обновляем только заголовок конкретного субпоста",
      media_type="application/json",
    ),
    OpenApiExample(
      "Частичное обновление с одновременным добавлением и удалением субпостов",
      value={
        "subposts": [
          {"id": 5, "title": "Обновлённый субпост"},
          {"title": "Новый субпост"}
        ]
      },
      description=(
        "Субпост с id=5 будет обновлён, второй — создан, "
        "а остальные, не указанные в списке, будут удалены."
      ),
      media_type="application/json",
    ),
  ],
  "responses": {
    200: OpenApiResponse(description="Возвращает обновлённый пост с данными"),
    400: OpenApiResponse(
      description="Ошибка валидации данных",
      examples=[
        OpenApiExample(
          "Некорректный тип поля subposts",
          value={"subposts": ["subposts ожидается type: list"]},
          media_type="application/json",
        )
      ],
    ),
    403: OpenApiResponse(
      description="Доступ запрещён",
      examples=[
        OpenApiExample(
          "Субпост не принадлежит посту",
          value={"detail": "Субпост(ы): (id){7} Не принадлежат посту: 3."},
          media_type="application/json",
        )
      ],
    ),
  },
  "tags": ["Посты"]
}


DELETE_POST_DOCS = {
  "summary": "Удалить пост",
  "description": (
    "Удаляет пост по указанному ID.\n\n"
    "Пример запроса:\n"
    "`DELETE /api/posts/10/`\n\n"
    "Удалятся все субпосты этого поста"
  ),
  "parameters": [
    OpenApiParameter(
      name="id",
      type=OpenApiTypes.INT,
      location=OpenApiParameter.PATH,
      description="ID поста, который необходимо удалить.",
      examples=[
        OpenApiExample(
          "Пример ID",
          value=10
        )
      ],
    )
  ],
  "responses": {
    204: OpenApiResponse(description="Возвращает удаленный объект"),
    404: OpenApiResponse(
      description="Если нет указанного поста"
    )
  },
  "tags": ["Посты"]
}


ADD_VIEW_DOCS = {
  "summary": "Добавить просмотр поста",
  "description": (
    "Увеличивает счётчик просмотров для поста с указанным ID.\n\n"
    "Пример запроса:\n"
    "`GET /api/posts/10/view`\n\n"
    "Если пост не найден - возвращает 404."
  ),
  "parameters": [
    OpenApiParameter(
      name="id",
      type=OpenApiTypes.INT,
      location=OpenApiParameter.PATH,
      description="ID поста, для которого нужно увеличить счётчик просмотров."
    )
  ],
  "responses": {
    200: OpenApiResponse(description="Просмотр увеличен"),
    404: OpenApiResponse(
      description="Пост не найден",
      examples=[
        OpenApiExample(
          "Not Found Example",
          value={"detail": "Пост с id=123 не найден"}
        )
      ]
    )
  },
  "tags": ["Просмотр"]
}
