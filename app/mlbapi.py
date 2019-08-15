import requests
from app.models import GameData, PlayerData, BatGame, PitchGame

URL_BASE = "http://statsapi.mlb.com/api/v1/"

BOX_URL = URL_BASE + "game/{}/boxscore"
SCHEDULE_URL = URL_BASE + "schedule/games/?sportId=1&date={}/{}/{}"
PLAYER_URL = URL_BASE + "people/{}"

# Queries the MLB API for the box score of the given game
# Returns a list of BatGame objects for the given game
# Returns the empty list if the game exists but has no player stats
# Returns None if the game_pk does not exist or something else weird happens
# Optionally uses the provided request object
def get_game_batters(game_pk, r=None):
	if not r:
		request_url = BOX_URL.format(game_pk)
		r = requests.get(request_url)
	if not (r.status_code == requests.codes.ok):
		return None
	r_json = r.json()
	if not ('teams' in r_json):
		return None
	away_batters = _get_batters_util(r_json['teams']['away']['players'], game_pk)
	home_batters = _get_batters_util(r_json['teams']['home']['players'], game_pk)
	return away_batters + home_batters

# Queries the MLB API for the box score of the given game
# Returns a list of PitchGame objects for the given game
# Returns the empty list if the game exists but has no player stats
# Returns None if the game_pk does not exist or something else weird happens
# Optionally uses the provided request object
def get_game_pitchers(game_pk, r=None):
	if not r:
		request_url = BOX_URL.format(game_pk)
		r = requests.get(request_url)
	if not (r.status_code == requests.codes.ok):
		return None
	r_json = r.json()
	if not ('teams' in r_json):
		return None
	away_pitchers = _get_pitchers_util(r_json['teams']['away']['players'], game_pk)
	home_pitchers = _get_pitchers_util(r_json['teams']['home']['players'], game_pk)
	return away_pitchers + home_pitchers

# Returns results from get_game_batters and get_game_pitchers, reusing the request
def get_game_batters_and_pitchers(game_pk):
	request_url = BOX_URL.format(game_pk)
	r = requests.get(request_url)
	b = get_game_batters(game_pk, r=r)
	p = get_game_pitchers(game_pk, r=r)
	return (b, p)

# Utility function - takes the chunk of JSON from an MLB API box score
# corresponding to one team's players (at ['home/away']['team']['players'])
# and the game_pk and returns a list of BatGame objects for those who batted
def _get_batters_util(batters, game_pk):
	b = []
	for batter in batters.values():
		if ('stats' in batter) and (len(batter['stats']['batting']) > 0):
			bg = BatGame(game_pk=game_pk,
						 batter_id = batter['person']['id'],
						 ab=batter['stats']['batting']['atBats'],
						 r=batter['stats']['batting']['runs'],
						 h=batter['stats']['batting']['hits'],
						 doubles=batter['stats']['batting']['doubles'],
						 triples=batter['stats']['batting']['triples'],
						 hr=batter['stats']['batting']['homeRuns'],
						 rbi=batter['stats']['batting']['rbi'],
						 sb=batter['stats']['batting']['stolenBases'],
						 cs=batter['stats']['batting']['caughtStealing'],
						 k=batter['stats']['batting']['strikeOuts'],
						 bb=batter['stats']['batting']['baseOnBalls'],
						 hbp=batter['stats']['batting']['hitByPitch'],
						 sf=batter['stats']['batting']['sacFlies'])
			b.append(bg)
	return b

# Utility function - takes the chunk of JSON from an MLB API box score
# corresponding to one team's players (at ['home/away']['team']['players'])
# and the game_pk and returns a list of PitchGame objects for those who pitched
def _get_pitchers_util(pitchers, game_pk):
	p = []
	for pitcher in pitchers.values():
		if ('stats' in pitcher) and (len(pitcher['stats']['pitching']) > 0):
			pg = PitchGame(game_pk=game_pk,
						   pitcher_id=pitcher['person']['id'],
						   w=pitcher['stats']['pitching'].get('wins', 0),
						   losses=pitcher['stats']['pitching'].get('losses', 0),
						   gs=pitcher['stats']['pitching'].get('gamesStarted', 0),
						   gf=pitcher['stats']['pitching'].get('gamesFinished', 0),
						   sv=pitcher['stats']['pitching'].get('saves', 0),
						   h=pitcher['stats']['pitching'].get('hits', 0),
						   r=pitcher['stats']['pitching'].get('runs', 0),
						   er=pitcher['stats']['pitching'].get('earnedRuns', 0),
						   hr=pitcher['stats']['pitching'].get('homeRuns', 0),
						   bb=pitcher['stats']['pitching'].get('baseOnBalls', 0),
						   so=pitcher['stats']['pitching'].get('strikeOuts', 0),
						   outs=pitcher['stats']['pitching'].get('outs', 0))
			p.append(pg)
	return p
					 
	
# Queries the MLB API for completed games on the given date (given as a date or datetime object)
# Returns a list of GameData object
# Returns None if an HTTP error happens or no games are found
def get_schedule(d):
	request_url = SCHEDULE_URL.format(d.month, d.day, d.year)
	r = requests.get(request_url)
	if not (r.status_code == requests.codes.ok):
		return None
	r = r.json()
	if ('dates' not in r) or (len(r['dates']) <= 0):
		return None
	games = []
	date_str = d.isoformat()
	if ('games' not in r['dates'][0]):
		return None
	for game in r['dates'][0]['games']:
		if game['status']['codedGameState'] == 'F':
			if game['doubleHeader'] == 'Y':
				dh_status = game['gameNumber']
			else:
				dh_status = 0
			g = GameData(game_pk=game['gamePk'],
						 date=date_str,
						 home_team=game['teams']['home']['team']['name'],
						 home_score=game['teams']['home']['score'],
						 away_team=game['teams']['away']['team']['name'],
						 away_score=game['teams']['away']['score'],
						 dh_status=dh_status
						 )
			games.append(g)
	return games
		

# Queries the MLB API for the player with the given ID
# Returns a PlayerData object for the player, or None if not found
def get_player(id):
	request_url = PLAYER_URL.format(id)
	r = requests.get(request_url)
	if not (r.status_code == requests.codes.ok):
		return None
	r = r.json()
	if ("people" not in r) or (len(r["people"]) <= 0):
		return None
	else:
		player = PlayerData(id=id,
							name=r['people'][0]['fullName'],
							sort_name=r['people'][0]['lastFirstName'])
		return player
		
# Queries the MLB API and returns a GameData object for the given
# game_pk and date
# Optionally uses the given request object
def get_game_data(game_pk, date, r=None):
	if not r:
		request_url = BOX_URL.format(game_pk)
		r = requests.get(request_url)
	if not (r.status_code == requests.codes.ok):
		return None
	r_json = r.json()
	if ('teams' not in r_json):
		return None
	gd = GameData(game_pk=game_pk,
				  date=date,
				  home_team=r_json['teams']['home']['team']['name'],
				  home_score=r_json['teams']['home']['teamStats']['batting']['runs'],
				  away_team=r_json['teams']['away']['team']['name'],
				  away_score=r_json['teams']['away']['teamStats']['batting']['runs'])
	return gd