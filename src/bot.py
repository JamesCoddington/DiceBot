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
    def __init__(self, sides: int, is_plot: bool = False):
        self.sides = sides
        self.is_plot = is_plot
        options = [
            discord.SelectOption(label=str(i), description=f"Roll {i} dice")
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

        if self.is_plot:
            # Plot die: 1-2=Complication, 3-4=Nothing, 5-6=Opportunity
            results = []
            for _ in range(count):
                roll = secrets.randbelow(6) + 1  # 1-6
                if roll <= 2:
                    results.append("Complication")
                elif roll <= 4:
                    results.append("Nothing happens")
                else:
                    results.append("Opportunity")

            rolls_str = ", ".join(results)
            await interaction.response.send_message(
                f"🎲 {interaction.user.mention} rolled **{count} × Plot die**\n"
                f"➡️ Results: **{rolls_str}**"
            )
        else:
            rolls = [secrets.randbelow(self.sides) + 1 for _ in range(count)]
            total = sum(rolls)
            rolls_str = ", ".join(str(r) for r in rolls)

            await interaction.response.send_message(
                f"🎲 {interaction.user.mention} rolled **{count} × d{self.sides}**\n"
                f"➡️ Rolls: **{rolls_str}**\n"
                f"🧮 Total: **{total}**"
            )

        # Then: immediately prompt again in the channel
        await interaction.followup.send(
            "**Let's roll babay!**",
            view=DiceRollView()
        )


class DiceCountView(discord.ui.View):
    def __init__(self, sides: int, is_plot: bool = False):
        super().__init__(timeout=20)
        self.add_item(DiceCountSelect(sides, is_plot))


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
        dice_name = "Plot die" if self.is_plot else f"d{self.sides}"
        await interaction.response.send_message(
            f"🎲 {interaction.user.mention} Select how many **{dice_name}** to roll:",
            view=DiceCountView(self.sides, self.is_plot),
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
