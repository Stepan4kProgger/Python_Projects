import discord, asyncio, requests, math
from discord.ext import commands
from datetime import datetime
import dconfig as cfg

HELLO_MSG = 'https://tenor.com/view/say-what-gif-21920122'
PREFIX = '!'
HELP_COMMA = {
    'hi': 'Привет вызвавшему от бота',
    'clear *количество*': 'Очищает определённое количество сообщений в чате. Требует *админ* права',
    'repeat *фраза*': 'Повторяет введённое в команде сообщение',
    'ping *секунды*': 'Пингует вызвавшего через указанное кол-во секунд',
    'osu *ник/id*': 'Выводит информацию об игроке в **osu!** по нику либо id',
    'calc *выражение*': 'Выводит рассчитанное выражение',
    'viewreqprerm': 'Выводит инфу о требуемых разрешениях на сервере'
}
REQUIREMENTS=['1. Отправлять сообщения',
              '2. Управлять сообщениями',
              '3. Читать историю сообщений',
              '4. Использовать режим активации по голосу']
ALLOWED_MATH_NAMES = {
    k: v for k, v in math.__dict__.items() if not k.startswith("__")
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix=PREFIX, intents=intents)
client.remove_command('help')


# Блок вспомогательных функций
def get_response(user):
    data = {
        'client_id': cfg.CLIENT_ID,
        'client_secret': cfg.encToken('osu'),
        'grant_type': 'client_credentials',
        'scope': 'public'
    }
    response = requests.post(cfg.TOKEN_URL, data=data)
    token = response.json().get('access_token')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(f'{cfg.API_URL}/users/{user}', headers=headers)
    return response.json()


def evaluate(expression):
    if expression.count('pow') > 1:
        raise NameError(f"Использование повышения степени в выражении допускается не более 1 раза.")
    code = compile(expression, "<string>", "eval")
    for name in code.co_names:
        if name not in ALLOWED_MATH_NAMES:
            raise NameError(f"Использование '{name}' запрещено")
    return eval(code, {"__builtins__": {}}, ALLOWED_MATH_NAMES)


def write_description(player):
    statistics = player.get('statistics')
    pp = statistics.get('pp')
    rank = statistics.get('rank')
    ranked_score = statistics.get('ranked_score')
    global_rank = statistics.get('global_rank')
    country_rank = rank.get('country')
    country_code = player.get('country_code').lower()
    hit_accuracy = statistics.get('hit_accuracy')
    grade_counts = statistics.get('grade_counts')
    total_ss = grade_counts.get('ss')
    total_ssh = grade_counts.get('ssh')
    total_s = grade_counts.get('s')
    total_sh = grade_counts.get('sh')
    total_a = grade_counts.get('a')
    country = player.get('country')
    country_name = country.get('name')
    total_time = statistics.get('play_time')
    user_id = player.get('id')
    return f"""
            Showing only __RANKED__ statistics in __OSU__ game mode.

            **PP:** **`{pp}`**
            **Rank:** `{global_rank}` | `{country_rank}` :flag_{country_code}:
            **Accuracy**: `{hit_accuracy}%`
            **Ranked points** `{ranked_score}`

            **SS** count: `{total_ss}`
            **SSH** count: `{total_ssh}`
            **S** count: `{total_s}`
            **SH** count: `{total_sh}`
            **A** count: `{total_a}`

            Player country is **{country_name}** :flag_{country_code}:

            Total played time: **{total_time}**

            [Go to website profile](https://osu.ppy.sh/users/{user_id})
        """


# Блок @CLIENT_COMMAND()
@client.command()
async def help(ctx):
    emb = discord.Embed(title='Нужны комманды? Вот они')
    for comma in HELP_COMMA:
        emb.add_field(name=format(PREFIX) + comma, value=HELP_COMMA.get(comma, 'описание упущено'))
    await ctx.send(embed=emb)


@client.command()
async def hi(ctx):
    await ctx.send('Здарова, <@{0}>)'.format(ctx.message.author.id))


@client.command()
async def clear(ctx, amount: int):
    for role in ctx.message.author.roles:
        if role.permissions.administrator:
            await ctx.channel.purge(limit=int(amount) + 1)
            await ctx.send('Успешно очищено **' + str(amount) + '** сообщений', delete_after=5.0)
            return
    await ctx.channel.send('Только пользователям с админ правами доступна эта опция', delete_after=5.0)


@client.command()
async def repeat(ctx):
    await ctx.send(format(ctx.message.content)[8::])


@client.command()
async def ping(ctx, arg):
    await ctx.send(f'<@{format(ctx.message.author.id)}>, ты будешь повторно упомянут через {arg} секунд',
                   delete_after=int(arg))
    await asyncio.sleep(int(arg))
    await ctx.send('<@{0}>, упоминаю тебя, как ты и просил'.format(ctx.message.author.id), delete_after=30.0)


@client.command()
async def osu(ctx, user: str):
    player = get_response(user)

    if 'error' in player:
        await ctx.send('Что-то пошло не так. Проверь введённые данные об игроке', delete_after=10)
        return

    username = player.get('username')
    avatar_url = player.get('avatar_url')
    user_id = player.get('id')
    statistics = player.get('statistics')
    level = statistics.get('level')
    current = level.get('current')

    embed = discord.Embed(
        title=f'{username} - Lvl. {current}',
        timestamp=datetime.fromtimestamp(datetime.timestamp(datetime.now())),
        description=write_description(player),
        colour=discord.Colour.purple(),
    )

    embed.set_thumbnail(url=avatar_url)
    embed.set_footer(text=f'ID: {user_id}', icon_url=avatar_url)

    await ctx.send(embed=embed)


@client.command()
async def calc(ctx):
    try:
        result = evaluate(ctx.message.content[6::])
    except SyntaxError:
        await ctx.send('С выражением что-то не то. Проверьте ввод', delete_after=5)
        return
    except (NameError, ValueError) as err:
        await ctx.send(f'Я не смог это высчитать из-за ошибки: "{err}"', delete_after=5)
        return
    if len(str(result)) > 4000:
        await ctx.send('Результат настолько большой, что я не могу его уместить в сообщение', delete_after=5)
        return
    await ctx.send(result)


@client.command()
async def viewreqperm(ctx):
    embed = discord.Embed(title='Требуемые разрешения')
    for var in requirements:
        embed.add_field(value=var)
    await ctx.send(format(embed))

# Блок @CLIENT.EVENT
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Этой команды не существует\nВоспользуйтесь командой "!help" для вывода списка доступных команд',
                       delete_after=5.0)


@client.event
async def on_ready():
    print(format(client.user) + ' запущен')
    ctx = client.get_channel(1010919950065614968)
    await ctx.send(HELLO_MSG)
    await client.change_presence(status=discord.Status.dnd,
                                 activity=discord.Activity(type=discord.ActivityType.listening,
                                                           name='поток бреда в чате'))


@client.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel != before.channel:
        print(f"Пользователь {member.name} зашёл на {after.channel.name}")

    if before.channel and after.channel != before.channel:
        print(f"Пользователь {member.name} вышел с {before.channel.name}")


client.run(cfg.encToken('discord'))