from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, DateForm, RegistrationForm
from app.models import User, Game, GameData, PlayerData, BatGame, PitchGame
import app.mlbapi as mlbapi
import app.dbhandler as dbhandler
from collections import defaultdict
import datetime as dt

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
	date = dt.date(int(year), int(month), int(day))
	games = mlbapi.get_schedule(date)
	if len(games) == 0:
		flash("No games found for {}".format(date.isoformat()))
		return redirect(url_for('choose_date'))
	else:
		return render_template('gameselect.html', games=games)
		
@app.route('/mygames')
@login_required
def list_games():
	games = db.session.query(Game, GameData).\
					   filter(Game.user_id==current_user.id).\
					   filter(GameData.game_pk==Game.game_pk).\
					   order_by(Game.game_pk).\
					   all()
	return render_template('mygames.html', games=games)

@app.route('/addgame/<game_pk>/<date>', methods=['GET', 'POST'])
@login_required
def add_game(game_pk, date):
	game = Game(game_pk=game_pk, user_id=current_user.id)
	check_game = GameData.query.filter_by(game_pk=game_pk).first()
	if check_game is None:
		game_data = mlbapi.get_game_data(game_pk, date)
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
	batters = dbhandler.get_cum_batter_stats(current_user.id)
	players = sorted(batters.items(), key=lambda x: x[1]['sortname'])
	return render_template('bat_stats.html', players=players)
	
@app.route('/pitcherstats')
@login_required
def pitcher_stats():
	pitchers = dbhandler.get_cum_pitcher_stats(current_user.id)
	players = sorted(pitchers.items(), key=lambda x: x[1]['sortname'])
	return render_template("pitch_stats.html", players=players)
	
@app.route('/teamrecords')
@login_required
def team_records():
	teams = dbhandler.get_cum_team_records(current_user.id)
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

#DON'T RUN if game stats are already in the db!
def add_game_stats_to_db(game_pk):
	bat_stats, pitch_stats = mlbapi.get_game_batters_and_pitchers(game_pk)
	for batter in bat_stats:
		dbhandler.add_player_if_missing(batter.batter_id, commit=False)
	for pitcher in pitch_stats:
		dbhandler.add_player_if_missing(pitcher.pitcher_id, commit=False)
	db.session.add_all(bat_stats)
	db.session.add_all(pitch_stats)
	db.session.commit()

#Convert an integer number of outs to a string representation of innings pitched
def outs_to_ip(outs):
	return str(int(outs/3)) + '.' + str(outs % 3)