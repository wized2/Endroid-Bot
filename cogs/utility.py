"""Lightweight utility commands."""
from datetime import datetime, timezone
import discord
from discord import app_commands
from discord.ext import commands
import config


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        ws = round(self.bot.latency * 1000)
        embed = discord.Embed(title="Pong", color=config.Colors.SUCCESS)
        embed.add_field(name="Websocket", value=f"`{ws} ms`", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server", description="Server information")
    async def server(self, interaction: discord.Interaction):
        g = interaction.guild
        if not g:
            await interaction.response.send_message("Guild only.", ephemeral=True)
            return
        embed = discord.Embed(title=g.name, color=config.Colors.PRIMARY)
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="Members", value=str(g.member_count), inline=True)
        embed.add_field(name="Channels", value=str(len(g.channels)), inline=True)
        embed.add_field(name="Roles", value=str(len(g.roles)), inline=True)
        embed.add_field(name="Owner", value=str(g.owner), inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(g.created_at, "R"), inline=True)
        embed.set_footer(text=f"ID {g.id}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="user", description="User information")
    @app_commands.describe(member="Member to inspect")
    async def user(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        embed = discord.Embed(title=str(member), color=member.color if member.color.value else config.Colors.INFO)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, "R") if member.joined_at else "—", inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, "R"), inline=True)
        roles = [r.mention for r in member.roles[1:][:15]]
        embed.add_field(name="Roles", value=" ".join(roles) if roles else "None", inline=False)
        embed.set_footer(text=f"ID {member.id}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Show avatar")
    @app_commands.describe(member="Whose avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member.display_name}", color=config.Colors.ACCENT)
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="Invite this bot")
    async def invite(self, interaction: discord.Interaction):
        url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(administrator=True),
            scopes=("bot", "applications.commands"),
        )
        embed = discord.Embed(
            title="Invite Endroid",
            description=f"[Add to server]({url})",
            color=config.Colors.PRIMARY,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
