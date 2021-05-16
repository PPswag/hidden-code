import discord
from discord.ext import commands
import os
import asyncio
from asyncio import sleep
import random


prefix = "prefix u have"
bot = commands.Bot(command_prefix=prefix,intents=discord.Intents.all(), case_insensitive=True)
#bot.remove_command('help') <- if u  want

@bot.event
async def on_ready():
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
        
 
@bot.command()
    async def fight(ctx, member:discord.Member = None):
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
