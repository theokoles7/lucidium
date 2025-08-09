[lucidium](https://github.com/theokoles7/lucidium) / [documentation](https://github.com/theokoles7/lucidium/blob/main/documentation/README.md) / [environments](../README.md) / grid-world

# Grid World Environment

The Grid World environment is a simple grid-based environment where an agent can navigate through a grid to reach a goal. The agent can move in four directions: up, down, left, and right. The environment is defined by a grid of cells, where some cells may be obstacles or rewards.

![grid-world-animation](../../../assets/gifs/grid-world_animation.gif)

### Contents:
* [Action Space](#action-space)
* [Observation Space](#observation-space)
* [Components](./components/README.md)

## Action Space

The agent is only allowed 4 actions: `UP`, `DOWN`, `LEFT`, and `RIGHT`. This constitutes a discrete action space of size 4.

## Observation Space

The observation space is represented as a 2D grid, where each cell can have different values representing the agent's position, goal position, obstacles, and empty spaces. The observation is typically represented as a matrix or array.