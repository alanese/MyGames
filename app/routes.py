from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, DateForm, RegistrationForm
from app.models import User, Game, GameData, PlayerData, BatGame, PitchGame
from collections import defaultdict
import requests

@app.route('/')
@app.route('/index')
def index():
	if current_user.is_authenticated:
		num_games = Game.query.filter_by(user_id=current_user.id).count()
	else:
		num_games = GameData.query.count()
		
	return render_template("index.html", num_games=num_games)
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash("Successfully registered! Log in below.")
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)
	
@app.route('/choosedate', methods=['GET', 'POST'])
@login_required
def choose_date():
	form = DateForm()
	if form.validate_on_submit():
		return redirect(url_for('game_select', year=form.dt.data.year, month=form.dt.data.month, day=form.dt.data.day))
	return render_template('choosedate.html', form=form)

@app.route('/gameselect/<year>/<month>/<day>', methods=['GET', 'POST'])
@login_required
def game_select(year, month, day):
	games = get_games(month + '/' + day + '/' + year)
	if len(games) == 0:
		flash("No games found for {}-{}-{}".format(year, month.zfill(2), day.zfill(2)))
		return redirect(url_for('choose_date'))
	else:
		return render_template('gameselect.html', games=games, date="{}-{}-{}".format(year, month.zfill(2), day.zfill(2)))
		
@app.route('/mygames')
@login_required
def list_games():
	games = db.session.query(Game, GameData).\
					   filter(Game.user_id==current_user.id).\
					   filter(GameData.game_pk==Game.game_pk).\
					   order_by(Game.game_pk).\
					   all()
	#games = Game.query.filter_by(user_id=current_user.id).order_by(Game.game_pk)
	return render_template('mygames.html', games=games)

box_url = "http://statsapi.mlb.com/api/v1/game/{}/boxscore"
@app.route('/addgame/<game_pk>/<date>', methods=['GET', 'POST'])
@login_required
def add_game(game_pk, date):
	r = requests.get(box_url.format(game_pk))
	r = r.json()
	game = Game(game_pk=game_pk, user_id=current_user.id)
	check_game = GameData.query.filter_by(game_pk=game_pk).first()
	if check_game is None:
		game_data = GameData(game_pk=game_pk, date=date,
							 home_team=r['teams']['home']['team']['name'],
							 home_score=r['teams']['home']['teamStats']['batting']['runs'],
							 away_team=r['teams']['away']['team']['name'],
							 away_score=r['teams']['away']['teamStats']['batting']['runs'])
		db.session.add(game_data)
		db.session.commit()
		add_game_stats_to_db(game_pk)
	db.session.add(game)
	db.session.commit()
	flash("Game {} successfully added".format(game_pk))
	return redirect(url_for('list_games'))
	
@app.route('/removegame/<game_pk>', methods=['GET', 'POST'])
@login_required
def rm_game(game_pk):
	rm_count = Game.query.filter_by(user_id=current_user.id, game_pk=game_pk).delete()
	db.session.commit()
	if rm_count > 0:
		flash("Game {} removed".format(game_pk))
	else:
		flash("Game {} for user {} not found in db".format(game_pk, current_user.id))
	return redirect(url_for('list_games'))
	
@app.route('/batterstats')
@login_required
def batter_stats():
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

	players = sorted(batters.items(), key=lambda x: x[1]['sortname'])
	return render_template('bat_stats.html', players=players)
	
@app.route('/pitcherstats')
@login_required
def pitcher_stats():
	games = Game.query.filter_by(user_id=current_user.id)
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
			
	players = sorted(pitchers.items(), key=lambda x: x[1]['sortname'])
	return render_template("pitch_stats.html", players=players)
	
@app.route('/teamrecords')
@login_required
def team_records():
	games = Game.query.filter_by(user_id=current_user.id)
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
	teams = sorted(teams.items(), key=lambda x: x[1]['wpct'], reverse=True)
	return render_template("team_records.html", teams=teams)
	
@app.route('/batter/<player_id>')
@login_required
def batter_games(player_id):
	name = PlayerData.query.filter(PlayerData.id==player_id).first().name
	q = db.session.query(Game, BatGame, GameData).\
				   filter(Game.game_pk==BatGame.game_pk).\
				   filter(Game.game_pk==GameData.game_pk).\
				   filter(Game.user_id==current_user.id).\
				   filter(BatGame.batter_id==player_id).\
				   order_by(GameData.date).\
				   all()
	return render_template("batter.html", name=name, rows=q)
	
@app.route('/pitcher/<player_id>')
@login_required
def pitcher_games(player_id):
	name = PlayerData.query.filter(PlayerData.id==player_id).first().name
	q = db.session.query(Game, PitchGame, GameData).\
				   filter(Game.game_pk==PitchGame.game_pk).\
				   filter(Game.game_pk==GameData.game_pk).\
				   filter(Game.user_id==current_user.id).\
				   filter(PitchGame.pitcher_id==player_id).\
				   order_by(GameData.date).\
				   all()
	rows = [ (g, pg, gd, outs_to_ip(pg.outs)) for (g, pg, gd) in q ]			   
	return render_template("pitcher.html", name=name, rows=rows)
			
@app.route('/viewdb')	
def viewdb():
	return render_template('viewdb.html', games=GameData.query.all(),
										  batters=BatGame.query.all(),
										  pitchers=PitchGame.query.all(),
										  players=PlayerData.query.all())
	


#Return a dict of games for date in MM/DD/YYYY format
schedule_url_root = 'http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date='
def get_games(datestr):
	r = requests.get(schedule_url_root + datestr)
	r = r.json()
	if len(r['dates']) == 0:
		return {}
	else:
		
		scores = [ (x['gamePk'], '{0} {1} @ {2} {3}'.format(
								  x['teams']['away']['team']['name'],
								  x['teams']['away']['score'],
								  x['teams']['home']['team']['name'],
								  x['teams']['home']['score'])) for x in r['dates'][0]['games'] if x['status']['codedGameState'] == 'F']
		return scores
		
batting_stats = ['G', 'AB', 'R', 'H',
				 '2B', '3B', 'HR', 'RBI',
				 'SB', 'CS', 'K', 'BB',
				 'HBP', 'SF']

pitching_stats = ['W', 'L', 'G', 'GS', 'GF',
				  'SV', 'H', 'R', 'ER',
				  'HR', 'BB', 'SO']
#Return batting and pitching player stats for the given game
def get_game_stats(game_pk):
	bat_stats = {}
	pitch_stats = {}
	box = box_url.format(game_pk)
	r = requests.get(box).json()
	for id, player in r['teams']['away']['players'].items():
		if player['stats']['batting'] != {}:
			bat_stats[int(id[2:])] = batting_from_json(player['stats']['batting'])
		if player['stats']['pitching'] != {}:
			pitch_stats[int(id[2:])] = pitching_from_json(player['stats']['pitching'])
	for id, player in r['teams']['home']['players'].items():
		if player['stats']['batting'] != {}:
			bat_stats[int(id[2:])] = batting_from_json(player['stats']['batting'])
		if player['stats']['pitching'] != {}:
			pitch_stats[int(id[2:])] = pitching_from_json(player['stats']['pitching'])
	return (bat_stats, pitch_stats)

batting_stats_keys = {'atBats': 'AB', 'runs': 'R',
					  'hits': 'H', 'doubles': '2B', 'triples': '3B',
					  'homeRuns': 'HR', 'rbi': 'RBI', 'stolenBases': 'SB',
					  'caughtStealing': 'CS', 'strikeOuts': 'K',
					  'baseOnBalls': 'BB', 'hitByPitch': 'HBP',
					  'sacFlies': 'SF'}
def batting_from_json(stats):
	rv = {}
	for k, v in batting_stats_keys.items():
		rv[v] = stats.get(k, 0)
	return rv
	
pitching_stats_keys = {'wins': 'W', 'losses': 'L',
					   'gamesStarted': 'GS', 'gamesFinished': 'GF',
					   'saves': 'SV', 'hits': 'H', 'runs': 'R',
					   'earnedRuns': 'ER', 'homeRuns': 'HR',
					   'baseOnBalls': 'BB', 'strikeOuts': 'SO',
					   'outs': 'outs'}
def pitching_from_json(stats):
	rv = {}
	for k, v in pitching_stats_keys.items():
		rv[v] = stats.get(k, 0)
	return rv

#DON'T RUN if game stats are already in the db!
def add_game_stats_to_db(game_pk):
	bat_stats, pitch_stats = get_game_stats(game_pk)
	for id in bat_stats.keys():
		add_player_to_db(id)
	for id in pitch_stats.keys():
		add_player_to_db(id)
	for id, stats in bat_stats.items():
		db.session.add(BatGame(game_pk=game_pk, batter_id=id,
							   ab=stats['AB'], r=stats['R'],
							   h=stats['H'], doubles=stats['2B'],
							   triples=stats['3B'], hr=stats['HR'],
							   rbi=stats['RBI'], sb=stats['SB'],
							   cs=stats['CS'], k=stats['K'],
							   bb=stats['BB'], hbp=stats['HBP'],
							   sf=stats['SF']))
	for id, stats in pitch_stats.items():
		db.session.add(PitchGame(game_pk=game_pk, pitcher_id=id,
								 w=stats['W'], losses=stats['L'],
								 gs=stats['GS'], gf=stats['GF'],
								 sv=stats['SV'], h=stats['H'],
								 r=stats['R'], er=stats['ER'],
								 hr=stats['HR'], bb=stats['BB'],
								 so=stats['SO'], outs=stats['outs']))
	db.session.commit()
	
player_url_base = "https://statsapi.mlb.com/api/v1/people?personIds={}"
#return True if player was added, False if already there
def add_player_to_db(id):
	prev_player = PlayerData.query.filter_by(id=id).first()
	if not prev_player:
		r = requests.get(player_url_base.format(id)).json()
		new_player = PlayerData(id=id, name=r['people'][0]['fullName'],
									   sort_name=r['people'][0]['lastFirstName'])
		db.session.add(new_player)
		db.session.commit()
		return True
	else:
		return False

#Convert an integer number of outs to a string representation of innings pitched
def outs_to_ip(outs):
	return str(int(outs/3)) + '.' + str(outs % 3)