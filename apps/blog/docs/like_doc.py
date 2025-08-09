from drf_spectacular.utils import OpenApiExample, OpenApiResponse

LIKE_VIEW_SET_DOCS = {
  "tags": ["Лайки"],
  "description": (
    "Управление лайками для постов.\n\n"
  )
}

ADD_RO_REMOVE_LIKE = {
  "summary": "Поставить или убрать лайк",
  "description": (
    "Метод переключает состояние лайка для конкретного поста:\n\n"
    "- Если пользователь ещё не ставил лайк - он будет добавлен.\n"
    "- Если лайк уже был - он будет удалён.\n\n"
    "**Пример использования:**\n"
    "POST `/posts/{id}/like/` - переключение лайка для поста с ID `{id}`."
  ),
  "request": None,
  "responses": {
    200: OpenApiResponse(
      description="Результат действия (поставлен или убран лайк)",
      examples=[
        OpenApiExample(
          "Лайк поставлен",
          value={"message": "Вы поставили лайк"},
          media_type="application/json"
        ),
        OpenApiExample(
          "Лайк убран",
          value={"message": "Лайк убран"},
          media_type="application/json"
        )
      ]
    ),
    404: OpenApiResponse(
      description="Пост не найден",
      examples=[
        OpenApiExample(
          "Пост не найден",
          value={"detail": "Страница не найдена."},
          media_type="application/json"
        )
      ]
    )
  }
}
