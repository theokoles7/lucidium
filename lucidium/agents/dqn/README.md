[lucidium](https://github.com/theokoles7/lucidium/blob/main/README.md) / [documentation](../../../documentation/README.md) / [agents](../README.md) / dqn

# Deep Q-Network (DQN)

### Contents:
* [Overview](#overview)
* [Properties](#properties)
    * [Discount Rate](#discount-rate-gamma)
    * [Exploration Rate](#exploration-rate-epsilon)
    * [Learning Rate](#learning-rate-alpha)
    * [Replay Buffer Size](#replay-buffer-size)
    * [Batch Size](#batch-size)
    * [Target Network Update Frequency](#target-network-update-frequency)
* [References](#references)

## Overview

Deep Q-Networks (DQN) is a reinforcement learning algorithm that combines Q-learning with deep neural networks to enable agents to learn optimal policies in complex environments. DQN uses a neural network to approximate the Q-value function, which estimates the expected future rewards for each action in a given state. The key innovation of DQN is the use of experience replay and target networks to stabilize training and improve learning efficiency.

Experience replay involves storing the agent's experiences (state, action, reward, next state) in a replay buffer and randomly sampling mini-batches of experiences during training. This helps to break the correlation between consecutive experiences and improves the stability of the learning process. The target network is a separate neural network that is periodically updated with the weights of the main network. This helps to reduce the oscillations and divergence that can occur when using a single network for both action selection and Q-value estimation.

DQN has been successfully applied to various tasks, including playing Atari games, where it achieved human-level performance in several games. The algorithm has also been extended with various improvements, such as Double DQN, Dueling DQN, and Prioritized Experience Replay, to further enhance its performance and stability.

## Properties

### Discount Rate (Gamma)

The discount factor $\gamma$⁠ determines the importance of future rewards. A factor of 0 will make the agent "myopic" (or short-sighted) by only considering current rewards, i.e. $r_t$, while a factor approaching 1 will make it strive for a long-term high reward. If the discount factor meets or exceeds 1, the action values may diverge. For $\gamma = 1$⁠, without a terminal state, or if the agent never reaches one, all environment histories become infinitely long, and utilities with additive, undiscounted rewards generally become infinite. Even with a discount factor only slightly lower than 1, Q-function learning leads to propagation of errors and instabilities when the value function is approximated with an artificial neural network. In that case, starting with a lower discount factor and increasing it towards its final value accelerates learning.

### Exploration Rate (Epsilon)

The exploration rate $\epsilon$ determines the agent's balance between exploration (trying new actions) and exploitation (choosing the best-known action). A higher $\epsilon$ encourages the agent to explore the environment more thoroughly, selecting random actions with probability $\epsilon$ and the best-known action with probability $1 - \epsilon$. Conversely, a lower $\epsilon$ favors exploitation of current knowledge, potentially accelerating convergence but at the risk of suboptimal policies due to insufficient exploration.

### Learning Rate (Alpha)

The learning rate or step size determines to what extent newly acquired information overrides old information. A factor of 0 makes the agent learn nothing (exclusively exploiting prior knowledge), while a factor of 1 makes the agent consider only the most recent information (ignoring prior knowledge to explore possibilities). In fully deterministic environments, a learning rate of $\alpha_t = 1$ is optimal. When the problem is stochastic, the algorithm converges under some technical conditions on the learning rate that require it to decrease to zero. In practice, often a constant learning rate is used, such as $\alpha_t = 0.1$  for all $t$.

### Replay Buffer Size

The replay buffer size determines the maximum number of experiences that can be stored in the replay buffer. A larger buffer size allows the agent to learn from a more diverse set of experiences, which can improve learning stability and performance. However, a larger buffer also requires more memory and may slow down the training process due to increased sampling time. It is important to choose an appropriate buffer size based on the complexity of the environment and the available computational resources.

### Batch Size

The batch size determines the number of experiences sampled from the replay buffer for each training update. A larger batch size can lead to more stable updates and better gradient estimates, but it also requires more computational resources and may slow down the training process. Conversely, a smaller batch size can lead to faster updates but may result in higher variance in the gradient estimates, which can negatively impact learning stability. It is important to choose an appropriate batch size based on the complexity of the environment and the available computational resources.

### Target Network Update Frequency

The target network update frequency determines how often the weights of the target network are updated with the weights of the main network. A higher update frequency can lead to more stable learning, as the target network provides a more consistent estimate of the Q-values during training. However, updating the target network too frequently can lead to instability and divergence in the learning process. Conversely, a lower update frequency may result in slower learning but can help to stabilize the training process. It is important to choose an appropriate update frequency based on the complexity of the environment and the available computational resources.

## References

### Papers

1. [*Playing Atari with Deep Reinforcement Learning* (Mnih et al., 2013)](https://arxiv.org/pdf/1312.05602)
2. [*Human-level Control through Deep Reinforcement Learning* (Mnih et al., 2015)](https://training.incf.org/sites/default/files/2023-05/Human-level%20control%20through%20deep%20reinforcement%20learning.pdf)

### Code

* [`stablebaselines3`](https://github.com/DLR-RM/stable-baselines3/blob/master/stable_baselines3/dqn/dqn.py)