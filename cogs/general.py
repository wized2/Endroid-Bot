"""General-purpose community features — lightweight, no paid APIs."""
from __future__ import annotations

import asyncio
import json
import random
import time
from pathlib import Path

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks

import config

DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)


def _load(name: str, default):
    p = DATA / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save(name: str, obj) -> None:
    (DATA / name).write_text(json.dumps(obj, indent=2), encoding="utf-8")


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.snipe: dict[int, dict] = {}
        self.afk = _load("afk.json", {})
        self.warns = _load("warns.json", {})
        self.remind_task.start()

    def cog_unload(self):
        self.remind_task.cancel()

    # ── events ─────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        self.snipe[message.channel.id] = {
            "content": message.content[:1000] or "[embed/attachment]",
            "author": str(message.author),
            "avatar": message.author.display_avatar.url,
            "ts": time.time(),
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        uid = str(message.author.id)
        if uid in self.afk:
            self.afk.pop(uid, None)
            _save("afk.json", self.afk)
            try:
                await message.channel.send(
                    embed=discord.Embed(
                        description=f"Welcome back {message.author.mention} — AFK removed.",
                        color=config.Colors.SUCCESS,
                    ),
                    delete_after=8,
                )
            except Exception:
                pass
        # mention AFK users
        for m in message.mentions:
            data = self.afk.get(str(m.id))
            if data:
                try:
                    await message.channel.send(
                        embed=discord.Embed(
                            title="AFK",
                            description=f"{m.display_name}: {data.get('reason', 'AFK')}",
                            color=config.Colors.WARNING,
                        ),
                        delete_after=10,
                    )
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        ch_id = _load("welcome.json", {}).get(str(member.guild.id))
        if not ch_id:
            return
        ch = member.guild.get_channel(int(ch_id))
        if not isinstance(ch, discord.TextChannel):
            return
        embed = discord.Embed(
            title="Welcome",
            description=f"Hey {member.mention}, welcome to **{member.guild.name}**!",
            color=config.Colors.SUCCESS,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Member #{member.guild.member_count}")
        try:
            await ch.send(embed=embed)
        except Exception:
            pass

    # ── commands ───────────────────────────────────────
    @app_commands.command(name="snipe", description="Show the last deleted message in this channel")
    async def snipe_cmd(self, interaction: discord.Interaction):
        data = self.snipe.get(interaction.channel_id)
        if not data or time.time() - data["ts"] > 120:
            await interaction.response.send_message("Nothing to snipe.", ephemeral=True)
            return
        embed = discord.Embed(description=data["content"], color=config.Colors.ACCENT)
        embed.set_author(name=data["author"], icon_url=data["avatar"])
        embed.set_footer(text="Deleted recently")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="afk", description="Mark yourself AFK")
    @app_commands.describe(reason="Optional reason")
    async def afk_cmd(self, interaction: discord.Interaction, reason: str = "AFK"):
        self.afk[str(interaction.user.id)] = {"reason": reason[:200], "ts": time.time()}
        _save("afk.json", self.afk)
        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"AFK set: {reason[:200]}",
                color=config.Colors.INFO,
            )
        )

    @app_commands.command(name="poll", description="Create a quick yes/no or multi poll")
    @app_commands.describe(question="Poll question", options="Comma-separated options (2-8). Leave empty for Yes/No.")
    async def poll_cmd(self, interaction: discord.Interaction, question: str, options: str = ""):
        if options.strip():
            opts = [o.strip() for o in options.split(",") if o.strip()][:8]
            if len(opts) < 2:
                await interaction.response.send_message("Need at least 2 options.", ephemeral=True)
                return
        else:
            opts = ["Yes", "No"]
        nums = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
        body = "\n".join(f"{nums[i]} {o}" for i, o in enumerate(opts))
        embed = discord.Embed(title=question[:250], description=body, color=config.Colors.PRIMARY)
        embed.set_footer(text=f"by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        for i in range(len(opts)):
            await msg.add_reaction(nums[i])

    @app_commands.command(name="remind", description="Remind you after N minutes")
    @app_commands.describe(minutes="Minutes from now (1-10080)", text="What to remind")
    async def remind(self, interaction: discord.Interaction, minutes: app_commands.Range[int, 1, 10080], text: str):
        due = time.time() + minutes * 60
        items = _load("reminders.json", [])
        items.append(
            {
                "user": interaction.user.id,
                "channel": interaction.channel_id,
                "text": text[:300],
                "due": due,
            }
        )
        _save("reminders.json", items)
        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"Reminder set for **{minutes}m**: {text[:300]}",
                color=config.Colors.SUCCESS,
            ),
            ephemeral=True,
        )

    @tasks.loop(seconds=30)
    async def remind_task(self):
        items = _load("reminders.json", [])
        if not items:
            return
        now = time.time()
        keep = []
        for r in items:
            if r.get("due", 0) > now:
                keep.append(r)
                continue
            ch = self.bot.get_channel(r.get("channel", 0))
            if ch:
                try:
                    await ch.send(
                        f"<@{r['user']}>",
                        embed=discord.Embed(
                            title="Reminder",
                            description=r.get("text", ""),
                            color=config.Colors.WARNING,
                        ),
                    )
                except Exception:
                    pass
        if len(keep) != len(items):
            _save("reminders.json", keep)

    @remind_task.before_loop
    async def before_remind(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="warn", description="Warn a member (mods)")
    @app_commands.describe(member="Member", reason="Reason")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if not self._is_mod(interaction):
            await interaction.response.send_message("Mod only.", ephemeral=True)
            return
        gid = str(interaction.guild_id)
        uid = str(member.id)
        self.warns.setdefault(gid, {}).setdefault(uid, []).append(
            {"reason": reason[:200], "by": interaction.user.id, "ts": time.time()}
        )
        _save("warns.json", self.warns)
        count = len(self.warns[gid][uid])
        embed = discord.Embed(
            title="Warn",
            description=f"{member.mention} warned ({count} total)\n{reason[:200]}",
            color=config.Colors.WARNING,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="List warnings for a member")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        list_ = self.warns.get(str(interaction.guild_id), {}).get(str(member.id), [])
        if not list_:
            await interaction.response.send_message("No warnings.", ephemeral=True)
            return
        lines = [f"• {w.get('reason', '')}" for w in list_[-10:]]
        embed = discord.Embed(title=f"Warnings · {member.display_name}", description="\n".join(lines), color=config.Colors.WARNING)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setwelcome", description="Set this channel as welcome channel (mods)")
    async def setwelcome(self, interaction: discord.Interaction):
        if not self._is_mod(interaction):
            await interaction.response.send_message("Mod only.", ephemeral=True)
            return
        data = _load("welcome.json", {})
        data[str(interaction.guild_id)] = interaction.channel_id
        _save("welcome.json", data)
        await interaction.response.send_message("Welcome channel set.", ephemeral=True)

    @app_commands.command(name="say", description="Make the bot say something (mods)")
    async def say(self, interaction: discord.Interaction, message: str):
        if not self._is_mod(interaction):
            await interaction.response.send_message("Mod only.", ephemeral=True)
            return
        await interaction.response.send_message("Sent.", ephemeral=True)
        await interaction.channel.send(message[:1900])

    @app_commands.command(name="embed", description="Post a simple embed (mods)")
    @app_commands.describe(title="Title", description="Body", color="Hex color like #5865F2")
    async def embed_cmd(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: str = "#5865F2",
    ):
        if not self._is_mod(interaction):
            await interaction.response.send_message("Mod only.", ephemeral=True)
            return
        try:
            c = int(color.replace("#", ""), 16)
        except Exception:
            c = config.Colors.PRIMARY
        await interaction.response.send_message("Sent.", ephemeral=True)
        await interaction.channel.send(embed=discord.Embed(title=title[:250], description=description[:4000], color=c))

    @app_commands.command(name="translate", description="Quick translate via free LibreTranslate instance")
    @app_commands.describe(text="Text", target="Language code (en, ur, ar, es, …)")
    async def translate(self, interaction: discord.Interaction, text: str, target: str = "en"):
        await interaction.response.defer()
        url = "https://libretranslate.com/translate"
        payload = {"q": text[:1000], "source": "auto", "target": target[:8], "format": "text"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("Translate service unavailable.")
                        return
                    data = await resp.json()
            out = data.get("translatedText") or str(data)
            embed = discord.Embed(title=f"→ {target}", description=out[:4000], color=config.Colors.INFO)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Translate failed: {e}")

    @app_commands.command(name="urban", description="Look up a term on Urban Dictionary")
    async def urban(self, interaction: discord.Interaction, term: str):
        await interaction.response.defer()
        url = f"https://api.urbandictionary.com/v0/define?term={term[:80]}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=12)) as resp:
                    data = await resp.json()
            lst = data.get("list") or []
            if not lst:
                await interaction.followup.send("No results.")
                return
            top = lst[0]
            embed = discord.Embed(
                title=top.get("word", term)[:100],
                description=(top.get("definition") or "")[:4000].replace("[", "").replace("]", ""),
                color=config.Colors.FUN,
            )
            ex = (top.get("example") or "")[:1000].replace("[", "").replace("]", "")
            if ex:
                embed.add_field(name="Example", value=ex, inline=False)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")

    @app_commands.command(name="meme", description="Random meme")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://meme-api.com/gimme", timeout=aiohttp.ClientTimeout(total=12)) as resp:
                    data = await resp.json()
            embed = discord.Embed(title=data.get("title", "Meme")[:250], color=config.Colors.FUN)
            embed.set_image(url=data.get("url"))
            embed.set_footer(text=f"r/{data.get('subreddit', '?')}")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")

    @app_commands.command(name="quote", description="Inspirational quote")
    async def quote(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.quotable.io/random", timeout=aiohttp.ClientTimeout(total=12)) as resp:
                    data = await resp.json()
            embed = discord.Embed(
                description=f"*{data.get('content', '')}*",
                color=config.Colors.PRIMARY,
            )
            embed.set_footer(text=f"— {data.get('author', 'Unknown')}")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")

    @app_commands.command(name="password", description="Generate a random password")
    @app_commands.describe(length="Length 8-64")
    async def password(self, interaction: discord.Interaction, length: app_commands.Range[int, 8, 64] = 16):
        alphabet = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%"
        pw = "".join(random.choice(alphabet) for _ in range(length))
        await interaction.response.send_message(f"`{pw}`", ephemeral=True)

    def _is_mod(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in getattr(config.Roles, "ALLOWED_USERS", []):
            return True
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return False
        if interaction.user.guild_permissions.manage_messages or interaction.user.guild_permissions.administrator:
            return True
        roles = {r.id for r in interaction.user.roles}
        return bool(roles.intersection(set(getattr(config.Roles, "ALLOWED_ROLES", []))))


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
