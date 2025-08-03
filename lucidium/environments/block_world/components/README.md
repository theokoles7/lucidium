[lucidium](https://github.com/theokoles7/lucidium) / [documentation](https://github.com/theokoles7/lucidium/blob/main/documentation/README.md) / [environments](../../README.md) / [block_world](../README.md) / components

# Block World Components

### Contents:
* [Block](#block)
* [World](#world)

## Block

### Properties:

* #### `is_ground`

    A block $x$ is "grounded" if it is located on the ground, meaning that it currently has no parent.

    **WARNING**: Against intuition, this means that the block ***is the ground itself***, not that it is located on the ground. 

    <img src="../../../../assets/images/block-world_block_is-grounded.png">

* #### `is_moveable`

    A block $y$ is "moveable" if it is not located on the ground (i.e., it currently has a parent) and there are no blocks on top of it (i.e., it has no children).

    <img src="../../../../assets/images/block-world_block_is-moveable.png">

* #### `is_placeable`

    A block $z$ is "placeable if it is the ground (i.e., it has no parent) or there are no blocks on top of it (i.e., it has no children).

    <img src="../../../../assets/images/block-world_block_is-placeable.png">

## World