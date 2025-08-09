[lucidium](https://github.com/theokoles7/lucidium) / [documentation](https://github.com/theokoles7/lucidium/blob/main/documentation/README.md) / [environments](../README.md) / tic-tac-toe

# Tic-Tac-Toe

Tic-Tac-Toe is a simple, turn-based, two-player strategy game played on a 3×3 grid. It is commonly used as an introductory example in game theory, programming, and artificial intelligence.

### Contents:
* [Goal](#goal)
* [Rules](#rules)
* [Strategy](#strategy)
* [NSRL Context](#neuro-symbolic-context)

---

## Goal

The goal of the game is for a player to place three of their marks in a horizontal, vertical, or diagonal row before the opponent does.

## Rules

1. The game starts with an empty grid.
2. Players take turns placing their mark in one of the **unoccupied** cells.
3. A player **wins** if they successfully place three of their marks in:
   - A single **horizontal** row
   - A single **vertical** column
   - One of the two **diagonals**
4. If all cells are filled and no player has achieved a winning line, the game ends in a **draw**.

## Strategy

- The game is **fully deterministic** and has a relatively small state space.
- Optimal play by both players always results in a draw.

## Neuro-Symbolic Context

Tic-Tac-Toe provides a very straightforward opportunity for demonstrating neuro-symbolic reinforcement learning examples due to its simplicity. 

* Unary predicates can be used for determining which player has entered a position on the board or if the position is empty.
* Binary, Ternary, & U-nary predicates can be used to determine strategic/tactical concepts.

    <img src="../../../assets/images/tic-tac-toe_fork-pattern.png">