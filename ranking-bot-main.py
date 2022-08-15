import discord
import collections
from datetime import datetime
from discord.ext import commands ,tasks
import random
import re

#guild ranking message 送付先
ranking_message_channel_dict = dict()



class Basic(commands.Cog):
    """
    基本機能
    """
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.loop.start()
        self.gd = dict()

    def ranking_message(self,guild_id):
        ranking_message = '>>> ✨今日の書き込み数ランキング✨\n'
        if guild_id in self.gd:
            c = collections.Counter(self.gd[guild_id]).most_common()

            ranking_count = 0
            # 同率の順位の場合、同率表示させるために必要
            prenumber = 0

            for user_id_and_number in c:
                ranking_count +=1
                # 10位までを表示する
                if ranking_count > 10:
                    break
                else:
                    print(user_id_and_number)
                    user_id = user_id_and_number[0]
                    number = user_id_and_number[1]
                    user = bot.get_user(user_id)

                    # 同率の順位の場合、同率表示させるために必要
                    if prenumber == number:
                        ranking_count -= 1
                    prenumber = number
                    ranking_message += f'{ranking_count}位:{user.display_name}, {number}回\n'

            ranking_message += f'総書き込みユーザー数:{len(set( self.gd[guild_id] ) )}名、総書き込み数：{len(self.gd[guild_id])}回'
            return ranking_message
        else:
            return f'{ranking_message}書き込み数計測不能(もしくは書き込み無し)'

    @commands.Cog.listener()
    async def on_message(self,msg):
        # 自身の書き込みは無視
        if msg.author == bot.user:
            return
        # gdのkeyにguild idが既にある場合、author idをvalueのlistに追加
        elif msg.guild.id in self.gd.keys():
            self.gd[msg.guild.id].append(msg.author.id)
        # gdのkeyにguild idがない場合、Keyにguild id。valueをlistとしてauthor idを追加
        else:
            self.gd[msg.guild.id] = [msg.author.id]

    @commands.command()
    async def myrank(self,ctx,*arg):
        '''
        あなたの書き込み数・ranking表示
        '''
        #author idによるguild内の書き込み数をカウント
        if ctx.guild.id in self.gd:
            if ctx.author.id in self.gd[ ctx.guild.id]:
                message_count = self.gd[ctx.guild.id].count(ctx.author.id)
                #guid内の各author idをkeyに、valueに同author idの出現回数をもつ辞書を作成。最頻値順でソートされる。
                c = collections.Counter(self.gd[ctx.guild.id]).most_common()

                # cの何番目でauthor idと一致するか
                ranking_count = 0
                prenumber = 0
                
                for user_id_and_number in c:
                    ranking_count += 1
                    user_id = user_id_and_number[0]
                    number = user_id_and_number[1]
                    if prenumber == number:
                        ranking_count -= 1
                    if user_id == ctx.author.id:
                        break
                await ctx.channel.send(f'>>> {ctx.author.nick or ctx.author.name}:{message_count}回, {ranking_count} 位')
        else:
            await ctx.send('>>> 書き込み0もしくはコマンドのみ書き込み')

    @commands.command()
    async def ranking(self,ctx,*arg):
        '''
        本日0:00以降の書き込み数ranking表示
        '''
        await ctx.channel.send(f'{self.ranking_message(ctx.guild.id)}')  

    # 書き込み数ランキングの自動発表
    @tasks.loop(seconds=60)
    async def loop(self):
        # 現在の時刻
        now = datetime.now().strftime('%H:%M')
        if now == '12:00' or now == '23:59':
            # botが入っているguildリスト
            guilds = [guild async for guild in bot.fetch_guilds(limit=200)]
            for guild in guilds:
                ranking_message = self.ranking_message(guild.id)
                if now == '12:00':
                    ranking_message = '*🔻中間発表🔻* \n' + ranking_message
                print(ranking_message)
                # 自動投稿先が設定されている場合
                if guild in ranking_message_channel_dict:
                    channel = ranking_message_channel_dict[guild]
                    await channel.send(ranking_message)
                # 自動投稿先が設定されていない場合、システムメッセージチャンネルに送付
                elif guild.system_channel:
                    await guild.system_channel.send(ranking_message)
                # システムメッセージチャンネルが設定されていない場合、ランダムなテキストチャンネルに投稿            
                elif guild.text_channels:
                    channel = random.choice(guild.text_channels)
                    await channel.send(f'{ranking_message}\n 現在、1日の集計を送信する指定チャンネルがないので、ランダムなチャンネルに送付しています。\n 指定するにはチャンネルで {bot.command_prefix}rktと書き込んで下さい。')
            self.gd.clear()

class EmojiRanking(commands.Cog):
    '''
    discord絵文字ランキング
    '''
    def __init__(self,bot):
        super().__init__()
        self.bot = bot
        self.emoji_gd = dict()
        self.loop.start()

    def ranking_message(self,guild_id):
        ranking_message = '>>> 🌟今日の絵文字書き込み数ランキング🌟\n'
        if guild_id in self.emoji_gd:
            c = collections.Counter(self.emoji_gd[guild_id]).most_common()

            ranking_count = 0
            # 同率の順位の場合、同率表示させるために必要
            prenumber = 0

            for emoji_and_number in c:
                ranking_count +=1
                # 10位までを表示する
                if ranking_count > 10:
                    break
                else:
                    print(emoji_and_number)
                    emoji = emoji_and_number[0]
                    number = emoji_and_number[1]
                    # 同率の順位の場合、同率表示させるために必要
                    if prenumber == number:
                        ranking_count -= 1
                    prenumber = number
                    ranking_message += f'{ranking_count}位:{emoji} :, {number}回 \n'

            ranking_message += f'総書き込み絵文字数:{len(set( self.emoji_gd[guild_id] ) )}、総書き込み数：{len(self.emoji_gd[guild_id])}回'
            return ranking_message
        else:
            return f'{ranking_message}書き込み数計測不能(もしくは書き込み無し)'

    @commands.Cog.listener()
    async def on_message(self,msg):
        # 自身の書き込みは無視
        if msg.author == bot.user:
            return
        elif not msg.guild.id in self.emoji_gd.keys():
            self.emoji_gd[msg.guild.id] = list()
        if re.findall(r'<:\w*:\d*>', msg.content):
            custom_emojis = re.findall(r'<:\w*:\d*>', msg.content)
            print(custom_emojis)
            for custom_emoji in custom_emojis:
                self.emoji_gd[msg.guild.id].append(custom_emoji)
                print(self.emoji_gd)


    @commands.command()
    async def emoranking(self,ctx,*arg):
        '''
        本日0:00以降のdiscord絵文字 使用数ランキング
        ※書き込まれた後削除されてしまった絵文字は表示されません。
        '''
        await ctx.channel.send(f'{self.ranking_message(ctx.guild.id)}')  

    # 書き込み数ランキングの自動発表
    @tasks.loop(seconds=60)
    async def loop(self):
        # 現在の時刻
        now = datetime.now().strftime('%H:%M')
        if now == '12:00' or now == '23:59':
            # botが入っているguildリスト
            guilds = [guild async for guild in bot.fetch_guilds(limit=200)]
            for guild in guilds:
                ranking_message = self.ranking_message(guild.id)
                if now == '12:00':
                    ranking_message = '*🔻中間発表🔻* \n' + ranking_message
                print(ranking_message)
                # 自動投稿先が設定されている場合
                if guild in ranking_message_channel_dict:
                    channel = ranking_message_channel_dict[guild]
                    await channel.send(ranking_message)
                # 自動投稿先が設定されていない場合、システムメッセージチャンネルに送付
                elif guild.system_channel:
                    await guild.system_channel.send(ranking_message)
                # システムメッセージチャンネルが設定されていない場合、ランダムなテキストチャンネルに投稿            
                elif guild.text_channels:
                    channel = random.choice(guild.text_channels)
                    await channel.send(f'{ranking_message}\n 現在、1日の集計を送信する指定チャンネルがないので、ランダムなチャンネルに送付しています。\n 指定するにはチャンネルで {bot.command_prefix}rktと書き込んで下さい。')
            self.emoji_gd.clear()

class Setting(commands.Cog):
    """
    設定用
    """
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def rks(self,ctx,*arg):
        '''
        1日の書き込み数ランキング自動投稿先を設定する
        '''
        ranking_message_channel_dict[ctx.guild] = ctx.channel
        await ctx.send(f'>>> 設定: \n自動投稿の1日のランキング集計はこのチャンネルに投稿されます')

    @commands.command()
    async def profile(self,ctx,*args):
        '''
        bot作成者の紹介
        '''
        embed= discord.Embed(title="**bot作成者**", description=f"趣味でbot等を作っています。\n [GitHubプロフィールページ](https://github.com/G1998G)")
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/60283066?s=400&v=4")
        await ctx.send(embed=embed)

class Omikuji(commands.Cog):
    """
    おまけ
    """
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def omikuji(self,ctx,*arg):
        '''
        おまけ機能omikuji
        '''
        contents = ["大吉", "吉", "中吉", "小吉", "末吉", "凶", "中凶", "大凶", "末凶", "ぴょん吉", "だん吉","かん吉"]
        res = random.choice(contents)
        await ctx.send(f'>>> omikuji結果: {res} ')
        if res == '大吉':
            await ctx.message.add_reaction("🎉")

class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "HelpCommand"
        self.command_attrs["description"] = "コマンドリストを表示します。"

    async def send_bot_help(self,mapping):
        '''
        ヘルプを表示するコマンド
        '''
        content = ""
        for cog in mapping:
            # 各コグのコマンド一覧を content に追加していく
            command_list = await self.filter_commands(mapping[cog])
            if not command_list:
                # 表示できるコマンドがないので、他のコグの処理に移る
                continue
            if cog is None:
                # コグが未設定のコマンドなので、no_category属性を参照する
                content += f"\n**{self.no_category}**\n"
            else:
                content += f"\n**{cog.qualified_name}**\n"
            for command in command_list:
                content += f"{self.context.prefix}{command.name}  `{command.help}`\n"
            content += "\n"
        embed = discord.Embed(title="**🌵ランキングbot🌵**",description=f'サーバー内の書き込み数ランキングを表示するbotです。 \n コマンドの先頭には「{self.context.prefix}」を付けてください。')
        embed = embed.add_field(name="**コマンドリスト**",value=content)

        await self.get_destination().send(embed=embed)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),intents=intents, help_command=HelpCommand())
bot.add_cog(Basic(bot))
bot.add_cog(Setting(bot))
bot.add_cog(Omikuji(bot))
bot.add_cog(EmojiRanking(bot))

@bot.event
async def on_ready():
    print(f'🟠ログインしました🟠{len(bot.guilds)}ギルドにログイン')

# 実行
bot.run( 'TOKEN')
