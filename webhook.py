import requests
import json
from types import SimpleNamespace
import threading
import dotenv
import os
import time

dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")

def getUrl(url : str, head : dict = {}) :
	print(f"DEBUG : Issued get request to URL : {url}")
	if head :
		print(f"DEBUG : Header : {head}")
	r = requests.get(url, headers = head)

	print(f"DEBUG : Response code : {r.status_code}")
	if not(r.ok) :
		return json.loads(r.text)["reason"]

	return r

def GET(url : str | None, head : dict = {}) :
	if url == None :
		print("No url provided!")
		return

	res = getUrl(url, head)

	if type(res) is str :
		return res

	return json.loads(res.text, object_hook=lambda d: SimpleNamespace(**d))

#GET = lambda url, head = {} :

hookUrl = GET(os.getenv("HOOK_URL"))

if type(hookUrl) is str :
	print(f"Failed to load webhook, reason : {hookUrl}")
	exit()

hookId = hookUrl.id
hookToken = hookUrl.token

hookUrl = f"https://discord.com/api/webhooks/{hookId}/{hookToken}"

messageQueue = []

def hook(text, extra = {}) :
	global hookUrl

	text = text.strip()

	form = {"content" : f"```{text}```"}

	form.update(extra)

	messageQueue.append(form)

running = True

def hookThread() :
	while running or messageQueue :
		if len(messageQueue) == 0 :
			continue

		form = messageQueue.pop(0)

		print(f"CHAT : {form['content'].strip('`')}")
		requests.post(hookUrl, json = form)

		time.sleep(2)

threading.Thread(target = hookThread).start()

hook("Brawl Tournament bot started")

def showPlayers() :
	if len(players) > 0 :
		full = "PLayers :\n\n"
		for i in players :
			full += f"{i.name} ({i.tag})\n"
		hook(full)
	else :
		hook("No players in the tournament")

authHeader = {"Authorization" : f"Bearer {API_KEY}"}

def addPlayer(tag) :
	newPlayer = GET(
		f"https://api.brawlstars.com/v1/players/%23{tag.upper().strip('#')}",
		authHeader
	)

	if type(newPlayer) is str :
		hook(f"Failed to fetch player, reason : {newPlayer}")
		return

	players.append(newPlayer)
	points[newPlayer.name] = 0

	hook(f"Player '{players[-1].name}' added to tournament")

def addClub(tag) :
	club = GET(
		f"https://api.brawlstars.com/v1/clubs/%23{tag.upper().strip('#')}",
		authHeader
	)

	if type(club) is str :
		hook(f"Failed to fetch club, reason : {club}")
		return

	hook(f"Adding members from club : '{club.name}' ({len(club.members)})")
	for i in club.members :
		addPlayer(i.tag)

def removePlayer(identif) :
	for n,i in enumerate(players) :
		if i.tag == "#" + identif.strip("#") or i.name == identif :
			hook(f"Player '{i.name}' removed from tournament")
			players.pop(n)
			return

	hook("Player not found")

def closeTournament() :
	hook("Closing Tournament")
	exit()

possible = {
	"soloshowdown" : "soloShowdown",
	"duoshowdown" : "duoShowdown",
	"knockout" : "knockout",
	"bounty" : "bounty",
	"hotzone" : "hotZone",
	"gemgrab" : "genGrab",
	"footbrawl" : "brawlBall",
	"heist" : "heist",
	"paintbrawl" : "paintBrawl",
	"wipeout" : "wipeout",
	"wipeout5v5" : "wipeout5V5",
	"knockout5v5" : "knockout5V5",
	"brawlBall5v5" : "brawlBall5V5",
	"duels" : "duels",
}

players = []
stages = []

points = {}

def planStage(mode, num = -1) :
	if num == -1 :
		num = len(stages) + 1

	if num < 1 :
		hook("Invalid round number")
		return

	mode = mode.lower()

	if not(mode in possible) :
		hook("Invalid mode")
		return

	while len(stages) < num :
		stages.append(None)

	stages[num-1] = mode
	hook(f"Round {num} is now {mode} ({possible[mode]} for supercell)")

def showPlan() :
	if len(stages) > 0 :
		full = "Tournament Rounds :\n\n"

		for n,i in enumerate(stages) :
			full += f"{n+1} : {i}\n"

		hook(full)

		return

	hook("No Rounds Planned")

def addPoints(identif, num = 1) :
	for n,i in enumerate(players) :
		if i.tag == "#" + identif.strip("#") or i.name == identif :
			hook(f"Added {num} point{'' if num == 1 else 's'} to '{i.name}'")
			points[i.name] += int(num)
			return

	hook("Player not found")

def showScoreBoard() :
	srt = sorted(points, key = lambda x : -points[x])

	full = "Scores :\n\n"

	for i in srt :
		pts = points[i]
		full += f"{i} : {pts} point{'' if pts == 1 else 's'}\n"

	hook(full)

def addClubmates(tag) :
	newPlayer = GET(
		f"https://api.brawlstars.com/v1/players/%23{tag.upper().strip('#')}",
		authHeader
	)

	if type(newPlayer) is str :
		hook(f"Failed to fetch player, reason : {newPlayer}")
		return

	addClub(newPlayer.club.tag)

passed = 0
stage = 0

def reset() :
	global stage
	global stages
	global players
	global points

	stage = 0
	players.clear()
	stages.clear()
	points = {}

	hook("Tournament reset")

def checkPlayer(last, player) :
	global passed
	global stages
	global stage

	while running :
		logs = GET(
			f"https://api.brawlstars.com/v1/players/%23{player.tag.strip('#')}/battlelog",
			authHeader
		)
		if type(logs) is str :
			hook(f"Failed to fetch battlelog, reason : {logs}")
			return

		lastBattle = logs.items[0].battle

		if lastBattle != last and lastBattle.mode == possible[stages[stage]] :
			try :
				teams = lastBattle.teams.copy()
			except :
				teams = [[x] for x in lastBattle.players]

			gain = len(teams)+1

			try :
				if lastBattle.starPlayer.tag == player.tag :
					gain += len(teams)/2
			except :
				...

			for i in teams :
				gain -= 1
				for p in i :
					if p.tag == player.tag :
						passed += 1
						hook(f"Player '{player.name}' finished! ({passed}/{len(players)})")
						addPoints(player.tag, gain)
						return

def startTournament() :
	global passed
	global stage

	if len(stages) == 0 :
		hook("Cannot start a tournament with no stages")
		return

	hook("Tournament Started!")

	lastBattle = {}

	for i in players :
		logs = GET(
			f"https://api.brawlstars.com/v1/players/%23{i.tag.strip('#')}/battlelog",
			authHeader
		)
		if type(logs) is str :
			hook(f"Failed to fetch battlelog, reason : {logs}")
			return

		player = GET(
			f"https://api.brawlstars.com/v1/players/%23{i.tag.strip('#')}",
			authHeader
		)
		if type(player) is str :
			hook(f"Failed to fetch player, reason : {player}")
			return

		lastBattle[player.name] = (
			logs.items[0],
			player
		)

	stage = 0

	while True :
		mode = stages[stage]
		hook(f"Round {stage+1} : {mode}")
		for i in lastBattle.items() :
			threading.Thread(target = checkPlayer, args = i[1]).start()
		passed = 0
		while passed < len(players) :
			...

		stage += 1

		if stage >= len(stages) or not(running):
			hook("Tournament finished!")
			announceWinners()
			return

		hook(f"Round {stage} finished!")
		showScoreBoard()

def kill() :
	global running

	hook("Bye bye")

	running = False

def restart() :
	global running

	running = True
	threading.Thread(target = hookThread).start()

	hook("Welcome back")

def announceWinners() :
	srt = sorted(points.items(), key = lambda x : -x[1])

	for n,i in enumerate(srt) :
		p = i[1]
		j = i[0]
		ptext = f"{j}, with {p} point{'' if p==1 else 's'}"

		if n == 0 :
			hook("First place goes to ...")
			hook(ptext)
		elif n == 1 :
			hook("Second place goes to ...")
			hook(ptext)
		elif n == 2 :
			hook("Third place goes to ...")
			hook(ptext)
		else :
			ptext = f"{n+1} | " + ptext
			hook(ptext)

accept = True

def acceptBot() :
	global accept
	hook("Accepting commands from bot")
	accept =  True

def rejectBot() :
	global accept
	hook("Rejecting commands from bot")
	accept =  False

def eliminate(remaining) :
	hook(f"{remaining} players will be left")
	srt = list(sorted(points, key = lambda x : -points[x]))

	for i in players[::-1] :
		if srt.index(i.name) > int(remaining) :
			removePlayer(i.tag)

cmds = {
	"show" : showPlayers,
	"add" : addPlayer,
	"addClub" : addClub,
	"rmv" : removePlayer,
	"end" : closeTournament,
	"plan" : planStage,
	"showPlan" : showPlan,
	"point" : addPoints,
	"scores" : showScoreBoard,
	"addMates" : addClubmates,
	"start" : startTournament,
	"kill" : kill,
	"winners" : announceWinners,
	"accept" : acceptBot,
	"reject" : rejectBot,
	"eliminate" : eliminate,
	"reset" : reset,
}

def execFunc(string) :
	cmd = string.split(" ")

	try :
		func = cmds[cmd.pop(0)]
	except :
		hook("Invalid command")
		return

	func(*cmd)

if __name__ == "__main__" :
	while running :
		execFunc(input(""))
