from app import db
from app.models import Game, BatGame, PlayerData
from flask_login import current_user
from collections import defaultdict

def get_cum_batter_stats():
	games = Game.query.filter_by(user_id=current_user.id)
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
		if batters[id]['ab'] == 0:
			batters[id]['ba'] = '.---'
			batters[id]['slg'] = '.---'
			slg = None
		else:
			ba = batters[id]['h'] / batters[id]['ab']
			slg = (batters[id]['h'] + batters[id]['2b'] + 2 * batters[id]['3b'] + 3 * batters[id]['hr']) / batters[id]['ab']
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