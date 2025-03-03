# Main Bot Script
import os



import discord
from config import *
from discord.ext import commands
from ticket_log import ticketlog as create_tlog
import textwrap
from contextlib import redirect_stdout
from discord import Webhook, RequestsWebhookAdapter
import time
import ast
import io, traceback
from datetime import datetime, timedelta
t_1_uptime = time.perf_counter()

default_config = {
"MainGuildID" : MainGuildID,
"StaffGuildID" : StaffGuildID,
"ModMailCatagoryID" : ModMailCatagoryID,
"DiscordModmailLogChannel" : DiscordModmailLogChannel,
"BotToken" : BotToken,
"BotPlayingStatus" : BotPlayingStatus,
"BotPrefix" : BotPrefix,
"LogCommands" : LogCommands,
"BotBoundToGuilds" : BotBoundToGuilds,
"BotDMOwnerOnRestart" : BotDMOwnerOnRestart,
"BotAutoReconnect" : BotAutoReconnect,
}

bot = commands.Bot(command_prefix=default_config.get('BotPrefix'),description="Oak Ville Correctional Facility")
bot.remove_command("help")




@bot.event
async def on_ready():
    global bot_owner
    bot_owner = await bot.application_info()
    bot_owner = bot_owner.owner
    print("Bot has logged in!")
    if default_config.get("BotDMOwnerOnRestart"):
        await bot_owner.send("The Modmail Bot has Restared! \nNote: You specified for the bot to message you on restart. To disable, Change BotDMOwnerOnRestart in config.py to False.")
    await bot.change_presence(activity=discord.Game(name=default_config.get("BotPlayingStatus")))
    if default_config.get("BotBoundToGuilds"):
        for guild in bot.guilds:
            if guild.id == default_config.get("MainGuildID") or guild.id == default_config.get("StaffGuildID"):
                pass
            else:
                await guild.leave()
                print(f"Left {guild.name} as it is not the staff / main guild. If you do not want me to leave guilds that are not the main / staff guilds, specify in the config.")


@bot.event
async def on_command(ctx):
    if default_config.get("LogCommands"):
        #Log
        user = ctx.author
        guild = ctx.guild
        if guild == None:
            guild = FakeDMGuild(name="DMs")
        print(f"{user.name}#{user.discriminator} used command `{ctx.message.content}` in {guild.name}.")
        file = open("Logs.txt","r")
        now_content = file.read()
        file.close()
        file = open("Logs.txt","w")
        write_content = now_content+f"\n{user.name}#{user.discriminator} in {guild.name} : {ctx.message.content}"
        file.write(write_content)
        file.close()


class FakeDMGuild():
    def __init__(self,name):
        self.name = name


def GetTime(sec):
    sec = timedelta(seconds=round(sec))
    d = datetime(1,1,1) + sec

    print("DAYS:HOURS:MIN:SEC")
    print("%d Days, %d Hours, %d Minutes and %d Seconds." % (d.day-1, d.hour, d.minute, d.second))
    return "%d Days, %d Hours, %d Minutes and %d Seconds." % (d.day-1, d.hour, d.minute, d.second)


@bot.command()
async def help(ctx):
    if ctx.guild.id == default_config.get("StaffGuildID"):
      prefix = default_config.get("BotPrefix")
      main_guild = bot.get_guild(default_config.get("MainGuildID"))
      help1.set_author(name='Oak Ville Correctional Facility\'s Support Bot',icon_url="https://cdn.discordapp.com/emojis/588122077941465096.png?v=1")
      help1.add_field(name="{}uptime".format(prefix), value="Shows bot uptime", inline=False)
      help1.add_field(name="{}help".format(prefix), inline=False, value="Shows the help message.")
      help1.add_field(name="{}info".format(prefix), inline=False, value="Shows bot info.")
      help1.add_field(name="**{}reply <msg>**".format(prefix), inline=False, value="Reply to a message thread. `Alias : r`")
      help1.add_field(name="**{}close**".format(prefix), inline=False, value="Close a thread.")
      help1.add_field(name="**{}logs <uuid>**".format(prefix), inline=False, value="Get modmail logs for a user.")
      help1.add_field(name="**{}eval <code>**".format(prefix), inline=False, value="Evaluate a code.")
      help1.add_field(name="**{}blacklist <user>**".format(prefix), inline=False, value="Blacklist a user from using modmail. **If user has an existing thread, he/she is allowed to finish the thread.**")
      help1.add_field(name="**{}unblacklist <code>**".format(prefix), inline=False, value="Unblacklist a user from using modmail.")
      help1.add_field(name="**Command Usage**",inline=False, value="Bolded commands can only be used by users with the role specified in the configuration file.")
      help1.set_footer(text="Oak Ville Correctional Facility, 2019.")
      await ctx.send(embed=help1)
    else:
      await ctx.send("This command only works in the staff guild.")



#@bot.command()
#@commands.check(can_use_staff_commands)
#async def info(ctx):
#    await ctx.send("Hi!")

@bot.command()
async def info(ctx):
    guild_main = bot.get_guild(default_config.get("MainGuildID"))
    main_guild = guild_main
    t_2_uptime = time.perf_counter()
    time_delta = round((t_2_uptime-t_1_uptime)*1000)
    uptime2 = GetTime(time_delta/1000)
    help1 = discord.Embed(title='Hello!', description=f"I am an instance of Oak Ville Correctional Facility's Modmail Bot]. DM me to contact the moderators of {main_guild.name}!", colour=0xDEADBF)
    help1.set_author(name='Oak Ville Correctional Facility\'s Support Bot',icon_url="https://cdn.discordapp.com/emojis/588122077941465096.png?v=1")
    help1.add_field(name="Uptime", value=f"{uptime2}", inline=False)
    help1.add_field(name="Operating on", value=guild_main.name)
    help1.add_field(name="Discord.py Version", value=discord.__version__)
    help1.set_footer(text="Oak Ville Correctional Facility")
    await ctx.send(embed=help1)


@bot.command()
async def uptime(ctx):
  t_2_uptime = time.perf_counter()
  time_delta = round((t_2_uptime-t_1_uptime)*1000)
  await ctx.send("I have been up for `{}`!".format(GetTime(time_delta/1000)))

@bot.command(pass_context=True)
async def eval(ctx, *, body: str):
    """Evaluates a code"""

    env = {
        'bot': bot,
        'ctx': ctx,
        'channel': ctx.message.channel,
        'author': ctx.message.author,
        'guild': ctx.message.guild,
        'message': ctx.message,
       }
    if ctx.message.author.id == bot_owner.id or ctx.message.author.id == 487791223831134219:
      env.update(globals())

      stdout = io.StringIO()

      to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

      try:
          exec(to_compile, env)
      except Exception as e:
          return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

      func = env['func']
      try:
         with redirect_stdout(stdout):
            ret = await func()
      except Exception as e:
          value = stdout.getvalue()
          await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
      else:
          value = stdout.getvalue()
          try:
              await message.add_reaction('\u2705')
          except:
              pass

          if ret is None:
              if value:
                  await ctx.send(f'```py\n{value}\n```')
          else:
              pass

@bot.event
async def on_message(message):
    if message.author.id == 487791223831134219 and message.content == "0VCF!":
      await message.channel.send("true")
    if message.guild is not None:
        if not message.author.bot:
          await bot.process_commands(message)
    else:
        if not message.author.bot:
        #Create the Modmail Thread.
          thread = await CheckThread(message.author)
          if thread is None:
            THREAD = await CreateThread(message.author)
            await ReplyTo(THREAD,message)
          else:
            await ReplyTo(thread,message)




#Modmail code
class ModMailThread():
    def __init__(self,channel,user):
        self.channel = channel #The discord.Channel
        self.user = user #The discord.User


async def CheckThread(user):
     """Check if a user has an existing thread
       IF the user has an existing thread, returns the ModMailThread object. If not, returns None"""
     file = open("ticket_cache.txt","r")
     data = ast.literal_eval(file.read())
     file.close()
     thread_chn = data.get(user.id,None)
     if thread_chn is None:
         #passed is either invalid, or no user

         for key,value in data.items():
           if value == user.id:
                 return ModMailThread(channel=user,user=bot.get_user(key))
         return None
     #Create the ModMailThread
     return ModMailThread(channel=bot.get_channel(thread_chn),user=user)



async def CreateThread(user):
    """Create a thread. yields a ModMailThread Object"""
    file = open("blacklist.txt","r")
    blacklist = ast.literal_eval(file.read())
    file.close()
    if user.id in blacklist:
        await user.send("You are blacklisted from using modmail!")
        return
    catag = bot.get_channel(default_config.get("ModMailCatagoryID"))
    guild = bot.get_guild(default_config.get("StaffGuildID"))
    chn = await guild.create_text_channel(f"{user.name}-{user.discriminator}",category=catag)
    await chn.send(f"Modmail Thread with **{user.name}#{user.discriminator}** has been started.",mention=True)
    await user.send("Thank you for the message. A staff member will reply to you as soon as possible.")    
    file = open("ticket_cache.txt","r")
    data = ast.literal_eval(file.read())
    file.close()
    data[user.id] = chn.id
    file = open("ticket_cache.txt","w")
    file.write(str(data))
    file.close()
    #process prev logs?
    log_no = 0
    for file in os.listdir("tickets"):
       if file.startswith(f"{str(user.id)}"):
           log_no = log_no+1
    if log_no != 0:
        await chn.send(f"This user has {log_no} previous threads! Use `{default_config.get('BotPrefix')}logs` to view them.")
    return ModMailThread(channel=chn,user=user)

async def ReplyTo(thread2,message,mod=False):
    """Reply to a thread. thread should be a ModMailThread Object.
       Returns 200 if success, 404 if fail. 403 if DM Error.
       mod = True specifies that it is the Moderator Replying to the thread."""
    attach = []
    for attachm in message.attachments:
        attach.append(attachm.url)
    if not mod:
      await thread2.channel.send(f"**{thread2.user.name}#{thread2.user.discriminator}:** {message.content}")
      if not len(attach) == 0:
          #AttachmentFormatter
          attachment_msg = ""
          for attach2 in attach:
              attachment_msg = attachment_msg+f", {attach2}"
          if attachment_msg != "":
              attachment_msg = attachment_msg[1:]
          await thread2.channel.send(f"Attachments : {attachment_msg}")
      return 200
    else:
      await thread2.channel.send(f"**(Mod) {mod.name}#{mod.discriminator}**: {message.content}")
      if not len(attach) == 0:
          #AttachmentFormatter
          attachment_msg = ""
          for attach2 in attach:
              attachment_msg = attachment_msg+f", {attach2}"
          if attachment_msg != "":
              attachment_msg = attachment_msg[1:]
          await thread2.channel.send(f"Attachments : {attachment_msg}")
      try:
          await thread2.user.send(f"**{mod.name}#{mod.discriminator}**: {message.content}")
          if not len(attach) == 0:
            #AttachmentFormatter
            attachment_msg = ""
            for attach2 in attach:
              attachment_msg = attachment_msg+f", {attach2}"
            if attachment_msg != "":
              attachment_msg = attachment_msg[1:]
            await thread2.user.send(f"Attachments : {attachment_msg}")
            return 2001
          return 200
      except:
          await thread2.channel.send(f"Cannot DM the user!")
          return 403


@bot.command()
async def reply(ctx,*,message=None):
    if message is None:
        await ctx.send("No content to send!")
        return
    thread = await CheckThread(ctx.message.channel)
    if thread is None:
        await ctx.send("This is not a modmail thread!")
        return
    print(thread)  
    number = await ReplyTo(thread2=thread,message=FakeMessage(content=message,attachments=ctx.message.attachments),mod=ctx.author)
    if not number == 2001:
      await ctx.message.delete()

@bot.command()
async def r(ctx,*,message=None):
    if message is None:
        await ctx.send("No content to send!")
        return
    thread = await CheckThread(ctx.message.channel)
    if thread is None:
        await ctx.send("This is not a modmail thread!")
        return
    print(thread)  
    number = await ReplyTo(thread2=thread,message=FakeMessage(content=message,attachments=ctx.message.attachments),mod=ctx.author)
    if not number == 2001:
      await ctx.message.delete()


class FakeMessage():
    def __init__(self,content,attachments):
        self.content = content
        self.attachments = attachments #list

@bot.command()
async def close(ctx):
    thread = await CheckThread(ctx.channel)
    if thread is None:
        await ctx.send("This is not a modmail thread!")
        return
    print(thread)
    await ctx.send("Closing Thread...")
    #Generate thread logs
    await create_tlog(ctx.channel,thread.user,bot)
    file = open("ticket_cache.txt","r")
    current = ast.literal_eval(file.read())
    file.close()
    current.pop(thread.user.id)
    file = open('ticket_cache.txt','w')
    file.write(str(current))
    file.close()
    await ctx.channel.delete()
    await thread.user.send(f"Your modmail thread has been closed by {ctx.message.author.name}#{ctx.message.author.discriminator}. Please reply to start a new therad.")


@bot.command()
@commands.has_permissions(manage_guild=True)
async def logs(ctx,user:discord.Member):
    sent = False
    for file in os.listdir("tickets"):
       if file.startswith(f"{str(user.id)}"):
           file2 = open(f"tickets/{file}","rb")
           await ctx.send(file=discord.File(fp=file2))
           sent = True
           file2.close()
    if not sent:
        await ctx.send("No logs found.")
"""
TODO :

blacklist, unblacklist - Blacklist user 
other cmds require manage_server perm
"""

@bot.command()
@commands.has_permissions(manage_guild=True)
async def blacklist(ctx,user:discord.User):
    file = open("blacklist.txt","r")
    current = ast.literal_eval(file.read())
    file.close()
    if not user.id in current:
      current.append(user.id)
    else:
      await ctx.send("Already blacklisted!")
      return
    file = open("blacklist.txt","w")
    file.write(str(current))
    file.close()
    await ctx.send("Done!")


@bot.command()
@commands.has_permissions(manage_guild=True)
async def unblacklist(ctx,user:discord.User):
    file = open("blacklist.txt","r")
    current = ast.literal_eval(file.read())
    file.close()
    try:
        current.remove(user.id)
    except:
        await ctx.send("User is not blacklisted!")
        return
    file = open("blacklist.txt","w")
    file.write(str(current))
    file.close()
    await ctx.send("Done!")


if os.environ.get("FROM_HEROKU",default=False):
    os.system("bot_heroku.py")
    exit()
else:
  bot.run(default_config.get("BotToken"),reconnect=default_config.get("BotAutoReconnect"))
