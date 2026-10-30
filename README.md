# Orbitra V13

Учебный Flask-проект с мобильным интерфейсом рынков и demo-сделок.

## Что добавлено в V13
- Автовыбор языка по стране/IP с fallback на язык браузера.
- Ручной выбор языка в верхней панели: ES / EN / FR / PT / AR / RU.
- Расширенная главная: возможности, безопасность, FAQ, CTA и footer.
- Отдельные информационные разделы: About, Security, Help, Terms, Privacy.
- Копирование личного ID после регистрации и из профиля.
- Бегущая лента DEMO ACTIVITY с явно учебными примерами активности.
- Сохранены V12 live ticker, mobile fixes и современный выбор рынка.

## Render
Build command:
`pip install -r requirements.txt`

Start command:
`gunicorn app:app`

После `git push` Render может автоматически развернуть новый commit. Если Auto-Deploy не сработал: Manual Deploy -> Deploy latest commit.

> Demo-баланс и demo-сделки не являются реальными деньгами или инвестиционным сервисом.
