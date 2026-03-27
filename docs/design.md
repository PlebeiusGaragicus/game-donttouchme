# Don't Touch Me -- Design

## Overview

Single-player survival game. Prove out the Landus arcade system's game integration.

## Mechanics

- Player: blue circle, WASD movement, clamped to screen bounds
- Enemies: red circles, spawn from edges every 2s, chase player at constant speed, max 30
- Projectiles: fired via arrow keys (8-direction), travel until off-screen or lifetime expires
- Collision: bullet kills enemy on contact; enemy kills player on contact
- Score: +1 per enemy killed
- Game over: freeze on death, display score, ESC to exit

## ESC contract

Hold ESC for 1 second to close the game window cleanly (exit code 0).
