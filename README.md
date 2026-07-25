# Don't Touch Me

Proof-of-concept game for the Landus arcade system.

## Concept

Player is a blue ball. Red enemies spawn from screen edges and chase the player. Arrow keys fire projectiles (8-direction via 4-way combos). Enemies die on hit. Player dies on contact with any enemy.

## Controls

| Action | Key |
|--------|-----|
| Move up | W |
| Move down | S |
| Move left | A |
| Move right | D |
| Shoot up | Up arrow |
| Shoot down | Down arrow |
| Shoot left | Left arrow |
| Shoot right | Right arrow |
| Quit (hold) | ESC |

Diagonal shooting: press two arrow keys simultaneously.

## Run standalone

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/main.py
```

Under Landus this `.venv` is provisioned by the parent repo's `./setup`, and the
launcher runs `.venv/bin/python` from here — each game has its own environment.

Set `LANDUS_FULLSCREEN=1` for fullscreen mode; the launcher always sets it.

No cover art or theme song yet, so `game.json` declares neither and the launcher
draws a procedural cover. Add the file and the manifest key together.
