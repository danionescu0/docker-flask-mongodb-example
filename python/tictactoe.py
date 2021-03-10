from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
from tempfile import mkdtemp


app = Flask(__name__)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


class Game:
    WIN_LINES = [
        [1, 2, 3], [4, 5, 6], [7, 8, 9],  # horiz.
        [1, 4, 7], [2, 5, 8], [3, 6, 9],  # vertical
        [1, 5, 9], [3, 5, 7]  # diagonal
    ]

    def has_won(self, board: list, turn: str) -> bool:
        wins = [all(
            [(board[c - 1] == turn) for c in line]
        ) for line in self.WIN_LINES]
        return any(wins)

    def has_moves_left(self, board: list) -> bool:
        return all([move is not None for move in board])

    def get_next_player(self, turn: str):
        return {"O": "X", "X": "O"}[turn]


game = Game()


def initiate_session(session):
    session["board"] = [None, None, None, None, None, None, None, None, None]
    session["turn"] = "X"
    session["winner"] = False
    session["draw"] = False


@app.route("/")
def index():
    if "board" not in session:
        initiate_session(session)
    winner_x = game.has_won(session["board"], "X")
    winner_O = game.has_won(session["board"], "O")
    if winner_x or winner_O:
        session["winner"] = True
        session["turn"] = 'X' if winner_x else 'O'
    if game.has_moves_left(session["board"]):
        session["draw"] = True
    return render_template("tictactoe.html",
                           game=session["board"],
                           turn=session["turn"],
                           winnerFound=session["winner"],
                           winner=session["turn"],
                           draw=session["draw"])


@app.route("/play/<int:row>/<int:col>")
def play(row: int, col: int):
    session["board"][col*3+row] = session["turn"]
    session["turn"] = game.get_next_player(session["turn"])
    return redirect(url_for("index"))


@app.route("/reset")
def reset():
    initiate_session(session)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)