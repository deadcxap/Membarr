[![Discord](https://img.shields.io/discord/997761163020488815?color=7289DA&label=Discord&style=for-the-badge&logo=discord)](https://discord.gg/7hAUKKTyTd)
[![DockerHub](https://img.shields.io/badge/Docker-Hub-%23099cec?style=for-the-badge&logo=docker)](https://hub.docker.com/r/yoruio/membarr)
![Docker Pulls](https://img.shields.io/docker/pulls/yoruio/membarr?color=099cec&style=for-the-badge)
[![docker-sync](https://github.com/Yoruio/Membarr/actions/workflows/docker-sync.yml/badge.svg)](https://github.com/Yoruio/Membarr/actions/workflows/docker-sync.yml)

Membarr 
=================

Membarr — это форк Invitarr, который приглашает пользователей Discord в Plex и Jellyfin. Вы также можете автоматизировать этого бота, чтобы он приглашал пользователей Discord на медиасервер, как только пользователю будет присвоена определенная роль, или же пользователя можно добавить вручную.

### Features

- Возможность приглашать пользователей в Plex и Jellyfin из дискорда.
- Полностью автоматические приглашения с использованием ролей
- Возможность выкидывать пользователей из plex, если они покидают сервер Discord или если их роль отбирают.
- Возможность просмотра базы данных в Discord и ее редактирования.Commands: 

```
/plex invite <email>
Эта команда используется для добавления электронной почты в plex
/plex remove <email>
Эта команда используется для удаления почты из plex
/jellyfin invite <jellyfin username>
Эта команда используется для добавления пользователя в Jellyfin.
/jellyfin remove <jellyfin username>
Эта команда используется для удаления пользователя из Jellyfin.
/membarr dbls
Эта команда используется для получения списка базы данных Membarr
/membarr dbadd <@user> <optional: plex email> <optional: jellyfin username>
Эта команда используется для добавления в БД существующих plex email'ов, jellyfin пользователей и discord id.
/membarr dbrm <position>
Эта команда используется для удаления записи из базы данных. Для определения позиции записи используйте /membarr dbls. пример: /membarr dbrm 1
```
# Создание Discord-бота
1. Создайте дискорд-сервер, на котором пользователи будут получать роли участников, или используйте существующий сервер, в котором можно назначать роли
2. Авторизуйтесь на https://discord.com/developers/applications и нажмите 'New Application'
3. (Дополнительно) Добавьте краткое описание и иконку для бота. Сохраните изменения.
4. Перейдите в раздел 'Бот' в боковом меню
5. Снимите флажок 'Public Bot' в разделе Authorization Flow
6. Установите все три флажка в разделе Privileged Gateway Intents: Presence Intent, Server Members Intent, Message Content Intent. Сохранить изменения.
7. Скопируйте токен под именем пользователя или сбросьте его для копирования. Это токен, используемый в образе докера.
8. Перейдите в раздел 'OAuth2' в боковом меню, затем 'URL Generator'
9. В разделе Scopes отметьте 'bot' и applications.commands
10. Скопируйте 'Generated URL', вставьте его в свой браузер и добавьте его на свой сервер Discord, из шага 1.
11. Бот подключится к сети после запуска Docker-контейнера с правильным токеном бота.

# Ручная настройка (для Docker см. ниже)

**1. Введите токен бота Discord в bot.env**

**2. Требования к установке**

```
pip3 install -r requirements.txt 
```
**3. Запустить бота**
```
python3 Run.py
```

# Настройка и запуск Docker
Чтобы запустить Membarr в Docker, выполните следующую команду, заменив [path to config] абсолютным путем к папке конфигурации вашего бота:
```
docker run -d --restart unless-stopped --name membarr -v /[path to config]:/app/app/config -e "token=YOUR_DISCORD_TOKEN_HERE" yoruio/membarr:latest
```

# После запуска бота

# Команды настройки Plex: 

```
/plexsettings setup <username> <password> <server name>
Эта команда используется для настройки входа в plex.
/plexsettings addrole <@role>
Эти роли будут использоваться в качестве ролей для автоматического приглашения пользователя в plex.
/plexsettings removerole <@role>
Эта команда используется для удаления роли, которая используется для автоматического приглашения пользователей в plex.
/plexsettings setuplibs <libraries>
Эта команда используется для настройки библиотек plex. По умолчанию выбраны все. Библиотеки — это список, разделенный запятыми.
/plexsettings enable
Эта команда включает интеграцию Plex (в настоящее время включает только автоматическое добавление/автоудаление)
/plexsettings disable
Эта команда отключает интеграцию Plex (в настоящее время отключает только автоматическое добавление/автоудаление).
```

# Команды настройки Jellyfin:
```
/jellyfinsettings setup <server url> <api key> <optional: external server url (default: server url)>
Эта команда используется для настройки сервера Jellyfin. URL-адрес внешнего сервера — это URL-адрес, который отправляется пользователям для входа на ваш сервер Jellyfin.
/jellyfinsettings addrole <@role>
Эти роли будут использоваться в качестве ролей для автоматического приглашения пользователя в Jellyfin.
/jellyfinsettings removerole <@role>
Эта команда используется для удаления роли, которая используется для автоматического приглашения пользователей в Jellyfin.
/jellyfinsettings setuplibs <libraries>
Эта команда используется для настройки библиотек Jellyfin. По умолчанию выбраны все. Библиотеки — это список, разделенный запятыми.
/jellyfinsettings enable
Эта команда включает интеграцию Jellyfin (в настоящее время включает только автоматическое добавление/автоудаление)
/jellyfinsettings disable
Эта команда отключает интеграцию Jellyfin (в настоящее время отключает только автоматическое добавление/автоудаление)
```

# Миграция с Invitarr
Для Invitarr не требуется область application.commands, поэтому вам нужно будет выгнать и повторно пригласить бота Discord на свой сервер, обязательно отметив обе области "bot" и "applications.commands" в генераторе URL-адресов Oauth.

Membarr использует немного другую таблицу базы данных, чем Invitarr. Membarr автоматически обновит таблицу базы данных Invitarr до текущего формата таблицы Membarr, но новая таблица больше не будет совместима с Invitarr, поэтому сделайте резервную копию файла app.db перед запуском Membarr!

# Миграция на Invitarr
Как упоминалось в [Миграция с Invitarr](#Migration-From-Invitarr), у Membarr немного другая таблица базы данных, чем у Invitarr. Чтобы вернуться к Invitarr, вам придется вручную изменить формат таблицы обратно. Откройте app.db в инструменте sqlite cli или в браузере, таком как DB Browser, затем удалите столбец «jellyfin_username» и сделайте столбец «email» ненулевым.

# Содействие
Мы ценим любой вклад, внесенный в проект, будь то новые функции, исправления ошибок или даже исправления опечаток! Если вы хотите внести свой вклад в проект, просто создайте ветку разработки, внесите изменения и откройте запрос на включение. *Запросы на включение, не относящиеся к ветке разработки, будут отклонены.*

# Прочее
**Включите Intents, в противном случае бот не будет добавлять пользователей в Dm после получения ими роли.**
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents
**Для полноценной работы Discord Bot требуется разрешение Bot и application.commands.**
