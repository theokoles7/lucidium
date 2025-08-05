[lucidium](../../README.md) / [documentation](../../documentation/README.md) / [agents](../README.md) / q-learning

# Q-Learning


### Contents:
* [Q-Table](#q-table)
    * [Initialization](#initialization)
* [Properties](#properties)
    * [Discount Rate](#discount-rate-gamma)
    * [Exploration Rate](#exploration-rate-epsilon)
    * [Learning Rate](#learning-rate-alpha)
* [References](#references)

## Q-Table

The Q-table is essentially a memory structure where the agent stores information about which actions yield the best rewards in each state. It is a table of Q-values representing the agent's understanding of the environment. As the agent explores and learns from its interactions with the environment, it updates the Q-table. The Q-table helps the agent make informed decisions by showing which actions are likely to lead to better rewards.

### Initialization

Since Q-learning is an iterative algorithm, it implicitly assumes an initial condition before the first update occurs. High initial values, also known as "optimistic initial conditions", can encourage exploration: no matter what action is selected, the update rule will cause it to have lower values than the other alternative, thus increasing their choice probability. The first reward $r$ can be used to reset the initial conditions. According to this idea, the first time an action is taken the reward is used to set the value of $Q$. This allows immediate learning in case of fixed deterministic rewards. A model that incorporates reset of initial conditions (RIC) is expected to predict participants' behavior better than a model that assumes any arbitrary initial condition (AIC). RIC seems to be consistent with human behaviour in repeated binary choice experiments.

## Properties

### Discount Rate (Gamma)

The discount factor $\gamma$⁠ determines the importance of future rewards. A factor of 0 will make the agent "myopic" (or short-sighted) by only considering current rewards, i.e. $r_t$, while a factor approaching 1 will make it strive for a long-term high reward. If the discount factor meets or exceeds 1, the action values may diverge. For $\gamma = 1$⁠, without a terminal state, or if the agent never reaches one, all environment histories become infinitely long, and utilities with additive, undiscounted rewards generally become infinite. Even with a discount factor only slightly lower than 1, Q-function learning leads to propagation of errors and instabilities when the value function is approximated with an artificial neural network. In that case, starting with a lower discount factor and increasing it towards its final value accelerates learning.

### Exploration Rate (Epsilon)

The exploration rate $\epsilon$ determines the agent's balance between exploration (trying new actions) and exploitation (choosing the best-known action). A higher $\epsilon$ encourages the agent to explore the environment more thoroughly, selecting random actions with probability $\epsilon$ and the best-known action with probability $1 - \epsilon$. Conversely, a lower $\epsilon$ favors exploitation of current knowledge, potentially accelerating convergence but at the risk of suboptimal policies due to insufficient exploration.

### Learning Rate (Alpha)

The learning rate or step size determines to what extent newly acquired information overrides old information. A factor of 0 makes the agent learn nothing (exclusively exploiting prior knowledge), while a factor of 1 makes the agent consider only the most recent information (ignoring prior knowledge to explore possibilities). In fully deterministic environments, a learning rate of $\alpha_t = 1$ is optimal. When the problem is stochastic, the algorithm converges under some technical conditions on the learning rate that require it to decrease to zero. In practice, often a constant learning rate is used, such as $\alpha_t = 0.1$  for all $t$.

## References

1. [Watkins, Christopher JCH, and Peter Dayan. "Q-learning." Machine learning 8 (1992): 279-292.](../../../documentation/references/Q-Learning_Watkins_1992.pdf)