from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(128), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	
	def __repr__(self):
		return '<User {}>'.format(self.username)
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	game_pk = db.Column(db.Integer, db.ForeignKey('game_data.game_pk'), index=True)
	game_result = db.Column(db.String(64))
	date = db.Column(db.String(10))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
class GameData(db.Model):
	game_pk = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.String(10))
	home_team = db.Column(db.String(32), index=True)
	home_score = db.Column(db.Integer)
	away_team = db.Column(db.String(32), index=True)
	away_score = db.Column(db.Integer)

class PlayerData(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True)
	sort_name = db.Column(db.String(64), index=True)
	
class BatGame(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	game_pk = db.Column(db.Integer, db.ForeignKey('game_data.game_pk'), index=True)
	batter_id = db.Column(db.Integer, db.ForeignKey('player_data.id'), index=True)
	ab = db.Column(db.Integer)
	r = db.Column(db.Integer)
	h = db.Column(db.Integer)
	doubles = db.Column(db.Integer)
	triples = db.Column(db.Integer)
	hr = db.Column(db.Integer)
	rbi = db.Column(db.Integer)
	sb = db.Column(db.Integer)
	cs = db.Column(db.Integer)
	k = db.Column(db.Integer)
	bb = db.Column(db.Integer)
	hbp = db.Column(db.Integer)
	sf = db.Column(db.Integer)
	
class PitchGame(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	game_pk = db.Column(db.Integer, db.ForeignKey('game_data.game_pk'), index=True)
	pitcher_id = db.Column(db.Integer, db.ForeignKey('player_data.id'), index=True)
	w = db.Column(db.Integer)
	losses = db.Column(db.Integer)
	gs = db.Column(db.Integer)
	gf = db.Column(db.Integer)
	sv = db.Column(db.Integer)
	h = db.Column(db.Integer)
	r = db.Column(db.Integer)
	er = db.Column(db.Integer)
	hr = db.Column(db.Integer)
	bb = db.Column(db.Integer)
	so = db.Column(db.Integer)
	outs = db.Column(db.Integer)
	

@login.user_loader
def load_user(id):
	return User.query.get(int(id))