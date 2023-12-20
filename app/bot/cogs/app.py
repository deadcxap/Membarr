from pickle import FALSE
import app.bot.helper.jellyfinhelper as jelly
from app.bot.helper.textformat import bcolors
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import app.bot.helper.db as db
import app.bot.helper.plexhelper as plexhelper
import app.bot.helper.jellyfinhelper as jelly
import texttable
from app.bot.helper.message import *
from app.bot.helper.confighelper import *

CONFIG_PATH = 'app/config/config.ini'
BOT_SECTION = 'bot_envs'

plex_configured = True
jellyfin_configured = True

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

plex_token_configured = True
try:
    PLEX_TOKEN = config.get(BOT_SECTION, 'plex_token')
    PLEX_BASE_URL = config.get(BOT_SECTION, 'plex_base_url')
except:
    print("Сведения о токене аутентификации Plex не найдены.")
    plex_token_configured = False

# Get Plex config
try:
    PLEXUSER = config.get(BOT_SECTION, 'plex_user')
    PLEXPASS = config.get(BOT_SECTION, 'plex_pass')
    PLEX_SERVER_NAME = config.get(BOT_SECTION, 'plex_server_name')
except:
    print("Информация для входа в Plex не найдена")
    if not plex_token_configured:
        print("Не удалось загрузить конфигурацию plex")
        plex_configured = False

# Get Plex roles config
try:
    plex_roles = config.get(BOT_SECTION, 'plex_roles')
except:
    plex_roles = None
if plex_roles:
    plex_roles = list(plex_roles.split(','))
else:
    plex_roles = []

# Get Plex libs config
try:
    Plex_LIBS = config.get(BOT_SECTION, 'plex_libs')
except:
    Plex_LIBS = None
if Plex_LIBS is None:
    Plex_LIBS = ["all"]
else:
    Plex_LIBS = list(Plex_LIBS.split(','))
    
# Get Jellyfin config
try:
    JELLYFIN_SERVER_URL = config.get(BOT_SECTION, 'jellyfin_server_url')
    JELLYFIN_API_KEY = config.get(BOT_SECTION, "jellyfin_api_key")
except:
    jellyfin_configured = False

# Get Jellyfin roles config
try:
    jellyfin_roles = config.get(BOT_SECTION, 'jellyfin_roles')
except:
    jellyfin_roles = None
if jellyfin_roles:
    jellyfin_roles = list(jellyfin_roles.split(','))
else:
    jellyfin_roles = []

# Get Jellyfin libs config
try:
    jellyfin_libs = config.get(BOT_SECTION, 'jellyfin_libs')
except:
    jellyfin_libs = None
if jellyfin_libs is None:
    jellyfin_libs = ["all"]
else:
    jellyfin_libs = list(jellyfin_libs.split(','))

# Get Enable config
try:
    USE_JELLYFIN = config.get(BOT_SECTION, 'jellyfin_enabled')
    USE_JELLYFIN = USE_JELLYFIN.lower() == "true"
except:
    USE_JELLYFIN = False

try:
    USE_PLEX = config.get(BOT_SECTION, "plex_enabled")
    USE_PLEX = USE_PLEX.lower() == "true"
except:
    USE_PLEX = False

try:
    JELLYFIN_EXTERNAL_URL = config.get(BOT_SECTION, "jellyfin_external_url")
    if not JELLYFIN_EXTERNAL_URL:
        JELLYFIN_EXTERNAL_URL = JELLYFIN_SERVER_URL
except:
    JELLYFIN_EXTERNAL_URL = JELLYFIN_SERVER_URL
    print("Не удалось получить внешний URL-адрес Jellyfin. По умолчанию используется URL-адрес сервера.")

if USE_PLEX and plex_configured:
    try:
        print("Подключение к Plex......")
        if plex_token_configured and PLEX_TOKEN and PLEX_BASE_URL:
            print("Использование токена аутентификации Plex")
            plex = PlexServer(PLEX_BASE_URL, PLEX_TOKEN)
        else:
            print("Использование данных для входа в Plex")
            account = MyPlexAccount(PLEXUSER, PLEXPASS)
            plex = account.resource(PLEX_SERVER_NAME).connect()  # returns a PlexServer instance
        print('Зашёл в Plex!')
    except Exception as e:
        # probably rate limited.
        print('Ошибка при входе в plex. Пожалуйста, проверьте данные аутентификации Plex. Если вы в последнее время перезапускали бота несколько раз, скорее всего, это связано с ограничением скорости в Plex API. Повторите попытку через 10 минут.')
        print(f'Error: {e}')
else:
    print(f"Plex {'выключен' if not USE_PLEX else 'не настроен'}. Пропуск входа в Plex.")


class app(commands.Cog):
    # App command groups
    plex_commands = app_commands.Group(name="plex", description="Команды Membarr Plex")
    jellyfin_commands = app_commands.Group(name="jellyfin", description="Команды Membarr Jellyfin")
    membarr_commands = app_commands.Group(name="membarr", description="Membarr общие команды")

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('------')
        print("{:^41}".format(f"MEMBARR V {MEMBARR_VERSION}"))
        print(f'Made by Yoruio https://github.com/Yoruio/\n')
        print(f'Forked from Invitarr https://github.com/Sleepingpirates/Invitarr')
        print(f'Named by lordfransie')
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        print('------')

        # TODO: Make these debug statements work. roles are currently empty arrays if no roles assigned.
        if plex_roles is None:
            print('Настройте роли Plex, чтобы включить автоматическое приглашение в Plex после назначения роли.')
        if jellyfin_roles is None:
            print('Настройте роли Jellyfin, чтобы включить автоматическое приглашение в Jellyfin после назначения роли.')
    
    async def getemail(self, after):
        email = None
        await embedinfo(after,'Добро пожаловать в '+ PLEX_SERVER_NAME +'. Пожалуйста, ответьте на свой адрес электронной почты, который будет добавлен на сервер Plex!')
        await embedinfo(after,'Если вы не ответите в течение 24 часов, запрос будет отменен, и администратору сервера придется добавить вас вручную.')
        while(email == None):
            def check(m):
                return m.author == after and not m.guild
            try:
                email = await self.bot.wait_for('message', timeout=86400, check=check)
                if(plexhelper.verifyemail(str(email.content))):
                    return str(email.content)
                else:
                    email = None
                    message = "Указанный вами адрес электронной почты недействителен. В ответе укажите адрес электронной почты, который вы использовали при регистрации в Plex."
                    await embederror(after, message)
                    continue
            except asyncio.TimeoutError:
                message = "Время вышло. Пожалуйста, свяжитесь напрямую с администратором сервера."
                await embederror(after, message)
                return None
    
    async def getusername(self, after):
        username = None
        await embedinfo(after, f"Добро пожаловать в Jellyfin! Пожалуйста, укажите в ответе свое имя пользователя, которое будет добавлено на сервер Jellyfin!")
        await embedinfo(after, f"Если вы не ответите в течение 24 часов, запрос будет отменен, и администратору сервера придется добавить вас вручную.")
        while (username is None):
            def check(m):
                return m.author == after and not m.guild
            try:
                username = await self.bot.wait_for('message', timeout=86400, check=check)
                if(jelly.verify_username(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, str(username.content))):
                    return str(username.content)
                else:
                    username = None
                    message = "Это имя пользователя уже занято. Пожалуйста, выберите другое имя пользователя."
                    await embederror(after, message)
                    continue
            except asyncio.TimeoutError:
                message = "Время вышло. Пожалуйста, свяжитесь напрямую с администратором сервера."
                print("Время ожидания запроса пользователя Jellyfin истекло")
                await embederror(after, message)
                return None
            except Exception as e:
                await embederror(after, "Что-то пошло не так. Пожалуйста, попробуйте еще раз с другим именем пользователя.")
                print (e)
                username = None


    async def addtoplex(self, email, response):
        if(plexhelper.verifyemail(email)):
            if plexhelper.plexadd(plex,email,Plex_LIBS):
                await embedinfo(response, 'Этот адрес электронной почты был добавлен в plex')
                return True
            else:
                await embederror(response, 'Произошла ошибка при добавлении этого адреса электронной почты. Проверьте журналы.')
                return False
        else:
            await embederror(response, 'Неверный адрес электронной почты.')
            return False

    async def removefromplex(self, email, response):
        if(plexhelper.verifyemail(email)):
            if plexhelper.plexremove(plex,email):
                await embedinfo(response, 'Этот адрес электронной почты был удален из plex.')
                return True
            else:
                await embederror(response, 'Произошла ошибка при удалении этого адреса электронной почты. Проверьте журналы.')
                return False
        else:
            await embederror(response, 'Неверный адрес электронной почты.')
            return False
    
    async def addtojellyfin(self, username, password, response):
        if not jelly.verify_username(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username):
            await embederror(response, f'Учетная запись с именем пользователя {username} уже существует.')
            return False

        if jelly.add_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username, password, jellyfin_libs):
            return True
        else:
            await embederror(response, 'Произошла ошибка при добавлении этого пользователя в Jellyfin. Проверьте журналы для получения дополнительной информации.')
            return False

    async def removefromjellyfin(self, username, response):
        if jelly.verify_username(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username):
            await embederror(response, f'Не удалось найти учетную запись с именем пользователя {username}.')
            return
        
        if jelly.remove_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username):
            await embedinfo(response, f'Пользователь {username} успешно удален из Jellyfin.')
            return True
        else:
            await embederror(response, f'Произошла ошибка при удалении этого пользователя из Jellyfin. Проверьте журналы для получения дополнительной информации.')
            return False

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if plex_roles is None and jellyfin_roles is None:
            return
        roles_in_guild = after.guild.roles
        role = None

        plex_processed = False
        jellyfin_processed = False

        # Check Plex roles
        if plex_configured and USE_PLEX:
            for role_for_app in plex_roles:
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    # Plex role was added
                    if role is not None and (role in after.roles and role not in before.roles):
                        email = await self.getemail(after)
                        if email is not None:
                            await embedinfo(after, "Понятно, в ближайшее время мы добавим ваш адрес электронной почты в plex!")
                            if plexhelper.plexadd(plex,email,Plex_LIBS):
                                db.save_user_email(str(after.id), email)
                                await asyncio.sleep(5)
                                await embedinfo(after, 'Вас добавили в Plex! Войдите в plex и примите приглашение!')
                            else:
                                await embedinfo(after, 'Произошла ошибка при добавлении этого адреса электронной почты. Напишите администраторам сервера.')
                        plex_processed = True
                        break

                    # Plex role was removed
                    elif role is not None and (role not in after.roles and role in before.roles):
                        try:
                            user_id = after.id
                            email = db.get_useremail(user_id)
                            plexhelper.plexremove(plex,email)
                            deleted = db.remove_email(user_id)
                            if deleted:
                                print("Удален адрес электронной почты Plex {} из базы данных.".format(after.name))
                                #await secure.send(plexname + ' ' + after.mention + ' was removed from plex')
                            else:
                                print("Невозможно удалить Plex у этого пользователя.")
                            await embedinfo(after, "Вас удалили из Plex")
                        except Exception as e:
                            print(e)
                            print("{} Невозможно удалить этого пользователя из plex.".format(email))
                        plex_processed = True
                        break
                if plex_processed:
                    break

        role = None
        # Check Jellyfin roles
        if jellyfin_configured and USE_JELLYFIN:
            for role_for_app in jellyfin_roles:
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    # Jellyfin role was added
                    if role is not None and (role in after.roles and role not in before.roles):
                        print("Добавлена ​​роль Jellyfin")
                        username = await self.getusername(after)
                        print("Имя пользователя получено от пользователя")
                        if username is not None:
                            await embedinfo(after, "Поодождите, в ближайшее время мы создадим вашу учетную запись Jellyfin!")
                            password = jelly.generate_password(16)
                            if jelly.add_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username, password, jellyfin_libs):
                                db.save_user_jellyfin(str(after.id), username)
                                await asyncio.sleep(5)
                                await embedcustom(after, "Вы добавлены в Jellyfin!", {'Username': username, 'Password': f"||{password}||"})
                                await embedinfo(after, f"Перейдите по адресу {JELLYFIN_EXTERNAL_URL}, чтобы войти!")
                            else:
                                await embedinfo(after, 'Произошла ошибка при добавлении этого пользователя в Jellyfin. Напишите администраторам сервера.')
                        jellyfin_processed = True
                        break

                    # Jellyfin role was removed
                    elif role is not None and (role not in after.roles and role in before.roles):
                        print("Роль Jellyfin удалена")
                        try:
                            user_id = after.id
                            username = db.get_jellyfin_username(user_id)
                            jelly.remove_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username)
                            deleted = db.remove_jellyfin(user_id)
                            if deleted:
                                print("Удален Jellyfin из {}".format(after.name))
                                #await secure.send(plexname + ' ' + after.mention + ' was removed from plex')
                            else:
                                print("Невозможно удалить Jellyfin у этого пользователя.")
                            await embedinfo(after, "Вас удалили из Jellyfin")
                        except Exception as e:
                            print(e)
                            print("{} Невозможно удалить этого пользователя из Jellyfin.".format(username))
                        jellyfin_processed = True
                        break
                if jellyfin_processed:
                    break

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if USE_PLEX and plex_configured:
            email = db.get_useremail(member.id)
            plexhelper.plexremove(plex,email)
        
        if USE_JELLYFIN and jellyfin_configured:
            jellyfin_username = db.get_jellyfin_username(member.id)
            jelly.remove_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, jellyfin_username)
            
        deleted = db.delete_user(member.id)
        if deleted:
            print("Удален {} из базы данных, поскольку пользователь покинул сервер Discord.".format(email))

    @app_commands.checks.has_permissions(administrator=True)
    @plex_commands.command(name="invite", description="Пригласить пользователя в Plex")
    async def plexinvite(self, interaction: discord.Interaction, email: str):
        await self.addtoplex(email, interaction.response)
    
    @app_commands.checks.has_permissions(administrator=True)
    @plex_commands.command(name="remove", description="Удаление пользователя из Plex")
    async def plexremove(self, interaction: discord.Interaction, email: str):
        await self.removefromplex(email, interaction.response)
    
    @app_commands.checks.has_permissions(administrator=True)
    @jellyfin_commands.command(name="invite", description="Пригласить пользователя в Jellyfin")
    async def jellyfininvite(self, interaction: discord.Interaction, username: str):
        password = jelly.generate_password(16)
        if await self.addtojellyfin(username, password, interaction.response):
            await embedcustom(interaction.response, "Пользователь Jellyfin создан!", {'Username': username, 'Password': f"||{password}||"})

    @app_commands.checks.has_permissions(administrator=True)
    @jellyfin_commands.command(name="remove", description="Удаление пользователя из Jellyfin")
    async def jellyfinremove(self, interaction: discord.Interaction, username: str):
        await self.removefromjellyfin(username, interaction.response)
    
    @app_commands.checks.has_permissions(administrator=True)
    @membarr_commands.command(name="dbadd", description="Добавьте пользователя в базу данных Membarr")
    async def dbadd(self, interaction: discord.Interaction, member: discord.Member, email: str = "", jellyfin_username: str = ""):
        email = email.strip()
        jellyfin_username = jellyfin_username.strip()
        
        # Check email if provided
        if email and not plexhelper.verifyemail(email):
            await embederror(interaction.response, "Неверный адрес электронной почты.")
            return

        try:
            db.save_user_all(str(member.id), email, jellyfin_username)
            await embedinfo(interaction.response,'Пользователь добавлен в базу данных.')
        except Exception as e:
            await embedinfo(interaction.response, 'Произошла ошибка при добавлении этого пользователя в базу данных. Проверьте журналы Membarr для получения дополнительной информации.')
            print(e)

    @app_commands.checks.has_permissions(administrator=True)
    @membarr_commands.command(name="dbls", description="Посмотреть базу данных Memarr")
    async def dbls(self, interaction: discord.Interaction):

        embed = discord.Embed(title='База данных Memarr.')
        all = db.read_all()
        table = texttable.Texttable()
        table.set_cols_dtype(["t", "t", "t", "t"])
        table.set_cols_align(["c", "c", "c", "c"])
        header = ("#", "Name", "Email", "Jellyfin")
        table.add_row(header)
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            dbjellyfin = peoples[3] if peoples[3] else "No Jellyfin"
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(name=f"**{index}. {username}**", value=dbemail+'\n'+dbjellyfin+'\n', inline=False)
            table.add_row((index, username, dbemail, dbjellyfin))
        
        total = str(len(all))
        if(len(all)>25):
            f = open("db.txt", "w")
            f.write(table.draw())
            f.close()
            await interaction.response.send_message("База данных слишком велика! Итого: {total}".format(total = total),file=discord.File('db.txt'), ephemeral=True)
        else:
            await interaction.response.send_message(embed = embed, ephemeral=True)
        
            
    @app_commands.checks.has_permissions(administrator=True)
    @membarr_commands.command(name="dbrm", description="Удалить пользователя из базы данных Membarr")
    async def dbrm(self, interaction: discord.Interaction, position: int):
        embed = discord.Embed(title='База данных Memarr.')
        all = db.read_all()
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            dbjellyfin = peoples[3] if peoples[3] else "No Jellyfin"
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(name=f"**{index}. {username}**", value=dbemail+'\n'+dbjellyfin+'\n', inline=False)

        try:
            position = int(position) - 1
            id = all[position][1]
            discord_user = await self.bot.fetch_user(id)
            username = discord_user.name
            deleted = db.delete_user(id)
            if deleted:
                print("{} удален из базы данных.".format(username))
                await embedinfo(interaction.response,"{} удален из базы данных.".format(username))
            else:
                await embederror(interaction.response,"Невозможно удалить этого пользователя из базы данных.")
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(app(bot))
