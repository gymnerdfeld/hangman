import random

from api_utils import API, run, NotFound, UnprocessableEntity

api = API()

words = [
    "Gerstensuppe",
    "Haferbrei",
    "Endokrinologie",
    "Zwerchfell",
    "Gurtschnalle",
    "Weinflasche",
    "Essiggurke",
    "Fensterbrett",
    "Schleifpapier",
    "Herzensangelegenheit",
    "Liebeskummer",
    "Eifersucht",
    "Scherzkeks",
    "Lobeshymne",
    "Schlaumeier",
    "Endorphine",
    "Flaschenhals",
    "Greifvogel",
    "Hustensaft",
    "Irritationen",
    "Kunstobjekt",
    "Langeweile",
    "Osmose",
    "Putzfimmel",
    "Querverstrebung",
    "Sandkasten",
    "Trotzreaktion",
    "Unkenrufe",
    "Verkehrsberuhigung",
    "Weiterbildung",
    "Zentralmassiv",
]

games = {}

max_guesses = 6

@api.POST("/api/hangman/")
def new_game(request):
    done = False
    while not done:
        game_id = random.randrange(100_000_000)
        if game_id not in games:
            done = True
    word = random.choice(words)

    games[game_id] = {
        "word": word,
        "guessed_letters": [],
        "guesses": 0,
        "state": "playing",
    }
    return {
        "game_id": game_id, 
        "word_length": len(word), 
        "guesses_left": max_guesses,
    }
    
@api.PUT("/api/hangman/<int:game_id>")
def guess(request, game_id, letter:str):
    letter = letter.lower()

    if game_id not in games:
        raise NotFound(f"Game not found: {game_id}")
    elif len(letter) != 1:
        raise UnprocessableEntity("Must suggest exactly one letter")
    elif letter not in "abcdefghijklmnopqrstuvwxyz":
        raise UnprocessableEntity(f"Invalid letter: {letter}")
    elif games[game_id]["state"] != "playing":
        raise UnprocessableEntity(f"Game over. You {games[game_id]['state']}!")
    elif letter in games[game_id]["guessed_letters"]:
        raise UnprocessableEntity(f"Letter already guessed: {letter}")
    elif letter not in games[game_id]["word"].lower():
        games[game_id]["guesses"] += 1
        games[game_id]["guessed_letters"].append(letter)
        if games[game_id]["guesses"] >= max_guesses:
            games[game_id]["state"] = "lost"
        return {
            "letter_found": False, 
            "guesses_left": max_guesses - games[game_id]["guesses"]
        }
    else:
        games[game_id]["guessed_letters"].append(letter)

        positions = []
        for i, l in enumerate(games[game_id]["word"].lower()):
            if l == letter:
                positions.append(i)
        
        if set(games[game_id]["word"].lower()) - \
           set(games[game_id]["guessed_letters"])  == set():
            games[game_id]["state"] = "won"

        return {
            "letter_found": True, 
            "positions": positions,
        }
    
@api.DELETE("/api/hangman/<int:game_id>")
def delete_game(request, game_id):
    if game_id not in games:
        raise NotFound(f"Game not found: {game_id}")
    del games[game_id]

run(api, port=5000)