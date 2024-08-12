import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")

from cogs.discordbot import DiscordBot

if __name__ == "__main__":
    discord_bot = DiscordBot(DISCORD_TOKEN, SLACK_TOKEN, SLACK_CHANNEL)
    discord_bot.run_discord_bot()
