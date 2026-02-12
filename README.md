<div align="center">
  <img src="https://raw.githubusercontent.com/wized2/Endroid-Bot/refs/heads/main/assets/banner.png" alt="Endroid Manager Banner" width="100%">
</div>

<h1 align="center">🤖 Endroid Manager</h1>

<p align="center">
  <strong>A powerful, modern Discord moderation bot with fun and utility features</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-commands">Commands</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-license">License</a>
</p>

<div align="center">
  <img src="https://img.shields.io/badge/license-MIT-00FFFF?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/python-3.12+-00FFFF?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/discord.py-2.3+-00FFFF?style=for-the-badge&logo=discord" alt="discord.py">
  <img src="https://img.shields.io/badge/status-online-00FFFF?style=for-the-badge" alt="Status">
</div>

<br>

---

## ✨ Features

<table>
  <tr>
    <td align="center" width="100">🛡️</td>
    <td><strong>Advanced Moderation</strong> - Kick, ban, timeout, clear messages with role-based permissions</td>
  </tr>
  <tr>
    <td align="center">🌍</td>
    <td><strong>Weather Updates</strong> - Real-time weather for any city worldwide (Open-Meteo)</td>
  </tr>
  <tr>
    <td align="center">📚</td>
    <td><strong>Random Facts</strong> - Interesting useless facts from Useless Facts API</td>
  </tr>
  <tr>
    <td align="center">🎨</td>
    <td><strong>Beautiful Embeds</strong> - Color-coded, responsive embeds with emoji support</td>
  </tr>
  <tr>
    <td align="center">🔒</td>
    <td><strong>Role-Based Access</strong> - Restrict commands to specific roles</td>
  </tr>
  <tr>
    <td align="center">⚡</td>
    <td><strong>Slash Commands</strong> - Modern, auto-complete enabled commands</td>
  </tr>
  <tr>
    <td align="center">🌐</td>
    <td><strong>Zero API Keys</strong> - All features work without paid API keys</td>
  </tr>
</table>

---

## 📋 Commands

### 🛡️ **Moderation** (Restricted)
| Command | Description | Options | Cooldown |
|---------|-------------|---------|----------|
| `/kick` | Kick a member from the server | `member`, `reason` | 3s |
| `/ban` | Ban a member from the server | `member`, `reason`, `delete_message_days` | 3s |
| `/unban` | Unban a user by ID | `user_id`, `reason` | 3s |
| `/timeout` | Timeout a member | `member`, `minutes`, `reason` | 3s |
| `/untimeout` | Remove timeout from a member | `member`, `reason` | 3s |
| `/clear` | Clear messages in a channel | `amount`, `member` (optional) | 5s |

### 🌍 **Utility** (Public)
| Command | Description | Options | Cooldown |
|---------|-------------|---------|----------|
| `/weather` | Get current weather for any city | `city`, `units` (C/F) | 10s |
| `/fact` | Get a random useless fact | None | 5s |

---

## 🚀 Installation

### Prerequisites
- Python 3.12 or higher
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))
- Git (optional)

### Step 1: Clone the Repository
```bash
git clone https://github.com/wized2/Endroid-Bot.git
cd Endroid-Bot
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the root directory:
```env
DISCORD_BOT_TOKEN=your_bot_token_here
GUILD_ID=your_server_id_here  # Optional: for instant command sync
```

### Step 4: Configure Roles and Permissions
Edit `config.py` and add your role IDs:
```python
class Roles:
    MODERATOR = 123456789012345678  # Replace with your moderator role ID
    ADMIN = 987654321098765432      # Replace with your admin role ID
    ALLOWED_ROLES = [MODERATOR, ADMIN]
    ALLOWED_USERS = []  # Add specific user IDs to bypass role check
```

### Step 5: Run the Bot
```bash
python bot.py
```

---

## ⚙️ Configuration

### 🔐 **Role-Based Access Control**
```python
# config.py
class Roles:
    MODERATOR = 123456789012345678  # Users with this role can use moderation commands
    ADMIN = 987654321098765432      # Users with this role can also use moderation commands
    ALLOWED_ROLES = [MODERATOR, ADMIN]  # List of allowed roles
    ALLOWED_USERS = [123456789012345678]  # Specific user IDs (bypass roles)
```

### 🎨 **Customize Icons and Colors**
```python
class Icons:
    YES = "✅"        # Success emoji
    NO = "❌"         # Error emoji
    WARNING = "⚠️"    # Warning emoji
    KICK = "👢"       # Kick command
    BAN = "🔨"        # Ban command
    TIMEOUT = "⏸️"    # Timeout command
    CLEAR = "🗑️"      # Clear command
    SHIELD = "🛡️"     # Moderation
    INFO = "ℹ️"       # Information
    
class Colors:
    SUCCESS = 0x00FF00  # Green
    ERROR = 0xFF0000    # Red
    WARNING = 0xFFA500  # Orange
    INFO = 0x3498DB     # Blue
    DANGER = 0x992D22   # Dark Red
    NEUTRAL = 0x7289DA  # Blurple
```

### 🤖 **Bot Configuration**
```python
class BotConfig:
    PREFIX = "!"  # Command prefix (not used for slash commands)
    STATUS_TYPE = "watching"  # playing, streaming, listening, watching
    STATUS_MESSAGE = "for /commands"
    LOG_COMMANDS = True
    LOG_ERRORS = True
    COMMAND_COOLDOWN = 3  # Seconds
    CLEAR_COOLDOWN = 5    # Seconds
```

---

## 📁 Project Structure

```
📦 Endroid-Bot
├── 📄 bot.py                 # Main bot file
├── 📄 config.py             # Configuration and constants
├── 📄 requirements.txt      # Python dependencies
├── 📄 .env                  # Environment variables (not in repo)
├── 📄 README.md            # Documentation
├── 📁 assets/              # Image assets
│   └── 🖼️ banner.png      # Repository banner
└── 📁 cogs/
    ├── 📄 moderation.py    # Moderation commands (restricted)
    ├── 📄 weather.py       # Weather commands (public)
    └── 📄 fact.py          # Random fact commands (public)
```

---

## 🎯 Usage Examples

### 🌤️ **Weather Command**
```
/weather city:Tokyo units:Celsius
```
**Response:** Beautiful embed with temperature, feels like, humidity, wind speed, pressure, visibility, sunrise/sunset, and location details!

### 📚 **Fact Command**
```
/fact
```
**Response:** Random useless fact with source and ID in a clean embed!

### 🛡️ **Moderation Command**
```
/kick member:@user reason:Spamming in general chat
```
**Response:** Confirmation embed with member info, moderator, and reason!

---

## 🔧 Troubleshooting

### Bot won't start
- ✅ Check if `DISCORD_BOT_TOKEN` is set correctly in `.env`
- ✅ Verify Python version is 3.12+
- ✅ Run `pip install -r requirements.txt` again

### Commands not showing up
- ✅ Wait 1-2 hours for global commands to register
- ✅ Set `GUILD_ID` in `.env` for instant guild-specific commands
- ✅ Check bot has `applications.commands` scope in invite link

### Permission errors
- ✅ Ensure bot role is **above** the roles it needs to moderate
- ✅ Check bot has necessary permissions in server settings
- ✅ Verify role IDs in `config.py` are correct

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### 📝 Contribution Guidelines
- Follow PEP 8 style guide
- Add comments for complex logic
- Update documentation for new features
- Test your changes before submitting

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Wized2

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgements

- [discord.py](https://github.com/Rapptz/discord.py) - Python Discord API wrapper
- [Open-Meteo](https://open-meteo.com/) - Free weather API (no key required)
- [Useless Facts API](https://uselessfacts.jsph.pl/) - Random facts API
---

## 📞 Support

<div align="center">
  
  **Endroid Manager** • Created with ⚡ by [@wized2](https://github.com/wized2)
  
  <br>
  
  [![GitHub Issues](https://img.shields.io/github/issues/wized2/Endroid-Bot?style=flat-square&color=00FFFF)](https://github.com/wized2/Endroid-Bot/issues)
  [![GitHub Stars](https://img.shields.io/github/stars/wized2/Endroid-Bot?style=flat-square&color=00FFFF)](https://github.com/wized2/Endroid-Bot/stargazers)
  [![GitHub Forks](https://img.shields.io/github/forks/wized2/Endroid-Bot?style=flat-square&color=00FFFF)](https://github.com/wized2/Endroid-Bot/network/members)
  
  <br>
  
  [Report Bug](https://github.com/wized2/Endroid-Bot/issues) • [Request Feature](https://github.com/wized2/Endroid-Bot/issues)
  
  <br>
  
  <sub>Made with ❤️ for the Discord community</sub>
</div>

---

<div align="center">
  <img src="https://raw.githubusercontent.com/wized2/Endroid-Bot/refs/heads/main/assets/banner.png" alt="Endroid Manager Footer" width="80%">
</div>
