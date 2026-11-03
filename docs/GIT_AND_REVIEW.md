# Публикация и ревью Kiromaka

Рабочий репозиторий находится в `ycheb_prac/attendance-system`. Внешняя папка `ycheb_prac` также содержит старый пустой `.git`: команды запускайте только во вложенном репозитории, чтобы не загрузить шаблоны и прежние отчеты случайно.

## Команды автора

```bash
cd /Users/aleksandrstepanov/univer/3_kyrs/ycheb_prac/attendance-system
git switch -c feature/stage-2-analytics
git status --short
git add .gitignore .dockerignore .env.example Dockerfile compose.yaml requirements.txt manage.py config journal templates .github README.md docs reports
git diff --cached --check
git commit -m "Implement stage 2 attendance backend and report"
git push -u origin feature/stage-2-analytics
```

`.env`, пароли локальной БД, SQLite и кэши не попадут в коммит. Пароль учебных демо-аккаунтов в README не является паролем БД или GitHub.

Откройте https://github.com/s1ntacs/attendance-system/compare/develop...feature/stage-2-analytics?expand=1 . Base: `develop`, compare: `feature/stage-2-analytics`. Название: «Аналитический этап — БД, Docker, аутентификация, CRUD и API». Скопируйте описание из `docs/PR_BODY.md`, нажмите Create pull request. В Reviewers выберите `Kiromaka`.

Если Kiromaka нельзя выбрать: Settings → Collaborators → Add people → Kiromaka. Он должен принять приглашение. Не передавайте пароль от своего GitHub.

## Действия Kiromaka

1. Открыть PR со своего аккаунта; прочитать описание и Files changed.
2. Запустить проект по README и `docker compose exec web python manage.py test`.
3. Проверить роли, чужие данные, CRUD и удаление с подтверждением.
4. При проблемах оставить конкретные замечания (Request changes). Автор исправляет их отдельным коммитом в этой же ветке и отправляет `git push`.
5. Когда результат устраивает: Files changed → Review changes → Approve → Submit review. Обычный комментарий «Approved!» не заменяет статус Approved.
6. Для отчета сохранить скриншот PR с названием, ссылкой и событием одобрения. Не выдавать чужой PR или пример за ревью этого проекта.

После одобрения и успешных Checks автор нажимает Merge pull request в develop. Не объединять до проверки. В отчете раздел собственной проверки уже заполнен; внешний approve можно добавить после его получения.

## Три feature-ветки из плана первого этапа

В этом PR собран второй этап. Не создавайте пустые ветки ради количества. Для следующих реальных задач используйте, например, `feature/attendance-filters`, `feature/csv-export`, `feature/audit-log`, с отдельными изменениями и ревью.

Официальная инструкция: https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-proposed-changes-in-a-pull-request
