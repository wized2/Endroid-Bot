"""Modern help with select menu — lightweight."""
import discord
from discord import app_commands
from discord.ext import commands
import config

SECTIONS = {
    "mod": (
        "Moderation",
        "Role-gated tools for keeping the server clean.",
        [
            ("/kick", "Remove a member"),
            ("/ban", "Ban a member"),
            ("/unban", "Unban by user id"),
            ("/timeout", "Timeout a member"),
            ("/untimeout", "Clear a timeout"),
            ("/clear", "Bulk-delete messages"),
        ],
        config.Colors.MOD,
    ),
    "util": (
        "Utility",
        "Everyday helpers — no API keys required.",
        [
            ("/weather", "Current weather for a city"),
            ("/fact", "Random fun fact"),
            ("/ping", "Latency check"),
            ("/server", "Server info card"),
            ("/user", "User info card"),
            ("/avatar", "Show avatar"),
            ("/invite", "Bot invite link"),
        ],
        config.Colors.INFO,
    ),
    "fun": (
        "Fun",
        "Light entertainment that stays easy on the host.",
        [
            ("/joke", "Random joke"),
            ("/coinflip", "Heads or tails"),
            ("/roll", "Roll NdM dice"),
            ("/choose", "Pick from options"),
            ("/8ball", "Magic answers"),
        ],
        config.Colors.FUN,
    ),
}


def build_embed(key: str) -> discord.Embed:
    title, desc, cmds, color = SECTIONS[key]
    e = discord.Embed(
        title=f"· {title}",
        description=desc,
        color=color,
    )
    e.add_field(
        name="Commands",
        value="\n".join(f"`{c}` — {d}" for c, d in cmds),
        inline=False,
    )
    e.set_footer(text="Endroid · slash commands")
    return e


class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderation", value="mod", description="Kick, ban, timeout, clear"),
            discord.SelectOption(label="Utility", value="util", description="Weather, info, ping"),
            discord.SelectOption(label="Fun", value="fun", description="Jokes, dice, 8ball"),
        ]
        super().__init__(placeholder="Browse command groups…", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=build_embed(self.values[0]), view=self.view)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(HelpSelect())


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Browse Endroid commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Endroid",
            description=(
                "Modern slash-command bot · low footprint.\n"
                "Pick a category below or try `/ping`."
            ),
            color=config.Colors.PRIMARY,
        )
        embed.add_field(name="Groups", value="Moderation · Utility · Fun", inline=False)
        embed.set_footer(text=f"Serving {len(self.bot.guilds)} server(s)")
        await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
