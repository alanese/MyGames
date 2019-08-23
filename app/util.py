from app.models import GameData

team_abbrevs = {"Anaheim Angels": "ANA",
				"Arizona Diamondbacks": "ARI",
				"Atlanta Braves": "ATL",
				"Baltimore Orioles": "BAL",
				"Boston Red Sox": "BOS",
				"Chicago Cubs": "CHC",
				"Chicago White Sox": "CHW",
				"Cincinnati Reds": "CIN",
				"Cleveland Indians": "CLE",
				"Colorado Rockies": "COL",
				"Detroit Tigers": "DET",
				"Florida Marlins": "FLA",
				"Houston Astros": "HOU",
				"Kansas City Royals": "KCR",
				"Los Angeles Angels": "LAA",
				"Los Angeles Angels of Anaheim": "LAA",
				"Miami Marlins": "MIA",
				"Milwaukee Brewers": "MIL",
				"Minnesota Twins": "MIN",
				"Montreal Expos": "MON",
				"New York Mets": "NYM",
				"New York Yankees": "NYY",
				"Oakland Athletics": "OAK",
				"Philadelphia Phillies": "PHI",
				"Pittsburgh Pirates": "PIT",
				"San Diego Padres": "SDP",
				"San Francisco Giants": "SFG",
				"Seattle Mariners": "SEA",
				"St. Louis Cardinals": "STL",
				"Tampa Bay Devil Rays": "TBD",
				"Tampa Bay Rays": "TBR",
				"Texas Rangers": "TEX",
				"Toronto Blue Jays": "TOR",
				"Washington Nationals": "WSN"}

BBREF_URL_BASE = "https://www.baseball-reference.com/boxes/{}/{}{}{}.shtml"
# Takes a GameData object as argument
# Returns the baseball-reference.com URL for the game's box score
def get_bbref_url(game):
	team_abbrev = team_abbrevs[game.home_team]
	date = "".join(game.date.split("-"))
	if game.dh_status is None:
		dh_status = 0
	else:
		dh_status = game.dh_status
	return BBREF_URL_BASE.format(team_abbrev, team_abbrev, date, dh_status)

MLB_URL_BASE = "https://www.mlb.com/gameday/{}"
# Takes a GameData object as argument
# Returns the mlb.com URL for the game's box score
def get_mlb_url(game):
	return MLB_URL_BASE.format(game.game_pk)