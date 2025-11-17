import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import secrets

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Bot state
bot_active = False

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('Waiting for /start command to activate bot...')

# --------------------------
# Select Menu (how many dice)
# --------------------------
async def roll_prompt(message: discord.Message):
    await message.channel.send(
        "**Let's roll babay!**",
        view=DiceRollView()
    )

class DiceCountSelect(discord.ui.Select):
    def __init__(self, dice_pool: dict, sides: int, is_plot: bool = False):
        self.dice_pool = dice_pool
        self.sides = sides
        self.is_plot = is_plot
        options = [
            discord.SelectOption(label=str(i), description=f"Add {i} dice")
            for i in range(1, 6)  # 1–5 dice
        ]
        super().__init__(
            placeholder="How many dice?",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        count = int(self.values[0])

        # Add dice to the pool
        dice_key = "plot" if self.is_plot else f"d{self.sides}"
        self.dice_pool[dice_key] = self.dice_pool.get(dice_key, 0) + count

        # Show updated pool and options
        await interaction.response.send_message(
            f"Added **{count} × {dice_key}** to your pool.",
            view=AddMoreOrRollView(self.dice_pool),
            ephemeral=True
        )


class DiceCountView(discord.ui.View):
    def __init__(self, dice_pool: dict, sides: int, is_plot: bool = False):
        super().__init__(timeout=20)
        self.add_item(DiceCountSelect(dice_pool, sides, is_plot))


class AddMoreOrRollView(discord.ui.View):
    def __init__(self, dice_pool: dict):
        super().__init__(timeout=30)
        self.dice_pool = dice_pool

    @discord.ui.button(label="Add More Dice", style=discord.ButtonStyle.secondary)
    async def add_more(self, interaction: discord.Interaction, button: discord.ui.Button):
        pool_str = ", ".join(f"{count}×{dice}" for dice, count in self.dice_pool.items())
        await interaction.response.send_message(
            f"**Current pool:** {pool_str}\n**Select more dice to add:**",
            view=AddDiceTypeView(self.dice_pool),
            ephemeral=True
        )

    @discord.ui.button(label="Roll Now!", style=discord.ButtonStyle.success)
    async def roll_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Perform the roll
        all_results = []
        total = 0
        roll_details = []

        for dice_key, count in self.dice_pool.items():
            if dice_key == "plot":
                # Plot die: 1-2=Complication, 3-4=Nothing, 5-6=Opportunity
                results = []
                for _ in range(count):
                    roll = secrets.randbelow(6) + 1  # 1-6
                    if roll <= 1:
                        results.append("Complication +4")
                    elif roll <= 2:
                        results.append("Complication +2")
                    elif roll <= 4:
                        results.append("Nothing happens")
                    else:
                        results.append("Opportunity")
                roll_details.append(f"**{count} × Plot die:** {', '.join(results)}")
            else:
                # Regular dice
                sides = int(dice_key[1:])  # Extract number from "d6", "d20", etc.
                rolls = [secrets.randbelow(sides) + 1 for _ in range(count)]
                roll_total = sum(rolls)
                total += roll_total
                rolls_str = ", ".join(str(r) for r in rolls)
                roll_details.append(f"**{count} × {dice_key}:** {rolls_str} (subtotal: {roll_total})")

        pool_str = ", ".join(f"{count}×{dice}" for dice, count in self.dice_pool.items())
        details_str = "\n".join(roll_details)

        await interaction.response.send_message(
            f"🎲 {interaction.user.mention} rolled **{pool_str}**\n"
            f"{details_str}\n"
            f"🧮 **Grand Total: {total}**"
        )

        # Prompt for next roll
        await interaction.followup.send(
            "**Let's roll babay!**",
            view=DiceRollView()
        )


class AddDiceTypeView(discord.ui.View):
    def __init__(self, dice_pool: dict):
        super().__init__(timeout=20)
        self.dice_pool = dice_pool
        dice = [4, 6, 8, 10, 12, 20, 100]
        for d in dice:
            self.add_item(AddDiceButton(dice_pool, d))
        # Add Plot die button
        self.add_item(AddDiceButton(dice_pool, sides=6, is_plot=True))


class AddDiceButton(discord.ui.Button):
    def __init__(self, dice_pool: dict, sides: int, is_plot: bool = False):
        label = "Plot" if is_plot else f"d{sides}"
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary
        )
        self.dice_pool = dice_pool
        self.sides = sides
        self.is_plot = is_plot

    async def callback(self, interaction: discord.Interaction):
        dice_name = "Plot die" if self.is_plot else f"d{self.sides}"
        await interaction.response.send_message(
            f"🎲 Select how many **{dice_name}** to add:",
            view=DiceCountView(self.dice_pool, self.sides, self.is_plot),
            ephemeral=True
        )


# ----------------------
# Dice buttons (d4–d20)
# ----------------------
class DiceButton(discord.ui.Button):
    def __init__(self, sides: int, is_plot: bool = False):
        label = "Plot" if is_plot else f"d{sides}"
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary
        )
        self.sides = sides
        self.is_plot = is_plot

    async def callback(self, interaction: discord.Interaction):
        # Create a new dice pool for this roll
        dice_pool = {}
        dice_name = "Plot die" if self.is_plot else f"d{self.sides}"
        await interaction.response.send_message(
            f"🎲 {interaction.user.mention} Select how many **{dice_name}** to roll:",
            view=DiceCountView(dice_pool, self.sides, self.is_plot),
            ephemeral=True
        )


class DiceRollView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        dice = [4, 6, 8, 10, 12, 20, 100]
        for d in dice:
            self.add_item(DiceButton(d))
        # Add Plot die button
        self.add_item(DiceButton(sides=6, is_plot=True))


# ----------------------
# Mention → open dice UI
# ----------------------
@bot.event
async def on_message(message: discord.Message):
    # Prevent the bot from responding to itself
    if message.author == bot.user:
        return

    # Check if the bot was mentioned
    if bot.user in message.mentions:
        await roll_prompt(message)

    # Allow commands to still work
    await bot.process_commands(message)



if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()

    # Load token from environment variable
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print('Error: DISCORD_BOT_TOKEN environment variable not set')
        exit(1)

    bot.run(TOKEN)
