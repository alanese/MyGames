from app import db
from app.models import Game, GameData, BatGame, PitchGame, PlayerData
import app.mlbapi as mlbapi
from collections import defaultdict

def get_cum_batter_stats(user_id):
	games = Game.query.filter_by(user_id=user_id)
	pks = [ game.game_pk for game in games ]
	batters = defaultdict(lambda: defaultdict(int))
	for pk in pks:
		bat_games = BatGame.query.filter_by(game_pk=pk)
		for game in bat_games:
			id = game.batter_id
			batters[id]['g'] = batters[id]['g'] + 1
			batters[id]['ab'] = batters[id]['ab'] + game.ab
			batters[id]['r'] = batters[id]['r'] + game.r
			batters[id]['h'] = batters[id]['h'] + game.h
			batters[id]['2b'] = batters[id]['2b'] + game.doubles
			batters[id]['3b'] = batters[id]['3b'] + game.triples
			batters[id]['hr'] = batters[id]['hr'] + game.hr
			batters[id]['rbi'] = batters[id]['rbi'] + game.rbi
			batters[id]['sb'] = batters[id]['sb'] + game.sb
			batters[id]['cs'] = batters[id]['cs'] + game.cs
			batters[id]['k'] = batters[id]['k'] + game.k
			batters[id]['bb'] = batters[id]['bb'] + game.bb
			batters[id]['hbp'] = batters[id]['hbp'] + game.hbp
			batters[id]['sf'] = batters[id]['sf'] + game.sf

	for id in batters.keys():
		batters[id]['tb'] = batters[id]['h'] + batters[id]['2b'] + 2 * batters[id]['3b'] + 3 * batters[id]['hr']
		if batters[id]['ab'] == 0:
			batters[id]['ba'] = '.---'
			batters[id]['slg'] = '.---'
			slg = None
		else:
			ba = batters[id]['h'] / batters[id]['ab']
			slg = batters[id]['tb'] / batters[id]['ab']
			batters[id]['ba'] = '{:.3f}'.format(ba)
			batters[id]['slg'] = '{:.3f}'.format(slg)
		
		obp_denom = batters[id]['ab'] + batters[id]['bb'] + batters[id]['hbp'] + batters[id]['sf']
		if obp_denom == 0:
			batters[id]['obp'] = '.---'
			obp = None
		else:
			obp = (batters[id]['h'] + batters[id]['bb'] + batters[id]['hbp']) / obp_denom
			batters[id]['obp'] = '{:.3f}'.format(obp)
		
		if (slg is None) or (obp is None):
			batters[id]['ops'] = '.---'
		else:
			ops = obp + slg
			batters[id]['ops'] = '{:.3f}'.format(ops)
		player_record = PlayerData.query.filter_by(id=id).first()
		if player_record is not None:
			batters[id]['name'] = player_record.name
			batters[id]['sortname'] = player_record.sort_name
		else:
			batters[id]['name'] = "???"
			batters[id]['sortname'] = "???"

	return batters

def get_cum_pitcher_stats(user_id):
	games = Game.query.filter_by(user_id=user_id)
	pks = [ game.game_pk for game in games ]
	pitchers = defaultdict(lambda: defaultdict(int))
	for pk in pks:
		pitch_games = PitchGame.query.filter_by(game_pk=pk)
		for game in pitch_games:
			id = game.pitcher_id
			pitchers[id]['w'] = pitchers[id]['w'] + game.w
			pitchers[id]['losses'] = pitchers[id]['losses'] + game.losses
			pitchers[id]['g'] = pitchers[id]['g'] + 1
			pitchers[id]['gs'] = pitchers[id]['gs'] + game.gs
			pitchers[id]['gf'] = pitchers[id]['gf'] + game.gf
			pitchers[id]['sv'] = pitchers[id]['sv'] + game.sv
			pitchers[id]['outs'] = pitchers[id]['outs'] + game.outs
			pitchers[id]['h'] = pitchers[id]['h'] + game.h
			pitchers[id]['r'] = pitchers[id]['r'] + game.r
			pitchers[id]['er'] = pitchers[id]['er'] + game.er
			pitchers[id]['hr'] = pitchers[id]['hr'] + game.hr
			pitchers[id]['bb'] = pitchers[id]['bb'] + game.bb
			pitchers[id]['so'] = pitchers[id]['so'] + game.so
	
	for id in pitchers.keys():
		pitchers[id]['ip'] = '{}.{}'.format(int(pitchers[id]['outs'] / 3),
											pitchers[id]['outs'] % 3)
		if pitchers[id]['outs'] == 0:
			pitchers[id]['era'] = '-.--'
		else:
			era = (pitchers[id]['er'] / pitchers[id]['outs']) * 27
			pitchers[id]['era'] = '{:.2f}'.format(era)
		player_record = PlayerData.query.filter_by(id=id).first()
		if player_record is not None:
			pitchers[id]['name'] = player_record.name
			pitchers[id]['sortname'] = player_record.sort_name
		else:
			pitchers[id]['name'] = "???"
			pitchers[id]['sortname'] = "???"
	return pitchers

def get_cum_team_records(user_id):
	games = Game.query.filter_by(user_id=user_id)
	pks = [ game.game_pk for game in games ]
	teams = defaultdict(lambda: defaultdict(int))
	for pk in pks:
		game_rec = GameData.query.filter_by(game_pk=pk).first()
		if game_rec is not None:
			h_team = game_rec.home_team
			h_score = game_rec.home_score
			a_team = game_rec.away_team
			a_score = game_rec.away_score
			
			teams[h_team]['rs'] = teams[h_team]['rs'] + h_score
			teams[h_team]['ra'] = teams[h_team]['ra'] + a_score
			teams[a_team]['rs'] = teams[a_team]['rs'] + a_score
			teams[a_team]['ra'] = teams[a_team]['ra'] + h_score
			if h_score > a_score:
				teams[h_team]['wins'] = teams[h_team]['wins'] + 1
				teams[a_team]['losses'] = teams[a_team]['losses'] + 1
			elif h_score < a_score:
				teams[a_team]['wins'] = teams[a_team]['wins'] + 1
				teams[h_team]['losses'] = teams[h_team]['losses'] + 1
			else:
				teams[h_team]['ties'] = teams[h_team]['ties'] + 1
				teams[a_team]['ties'] = teams[a_team]['ties'] + 1
				
	for name in teams.keys():
		wpct = teams[name]['wins'] / (teams[name]['wins'] + teams[name]['losses'])
		teams[name]['wpct'] = "{:.3f}".format(wpct)
	return teams

# If the PlayerData table does not have a record with the given
# player id, construct one and add it to the table.
# Returns True if the record was added and False if it was already there
def add_player_if_missing(id, commit=True):
	player_record = PlayerData.query.filter_by(id=id).first()
	if not player_record:
		new_record = mlbapi.get_player(id)
		db.session.add(new_record)
		if commit:
			db.session.commit()
		return True
	else:
		return False

# Retrieve a list of game_pk values for games the given user has registered
def get_user_game_pks(user_id):
	games = Game.query.filter_by(user_id=user_id)
	return [game.game_pk for game in games]

# Adds BatGame and PitchGame records, and PlayerData where necessary,
# for the given game_pk
def add_game_stats(game_pk, commit=True):
	bat_stats, pitch_stats = mlbapi.get_game_batters_and_pitchers(game_pk)
	for batter in bat_stats:
		add_player_if_missing(batter.batter_id)
	for pitcher in pitch_stats:
		add_player_if_missing(pitcher.pitcher_id)
	db.session.add_all(bat_stats)
	db.session.add_all(pitch_stats)
	if commit:
		db.session.commit()

def add_game_data_if_missing(game_data, commit=True):
	record = GameData.query.filter_by(game_pk=game_data.game_pk).first()
	if record is None:
		db.session.add(game_data)
		print("Added game {}".format(game_data.game_pk))
		if commit:
			db.session.commit()
		return True
	return False

def add_all_game_data_if_missing(game_data_list, commit=True):
	added=False
	for game in game_data_list:
		added = (add_game_data_if_missing(game, commit=False)) or added
	if commit:
		db.session.commit()
	return added

def get_all_game_stats(game_pk):
	b = get_batter_game_stats(game_pk)
	p = get_pitcher_game_stats(game_pk)
	return (b, p)

def get_batter_game_stats(game_pk):
	stats = db.session.query(BatGame, PlayerData).\
					   filter(BatGame.game_pk==game_pk).\
					   filter(BatGame.batter_id==PlayerData.id).\
					   all()
	return stats

def get_pitcher_game_stats(game_pk):
	stats = db.session.query(PitchGame, PlayerData).\
					   filter(PitchGame.game_pk==game_pk).\
					   filter(PitchGame.pitcher_id==PlayerData.id).\
					   all()
	return stats