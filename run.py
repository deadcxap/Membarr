from pydoc import describe
import discord
import os
from discord.ext import commands, tasks
from discord.utils import get
from discord.ui import Button, View, Select
from discord import app_commands
import asyncio
import sys
from app.bot.helper.confighelper import MEMBARR_VERSION, switch, Discord_bot_token, plex_roles, jellyfin_roles
import app.bot.helper.confighelper as confighelper
import app.bot.helper.jellyfinhelper as jelly
from app.bot.helper.message import *
from requests import ConnectTimeout
from plexapi.myplex import MyPlexAccount

maxroles = 10

if switch == 0:
    print("Потеря конфига.")
    sys.exit()


class Bot(commands.Bot):
    def __init__(self) -> None:
        print("Инициализация дискорд бота")
        intents = discord.Intents.all()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=".", intents=intents)

    async def on_ready(self):
        print("Бот онлайн.")
        for guild in self.guilds:
            print("Синхронизация команд с " + guild.name)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_guild_join(self, guild):
        print(f"Зашёл на сервер {guild.name}")
        print(f"Синхронизация команд с {guild.name}")
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def setup_hook(self):
        print("Загрузка подключений медиасервера")
        await self.load_extension(f'app.bot.cogs.app')


bot = Bot()


async def reload():
    await bot.reload_extension(f'app.bot.cogs.app')


async def getuser(interaction, server, type):
    value = None
    await interaction.user.send("Пожалуйста, ответьте с вашим {} {}:".format(server, type))
    while (value == None):
        def check(m):
            return m.author == interaction.user and not m.guild

        try:
            value = await bot.wait_for('message', timeout=200, check=check)
            return value.content
        except asyncio.TimeoutError:
            message = "Тайм-аут. Попробуйте снова."
            return None


plex_commands = app_commands.Group(name="plexsettings", description="Membarr Plex команды")
jellyfin_commands = app_commands.Group(name="jellyfinsettings", description="Membarr Jellyfin команды")


@plex_commands.command(name="addrole", description="Роль для автоматического создания пользователя в Plex")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def plexroleadd(interaction: discord.Interaction, role: discord.Role):
    if len(plex_roles) <= maxroles:
        # Do not add roles multiple times.
        if role.name in plex_roles:
            await embederror(interaction.response, f"Plex роль \"{role.name}\" добавлена.")
            return

        plex_roles.append(role.name)
        saveroles = ",".join(plex_roles)
        confighelper.change_config("plex_roles", saveroles)
        await interaction.response.send_message("Обновлены роли Plex. Бот перезапускается. ЖДИТЕ.", ephemeral=True)
        print("Обновлены роли Plex. Бот перезапускается. Дайте ему уже поработать!")
        await reload()
        print("Бот перезапущен. ЖДИТЕ, ему нужно время, чтобы запуститься!")


@plex_commands.command(name="removerole", description="Прекратить создавать пользователй Plex с помощью ролей.")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def plexroleremove(interaction: discord.Interaction, role: discord.Role):
    if role.name not in plex_roles:
        await embederror(interaction.response, f"\"{role.name}\" больше не связана с Plex.")
        return
    plex_roles.remove(role.name)
    confighelper.change_config("plex_roles", ",".join(plex_roles))
    await interaction.response.send_message(f"Membarr больше не будет ассоциировать \"{role.name}\" с Plex", ephemeral=True)


@plex_commands.command(name="listroles", description="Список всех ролей, участники которых будут автоматически добавлены в Plex.")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def plexrolels(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Следующие роли автоматически добавляются в Plex:\n" +
        ", ".join(plex_roles), ephemeral=True
    )


@plex_commands.command(name="setup", description="Настройка интеграции с Plex")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def setupplex(interaction: discord.Interaction, username: str, password: str, server_name: str,
                    base_url: str = "", save_token: bool = True):
    await interaction.response.defer()
    try:
        account = MyPlexAccount(username, password)
        plex = account.resource(server_name).connect()
    except Exception as e:
        if str(e).startswith("(429)"):
            await embederror(interaction.followup, "Слишком много запросов. Пожалуйста, повторите попытку позже.")
            return

        await embederror(interaction.followup, "Не удалось подключиться к серверу Plex. Пожалуйста, проверьте свои учетные данные.")
        return

    if (save_token):
        # Save new config entries
        confighelper.change_config("plex_base_url", plex._baseurl if base_url == "" else base_url)
        confighelper.change_config("plex_token", plex._token)
        confighelper.change_config("plex_server_name", server_name)

        # Delete old config entries
        confighelper.change_config("plex_user", "")
        confighelper.change_config("plex_pass", "")
    else:
        # Save new config entries
        confighelper.change_config("plex_user", username)
        confighelper.change_config("plex_pass", password)
        confighelper.change_config("plex_server_name", server_name)

        # Delete old config entries
        confighelper.change_config("plex_base_url", "")
        confighelper.change_config("plex_token", "")

    print("Обновлены сведения об аутентификации в Plex. Перезапуск бота.")
    await interaction.followup.send(
        "Обновлены сведения об аутентификации в Plex. Перезапуск бота. ЖДИТЕ.\n" +
        "Пожалуйста, проверьте журналы и убедитесь, что вы видите эту строку: `Вошел в plex`. Если это не так, выполните эту команду еще раз и убедитесь, что ввели правильные значения.",
        ephemeral=True
    )
    await reload()
    print("Бот был перезапущен. Дайте ему несколько секунд.")


@jellyfin_commands.command(name="addrole", description="Добавление роли для автоматического добавления пользователей в Jellyfin")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def jellyroleadd(interaction: discord.Interaction, role: discord.Role):
    if len(jellyfin_roles) <= maxroles:
        # Do not add roles multiple times.
        if role.name in jellyfin_roles:
            await embederror(interaction.response, f"Jellyfin роль \"{role.name}\" добавлена.")
            return

        jellyfin_roles.append(role.name)
        saveroles = ",".join(jellyfin_roles)
        confighelper.change_config("jellyfin_roles", saveroles)
        await interaction.response.send_message("Обновлены роли Jellyfin. Бот перезапускается. Пожалуйста, подождите несколько секунд.",
                                                ephemeral=True)
        print("Обновлены роли Jellyfin. Перезапуск бота.")
        await reload()
        print("Бот был перезапущен. Дайте ему несколько секунд.")


@jellyfin_commands.command(name="removerole", description="Прекращение добавления пользователей с ролью в Jellyfin")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def jellyroleremove(interaction: discord.Interaction, role: discord.Role):
    if role.name not in jellyfin_roles:
        await embederror(interaction.response, f"\"{role.name}\" больше не связана с Jellyfin.")
        return
    jellyfin_roles.remove(role.name)
    confighelper.change_config("jellyfin_roles", ",".join(jellyfin_roles))
    await interaction.response.send_message(f"Membarr больше не будет ассоциировать \"{role.name}\" с Jellyfin",
                                            ephemeral=True)


@jellyfin_commands.command(name="listroles",
                           description="Список всех ролей, участники которых будут автоматически добавлены в Jellyfin.")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def jellyrolels(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Следующие роли автоматически добавляются в Jellyfin:\n" +
        ", ".join(jellyfin_roles), ephemeral=True
    )


@jellyfin_commands.command(name="setup", description="Настройка интеграции Jellyfin")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def setupjelly(interaction: discord.Interaction, server_url: str, api_key: str, external_url: str = None):
    await interaction.response.defer()
    # get rid of training slashes
    server_url = server_url.rstrip('/')

    try:
        server_status = jelly.get_status(server_url, api_key)
        if server_status == 200:
            pass
        elif server_status == 401:
            # Unauthorized
            await embederror(interaction.followup, "Предоставленный ключ API неправильный.")
            return
        elif server_status == 403:
            # Forbidden
            await embederror(interaction.followup, "Предоставленный ключ API не имеет прав доступа")
            return
        elif server_status == 404:
            # page not found
            await embederror(interaction.followup, "Указанная конечная точка сервера не найдена")
            return
        else:
            await embederror(interaction.followup,
                             "При подключении к Jellyfin произошла неизвестная ошибка. Проверьте журналы Membarr.")
    except ConnectTimeout as e:
        await embederror(interaction.followup,
                         "Время соединения с сервером истекло. Убедитесь, что Jellyfin онлайн и доступен.")
        return
    except Exception as e:
        print("Исключение при тестировании соединения с Jellyfin")
        print(type(e).__name__)
        print(e)
        await embederror(interaction.followup, "Неизвестное исключение при подключении к Jellyfin. Проверьте журналы Membarr")
        return

    confighelper.change_config("jellyfin_server_url", str(server_url))
    confighelper.change_config("jellyfin_api_key", str(api_key))
    if external_url is not None:
        confighelper.change_config("jellyfin_external_url", str(external_url))
    else:
        confighelper.change_config("jellyfin_external_url", "")
    print("URL-адрес сервера Jellyfin и ключ API обновлены. Перезапуск бота.")
    await interaction.followup.send("URL-адрес сервера Jellyfin и ключ API обновлены. Перезапуск бота.", ephemeral=True)
    await reload()
    print("Бот был перезапущен. Дайте ему несколько секунд.")


@plex_commands.command(name="setuplibs", description="Библиотеки настройки, к которым могут получить доступ новые пользователи")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def setupplexlibs(interaction: discord.Interaction, libraries: str):
    if not libraries:
        await embederror(interaction.response, "строка библиотек пуста.")
        return
    else:
        # Do some fancy python to remove spaces from libraries string, but only where wanted.
        libraries = ",".join(list(map(lambda lib: lib.strip(), libraries.split(","))))
        confighelper.change_config("plex_libs", str(libraries))
        print("Обновлены библиотеки Plex. Перезапуск бота. Пожалуйста, подождите.")
        await interaction.response.send_message("Обновлены библиотеки Plex. Пожалуйста, подождите несколько секунд, пока бот перезапустится.",
                                                ephemeral=True)
        await reload()
        print("Бот был перезапущен. Дайте ему несколько секунд.")


@jellyfin_commands.command(name="setuplibs", description="Настройка библиотек, к которым могут получить доступ новые пользователи")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def setupjellylibs(interaction: discord.Interaction, libraries: str):
    if not libraries:
        await embederror(interaction.response, "строка библиотек пуста.")
        return
    else:
        # Do some fancy python to remove spaces from libraries string, but only where wanted.
        libraries = ",".join(list(map(lambda lib: lib.strip(), libraries.split(","))))
        confighelper.change_config("jellyfin_libs", str(libraries))
        print("Обновлены библиотеки Jellyfin. Перезапуск бота. Пожалуйста, подождите.")
        await interaction.response.send_message(
            "Обновлены библиотеки Jellyfin. Пожалуйста, подождите несколько секунд, пока бот перезапустится.", ephemeral=True)
        await reload()
        print("Бот был перезапущен. Дайте ему несколько секунд.")


# Enable / Disable Plex integration
@plex_commands.command(name="enable", description="Включение автоматического добавления пользователей в Plex")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def enableplex(interaction: discord.Interaction):
    if confighelper.USE_PLEX:
        await interaction.response.send_message("Plex уже включен.", ephemeral=True)
        return
    confighelper.change_config("plex_enabled", True)
    print("Plex включен, перезагрузка сервера")
    await reload()
    confighelper.USE_PLEX = True
    await interaction.response.send_message("Plex включен. Перезапуск сервера. Дайте ему несколько секунд.", ephemeral=True)
    print("Бот перезапущен. Дайте ему несколько секунд.")


@plex_commands.command(name="disable", description="Отключение добавления пользователей в Plex")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def disableplex(interaction: discord.Interaction):
    if not confighelper.USE_PLEX:
        await interaction.response.send_message("Plex уже отключен.", ephemeral=True)
        return
    confighelper.change_config("plex_enabled", False)
    print("Plex отключен, перезагрузка сервера")
    await reload()
    confighelper.USE_PLEX = False
    await interaction.response.send_message("Plex отключен. Перезапуск сервера. Дайте ему несколько секунд.", ephemeral=True)
    print("Бот перезапущен. Дайте ему несколько секунд.")


# Enable / Disable Jellyfin integration
@jellyfin_commands.command(name="enable", description="Включение добавления пользователей в Jellyfin")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def enablejellyfin(interaction: discord.Interaction):
    if confighelper.USE_JELLYFIN:
        await interaction.response.send_message("Jellyfin уже включен.", ephemeral=True)
        return
    confighelper.change_config("jellyfin_enabled", True)
    print("Jellyfin включен, перезагрузка сервера")
    confighelper.USE_JELLYFIN = True
    await reload()
    await interaction.response.send_message("Jellyfin включен. Перезапуск сервера. Дайте ему несколько секунд.",
                                            ephemeral=True)
    print("Бот перезапущен. Дайте ему несколько секунд.")


@jellyfin_commands.command(name="disable", description="Отключение добавления пользователей в Jellyfin")
@app_commands.checks.has_role(DISCORD_SERVER_PERM)
async def disablejellyfin(interaction: discord.Interaction):
    if not confighelper.USE_JELLYFIN:
        await interaction.response.send_message("Jellyfin уже отключен.", ephemeral=True)
        return
    confighelper.change_config("jellyfin_enabled", False)
    print("Jellyfin отключен, перезагрузка сервера")
    await reload()
    confighelper.USE_JELLYFIN = False
    await interaction.response.send_message("Jellyfin отключен. Перезапуск сервера. Дайте ему несколько секунд.",
                                            ephemeral=True)
    print("Бот перезапущен. Дайте ему несколько секунд.")


bot.tree.add_command(plex_commands)
bot.tree.add_command(jellyfin_commands)

bot.run(Discord_bot_token)
