import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from datetime import timedelta
import time
import config

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(1, config.BotConfig.COMMAND_COOLDOWN, commands.BucketType.user)
    
    # Role check function using config
    async def check_role(self, interaction: discord.Interaction):
        # Check allowed users first
        if interaction.user.id in config.Roles.ALLOWED_USERS:
            return True
        
        # If no roles are specified, allow all
        if not config.Roles.ALLOWED_ROLES:
            return True
        
        # Check if user has any of the allowed roles
        member = interaction.user
        if isinstance(member, discord.User):
            try:
                member = await interaction.guild.fetch_member(member.id)
            except:
                return False
        
        # Check for allowed roles
        for role_id in config.Roles.ALLOWED_ROLES:
            role = discord.utils.get(member.roles, id=role_id)
            if role is not None:
                return True
        
        return False
    
    # Create embed template
    def create_embed(self, title, description, color, icon=None):
        if icon:
            title = f"{icon} {title}"
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        return embed
    
    # Add footer to embed
    def add_embed_footer(self, embed, member, moderator):
        embed.set_footer(text=f"User ID: {member.id} | Moderator: {moderator.name}")
        embed.timestamp = discord.utils.utcnow()
        return embed
    
    # Check cooldown
    async def check_cooldown(self, interaction: discord.Interaction):
        bucket = self._cd.get_bucket(interaction.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        return True
    
    # Kick command
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for kicking"
    )
    @app_commands.checks.cooldown(1, config.BotConfig.COMMAND_COOLDOWN)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Kick a member from the server"""
        # Check permissions
        if not await self.check_role(interaction):
            return
        
        # Check if bot has permission
        if not interaction.guild.me.guild_permissions.kick_members:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if trying to kick self
        if member.id == interaction.user.id:
            embed = self.create_embed(
                "Invalid Action",
                config.Messages.NO_SELF_ACTION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if trying to kick the bot
        if member.id == self.bot.user.id:
            embed = self.create_embed(
                "Invalid Action",
                config.Messages.NO_BOT_ACTION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check hierarchy
        if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            embed = self.create_embed(
                "Hierarchy Error",
                config.Messages.HIERARCHY_ERROR,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Use default reason if none provided
        if not reason:
            reason = config.CommandDefaults.KICK_REASON
        
        # Kick the member
        try:
            await member.kick(reason=f"{interaction.user.name}: {reason}")
            
            embed = self.create_embed(
                "Member Kicked",
                f"**{member.name}** has been kicked from the server.",
                config.Colors.SUCCESS,
                config.Icons.KICK
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Member", value=member.mention, inline=True)
            embed = self.add_embed_footer(embed, member, interaction.user)
            
            await interaction.response.send_message(embed=embed)
            
            # Log the action
            if config.BotConfig.LOG_COMMANDS:
                print(f"{config.Icons.KICK} {interaction.user} kicked {member} for: {reason}")
            
        except discord.Forbidden:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = self.create_embed(
                "Error",
                f"An error occurred: {str(e)}",
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Ban command
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(
        member="The member to ban",
        reason="Reason for banning",
        delete_message_days="Number of days of messages to delete (0-7)"
    )
    @app_commands.choices(delete_message_days=[
        app_commands.Choice(name="Don't delete any", value=0),
        app_commands.Choice(name="1 day", value=1),
        app_commands.Choice(name="2 days", value=2),
        app_commands.Choice(name="3 days", value=3),
        app_commands.Choice(name="4 days", value=4),
        app_commands.Choice(name="5 days", value=5),
        app_commands.Choice(name="6 days", value=6),
        app_commands.Choice(name="7 days", value=7),
    ])
    @app_commands.checks.cooldown(1, config.BotConfig.COMMAND_COOLDOWN)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, 
                  reason: str = None, delete_message_days: int = config.CommandDefaults.BAN_DELETE_DAYS_DEFAULT):
        """Ban a member from the server"""
        # Check permissions
        if not await self.check_role(interaction):
            return
        
        # Check if bot has permission
        if not interaction.guild.me.guild_permissions.ban_members:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if trying to ban self
        if member.id == interaction.user.id:
            embed = self.create_embed(
                "Invalid Action",
                config.Messages.NO_SELF_ACTION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if trying to ban the bot
        if member.id == self.bot.user.id:
            embed = self.create_embed(
                "Invalid Action",
                config.Messages.NO_BOT_ACTION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check hierarchy
        if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            embed = self.create_embed(
                "Hierarchy Error",
                config.Messages.HIERARCHY_ERROR,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate delete days
        if delete_message_days < config.CommandDefaults.BAN_DELETE_DAYS_MIN or delete_message_days > config.CommandDefaults.BAN_DELETE_DAYS_MAX:
            delete_message_days = config.CommandDefaults.BAN_DELETE_DAYS_DEFAULT
        
        # Use default reason if none provided
        if not reason:
            reason = config.CommandDefaults.BAN_REASON
        
        # Ban the member
        try:
            await member.ban(reason=f"{interaction.user.name}: {reason}", delete_message_days=delete_message_days)
            
            embed = self.create_embed(
                "Member Banned",
                f"**{member.name}** has been banned from the server.",
                config.Colors.DANGER,
                config.Icons.BAN
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Messages Deleted", value=f"{delete_message_days} days", inline=True)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed = self.add_embed_footer(embed, member, interaction.user)
            
            await interaction.response.send_message(embed=embed)
            
            # Log the action
            if config.BotConfig.LOG_COMMANDS:
                print(f"{config.Icons.BAN} {interaction.user} banned {member} for: {reason}")
            
        except discord.Forbidden:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = self.create_embed(
                "Error",
                f"An error occurred: {str(e)}",
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Unban command
    @app_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user_id="The user ID to unban",
        reason="Reason for unbanning"
    )
    @app_commands.checks.cooldown(1, config.BotConfig.COMMAND_COOLDOWN)
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = None):
        """Unban a user from the server"""
        # Check permissions
        if not await self.check_role(interaction):
            return
        
        # Check if bot has permission
        if not interaction.guild.me.guild_permissions.ban_members:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Convert user_id to int
        try:
            user_id_int = int(user_id)
        except ValueError:
            embed = self.create_embed(
                "Invalid Input",
                "Please provide a valid numeric user ID.",
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Use default reason if none provided
        if not reason:
            reason = config.CommandDefaults.DEFAULT_REASON
        
        # Try to unban the user
        try:
            user = await self.bot.fetch_user(user_id_int)
            
            # Check if user is banned
            banned_users = [ban_entry async for ban_entry in interaction.guild.bans()]
            banned_ids = [ban.user.id for ban in banned_users]
            
            if user_id_int not in banned_ids:
                embed = self.create_embed(
                    "Not Banned",
                    f"User **{user.name}** is not banned.",
                    config.Colors.WARNING,
                    config.Icons.WARNING
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await interaction.guild.unban(user, reason=f"{interaction.user.name}: {reason}")
            
            embed = self.create_embed(
                "User Unbanned",
                f"**{user.name}** has been unbanned from the server.",
                config.Colors.SUCCESS,
                config.Icons.YES
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"User ID: {user.id}")
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.response.send_message(embed=embed)
            
            # Log the action
            if config.BotConfig.LOG_COMMANDS:
                print(f"{config.Icons.YES} {interaction.user} unbanned {user} for: {reason}")
            
        except discord.NotFound:
            embed = self.create_embed(
                "User Not Found",
                config.Messages.USER_NOT_FOUND,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.Forbidden:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = self.create_embed(
                "Error",
                f"An error occurred: {str(e)}",
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Timeout command
    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(
        member="The member to timeout",
        minutes="Duration in minutes",
        reason="Reason for timeout"
    )
    @app_commands.checks.cooldown(1, config.BotConfig.COMMAND_COOLDOWN)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, 
                      minutes: int, reason: str = None):
        """Timeout a member"""
        # Check permissions
        if not await self.check_role(interaction):
            return
        
        # Check if bot has permission
        if not interaction.guild.me.guild_permissions.moderate_members:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate minutes
        if minutes < config.CommandDefaults.TIMEOUT_MIN or minutes > config.CommandDefaults.TIMEOUT_MAX:
            embed = self.create_embed(
                "Invalid Duration",
                f"Timeout duration must be between {config.CommandDefaults.TIMEOUT_MIN} and {config.CommandDefaults.TIMEOUT_MAX} minutes.",
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if trying to timeout self
        if member.id == interaction.user.id:
            embed = self.create_embed(
                "Invalid Action",
                config.Messages.NO_SELF_ACTION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if trying to timeout the bot
        if member.id == self.bot.user.id:
            embed = self.create_embed(
                "Invalid Action",
                config.Messages.NO_BOT_ACTION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check hierarchy
        if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            embed = self.create_embed(
                "Hierarchy Error",
                config.Messages.HIERARCHY_ERROR,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Use default reason if none provided
        if not reason:
            reason = config.CommandDefaults.TIMEOUT_REASON
        
        # Calculate timeout duration
        duration = timedelta(minutes=minutes)
        
        # Apply timeout
        try:
            await member.timeout(duration, reason=f"{interaction.user.name}: {reason}")
            
            embed = self.create_embed(
                "Member Timed Out",
                f"**{member.name}** has been timed out.",
                config.Colors.WARNING,
                config.Icons.TIMEOUT
            )
            embed.add_field(name="Duration", value=f"{minutes} minutes", inline=True)
            embed.add_field(name="Until", value=f"<t:{int((discord.utils.utcnow() + duration).timestamp())}:R>", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed = self.add_embed_footer(embed, member, interaction.user)
            
            await interaction.response.send_message(embed=embed)
            
            # Log the action
            if config.BotConfig.LOG_COMMANDS:
                print(f"{config.Icons.TIMEOUT} {interaction.user} timed out {member} for {minutes} minutes: {reason}")
            
        except discord.Forbidden:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = self.create_embed(
                "Error",
                f"An error occurred: {str(e)}",
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Remove timeout command
    @app_commands.command(name="untimeout", description="Remove timeout from a member")
    @app_commands.describe(
        member="The member to remove timeout from",
        reason="Reason for removing timeout"
    )
    @app_commands.checks.cooldown(1, config.BotConfig.COMMAND_COOLDOWN)
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member, 
                        reason: str = None):
        """Remove timeout from a member"""
        # Check permissions
        if not await self.check_role(interaction):
            return
        
        # Check if bot has permission
        if not interaction.guild.me.guild_permissions.moderate_members:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if member is timed out
        if member.timed_out_until is None:
            embed = self.create_embed(
                "Not Timed Out",
                "This member is not timed out.",
                config.Colors.WARNING,
                config.Icons.WARNING
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Use default reason if none provided
        if not reason:
            reason = config.CommandDefaults.DEFAULT_REASON
        
        # Remove timeout
        try:
            await member.timeout(None, reason=f"{interaction.user.name}: {reason}")
            
            embed = self.create_embed(
                "Timeout Removed",
                f"Timeout removed from **{member.name}**.",
                config.Colors.SUCCESS,
                config.Icons.YES
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Member", value=member.mention, inline=True)
            embed = self.add_embed_footer(embed, member, interaction.user)
            
            await interaction.response.send_message(embed=embed)
            
            # Log the action
            if config.BotConfig.LOG_COMMANDS:
                print(f"{config.Icons.YES} {interaction.user} removed timeout from {member}: {reason}")
            
        except discord.Forbidden:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = self.create_embed(
                "Error",
                f"An error occurred: {str(e)}",
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Clear messages command
    @app_commands.command(name="clear", description="Clear a number of messages")
    @app_commands.describe(
        amount="Number of messages to clear",
        member="Only clear messages from this member (optional)"
    )
    @app_commands.checks.cooldown(1, config.BotConfig.CLEAR_COOLDOWN)
    async def clear(self, interaction: discord.Interaction, amount: int, member: discord.Member = None):
        """Clear messages from a channel"""
        # Check permissions
        if not await self.check_role(interaction):
            return
        
        # Check if bot has permission
        if not interaction.guild.me.guild_permissions.manage_messages:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate amount
        if amount < config.CommandDefaults.CLEAR_MIN or amount > config.CommandDefaults.CLEAR_MAX:
            embed = self.create_embed(
                "Invalid Amount",
                f"Amount must be between {config.CommandDefaults.CLEAR_MIN} and {config.CommandDefaults.CLEAR_MAX}.",
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Clear messages
        try:
            await interaction.response.defer(ephemeral=True)
            
            def check(msg):
                return member is None or msg.author.id == member.id
            
            deleted = await interaction.channel.purge(limit=amount, check=check if member else None, bulk=True)
            
            embed = self.create_embed(
                "Messages Cleared",
                f"Cleared **{len(deleted)}** messages.",
                config.Colors.SUCCESS,
                config.Icons.CLEAR
            )
            if member:
                embed.add_field(name="Filtered By", value=member.mention, inline=True)
            embed.add_field(name="Channel", value=interaction.channel.mention, inline=True)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.set_footer(text=f"Cleared at")
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Log the action
            if config.BotConfig.LOG_COMMANDS:
                print(f"{config.Icons.CLEAR} {interaction.user} cleared {len(deleted)} messages in #{interaction.channel}")
            
            # Delete the success message after 5 seconds
            await asyncio.sleep(5)
            await interaction.delete_original_response()
            
        except discord.Forbidden:
            embed = self.create_embed(
                "Permission Error",
                config.Messages.NO_BOT_PERMISSION,
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = self.create_embed(
                "Error",
                f"An error occurred: {str(e)}",
                config.Colors.ERROR,
                config.Icons.NO
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))