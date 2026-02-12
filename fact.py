import discord

from discord import app_commands

from discord.ext import commands

import aiohttp

import asyncio

import config

from datetime import datetime

class Fact(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.fact_api = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"

    

    @app_commands.command(name="fact", description="Get a random useless fact!")

    @app_commands.checks.cooldown(1, 5)  # 5 second cooldown

    async def fact(self, interaction: discord.Interaction):

        """Fetch and display a random useless fact"""

        

        # Defer response while we fetch the fact

        await interaction.response.defer()

        

        try:

            async with aiohttp.ClientSession() as session:

                async with session.get(self.fact_api) as response:

                    if response.status == 200:

                        data = await response.json()

                        fact_text = data.get('text', 'No fact found!')

                        fact_id = data.get('id', 'Unknown')

                        source = data.get('source', 'Unknown')

                        permalink = data.get('permalink', '')

                        

                        # Create beautiful embed

                        embed = discord.Embed(

                            title=f"{config.Icons.INFO} Random Useless Fact",

                            description=fact_text,

                            color=config.Colors.INFO

                        )

                        

                        # Add fields

                        embed.add_field(name="Source", value=f"[{source}]({permalink})" if permalink else source, inline=True)

                        embed.add_field(name="Fact ID", value=f"`{fact_id[:8]}`", inline=True)

                        

                        # Add fun footer

                        embed.set_footer(text="Did you know? • Powered by uselessfacts.jsph.pl")

                        embed.timestamp = datetime.utcnow()

                        

                        await interaction.followup.send(embed=embed)

                    else:

                        await interaction.followup.send(

                            f"{config.Icons.NO} Failed to fetch a fact. Please try again later.",

                            ephemeral=True

                        )

                        

        except aiohttp.ClientError:

            await interaction.followup.send(

                f"{config.Icons.NO} Network error. Couldn't reach the fact API.",

                ephemeral=True

            )

        except Exception as e:

            if config.BotConfig.LOG_ERRORS:

                print(f"{config.Icons.NO} Fact command error: {e}")

            await interaction.followup.send(

                f"{config.Icons.NO} An error occurred while fetching your fact.",

                ephemeral=True

            )

async def setup(bot):

    await bot.add_cog(Fact(bot))