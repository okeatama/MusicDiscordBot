import random
import linecache
import asyncio
import discord
from discord.ext import commands, tasks
import youtube_dl
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("..//secret.env")
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)

client = commands.Bot(command_prefix="!")


# @client.command()
# async def helpcommand(ctx):
#     embed = discord.Embed(
#         title = "This is title",
#         description = "This is description",
#         color = discord.Color.blue()
#         )
#     embed.add_field(name="!play", value="give YT URL after the command and play the song in General VC", inline = True)
#     embed.add_field(name="!leave", value="bot stops playing music and leaves VC",inline = True)
#     embed.add_field(name="!pause", value="pauses music",inline = True)
#     embed.add_field(name="!resume", value="resumes music",inline = True)
#     embed.add_field(name="!stop", value="stop playing music, but still in VC",inline = True)
#     embed.add_field(name="!game", value="starts the guessing game by playing music for 5 seconds at a time. en for english, jp for japanese",inline = True)
#     embed.add_field(name="!guess", value="guess the song in the game",inline = True)
#     embed.add_field(name="!part", value="plays the next 5 seconds of song during the game",inline = True)
    
#     await ctx.send(embed = embed)

@client.command(
    brief = "Play song",
    help = "Give YT URL after the command"    
)
async def play(ctx, url : str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            
    except PermissionError:
        await ctx.send("Wait for playing music to end or use '!stop'")
        return
        
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name = "General")
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
        
    ydl_opts = {
        "format": "bestaudio",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3", #preferred file
            "preferredquality": "192",
            }],
        }
        
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
    
    voice.play(discord.FFmpegPCMAudio("song.mp3"))
    
    
@client.command(
    brief = "Bot leave the VC",
    help = "Bot stops playing music and leaves the VC"
    )
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else: 
        await ctx.send("Bot is not connected to VC")
        
@client.command(
    brief = "Pauses song being played",
    help = "Can be resumed by using resume command"
    )
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("No audio is playing")
        
@client.command(
    brief = "Resumes paused song",
    help = "Resumes paused song by pause command"
    )
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice.is_paused:
        voice.resume()
    else:
        await ctx.send("Audio is already playing")

@client.command(
    brief = "Stop playing song, cannot be resumed",
    help = "Similiar to leave, but bot stays in VC"
    )
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    voice.stop()
    
@client.command(
    brief = "Starts a guessing game",
    help = "give en for english songs, jp for japanese songs. First 5 seconds will be played, use guess to guess the name and part for next 5 second"
    )
async def game(ctx, genre):
    global songName
    global path
    
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name = "General")
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    
    #for english
    if genre.lower() == "en":
        with open("musiclistjp.txt") as f:
            FileLine = len(f.readlines())
            
        randNumber = random.randint(1, FileLine)
        songName = linecache.getline("musiclisten.txt", randNumber)
        path = "./enmusic/" + songName
        path = path[:-1] + ".mp3"
        file = open("temp.txt","w")
        file.write(songName)
        file.close()
        
    #for japanese
    elif genre.lower() == "jp":
        with open("musiclistjp.txt") as f:
            FileLine = len(f.readlines())
        randNumber = random.randint(1, FileLine)
        songName = linecache.getline("musiclistjp.txt", randNumber)
        path = "./jpmusic/" + songName
        path = path[:-1] + ".mp3"
        file = open("temp.txt","w")
        file.write(songName)
        file.close()
           
    voice.play(discord.FFmpegPCMAudio(path))
    
    try:
        await client.wait_for("guild_remove", timeout = 10.0)
        
    except asyncio.TimeoutError:
        voice.pause()
        
    
    
@client.command(
    brief = "Guess the song being played",
    help = "give song name after the command, can have spaces, case insensitive"
    )

async def guess(ctx, *songGuess):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    GuessName = ""
    for word in songGuess:
        GuessName = GuessName + word.lower()
    file = open("temp.txt","r")
    songName = file.read()
    file.close()
    if songName[:-1] == GuessName:
        await ctx.send(str(ctx.message.author) + " guessed right!")
        voice.pause()
    else:
        await ctx.send("Guessed wrong!")

            
    
@client.command(
    brief = "Plays next 5 second of song",
    help = "Plays the next 5 second of song being played"
    )
async def part(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    voice.resume()
    try:
        await client.wait_for("guild_remove", timeout = 5.0)
    
    except asyncio.TimeoutError:
        voice.pause()
            
@client.command(
    brief = "ONLY FOR ME",
    help = "*smug face*"
    )
async def songjp(ctx, *arg):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name = "General")
    if str(ctx.message.author) == "okeatama#4919":
        await voiceChannel.connect()
        voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    
        songName = ""
        for word in arg:
            songName = songName + word.lower()
    
        path = "./jpmusic/" + songName + ".mp3"
        voice.play(discord.FFmpegPCMAudio(path))

@client.command(
    brief = "ONLY FOR ME",
    help = "*smug face*"
    )
async def songen(ctx, *arg):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name = "General")
    if str(ctx.message.author) == "okeatama#4919":
        await voiceChannel.connect()
        voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    
        songName = ""
        for word in arg:
            songName = songName + word.lower()
    
        path = "./enmusic/" + songName + ".mp3"
        voice.play(discord.FFmpegPCMAudio(path))

@client.command(
    brief="Play a random song"
    )
async def randomsong(ctx):
    JP_NUM = 21
    EN_NUM = 20
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name = "General")

    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    
    Pool = [("en", EN_NUM),("jp", JP_NUM)]
    PoolNumber = random.randint(0,1)
    Choice = Pool[PoolNumber][0]
    randNumber = random.randint(1, Pool[PoolNumber][1])
    songName = linecache.getline(f"musiclist{Choice}.txt", randNumber).strip()
    path = f"./{Choice}music/" + songName
    path = path.strip() + ".mp3"
    with open("temp.txt", "w") as file:
        file.write(songName)
        
    
    voice.play(discord.FFmpegPCMAudio(path))
        
client.run(os.getenv("DISCORD_BOT_TOKEN"))