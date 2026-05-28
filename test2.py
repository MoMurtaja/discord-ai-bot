import discord
from discord.ext import commands

TOKEN = "MTE0MjEzODMxNTg2NTM0MjExNA.GSUbLH.XLOHByrkw9p-nNlOTLqVty4TQt6GR8mIiVHDHw"

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print("READY")

@bot.command()
async def join(ctx):

    if ctx.author.voice is None:
        await ctx.send("Join VC first")
        return

    channel = ctx.author.voice.channel

    await channel.connect()

    await ctx.send("Joined!")

bot.run(TOKEN)
