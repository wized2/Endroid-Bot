import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import config

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', 0))

# Bot setup with required intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class Bot(commands.Bot):
    def __init__(self):
        # Pre-define activity to avoid NoneType errors during startup
        activity_type = getattr(discord.ActivityType, config.BotConfig.STATUS_TYPE, discord.ActivityType.watching)
        initial_activity = discord.Activity(type=activity_type, name=config.BotConfig.STATUS_MESSAGE)

        super().__init__(
            command_prefix=config.BotConfig.PREFIX,
            intents=intents,
            help_command=None,
            activity=initial_activity  # This sets status safely on login
        )
    
    async def setup_hook(self):
        # Automatically load all cogs from the /cogs folder
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('_'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'{config.Icons.YES} Loaded cog: {filename}')
                except Exception as e:
                    print(f'{config.Icons.NO} Failed to load cog {filename}: {e}')
        
        # Sync commands
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"{config.Icons.INFO} Commands synced to guild ID: {GUILD_ID}")
        else:
            await self.tree.sync()
            print(f"{config.Icons.YES} Commands synced globally")
    
    async def on_ready(self):
        print(f'{config.Icons.YES} Logged in as {self.user.name} (ID: {self.user.id})')
        print(f'{config.Icons.INFO} Invite URL: https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands')
        print(f'{config.Icons.SHIELD} Allowed roles: {config.Roles.ALLOWED_ROLES}')
        print('─' * 40)
    
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.CheckFailure):
            pass
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title=f"{config.Icons.CLOCK} Command on Cooldown",
                description=config.CommandDefaults.COOLDOWN_MESSAGE.format(time=f"{error.retry_after:.1f}"),
                color=config.Colors.WARNING
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if config.BotConfig.LOG_ERRORS:
                print(f"{config.Icons.NO} Error: {error}")
            
            embed = discord.Embed(
                title=f"{config.Icons.NO} Error",
                description=f"{config.Messages.UNKNOWN_ERROR}\n```{str(error)[:1000]}```",
                color=config.Colors.ERROR
            )
            
            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except discord.InteractionResponded:
                await interaction.followup.send(embed=embed, ephemeral=True)

# Role check decorator
def has_allowed_role():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id in config.Roles.ALLOWED_USERS:
            return True
        
        if not config.Roles.ALLOWED_ROLES:
            return True
        
        member = interaction.user
        if not isinstance(member, discord.Member):
            try:
                member = await interaction.guild.fetch_member(member.id)
            except:
                return False
        
        for role_id in config.Roles.ALLOWED_ROLES:
            if any(role.id == role_id for role in member.roles):
                return True
        
        embed = discord.Embed(
            title=f"{config.Icons.NO} Permission Denied",
            description=config.Messages.NO_PERMISSION,
            color=config.Colors.ERROR
        )
        embed.add_field(
            name="Required Roles",
            value="\n".join([f"<@&{role_id}>" for role_id in config.Roles.ALLOWED_ROLES]) or "Not configured",
            inline=False
        )
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False
    return discord.app_commands.check(predicate)

bot = Bot()

if __name__ == '__main__':
    if not TOKEN:
        print(f"{config.Icons.NO} ERROR: DISCORD_BOT_TOKEN not found!")
        exit(1)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print(f"{config.Icons.NO} ERROR: Invalid bot token!")
    except Exception as e:
        print(f"{config.Icons.NO} ERROR: {e}")