"""

Configuration file for Discord Bot

Customize roles, icons, and other settings here

"""

# ==============================

# ROLE CONFIGURATION

# ==============================

class Roles:

    # Add role IDs that are allowed to use moderation commands

    # Format: ROLE_NAME = role_id_here

    MODERATOR = 1456187347124359200  # Replace with your moderator role ID

    ADMIN = 1456193945494098005     # Replace with your admin role ID

    

    # List of all allowed roles (users with any of these roles can use commands)

    ALLOWED_ROLES = [MODERATOR, ADMIN]

    

    # Alternative: Allow specific users by ID (useful for bot owners)

    ALLOWED_USERS = [1295712187200835639]  # Add user IDs here

# ==============================

# EMOJI/ICON CONFIGURATION

# ==============================

class Icons:

    # Success/Yes emoji

    YES = "✅"

    

    # No/Error emoji

    NO = "❌"

    

    # Warning emoji

    WARNING = "⚠️"

    

    # Info emoji

    INFO = "ℹ️"

    

    # Clock/Time emoji

    CLOCK = "⏰"

    

    # Ban hammer emoji

    BAN = "🔨"

    

    # Kick emoji

    KICK = "👢"

    

    # Timeout emoji

    TIMEOUT = "⏸️"

    

    # Clear/Trash emoji

    CLEAR = "🗑️"

    

    # User emoji

    USER = "👤"

    

    # Shield/Mod emoji

    SHIELD = "🛡️"

    

    # Question mark emoji

    QUESTION = "❓"

# ==============================

# EMBED COLOR CONFIGURATION

# ==============================

class Colors:

    # Discord color codes (decimal)

    SUCCESS = 0x00FF00  # Green

    ERROR = 0xFF0000    # Red

    WARNING = 0xFFA500  # Orange

    INFO = 0x3498DB     # Blue

    NEUTRAL = 0x7289DA  # Blurple

    DANGER = 0x992D22   # Dark Red

# ==============================

# BOT CONFIGURATION

# ==============================

class BotConfig:

    # Default command prefix (not used for slash commands but kept for compatibility)

    PREFIX = "!"

    

    # Bot status (playing, streaming, listening, watching)

    STATUS_TYPE = "watching"  # Can be: playing, streaming, listening, watching

    STATUS_MESSAGE = "for /commands"

    

    # Logging configuration

    LOG_COMMANDS = True

    LOG_ERRORS = True

    

    # Cooldown settings (in seconds)

    COMMAND_COOLDOWN = 3

    CLEAR_COOLDOWN = 5

# ==============================

# MESSAGE CONFIGURATION

# ==============================

class Messages:

    # Permission denied messages

    NO_PERMISSION = "You don't have permission to use this command."

    NO_BOT_PERMISSION = "I don't have the necessary permissions to perform this action."

    HIERARCHY_ERROR = "You cannot perform this action on this member due to role hierarchy."

    

    # Success messages

    ACTION_SUCCESS = "Action completed successfully."

    

    # Error messages

    UNKNOWN_ERROR = "An unknown error occurred."

    MEMBER_NOT_FOUND = "Member not found."

    USER_NOT_FOUND = "User not found."

    

    # Self-operation prevention

    NO_SELF_ACTION = "You cannot perform this action on yourself."

    NO_BOT_ACTION = "I cannot perform this action on myself."

# ==============================

# COMMAND CONFIGURATION

# ==============================

class CommandDefaults:

    # Clear command defaults

    CLEAR_MIN = 1

    CLEAR_MAX = 100

    CLEAR_DEFAULT = 10

    

    # Timeout command defaults

    TIMEOUT_MIN = 1  # minutes

    TIMEOUT_MAX = 40320  # 28 days in minutes

    TIMEOUT_DEFAULT = 10  # minutes

    

    # Ban command defaults

    BAN_DELETE_DAYS_MIN = 0

    BAN_DELETE_DAYS_MAX = 7

    BAN_DELETE_DAYS_DEFAULT = 0

    

    # Default reasons

    DEFAULT_REASON = "No reason provided"

    KICK_REASON = "Violation of server rules"

    BAN_REASON = "Severe violation of server rules"

    TIMEOUT_REASON = "Inappropriate behavior"

    

    # Cooldown messages

    COOLDOWN_MESSAGE = "Please wait {time} seconds before using this command again."