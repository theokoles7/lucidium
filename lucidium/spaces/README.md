[lucidium](https://github.com/theokoles7/lucidium) / [documentation](https://github.com/theokoles7/lucidium/blob/main/documentation/README.md) / spaces

# Spaces
`lucidium.spaces`

| Class                                 | Description                             | Use Case Example                              |
| ------------------------------------- | --------------------------------------- | --------------------------------------------- |
| [`Discrete`](#discrete)               | Scalar integer action/observation space | Discrete actions (e.g. Rock/Paper/Scissors)   |
| [`MultiDiscrete`](#multidiscrete)     | Tuple of discrete values                | Board positions: `(row, col)` for Tic-Tac-Toe |
| [`Continuous`](#continuous)           | Scalar continuous space                 | 1D control (e.g. angle)                       |
| [`MultiContinuous`](#multicontinuous) | Tuple of continuous values              | 2D or 3D control (e.g. robotics)              |
| [`Box`](#box)                         | N-dimensional tensor box                | Image input, multi-channel features           |
| [`Composite`](#composite)             | Dictionary of multiple spaces           | For mixed modality state/action formats       |

## `(Abstract) Space`

## `Box`

## `Composite`

## `Continuous`

## `Discrete`

## `MultiContinuous`

## `MultiDiscrete`