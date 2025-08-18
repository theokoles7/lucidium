[lucidium](https://github.com/theokoles7/lucidium) / [documentation](https://github.com/theokoles7/lucidium/blob/main/documentation/README.md) / [concepts](./README.md) / agent-tags

# Agent Tags



Tags that are attrbuted to agents during registration should describe the agent's taxonomy based on the following criteria:

## Learning Paradigm
- **Model-Free**: Agents that learn directly from interactions with the environment without building a model of the environment.
- **Model-Based**: Agents that learn by building a model of the environment and using it to make decisions.

## Gradient Usage
- **Gradient-Based**: Agents that use gradient descent or similar methods to optimize their policies or value functions.
- **Gradient-Free**: Agents that do not rely on gradient information for learning, often using methods like evolutionary strategies or reinforcement learning without gradients.

## Policy Usage
- **On-Policy**: Agents that learn from actions taken by the current policy, updating the policy based on the rewards received.
- **Off-Policy**: Agents that learn from actions taken by a different policy, allowing them to learn from past experiences or from other agents.

## Function Approximation
- **Tabular**: Agents that use a table to store values for each state-action pair, suitable for small state spaces.
- **Deep**: Agents that use deep learning techniques, such as neural networks, to approximate value functions or policies, suitable for large or continuous state spaces.
- **Linear**: Agents that use linear functions to approximate value functions or policies, suitable for problems where relationships are linear or nearly linear.

## Control Strategy
- **Value-Based**: Agents that learn a value function to determine the best action to take in each state, such as Q-learning agents.
- **Policy-Based**: Agents that directly learn a policy that maps states to actions, such as REINFORCE agents.
- **Actor-Critic**: Agents that combine both value-based and policy-based methods, using an actor to select actions and a critic to evaluate those actions.