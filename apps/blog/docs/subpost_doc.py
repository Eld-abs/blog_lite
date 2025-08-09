from drf_spectacular.utils import OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.blog.serializers import SubPostSerializer

SUBPOST_VIEW_SET_DOCS = {
  "tags": ["Субпосты"],
  "description": (
    "Субпост - это дополнительный контент, связанный с основным постом.\n\n"
    "Данный ViewSet позволяет получать список субпостов и создавать новые.\n"
    "При создании субпоста проверяется, что текущий пользователь является владельцем поста.\n\n"
    "**Доступные методы:**\n"
    "- `GET /subposts/` - список субпостов (с пагинацией)\n"
    "- `POST /subposts/` - создание нового субпоста"
  )
}

LIST_SUBPOSTS_DOCS = {
  "summary": "Список субпостов",
  "description": (
    "Возвращает список всех постов.\n\n"
    "Результат может быть отфильтрован и пагинирован.\n"
    "Каждый элемент содержит подробную информацию о посте."
  ),
  "responses": {
    200: OpenApiResponse(
      description="Возвращается все субпосты",
      examples=[
        OpenApiExample(
          name="Пример успешного ответа",
          value={
            "count": 123,
            "next": "http://api.example.org/accounts/?page=4",
            "previous": "http://api.example.org/accounts/?page=2",
            "results": [
              {
                "id": 0,
                "title": "string",
                "author_display": "string",
                "body": "string",
                "create_at": "2025-08-09T07:05:11.554Z",
                "update_at": "2025-08-09T07:05:11.554Z",
                "views_count": 2147483647
              }
            ]
          },
          media_type="application/json"
        )
      ]
    )
  }
}

RETRIEVE_SUBPOST_DOCS = {
  "summary": "Получить детали субпоста",
  "description": (
    "Возвращает данные одного субпоста по его ID.\n\n"
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

CREATE_SUBPOST_DOCS = {
  "summary": "Создать новый субпост",
  "description": (
    "Метод создаёт новый субпост, связанный с определённым постом.\n\n"
    "- В теле запроса обязательно передаётся поле `post` - ID поста, к которому относится субпост.\n"
    "- Создание возможно только для постов, владельцем которых является текущий пользователь.\n"
    "- При нарушении этого условия вернётся ошибка 403.\n"
    "- В случае успешного создания возвращается объект нового субпоста."
  ),
  "request": {"application/json": SubPostSerializer},
  "examples": [
    OpenApiExample(
      "Пример создания субпоста",
      value={
        "post": 12,
        "title": "Заголовок субпоста",
        "content": "Текст субпоста"
      },
      description="Создаёт субпост для поста с ID=12",
      media_type="application/json"
    )
  ],
  "responses": {
    201: OpenApiResponse(description="Созданный субпост"),
    403: OpenApiResponse(
      description="Пост не принадлежит пользователю",
      examples=[
        OpenApiExample(
          "Ошибка доступа",
          value={"detail": "Вы не владелец поста: Пост #12"},
          media_type="application/json"
        )
      ]
    )
  },
  "tags": ["Субпосты"]
}

UPDATE_SUBPOST_DOCS = {
  "summary": "Обновить субпост",
  "description": (
    "Обновляет данные субпоста по указанному ID.\n\n"
    "Пример запроса:\n"
    "```http\n"
    "PUT /api/subposts/10/\n"
    "Content-Type: application/json\n\n"
    "{\n"
    '  "title": "Новое название",\n'
    '  "body": "Новое содержание"\n'
    "}\n"
    "```\n"
  ),
  "parameters": [
    OpenApiParameter(
      name="id",
      type=OpenApiTypes.INT,
      location=OpenApiParameter.PATH,
      description="ID субпоста, который необходимо обновить.",
      examples=[
        OpenApiExample(
          "Пример ID",
          value=10
        )
      ]
    )
  ],
  "request": {
    "application/json": {
      "title": "string",
      "body": "string"
    }
  },
  "responses": {
    200: OpenApiResponse(
      description="Возвращает обновленный объект",
      examples=[
        OpenApiExample(
          "Пример ответа",
          value={
            "id": 10,
            "title": "Новое название",
            "body": "Новое содержание",
            "author": 1
          }
        )
      ]
    ),
    400: OpenApiResponse(description="Некорректные данные"),
    404: OpenApiResponse(description="Если нет указанного субпоста")
  },
  "tags": ["Субпосты"]
}

DELETE_SUBPOST_DOCS = {
  "summary": "Удалить субпост",
  "description": (
    "Удаляет пост по указанному ID.\n\n"
    "Пример запроса:\n"
    "`DELETE /api/subposts/10/`\n\n"
  ),
  "parameters": [
    OpenApiParameter(
      name="id",
      type=OpenApiTypes.INT,
      location=OpenApiParameter.PATH,
      description="ID субпост, который необходимо удалить.",
      examples=[
        OpenApiExample(
          "Пример ID",
          value=10
        )
      ]
    )
  ],
  "responses": {
    204: OpenApiResponse(description="Возвращает удаленный объект"),
    404: OpenApiResponse(
      description="Если нет указанного субпоста"
    )
  },
  "tags": ["Субпосты"]
}
