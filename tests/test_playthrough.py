"""Simulated play: run with `.venv/bin/python tests/test_playthrough.py`.

Drives the real GameView and asserts invariants. Correctness only -- whether
the enemies are too fast is a human question.
"""

import random
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

from harness import Harness, check, report  # noqa: E402

import arcade  # noqa: E402

from src.main import (  # noqa: E402
    MAX_ENEMIES, PLAYER_RADIUS, SCREEN_HEIGHT, SCREEN_WIDTH,
)

MOVE_KEYS = [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D]
SHOOT_KEYS = [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT]
FRAMES = 1800  # 30s at 60fps


def player_on_screen(v) -> bool:
    return (
        -PLAYER_RADIUS <= v.player_x <= SCREEN_WIDTH + PLAYER_RADIUS
        and -PLAYER_RADIUS <= v.player_y <= SCREEN_HEIGHT + PLAYER_RADIUS
    )


def check_random_input_playthrough(failures):
    rng = random.Random(11)
    h = Harness().game()
    v = h.view

    held = set()
    off_screen = 0
    peak_enemies = 0
    peak_bullets = 0
    score_went_backwards = False
    last_score = 0

    for _ in range(FRAMES):
        if rng.random() < 0.2:
            key = rng.choice(MOVE_KEYS + SHOOT_KEYS)
            if key in held:
                v.on_key_release(key, 0)
                held.discard(key)
            else:
                v.on_key_press(key, 0)
                held.add(key)
        h.step(1)

        off_screen += 0 if player_on_screen(v) else 1
        peak_enemies = max(peak_enemies, len(v.enemies))
        peak_bullets = max(peak_bullets, len(v.bullets))
        if v.score < last_score:
            score_went_backwards = True
        last_score = v.score

        if v._game_over:
            break

    check(f"survived {h.frames} frames of random input without crashing", True, failures)
    check("player never left the screen", off_screen == 0, failures)
    check(f"enemy count respected MAX_ENEMIES ({peak_enemies} <= {MAX_ENEMIES})",
          peak_enemies <= MAX_ENEMIES, failures)
    check(f"bullets did not leak ({peak_bullets} alive at peak)",
          peak_bullets < 500, failures)
    check("score never decreased", not score_went_backwards, failures)
    check(f"reached score {v.score} and {'died' if v._game_over else 'survived'}",
          True, failures)
    h.close()


def check_bullets_expire(failures):
    """Bullets have a lifetime; firing must not grow the list forever."""
    h = Harness().game()
    v = h.view
    v.on_key_press(arcade.key.UP, 0)
    h.step(120)
    peak = len(v.bullets)
    v.on_key_release(arcade.key.UP, 0)
    h.step(180)  # 3s: well past BULLET_LIFETIME
    check(f"bullets stop spawning on key release ({peak} -> {len(v.bullets)})",
          len(v.bullets) == 0, failures)
    h.close()


def check_shooting_kills_and_scores(failures):
    h = Harness().game()
    v = h.view
    from src.main import Enemy

    v.enemies = [Enemy(v.player_x + 60, v.player_y)]
    before = v.score
    v.on_key_press(arcade.key.RIGHT, 0)
    h.step(60)
    v.on_key_release(arcade.key.RIGHT, 0)
    check("shooting an enemy removes it", not v.enemies, failures)
    check("killing an enemy scores", v.score > before, failures)
    h.close()


def check_enemy_contact_ends_the_game(failures):
    h = Harness().game()
    v = h.view
    from src.main import Enemy

    check("not game over at the start", not v._game_over, failures)
    v.enemies = [Enemy(v.player_x, v.player_y)]
    h.step(2)
    check("an enemy touching the player ends the game", v._game_over, failures)

    # The game-over screen must be static, not still simulating.
    pos = (v.player_x, v.player_y)
    v.on_key_press(arcade.key.W, 0)
    h.step(30)
    v.on_key_release(arcade.key.W, 0)
    check("player cannot move after game over", (v.player_x, v.player_y) == pos, failures)
    h.close()


def check_esc_hold_quits(failures):
    h = Harness().game()
    closed = []
    h.window.close = lambda: closed.append(True)

    h.hold(arcade.key.ESCAPE, 20)
    check("still running mid-hold", not closed, failures)
    h.step(50)
    check("ESC held past the threshold closes the window", len(closed) >= 1, failures)

    h.view.on_key_release(arcade.key.ESCAPE, 0)
    h.window.close = lambda: None
    h.close()


def check_esc_works_after_game_over(failures):
    """The only way out of the game-over screen -- it must still respond."""
    h = Harness().game()
    v = h.view
    from src.main import Enemy

    v.enemies = [Enemy(v.player_x, v.player_y)]
    h.step(2)
    closed = []
    h.window.close = lambda: closed.append(True)
    h.hold(arcade.key.ESCAPE, 70)
    check("ESC still quits from the game-over screen", len(closed) >= 1, failures)
    v.on_key_release(arcade.key.ESCAPE, 0)
    h.window.close = lambda: None
    h.close()


def main() -> int:
    failures = []
    print("random-input playthrough")
    check_random_input_playthrough(failures)
    print("\nbullets")
    check_bullets_expire(failures)
    check_shooting_kills_and_scores(failures)
    print("\ngame over")
    check_enemy_contact_ends_the_game(failures)
    print("\nESC protocol")
    check_esc_hold_quits(failures)
    check_esc_works_after_game_over(failures)
    return report(failures, "playthrough")


if __name__ == "__main__":
    sys.exit(main())
