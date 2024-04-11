import discord
from discord.ext import commands
import sqlite3 as sq
import time, datetime, asyncio, random

client = commands.Bot(command_prefix="--")
#This command creates our bot (client is the object/variable that represents our bot)

client.remove_command('help')
#Removing the default help command so that we can customize it later



@client.event #This is called a decorator. It specifies when the function gets called.
#Here it tells the interpreter that the function gets called during a specific EVENT called 'on_ready'
async def on_ready():
    #This function automatically gets called when the bot is ready, when the bot comes online
    #The 'async' keyword is used to specify that the funtion is asynchronous, which means the program will not wait for this function to end but will continue with its other work whil this function runs simultaneously
    general_channel = client.get_channel(795871022942912513) #The number is the channel id in discord
    await general_channel.send('The hangman bot is online') #await is the same as async but async is for functions while await is for a statement
    await general_channel.send('Use the --help command to get to know more about this bot')
    db = sq.connect('profiles.sqlite') #Creating a connection with the database (database is a file that stores lots of data)
    cursor = db.cursor() #cursor is the object that writes/reads stuff from the database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles(
        user TEXT,
        wins INT,
        games INT,
        level INT
        ) ''')
    db.commit() #commit saves the changes
    cursor.close() #closing connections
    db.close()



@client.command(name='help') #here it tells us that the functions gets called only when the COMMAND is given 
async def help(ctx):
      #embeds are just fancy ways of displaying a message
      embed=discord.Embed(title="Bot commands", description="Prefix for this bot is '--'", color=0x1303fc)
      embed.add_field(name="hangman", value="Starts a hangman game             ", inline=True)
      embed.add_field(name="profile", value="Displays the profile of a user", inline=True)
      await ctx.send(embed=embed) #ctx stands for context. The context is an object that stores the channel name, message, author etc. of the command 



@client.command(name='hangman', aliases=['hm'])
async def hangman(ctx):
    player = ctx
    movies = ['inception', 'endgame','interstellar',' the godfather', 'schindler\'s list', 'forrest gump',' the matrix','the silence of the lambs','the lion king','the pianist','whiplash','the prestige','the dark knight rises','braveheart','toy story','up','inside out','gone girl','how to train your dragon']
    def check(msg):
        return msg.channel == ctx.channel
    def check2(msg):
        return msg.author == ctx.message.author and msg.channel == ctx.channel
    m = movies[random.randint(0, len(movies))-1]
    g_letters = []
    g_wletters = []
    def completed_word(m, g_letters):
        g = ''
        for i in m:
            if i in g_letters:
                g+=i + ' '
            elif i == ' ':
                g+= '  '   
            else:
                g+='_ '
        return g
    lives = 7
    life_emo = {7:'''     ——
    |  |
       |
       |
       |
       |
       |
    ———————''', 6:'''     ——
    |  |
    o  |
       |
       |
       |
       |
    ———————''', 5:'''     ——
    |  |
    o  |
   /   |
       |
       |
       |
    ———————''', 4:'''     ——
    |  |
    o  |
   /|  |
       |
       |
       |
    ———————''', 3:'''     ——
    |  |
    o  |
   /|\ |
       |
       |
       |
    ———————''', 2:'''     ——
    |  |
    o  |
   /|\ |
    |  |
       |
       |
    ———————''', 1:'''     ——
    |  |
    o  |
   /|\ |
    |  |
   /   |
       |
    ———————''', 0:'''     ——
    |  |
    o  |
   /|\ |
    |  |
   / \ |
       |
    ———————'''}

    await ctx.send('Do you want to start a single player game or a multiplayer game? Reply with `s` or `m`')
    mode = await client.wait_for('message', check = check2)
    
    if str(mode.content) == 'm':
        await ctx.send(f'{mode.author.mention} is starting a hangman multiplayer game!')
        await ctx.send('@everyone have 30 seconds to join')
        await ctx.send('Type \'join\' to join the game')
        players = []
        players += [player.message.author.mention]
        t = 30
        et = datetime.datetime.now() + datetime.timedelta(seconds=t)
        while True:
            try:
                time_left = et - datetime.datetime.now()
                pl = await client.wait_for("message", check=check, timeout=time_left.seconds)
                if str(pl.content).lower() == 'join':
                    if pl.author.mention in players:
                        await ctx.send('You have already joined the game!')
                    else:
                        players += [pl.author.mention]
                        await ctx.send(f'{pl.author.mention} has joined the game!')
            except asyncio.TimeoutError:
                await ctx.send('Time\'s up!')
                time.sleep(3)
                break

    mode = str(mode.content)
    await ctx.send('```The hangman game has begun!```')
    await ctx.send('```Prefix your guesses with \'hm-\'```')
    time.sleep(3)

    f = 1
    while True:
        if f == 1:
            g_movie = completed_word(m, g_letters)
            if g_movie.replace(' ', '') == m:
                won = True
                break
            await ctx.send(f'```{life_emo[lives]}```')
            await ctx.send('```Guesses: ' + ', '.join(g_wletters) + '\nMovie: ' + g_movie + '```')
        if mode == 'm':    
            msg = await client.wait_for('message', check=check)
        else:
            msg = await client.wait_for('message', check=check2)
        
        if (mode == 's' and msg.author == player.author and str(msg.content)[:3] == 'hm-') or (mode == 'm' and msg.author.mention in players and str(msg.content)[:3] == 'hm-'):
            f = 1
            msg = str(msg.content)[3:]
            if len(msg) != 1:
                if msg.lower() == m:
                    won = True
                    break
                if msg in g_wletters or msg in g_letters:
                    await ctx.send('```You have already guessed this letter before!```')
                    time.sleep(2)
                    continue
                await ctx.send('```Nope, that is not the movie```')
                time.sleep(2)
                g_wletters.append(msg)
                lives = lives - 1
                if lives == 0:
                    won = False
                    break
                continue
            elif msg in g_letters or msg in g_wletters:
                await ctx.send('```You have already guessed this letter before!```')
                time.sleep(2)
                continue
            else:
                if msg in m:
                    g_letters.append(msg)
                    await ctx.send('```Good guess! The letter was in the movie```')
                    time.sleep(2)
                else:
                    g_wletters.append(msg)
                    await ctx.send('```Tough luck, the letter was not there in the movie```')
                    time.sleep(2)
                    lives = lives - 1
                    if lives == 0:
                        won = False
                        break
        else:
            f = 0
    
    if won:
        if mode == 's':
            await ctx.send(f':partying_face: CONGRATULATIONS {player.message.author.mention}!! You have won this round of hangman')
        elif mode == 'm':
            await ctx.send(f':partying_face: CONGRATULATIONS {", ".join(players)}!! You have won this round of hangman')
        await ctx.send('The movie was `' + m.upper() + '`')
    else:
        await ctx.send(f'You\'ve lost all your lives! \nThe movie was `{m.upper()}`\nBetter luck next time')
    
    levels = {2:10, 3:25, 4:50, 5:100}
    if mode == 's':
        db = sq.connect('profiles.sqlite')
        cursor = db.cursor()
        cursor.execute(f'''
            SELECT user FROM profiles WHERE user = '{player.message.author.mention}'
        ''')
        result = cursor.fetchone()
        if result is None:
            cursor.execute(f'''
                INSERT INTO profiles(user, wins, games, level) VALUES ('{player.message.author.mention}', {int(won)}, 1, 1)
            ''')
        else:
            cursor.execute(f'''
                UPDATE profiles SET wins = wins+{int(won)}, games = games+1 WHERE user = '{player.message.author.mention}'
            ''')
            cursor.execute(f'''
                SELECT * FROM profiles WHERE user = '{player.message.author.mention}'
            ''')
            result = cursor.fetchone()
            w, l = result[1], 0
            if w == levels[2]:
                l = 2
            elif w == levels[3]:
                l = 3
            elif w == levels[4]:
                l = 4
            elif w == levels[5]:
                l = 5
            if l != 0:
                await ctx.send(f'GG {player.message.author.mention}! You have just reached Level {l}')
            
        db.commit()
        cursor.close()
        db.close()



@client.command(name='profile', aliases=['stats'])
async def profile(ctx, member: discord.Member = 'me'):
    if member == 'me':
        member = ctx.message.author
    avatar_url = member.avatar_url
    db = sq.connect('profiles.sqlite')
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT * FROM profiles WHERE user = '{member.mention}'
    ''')
    result = cursor.fetchone()
    if result is None:
        await ctx.send(f'{member.mention} hasn\'t even played a single player game yet!')
    else:
        result = list(result)
        embed=discord.Embed(title=f'{member.display_name}\'s Stats', color=0xff0000)
        embed.set_thumbnail(url=f"{avatar_url}")
        embed.add_field(name="Level", value=f":small_orange_diamond: {result[-1]}", inline=False)
        embed.add_field(name="Games played", value=f":small_blue_diamond: {result[2]}", inline=False)
        embed.add_field(name="Wins", value=f":white_check_mark:  {result[1]}", inline=False)
        embed.add_field(name="Win %", value=f":small_red_triangle: {round((result[1]*100)/result[2], 2)}%", inline=False)
        embed.add_field(name="Loses", value=f":x: {result[2] - result[1]}", inline=False)
        embed.add_field(name="Loss %", value=f":small_red_triangle_down: {round(((result[2] - result[1])*100)/result[2], 2)}%", inline=True)
        await ctx.send(embed=embed)
    cursor.close()
    db.close()


client.run('''bot_token here''')