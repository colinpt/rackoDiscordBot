import random
import discord
import time
import asyncio
from discord.ext import commands
from discord.utils import get
from racko_functions import *
from collections import deque
#-------------CONSTANTS-----------------
TOKEN = 'NzM3NzczMzE1MjQxOTM0ODc4.XyCO8Q.eZRHFqZZ8Px9me0O7z5vVm3z_DU'
GAME_BOARD = 0
GAME_INFO  = 1
CARD_DRAW  = 2
SLOT_PICK  = 3
MAX_LINES  = 6

#---------------SETUP-------------------
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)
client = discord.Client(intents=intents)
echochannel = None

#---------------GLOBALS------------------
messageDict = {}
gameInfo = deque([], MAX_LINES)

#--------------COMMANDS------------------
@bot.event
async def on_ready():
	print(f'{bot.user} is online.')

@bot.command(name='play', help='Starts a game of Racko')
async def play(ctx):
	previous = messageDict.get(ctx.author.id)
	if previous:
		for oldMessage in previous:
			await oldMessage.delete()
	messageCollection = [None, None, None, None]
	messageDict.update({ctx.message.author.id: messageCollection})
	for i in range(4):
		await botPrint(str(hash(ctx.message.author.id / (i + 1))), ctx.message.channel.id)
	await main(ctx.message.author)
	

@bot.command(name='rules', help='Provides the rules for Racko')
async def rules(ctx):
	await botPrint("Each player is assigned a rack with ten slots that have been randomly assigned with cards from the Racko deck. \nThere are 60 cards numbered 1-60. The objective is to fill slots 0-9 in ascending order. \nThe first player to do so wins.", ctx.message.channel.id)

@bot.command(name='purge', help='clears all bot messages from channel')
async def purge(ctx):
	messages = ctx.message.channel
	async for message in messages.history(limit=1000):
		if message.author.bot:
			await message.delete()		
#-------------EVENTS-----------------
@bot.event
async def on_message(message):
	if message.author.bot:
		users = message.channel.members
		for user in users:
			for i in range(4):
				hashed_id = str(hash(user.id / (i + 1)))
				if hashed_id in message.content:
					tempMessageCollection = messageDict.get(user.id)
					tempMessageCollection[i] = message
					messageDict.update({user.id: tempMessageCollection})
					await message.edit(content="``` ```")

	if message.content.startswith('$'):
		await message.delete()
		await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
	if "Would you like to draw from the deck?(1) Or the discard?(2)" in after.content:
		await after.add_reaction("1️⃣")
		await after.add_reaction("2️⃣")
	elif "Which slot would you like to replace? (0-9)" in after.content:
		nums = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
		for num in nums:
			await after.add_reaction(num)

#------------HELPERS-----------------

async def botPrint(str, channel):
	channel = bot.get_channel(channel)
	await channel.send("```" + str + "```")

async def editGameMessage(player, gameSlot, prefix, newContent):
	messages = messageDict.get(player.id)
	await messages[gameSlot].edit(content = ("```" + prefix + "\n" + newContent + "\n```"))

async def updateGameInfo(player, prefix, newContent):
	lines = newContent.split("\n")
	for line in lines:
		if len(gameInfo) == MAX_LINES:
			gameInfo.popleft()
		gameInfo.append(line)
	newContent = "\n".join(gameInfo)
	await editGameMessage(player, GAME_INFO, prefix, newContent)

async def checkForReaction(player, index):
	messages = messageDict.get(player.id)
	reacted = False
	while reacted == False:
		reactions = messages[index].reactions
		for reaction in reactions:
			users = await reaction.users().flatten()
			for user in users:
				if user.id == player.id:
					reacted = True
		await asyncio.sleep(0.1)
	
async def getReaction(player, index):

	nums = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
	messages = messageDict.get(player.id)
	reactions = messages[index].reactions

	for reaction in reactions:
		users = await reaction.users().flatten()
		for user in users:
			if user.id == player.id:
				if reaction.emoji in nums:
					emoji = reaction.emoji
					await reaction.remove(player)
					return nums.index(emoji)
				else :
					await reaction.remove(player)
					return -1

def calcWinRatio(wins, losses):
    return pow(wins, 1.35)/ (losses + 1)

#-----------GAME LOGIC----------------

async def main(player):
	# Stores the player so that others cannot interfere
	player = player
	output = "\nWelcome to Racko! --- This may take a moment to load.\nTo decide which player goes first, two cards will be dealt."
	deck = init_deck()
	discard = []
	shuffle_cards(deck)
	user_num = deal_card(deck)
	comp_num = deal_card(deck)
	turn = 0
	game = True
	check = False
	output = output + ("\nYou drew a {0}, and the computer drew a {1}.".format(user_num,comp_num))
	
	if user_num > comp_num:
		output = output + "\nYou go first!"
	else:
		output = output + "\nThe computer goes first."
		turn = 1

	deck.append(user_num)
	deck.append(comp_num)
	shuffle_cards(deck)

	hands = deal_hands(deck)
	user_rack = hands[0]
	comp_rack = hands[1]

	await updateGameInfo(player, "", output)

	while game == True:

		if turn == 0 and check_racko(user_rack) == False and check_racko(comp_rack) == False:
			await editGameMessage(player, GAME_BOARD, "", getGameBoard(user_rack, comp_rack, discard) )

			await editGameMessage(player, CARD_DRAW, "fix", "Would you like to draw from the deck?(1) Or the discard?(2)")
			await checkForReaction(player, CARD_DRAW)
			response = await getReaction(player, CARD_DRAW)
			
			while response <= 0 or response > 2:
				await updateGameInfo(player, "css", "[Invalid input. Try again.]")
				await checkForReaction(player, CARD_DRAW)
				response = await getReaction(player, CARD_DRAW)

			if response == 1:
				card = deal_card(deck)
			elif response == 2:
				if discard:
					card = discard[len(discard) - 1]
					discard.pop(len(discard) - 1)
				else:
					await updateGameInfo(player, "css", "[There's nothing in the discard pile.]\n Drawing from the deck...")
					card = deal_card(deck)

			await editGameMessage(player, CARD_DRAW, "", "Would you like to draw from the deck?(1) Or the discard?(2)")
			await editGameMessage(player, SLOT_PICK, "fix", "You drew a " + str(card) + "\nWhich slot would you like to replace? (0-9)")
			await checkForReaction(player, SLOT_PICK)
			slot = await getReaction(player, SLOT_PICK)
			while slot < 0 or slot > 9:
				await updateGameInfo(player, "css", "\n[Invalid input. Try again.]")
				await checkForReaction(player, SLOT_PICK)
				slot = await getReaction(player, SLOT_PICK)
			await updateGameInfo(player, "", find_and_replace(card, slot, user_rack, discard, "You"))
			await editGameMessage(player, SLOT_PICK, "", "\nWhich slot would you like to replace? (0-9)")
			await editGameMessage(player, GAME_BOARD, "", getGameBoard(user_rack, comp_rack, discard))

			turn = 1
		elif turn == 1 and check_racko(user_rack) == False and check_racko(comp_rack) == False:
			await updateGameInfo(player, "", computer_turn(comp_rack, deck, discard))
			await editGameMessage(player, GAME_BOARD, "", getGameBoard(user_rack, comp_rack, discard))
			turn = 0
		
		elif check_racko(user_rack) == True:
			await updateGameInfo(player, "css", '\n"You won!"')
			game = False

		elif check_racko(comp_rack) == True:
			await updateGameInfo(player, "diff", "- The computer won...")
			game = False

bot.run(TOKEN)


