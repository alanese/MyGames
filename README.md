# MyGames
A flask website which computes combined player stats for a selected list of baseball games.  

Currently the site only works for games with sufficient box score data available through the MLB API, which appears to be 2002-present.  

The database in the repository has two registered users - `admin` with password `admin` and `user` with password `user`.

## Required packages
- Flask
- Flask-Login
- Flask-Migrate
- Flask-SQLAlchemy
- Flask-WTForms
- python-dotenv
- Requests
- Werkzeug
- WTForms

## TODO
- Formatting, formatting everywhere.
- Refactor non-routing code to separate module
- Handle variations in team names
- Add team ID to BatGame, PitchGame tables
- Figure out how to handle pre-2002 games
- Documentation
- Other stuff I think of?

## Notes
Table sorting and paging with [DataTables](https://datatables.net/)
