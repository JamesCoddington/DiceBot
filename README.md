# DiceBot

A Discord bot designed for tabletop role-playing games (TTRPGs) that provides an interactive dice rolling interface with support for multiple dice types and plot dice mechanics.

## Features

- **Interactive Dice Rolling**: User-friendly button interface for rolling various dice types
- **Multiple Dice Types**: Supports d4, d6, d8, d10, d12, d20, and d100
- **Plot Die System**: Special plot dice with three outcomes (Complication, Nothing happens, Opportunity)
- **Batch Rolling**: Roll 1-5 dice of any type in a single action
- **Mention-Based Activation**: Simply mention the bot to bring up the dice interface
- **Persistent UI**: Automatically prompts for new rolls after each result
- **Secure Random Number Generation**: Uses `secrets` module for cryptographically secure randomness

## How It Works

### Dice Rolling Interface

When you mention the bot, it displays a row of buttons representing different dice types:
- **d4, d6, d8, d10, d12, d20, d100**: Standard polyhedral dice
- **Plot**: Special plot die with narrative outcomes

### Rolling Dice

1. Click on any dice button (e.g., "d20")
2. A dropdown menu appears asking "How many dice?" (1-5)
3. Select the number of dice you want to roll
4. The bot posts the results publicly in the channel:
   - Shows who rolled
   - Displays individual roll results
   - Calculates the total sum
5. A new dice interface automatically appears for the next roll

### Plot Die Mechanics

Plot dice work differently from standard dice:
- Roll a d6 internally
- **1-2**: Complication (something bad happens)
- **3-4**: Nothing happens (neutral outcome)
- **5-6**: Opportunity (something good happens)

Results are displayed as text outcomes rather than numbers.

## Technical Details

### Architecture

- **Framework**: discord.py with commands extension
- **UI Components**: Discord UI buttons and select menus
- **Random Generation**: `secrets.randbelow()` for cryptographically secure randomness
- **Message Handling**: Event-driven architecture with async/await

### Key Components

#### DiceRollView (src/bot.py:111)
Main view containing all dice type buttons. Created with `timeout=None` to persist indefinitely.

#### DiceButton (src/bot.py:92)
Individual button for each dice type. Clicking sends an ephemeral message to the user with the dice count selector.

#### DiceCountSelect (src/bot.py:30)
Dropdown menu allowing users to select 1-5 dice. Handles both standard dice and plot dice rolls.

#### DiceCountView (src/bot.py:83)
Container view for the DiceCountSelect component with a 20-second timeout.

### Security Features

- Uses `secrets.randbelow()` instead of `random` module for true randomness
- Bot ignores its own messages to prevent loops
- Ephemeral messages for dice count selection keep the channel clean

## Installation

### Prerequisites

- Python 3.14 or higher
- Poetry package manager
- Discord bot token

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DiceBot
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:
   ```env
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```

4. **Activate the Poetry virtual environment**
   ```bash
   poetry shell
   ```

5. **Run the bot**
   ```bash
   python src/bot.py
   ```

### Getting a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Navigate to the "Bot" section
4. Click "Add Bot"
5. Under the "Token" section, click "Copy" to get your bot token
6. Enable "Message Content Intent" under "Privileged Gateway Intents"
7. Invite the bot to your server using the OAuth2 URL generator with the following scopes:
   - `bot`
   - Permissions: Send Messages, Use Slash Commands, Read Message History

## Usage

### In Discord

1. **Activate the dice roller**: Mention the bot in any channel (e.g., `@DiceBot`)
2. **Select a dice type**: Click one of the dice buttons
3. **Choose quantity**: Select how many dice to roll from the dropdown
4. **View results**: Results are posted publicly in the channel
5. **Roll again**: A new dice interface appears automatically

### Example Output

```
🎲 @User rolled 3 × d20
➡️ Rolls: 15, 8, 19
🧮 Total: 42
```

```
🎲 @User rolled 2 × Plot die
➡️ Results: Opportunity, Complication
```

## Configuration

### Customizing Dice Types

To add or remove dice types, modify the `dice` list in `DiceRollView.__init__()` (src/bot.py:114):

```python
dice = [4, 6, 8, 10, 12, 20, 100]  # Add or remove dice sides
```

### Adjusting Maximum Dice Count

Change the range in `DiceCountSelect.__init__()` (src/bot.py:36):

```python
for i in range(1, 6)  # Change 6 to allow more dice (e.g., range(1, 11) for 10 dice)
```

### Modifying Timeouts

- **DiceRollView**: `timeout=None` (persistent)
- **DiceCountView**: `timeout=20` (20 seconds)

Adjust these in their respective class constructors.

## Dependencies

- **discord.py**: Discord API wrapper for building bots
- **python-dotenv**: Load environment variables from `.env` files

See `pyproject.toml` for specific version requirements.

## Project Structure

```
DiceBot/
├── src/
│   └── bot.py          # Main bot code
├── .env                # Environment variables (not in git)
├── pyproject.toml      # Poetry project configuration
├── poetry.lock         # Locked dependency versions
└── README.md           # This file
```

## Development

### Setting Up Your IDE

Ensure your IDE is configured to use the Poetry virtual environment:

```bash
poetry env info  # Show virtual environment path
```

Point your IDE's Python interpreter to the displayed path.

### Running in Development

```bash
poetry shell          # Activate virtual environment
python src/bot.py     # Run the bot
```

## Troubleshooting

### Bot doesn't respond to mentions

- Verify "Message Content Intent" is enabled in the Discord Developer Portal
- Check that `intents.message_content = True` is set in the code (src/bot.py:10)
- Ensure the bot has permission to read and send messages in the channel

### "DISCORD_BOT_TOKEN environment variable not set" error

- Verify `.env` file exists in the project root
- Check that the file contains `DISCORD_BOT_TOKEN=your_token`
- Ensure there are no extra spaces or quotes around the token

### Buttons don't work

- Verify the bot has "Use Application Commands" permission
- Check that the bot is still connected (watch console for disconnection messages)

## License

[Add your license information here]

## Author

James Coddington (james@coddington.io)

## Contributing

[Add contribution guidelines if applicable]
