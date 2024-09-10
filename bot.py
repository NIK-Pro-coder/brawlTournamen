import disnake
from disnake.ext import commands
import dotenv
import os
import json
import webhook
import threading
import asyncio

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

strGuild = os.getenv("GUILD_ID")

if strGuild == None :
    print("Failed to get guild ID from env file")
    exit(1)

GUILD_ID = int(strGuild)

bot = commands.InteractionBot(test_guilds=[GUILD_ID])

@bot.slash_command()
async def addplayer(inter, tag):
	"""Adds a player to the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.addPlayer(tag)

@bot.slash_command()
async def addclub(inter, tag):
	"""Adds the members of a club to the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.addClub(tag)

@bot.slash_command()
async def addclubmates(inter, tag):
	"""Add clubmates of the tag to the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.addClubmates(tag)

@bot.slash_command()
async def removeplayer(inter, tag):
	"""Removes a player from the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.removePlayer(tag)

@bot.slash_command()
async def addpoints(inter, identifier, amount = 1):
	"""Adds points to a player"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.addPoints(identifier, amount)

@bot.slash_command()
async def planround(inter, mode, stage = -1):
	"""Plans round for the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.planStage(mode, stage)

@bot.slash_command()
async def showplayers(inter):
	"""Shows the participants of the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.showPlayers()

@bot.slash_command()
async def showrounds(inter):
	"""Shows the round of the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.showPlan()

@bot.slash_command()
async def showscores(inter):
	"""Shows the scores of the players in the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.showScoreBoard()

@bot.slash_command()
async def start(inter):
	"""Starts the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	threading.Thread(target = webhook.startTournament).start()

@bot.slash_command()
async def announcewinners(inter):
	"""Announces the winners of the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.announceWinners()

@bot.slash_command()
async def eliminate(inter, remaining):
	"""Eliminate players so that [remaining] will be left"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.eliminate(remaining)

@bot.slash_command()
async def reset(inter):
	"""Resets the tournament"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.reset()

@bot.slash_command()
async def maketeams(inter, num = "3"):
	"""Makes teams of num players"""
	if not(webhook.accept) :
		await inter.response.send_message("Command rejected")
		return
	await inter.response.send_message("On it!")
	webhook.makeTeams(num)

def getConsole() :
	while True :
		ins = input("").strip()

		webhook.execFunc(ins)


threading.Thread(target = getConsole).start()

bot.run(BOT_TOKEN)
