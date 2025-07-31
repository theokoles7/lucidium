# BlockWorld Environment

BlockWorld is a classic AI planning domain where blocks can be stacked on top of each other or placed on a table. The goal is to rearrange blocks from an initial configuration to achieve a target configuration.

## Contents
* [Goal](#goal)
* [Rules](#rules)
* [Strategy](#strategy)
* [NSRL Context](#neuro-symbolic-context)
* [Configuration](#configuration)

---

## Goal

The goal is to rearrange blocks from a randomly generated initial configuration to match a randomly generated target configuration. Success is achieved when the current world state matches the target state (either exactly or by shape only, depending on configuration).

## Rules

1. **Block Movement**: Only blocks with no other blocks on top of them can be moved (clear blocks).
2. **Placement**: Blocks can only be placed on other clear blocks or on the ground.
3. **Stacking**: Blocks form vertical stacks with tree-like parent-child relationships.
4. **Ground Block**: Block 0 represents the ground/table and cannot be moved.
5. **Actions**: Actions specify moving one block onto another block.
6. **Termination**: Episode ends when target is achieved or maximum steps reached.

## Strategy

- **Planning**: Requires multi-step planning to achieve complex rearrangements.
- **Hierarchical**: Natural hierarchy from ground blocks to stacked blocks.
- **Constraint Satisfaction**: Must respect physical constraints of stacking.
- **State Space**: Exponential in number of blocks, making it challenging for larger worlds.

## Neuro-Symbolic Context

BlockWorld provides rich opportunities for neuro-symbolic reinforcement learning:

### Symbolic Predicates

**Unary Predicates:**
- `on_ground(block)`: Block is directly on the ground
- `moveable(block)`: Block can be moved (clear and not on ground)
- `placeable(block)`: Block can have others placed on it (clear)
- `clear(block)`: Block has no blocks on top

**Binary Predicates:**
- `on(block1, block2)`: Block1 is directly on top of Block2
- `supports(block1, block2)`: Block1 supports Block2 (same as above)
- `above(block1, block2)`: Block1 is somewhere above Block2 (transitive)
- `below(block1, block2)`: Block1 is somewhere below Block2 (transitive)

**Ternary Predicates:**
- `block_at(block, x, y)`: Block is at coordinate position (x, y)
- `in_stack(block, stack_id, height)`: Block is in stack with given ID at given height

**Meta Predicates:**
- `num_stacks(n)`: Number of separate stacks in the world
- `stack_height(stack_id, height)`: Height of a particular stack
- `goal_achieved()`: Target configuration has been reached

### Strategic Concepts

- **Tower Building**: Constructing tall stacks
- **Base Clearing**: Clearing blocks from desired base positions
- **Subgoal Planning**: Breaking complex goals into achievable subgoals
- **Dependency Analysis**: Understanding which moves must happen before others

## Configuration

### Basic Parameters

- `--nr-blocks`: Number of blocks (2-20, default: 4)
- `--random-order`: Randomly permute block indices to prevent memorization
- `--one-stack`: Generate worlds with only one stack of blocks

### Task Parameters

- `--shape-only`: Only require matching overall shape, not exact block positions
- `--fix-ground`: Keep ground block at fixed index 0

### Dynamics

- `--prob-unchange`: Probability that actions have no effect (0.0-1.0)
- `--prob-fall`: Probability that moved blocks fall to ground (0.0-1.0)

### Rewards

- `--success-reward`: Reward for achieving target configuration (default: 1.0)
- `--move-penalty`: Cost of making any move (default: -0.1)
- `--invalid-move-penalty`: Penalty for invalid moves (default: -0.5)
- `--max-steps`: Maximum steps before episode terminates (default: 100)

## Example Usage

```bash
# Basic 4-block world
lucidium blockworld

# Larger world with randomization
lucidium blockworld --nr-blocks 8 --random-order

# Shape-only matching with noise
lucidium blockworld --shape-only --prob-fall 0.1

# Single stack configuration
lucidium blockworld --one-stack --nr-blocks 6
```

## Implementation Details

The environment uses a modular component structure:

- **Block**: Individual blocks with parent-child relationships
- **World**: Manages collections of blocks and world-level operations
- **BlockWorld**: Main environment class with RL interface

This design provides clean separation of concerns and makes the code easy to extend and modify.