import discord
from discord.ext import commands
import os
import asyncio
from asyncio import sleep
import random
import aiosqlite
import typing


prefix = "prefix u have"
bot = commands.Bot(command_prefix=prefix,intents=discord.Intents.all(), case_insensitive=True)
#bot.remove_command('help') <- if u  want

db = aiosqlite.connect("blacklist.sqlite")


@bot.event
async def on_ready():
    await db

    cursor = await db.cursor()

    await cursor.execute("""
      CREATE TABLE IF NOT EXISTS blacklist(
        guild_id INTEGER,
        user_id INTEGER,
        blacklisted BOOL
      )""")
    await db.commit()
    print(f'Logged in as {bot.user}\n{bot.user.id}')
    await status()
    
async def status():
    while True:
        await bot.wait_until_ready()
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(bot.guilds)} servers!  '))
        await sleep(40)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'my prefix {prefix}'))
        await sleep(15)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.commands)} commands"))
        await sleep(15) # make it anything u want
        
 
async def GetMessage(
  bot, ctx, contentOne = "Default message", contentTwo = "\uFEFF", timeout = 100
):


  embed = discord.Embed(title = f"{contentOne}", description=f"{contentTwo}")
  sent = await ctx.send(embed=embed)

  try:
    msg = await bot.wait_for("message", timeout=timeout, check = lambda message: message.author == ctx.author and message.channel == ctx.channel,
    )
    if msg:
      return msg.content
  except asyncio.TimeoutError:
    return False # got this code from camberra, it will be modified.

@bot.command()
async def giveaway(ctx):
      await ctx.send("Ok we will run giveaway, now simply answer the questions **below**.")

      questionlist = [ 
        ["In which channel should the giveaway be in?", "Mention it!"],
        ["How long should this giveaway be?", "**AND AGAIN** use `s|m|h|d` ."],
        ["What is the prize of this giveaway?", "BE ***HUMBLE***."]
        ]
      answers = {}

      for i, question in  enumerate(questionlist):  
        answer = await GetMessage(bot, ctx, question[0], question[1])

        if not answer:
          await ctx.send("Oyy, give me an answer. ***BRUH***")
        
        answers[i] = answer

      em = discord.Embed(title="Giveaway questions", color = discord.Color.orange())
      for key, value in answers.items():
        em.add_field(name = f"Question {questionlist[key][0]}", value=f"Answer: `{value}`", inline=False)

      m = await ctx.send("Are these all valid? Gimme answer!", embed=em)
      await m.add_reaction("✅")
      await m.add_reaction("❌")

      try:
        reaction, member = await bot.wait_for('reaction_add', timeout=45, check = lambda reaction, user: user == ctx.author and reaction.message.channel == ctx.channel)
      except asyncio.TimeoutError:
        await ctx.send("You took too much. Sorry!")
        return

      if str(reaction.emoji) not in ["✅", "❌"] or str(reaction.emoji) == "❌":
        await ctx.send("Giveaway canceled!")

      channelid = re.findall(r"[0-9]+", answers[0])[0]
      channel = self.bot.get_channel(int(channelid))

      time = convert(answers[1])

      em = discord.Embed(title="**GIVEAWAY**", description=f" **Prize** : {answers[2]}\n **Time** : {time}\n **Winners** : 1", color = discord.Color.orange())
      em.set_footer(text= f"Holden by {ctx.author.name}.")
      em.set_thumbnail(url = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/mozilla/36/party-popper_1f389.png')
      message = await channel.send(embed=em)
      await message.add_reaction("EMOJI u want")

      await asyncio.sleep(time)

      message = await channel.fetch_message(message.id)
      users = await message.reactions[0].users().flatten()
      users.pop(users.index(ctx.guild.me))

      if len(users) == None:
        await channel.send("There was no winner! *Sucks*.")

      winner = random.choice(users)

      await channel.send(f"**Congrats** {winner.mention}!**\n Message him {ctx.author.mention} to get your beloved prize.")
        

        
 
blacklist = set() # to blacklsit users

@bot.command(name="blacklist")
async def _blacklist(ctx, mode, target: discord.Member = None, *, reason=None):
    """Owner Command, will blacklist a user from bot"""
    cursor = await db.cursor()
    if target == None:
      return await ctx.send("Bruh mention someone") # if you want to blacklsit roles jsut do this same code, for giveaways ofc, and change the param to discord.Role and create a new table
    await cursor.execute("SELECT user_id FROM blacklist WHERE user_id=?", (target.id,))
    row = await cursor.fetchone()
    if not row:
      await cursor.execute("INSERT INTO blacklist(guild_id, user_id, blacklisted) VALUES(?, ?, ?)", (ctx.guild.id, target.id, False, ))
    # if target.id == ctx.author.id:
    #   return await ctx.send("Dont blacklist yourself idiot")
    if mode != "remove" and mode != "add":
      return await ctx.send("Mate, it has to be add or remove")
    blacklists = True if mode == "add" else False
    await cursor.execute("UPDATE blacklist SET blacklisted = ? WHERE user_id = ? AND guild_id=?", (blacklists, target.id, ctx.guild.id))
    await db.commit()

    if mode == "add":
      em = discord.Embed(title="Man got blacklisted", description="Now you can't use bot you noob", color = discord.Color.red())
      em.add_field(name="Reason", value=reason or "None specified")
      await target.send(embed=em)
      await ctx.send(f"Succesfully blacklisted {target.name}")
      blacklist.add(target.id)
#       print(blacklist)
    else:
      await ctx.send(f"{target.name} is unblacklsited YAY!!!!")
      try:
        blacklist.remove(target.id)
        print(blacklist)
      except KeyError:
        return await ctx.send(f"Cant remove {target.name}")
@bot.command()
async def blacklisted(ctx):
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM blacklist WHERE guild_id=? AND blacklisted=?", (ctx.guild.id, True,))
    row = await cursor.fetchall()
    print(row)

@bot.event
async def on_message(message):
  if message.author.id in blacklist: # had to do in main file too lazy to do all the cog work since it would cause so many problems
    return 
  await bot.process_commands(message)
        
@bot.command()
    async def fight(ctx, member:discord.Member = None):# my code for people who want dank meme fight cmd
        health = {
            ctx.author: 100,
            member: 100
        }
      
        if ctx.author == member:
            await ctx.send("LEL, You seriously wanna beat the hell out of yourself, but **__NO__**.")
            return

        if member == None:
            await ctx.send("You aren't an airbender to fight with air, so choose an opponent.")
            return

#         if rank(ctx, member) < 10:
#             await ctx.send("**You need to be lvl 10 or higher!**")
#             return
# this if statement is only if u have the lvl code DO NOT USE

        option_1 = "punch"
        option_2 = "defend"
        option_3 = "end"
        damage = random.randint(1, 40)
        defend = random.randint(1, 40)
      

        em = discord.Embed(color=member.color)

        em.set_author(name=f"Peace was **never** an option. Now you are fighting {member}!")

        em.add_field(name="Options", value=f"{member.mention} what do u want to do: \n `{option_1}` `{option_2}` or `{option_3}`?", inline=False)

        em.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=em)

        skip = False

        players = [(ctx.author, member),(member,ctx.author)]

        for defender, attacker in itertools.cycle(players):
            if(skip):
                skip = False
                continue
            try: 
                msg = await prompt_choice(ctx, attacker)
            except asyncio.TimeoutError:
                await ctx.send(f"**{attacker.mention}** is nothing more than a sucker, so he left!")
                return

            if msg.lower() == 'punch':
                damage = random.randint(1, 40)
                health[defender] -= damage
                await ctx.send(f"Your serious punch just dealt {damage} damage and now {defender.mention} hp is at {health[defender]}!")
            elif msg.lower() == 'defend':
                heal = random.randint(1, 30)
                if health[attacker] == 100:
                    await ctx.send("Oy, You are at your max kiddo, you can't heal anymore.")
                    await ctx.send(f"**{attacker.mention}, what will you do now? OPTIONS: `punch` `defend` or `end`**")
                    skip = True
                    continue
                else:   
                    health[attacker] += heal
                    if health[attacker] > 100:
                        health[attacker] = 100
                    await ctx.send(f"You just healed {heal} hp and now {attacker.mention} is at hp is at {health[attacker]}!")
            elif msg.lower() == 'end':
                await ctx.send("**You ran away, your opponent wins scrub!**")
                return

            else:
                await ctx.send(f"{attacker.mention} did not enter a valid option!")
                await ctx.send(f"**{attacker.mention}, what will you do now? OPTIONS: `punch`, `defend`, `end`**")
                skip = True
                continue
              
          

            if health[attacker] <= 0:
                if health[attacker] < 0:
                    health[attacker] = 0
                await ctx.send(f"**{defender.mention}** has won. You are in for a treat.!")
                break
            elif health[defender] <= 0:
                if health[defender] < 0:
                    health[defender] = 0
                await ctx.send(f"**{attacker.mention}** won. You're in for a treat.!")
                break

            await ctx.send(f"**{defender.mention}, what will you do now? OPTIONS: `punch` `defend` `end`**")
            
async def prompt_choice(ctx: commands.Context, member: discord.Member) -> str: # now we need to import random...
   valid_choices = ["bm", "sp", "sd", "mc", "all", "end"] 
   responses = await bot.wait_for('message', check = lambda m: all((m.author == member, m.channel == ctx.channel)), timeout=60)
    
   return responses.content
              





bot.run(os.getenv('TOKEN'))
