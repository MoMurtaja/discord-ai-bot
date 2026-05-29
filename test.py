import discord
from discord.ext import commands
from gtts import gTTS
import openai
import asyncio

# ================= CONFIG =================

DISCORD_TOKEN = "MTE0MjEzODMxNTg2NTM0MjExNA.GD_ern.lRvUMr3LCOvXRMfa7PoI04iOEuO1P-zTXc-FUE"
OPENROUTER_KEY = "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"

openai.api_key = OPENROUTER_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# ================= BOT SETUP =================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= MEMORY =================

memory = {}

def get_memory(guild_id):
    if guild_id not in memory:
        memory[guild_id] = [
            {"role": "system", "content": "You are a short, helpful Discord assistant."}
        ]
    return memory[guild_id]

# ================= SAFE SPEAK =================

def speak(vc, text):
    try:
        tts = gTTS(text=text, lang="en")
        tts.save("voice.mp3")

        if vc.is_playing():
            vc.stop()

        vc.play(discord.FFmpegPCMAudio("voice.mp3"))

    except Exception as e:
        print("TTS error:", e)

# ================= READY =================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ================= AI CHAT =================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if not message.guild:
        return

    guild_id = str(message.guild.id)

    vc = message.guild.voice_client

    history = get_memory(guild_id)

    history.append({
        "role": "user",
        "content": message.content
    })

    history[:] = history[-15:]

    try:

        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=history,
            max_tokens=120
        )

        reply = response["choices"][0]["message"]["content"]

        history.append({
            "role": "assistant",
            "content": reply
        })

        await message.channel.send(reply)

        # Speak ONLY if stable connection exists
        if vc and vc.is_connected():
            speak(vc, reply)

    except Exception as e:
        await message.channel.send(f"AI Error: {e}")

    await bot.process_commands(message)

# ================= JOIN (FIXED STABLE VERSION) =================

@bot.command()
async def join(ctx):

    if not ctx.author.voice:
        await ctx.send("Join a voice channel first.")
        return

    channel = ctx.author.voice.channel

    try:

        vc = ctx.guild.voice_client

        # HARD RESET broken connections
        if vc:

            try:
                if vc.is_connected():
                    await vc.disconnect(force=True)
            except:
                pass

            vc = None

        await asyncio.sleep(1.5)

        vc = await channel.connect(
            reconnect=True,
            timeout=15
        )

        await asyncio.sleep(2)

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected():
            await ctx.send("Voice failed to stabilize.")
            return

        await ctx.send(f"Joined {channel.name} successfully.")

    except Exception as e:
        await ctx.send(f"Join error: {e}")

# ================= LEAVE (FORCED RESET) =================

@bot.command()
async def leave(ctx):

    vc = ctx.guild.voice_client

    try:

        if vc:

            await vc.disconnect(force=True)

            await asyncio.sleep(1)

        await ctx.send("Left voice chat.")

    except Exception as e:
        await ctx.send(f"Leave error: {e}")

# ================= SAY (STABLE) =================

@bot.command()
async def say(ctx, *, text):

    vc = ctx.guild.voice_client

    if not vc or not vc.is_connected():
        await ctx.send("Not connected to voice.")
        return

    try:

        tts = gTTS(text=text, lang="en")
        tts.save("voice.mp3")

        if vc.is_playing():
            vc.stop()

        vc.play(discord.FFmpegPCMAudio("voice.mp3"))

        await ctx.send("Speaking...")

    except Exception as e:
        await ctx.send(f"Voice error: {e}")

# ================= MUSIC (LYRICS) =================

@bot.command()
async def music(ctx, *, prompt):

    try:

        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Write song lyrics and a title."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        await ctx.send(response["choices"][0]["message"]["content"])

    except Exception as e:
        await ctx.send(f"Music error: {e}")

# ================= RUN =================

bot.run(DISCORD_TOKEN)
