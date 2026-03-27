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
pip install -r requirements.txt
python src/main.py
```

Set `LANDUS_FULLSCREEN=1` for fullscreen mode.
