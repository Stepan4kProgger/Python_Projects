import interactions
from interactions import slash_command, listen, Permissions, slash_default_member_permission
from interactions import Embed, EmbedField, EmbedFooter
from interactions.api.events import VoiceUserLeave, VoiceUserMove, VoiceUserJoin

token = ''
bot = interactions.Client(token=token)
owners_channels = dict()
servers_channels = dict()
with open('channel_creator_cfg.txt', 'r') as f:
    text = f.read()
    if len(text):
        for val in text.split('\n'):
            item = val.split('\t')
            servers_channels.update({int(item[0]): int(item[1])})
            
color = 12255232


@slash_command(name="set", description="Обозначает управляющий канал",
               options=[interactions.SlashCommandOption('voice_channel', type=interactions.OptionType.CHANNEL)])
@slash_default_member_permission(Permissions.MANAGE_CHANNELS)
async def set_creator_channel(ctx: interactions.SlashContext, voice_channel: interactions.BaseContext.channel):
    if voice_channel.type != 2:
        await ctx.send(embed=Embed(title=f'Выбранный канал <#{voice_channel.id}> не является голосовым', color=color,
                                   description='Функционал бота позволяет работать только с голосовым каналом'),
                       delete_after=12.5)
        return
    if ctx.guild.id not in servers_channels.keys():
        servers_channels.update({ctx.guild.id: voice_channel.id})
        with open('channel_creator_cfg.txt', 'r') as f:
            checksum = '\n' if len(f.read()) else ''
        with open('channel_creator_cfg.txt', 'a') as f:
            f.write(f'{checksum}{str(ctx.guild.id)}\t{str(voice_channel.id)}')
    else:
        servers_channels[ctx.guild.id] = voice_channel.id
        with open('channel_creator_cfg.txt', 'w') as f:
            f.write('\n'.join([f'{str(key)}\t{str(val)}' for key, val in servers_channels.items()]))
    await ctx.send(embed=Embed(title=f'Успешно задан канал - <#{voice_channel.id}>', color=color,
                               description='Изменить его можно так же при помощи команды **/set**'),
                   delete_after=12.5)


@slash_command(name="channel", description="Выдаёт информацию об управляющем канале")
async def creator_channel_info(ctx: interactions.SlashContext):
    try:
        # basic information
        chat = ctx.guild.get_channel(servers_channels[ctx.guild.id])
        await ctx.send(embed=Embed(title=f'Текущий управляющий канал - <#{chat.id}>', color=color,
                                   description='Чтобы изменить его, используйте команду **/set**'),
                       delete_after=12.5)
    except KeyError:
        # if not found in DB
        await ctx.send(embed=Embed(title='Управляющий канал для данного сервера не задан', color=color,
                                   description='Чтобы задать его, используйте команду **/set**'),
                       delete_after=12.5)
    except:
        # if deleted or unreachable
        await ctx.send(embed=Embed(title='Управляющий канал ныне недоступен', color=color,
                                   description='Задайте новый, используя команду **/set**'),
                       delete_after=12.5)


@slash_command(name="help", description="Описание и команды")
async def help_command(ctx: interactions.SlashContext):
    await ctx.send(embed=Embed(title='Описание бота', color=color,
                               description='При заходе в управляющий канал у вас создастся собственный голосовой '
                                           'канал, в который вы будете перемещены. При покидании его он удалится, '
                                           'либо его авторство передастся другому пользователю, находящемуся в нём.'
                                           '\n\n**Список команд**',
                               fields=[EmbedField(name='**/set** *канал*',
                                                  value='Устанавливает голосовой канал в качестве управляющего.'),
                                       EmbedField(name='**/channel**',
                                                  value='Возвращает информацию о том, какой канал является управляющим.')
                                       ],
                               footer=EmbedFooter(text='Использовать через /-меню',
                                                  icon_url='https://cdn.discordapp.com/attachments/1141167372363907092'
                                                           '/1141167410934730823/neon-arrows-that-look-in-different-'
                                                           'directions-in-a-blue-and-pink-glow-3d-rendering_503815-180.png')),
                   delete_after=60)


@listen(VoiceUserLeave)
async def owner_left_own_channel(ctx: VoiceUserLeave):
    if ctx.author.id in owners_channels.keys() and ctx.channel.id == owners_channels[ctx.author.id]:
        remain_ids = [item.id for item in ctx.channel.voice_members]
        remain_ids.remove(ctx.author.id)
        if len(remain_ids):
            new_author = remain_ids[0]
            await ctx.channel.edit(name=f'Канал {str(ctx.channel.guild.get_member(new_author))[1:]}')
            owners_channels[new_author] = owners_channels.pop(ctx.author.id)
        else:
            await ctx.channel.delete()
            owners_channels.pop(ctx.author.id)
    pass


@listen(VoiceUserJoin)
async def create_private_channel(ctx: VoiceUserJoin):
    try:
        if servers_channels[ctx.channel.guild.id] == ctx.channel.id:
            ch_info = await ctx.channel.guild.create_voice_channel(f'• {str(ctx.author)[1:]}',
                                                                   category=ctx.channel.category)
            await ch_info.add_permission(ctx.author, allow=[Permissions.MUTE_MEMBERS,
                                                            Permissions.MOVE_MEMBERS,
                                                            Permissions.DEAFEN_MEMBERS])
            owners_channels.update({ctx.author.id: ch_info.id})
            await ctx.author.move(ch_info.id)
            print('Channel created for', ctx.author)
        else:
            pass
    except KeyError:
        pass


@listen(VoiceUserMove)
async def user_moved(ctx: VoiceUserMove):
    try:
        if ctx.previous_channel.id == owners_channels[ctx.author.id]:
            await owner_left_own_channel(VoiceUserLeave(author=ctx.author,
                                                        channel=ctx.previous_channel,
                                                        state=ctx.state))
            if ctx.new_channel.id == servers_channels[ctx.new_channel.guild.id]:
                await ctx.author.disconnect()
    except KeyError:
        await create_private_channel(VoiceUserJoin(author=ctx.author,
                                                   channel=ctx.new_channel,
                                                   state=ctx.state))


bot.start()
