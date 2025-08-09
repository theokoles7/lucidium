[lucidium](https://github.com/theokoles7/lucidium) / [documentation](https://github.com/theokoles7/lucidium/blob/main/documentation/README.md) / [environments](../../README.md) / [grid-world](../README.md) / components

# Grid World Components

### Contantes:
* [Grid](#grid)
* [Squares](#squares)
  * [Goal](#goal)
  * [Loss](#loss)
  * [Coins](#coins)
  * [Portals](#portals)
  * [Walls](#walls)

## Grid

The grid is the main structure of the environment, representing the 2D space where the agent operates. It consists of cells that can be empty or occupied by various components such as walls, goals, coins, and portals. The grid defines the boundaries and layout of the environment.

## Squares

Each cell in the grid is represented as a square, which can have different properties based on what it contains. Squares can be empty or contain specific components that affect the agent's behavior and rewards.

### Goal

Goal squares represent the target location that the agent aims to reach. When the agent reaches a goal square, it typically receives a positive reward, and the episode may end or reset.

### Loss

Loss squares represent hazardous locations that the agent should avoid. If the agent steps on a loss square, it may receive a negative reward or penalty, which can impact its overall performance in the environment.

### Coins

Coin squares represent collectible items that the agent can gather to earn rewards. When the agent collects a coin, it typically receives a positive reward, which can contribute to its overall score. Coins are ephimeral and disappear once collected.

### Portals

Portal squares represent teleportation points that can transport the agent to a different location on the grid. When the agent steps on a portal square, it is instantly moved to another predefined portal square, which can help it navigate the environment more efficiently or impede its progression toward the goal square(s).

### Walls

Wall squares represent obstacles that the agent cannot pass through. They define the boundaries and layout of the environment, creating challenges for the agent to navigate around them to reach the goal or collect coins.