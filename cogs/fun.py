"""Lightweight fun commands — no heavy deps."""
import random
import discord
from discord import app_commands
from discord.ext import commands
import config

JOKES = [
    ("Why do programmers prefer dark mode?", "Because light attracts bugs."),
    ("How many programmers does it take to change a light bulb?", "None. It's a hardware problem."),
    ("Why did the developer go broke?", "Because he used up all his cache."),
    ("What's a programmer's favorite hangout?", "Foo Bar."),
    ("Why was the JavaScript developer sad?", "Because he didn't Node how to Express himself."),
]

BALL = [
    "Yes.", "No.", "Maybe later.", "Absolutely.", "Don't count on it.",
    "Looks good.", "Ask again.", "Not a chance.", "Sure thing.", "Cloudy — try again.",
]


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="joke", description="Random programming joke")
    async def joke(self, interaction: discord.Interaction):
        setup, punch = random.choice(JOKES)
        embed = discord.Embed(title="Joke", description=f"**{setup}**\n{punch}", color=config.Colors.FUN)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        side = random.choice(["Heads", "Tails"])
        embed = discord.Embed(title="Coin", description=f"**{side}**", color=config.Colors.PRIMARY)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="Roll dice like 2d6")
    @app_commands.describe(dice="Format NdM (default 1d6)")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d6"):
        try:
            n, m = dice.lower().split("d")
            n, m = int(n), int(m)
            if n < 1 or n > 20 or m < 2 or m > 100:
                raise ValueError
        except Exception:
            await interaction.response.send_message("Use `NdM` e.g. `2d6` (N≤20, M≤100).", ephemeral=True)
            return
        rolls = [random.randint(1, m) for _ in range(n)]
        embed = discord.Embed(
            title=f"Roll {n}d{m}",
            description=f"{' + '.join(map(str, rolls))} = **{sum(rolls)}**",
            color=config.Colors.FUN,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="choose", description="Pick one option")
    @app_commands.describe(options="Comma-separated choices")
    async def choose(self, interaction: discord.Interaction, options: str):
        parts = [p.strip() for p in options.split(",") if p.strip()]
        if len(parts) < 2:
            await interaction.response.send_message("Give at least two options, separated by commas.", ephemeral=True)
            return
        pick = random.choice(parts)
        embed = discord.Embed(title="Choice", description=f"**{pick}**", color=config.Colors.ACCENT)
        embed.set_footer(text=" · ".join(parts[:8]))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="8ball", description="Ask the magic 8-ball")
    @app_commands.describe(question="Your question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(title="8-ball", color=config.Colors.PRIMARY)
        embed.add_field(name="Question", value=question[:200], inline=False)
        embed.add_field(name="Answer", value=random.choice(BALL), inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
