# Адреса API

Аутентификация: cookie sessionid после POST /login/. Для POST/PUT/PATCH/DELETE передайте X-CSRFToken из cookie csrftoken. Сначала откройте /login/, затем отправьте форму с csrfmiddlewaretoken. После входа CSRF-токен обновляется.

- `GET /api/users/` — список: пользователи.
- `POST /api/users/` — создать: пользователи.
- `GET /api/users/{id}/` — получить одну запись: пользователи.
- `PUT /api/users/{id}/` — полностью обновить: пользователи.
- `PATCH /api/users/{id}/` — частично обновить: пользователи.
- `DELETE /api/users/{id}/` — удалить: пользователи.
- `GET /api/groups/` — список: группы.
- `POST /api/groups/` — создать: группы.
- `GET /api/groups/{id}/` — получить одну запись: группы.
- `PUT /api/groups/{id}/` — полностью обновить: группы.
- `PATCH /api/groups/{id}/` — частично обновить: группы.
- `DELETE /api/groups/{id}/` — удалить: группы.
- `GET /api/students/` — список: профили студентов.
- `POST /api/students/` — создать: профили студентов.
- `GET /api/students/{id}/` — получить одну запись: профили студентов.
- `PUT /api/students/{id}/` — полностью обновить: профили студентов.
- `PATCH /api/students/{id}/` — частично обновить: профили студентов.
- `DELETE /api/students/{id}/` — удалить: профили студентов.
- `GET /api/subjects/` — список: дисциплины.
- `POST /api/subjects/` — создать: дисциплины.
- `GET /api/subjects/{id}/` — получить одну запись: дисциплины.
- `PUT /api/subjects/{id}/` — полностью обновить: дисциплины.
- `PATCH /api/subjects/{id}/` — частично обновить: дисциплины.
- `DELETE /api/subjects/{id}/` — удалить: дисциплины.
- `GET /api/assignments/` — список: назначения преподавателей.
- `POST /api/assignments/` — создать: назначения преподавателей.
- `GET /api/assignments/{id}/` — получить одну запись: назначения преподавателей.
- `PUT /api/assignments/{id}/` — полностью обновить: назначения преподавателей.
- `PATCH /api/assignments/{id}/` — частично обновить: назначения преподавателей.
- `DELETE /api/assignments/{id}/` — удалить: назначения преподавателей.
- `GET /api/lessons/` — список: занятия.
- `POST /api/lessons/` — создать: занятия.
- `GET /api/lessons/{id}/` — получить одну запись: занятия.
- `PUT /api/lessons/{id}/` — полностью обновить: занятия.
- `PATCH /api/lessons/{id}/` — частично обновить: занятия.
- `DELETE /api/lessons/{id}/` — удалить: занятия.
- `GET /api/attendance/` — список: отметки.
- `POST /api/attendance/` — создать: отметки.
- `GET /api/attendance/{id}/` — получить одну запись: отметки.
- `PUT /api/attendance/{id}/` — полностью обновить: отметки.
- `PATCH /api/attendance/{id}/` — частично обновить: отметки.
- `DELETE /api/attendance/{id}/` — удалить: отметки.

- `GET /api/` — список ресурсов.
- `GET /api/me/` — текущий пользователь.
- `GET /api/stats/` — статистика по доступным отметкам.
- `GET /api/docs/` — справочник и форма запроса.
- `GET /health/` — доступность сервера и БД.

## Форматы POST и PATCH

- users: username, password (обязательны при создании), role, first_name, last_name.
- groups, subjects: name.
- students: user, group (числовые id), full_name.
- assignments: teacher, group, subject (id).
- lessons: assignment (id), starts_at (ISO 8601 с часовым поясом), topic.
- attendance: lesson, student (id), status (present / absent / excused). marked_by и updated_at устанавливаются сервером.

## Права

users — только администратор. Изменение groups/students/subjects/assignments — только администратор. Преподаватель изменяет свои lessons/attendance. Студент читает свои attendance, свой профиль и занятия своей группы. Все списки фильтруются сервером.

## Ошибки

400 — валидация, дубли, неправильная группа или статус. 403 — не выполнен вход, недостаточно прав или отсутствует CSRF. 404 — запись отсутствует либо вне области доступа. 409 — защищенная связь либо удаление занятия с отметками без confirm=true.

POST /register/ и POST /login/ — HTML-формы Django; POST /logout/ завершает сессию.
