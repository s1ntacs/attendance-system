# Модель данных

```mermaid
erDiagram
    User ||--o| Student : profile
    Group ||--o{ Student : contains
    User ||--o{ Assignment : teaches
    Group ||--o{ Assignment : assigned
    Subject ||--o{ Assignment : taught
    Assignment ||--o{ Lesson : schedules
    Lesson ||--o{ Attendance : contains
    Student ||--o{ Attendance : receives
    User ||--o{ Attendance : marks
    User {
        bigint id PK
        varchar username UK
        varchar password
        varchar role
    }
    Group {
        bigint id PK
        varchar name UK
    }
    Student {
        bigint id PK
        bigint user_id FK,UK
        bigint group_id FK
        varchar full_name
    }
    Subject {
        bigint id PK
        varchar name UK
    }
    Assignment {
        bigint id PK
        bigint teacher_id FK
        bigint group_id FK
        bigint subject_id FK
    }
    Lesson {
        bigint id PK
        bigint assignment_id FK
        timestamptz starts_at
        varchar topic
    }
    Attendance {
        bigint id PK
        bigint lesson_id FK
        bigint student_id FK
        varchar status
        bigint marked_by_id FK
        timestamptz updated_at
    }
```

Таблицы имеют префикс `journal_`. В User также используются стандартные поля AbstractUser (имя, фамилия, email, служебные флаги, last_login, date_joined). Технические таблицы Django для сессий, групп разрешений, типов содержимого и миграций на предметной схеме опущены.

Уникальны username, имя группы, название дисциплины, user_id профиля, тройка teacher/group/subject, пара assignment/starts_at и пара lesson/student. Для статуса посещения действует CHECK. Типы PK предметных таблиц — bigint. Точные типы и ограничения отражены в SQL миграции.

Внешние ключи обеспечивают наличие связанных записей. Правило «студент принадлежит группе занятия» проверяется сервером. Смена группы после отметок и изменение назначения после создания занятий блокируются. Связанные справочники защищены PROTECT на уровне Django; удаление занятия удаляет отметки CASCADE через ORM внутри транзакции. Не выполняйте прямые записи SQL в обход правил приложения.
