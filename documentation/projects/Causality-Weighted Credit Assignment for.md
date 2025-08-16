# Causality-Weighted Credit Assignment for RL (CauCA-RL)

## 1. Pitch

We propose CauCA-RL, a drop-in mechanism that replaces/augments temporal heuristics (eligibility traces, λ-returns, GAE) with per-step causal influence weights for credit assignment. For each action atat​, we estimate how much it caused later outcomes and reweight the return/advantage accordingly. The method is algorithm-agnostic (tabular Q/SARSA, DQN, PPO) and especially helpful in sparse-/delayed-reward tasks by amplifying truly pivotal decisions while muting irrelevant steps.

## 2. Current SOTA (and why it matters)

### 2.1 What people do now

* Eligibility traces / TD(λ): distribute credit backward by time recency; good bias-variance tradeoff but blind to causality.

* GAE: variance-reduced advantages via exponentially-weighted temporal factors—again, time-based rather than cause-based.

* RUDDER: learns to redistribute rewards to earlier time steps via contribution analysis; powerful for delayed rewards but requires sequence models and an explicit redistribution step.

* COMA / multi-agent counterfactual baselines: counterfactual across agents (credit which agent mattered), not across time within one agent’s trajectory.

* HER: goal relabeling to cope with sparsity; not a credit reweighing mechanism.

### 2.2 What we add

* A single-agent, per-time-step causal influence estimator I^t→kI^t→k​ that plugs into return/advantage computation (or traces) without reward redistribution or sequence models.

* Works in tabular settings (exact or simulated counterfactuals) and function-approximation settings (light model-based rollouts), aligning with recent surveys that highlight the gap in temporal credit framed as influence estimation.

* Complements causal-RL lines (which largely focus on environment modeling/exploration), by tackling in-policy temporal credit directly.

## 3. Method: Causality-Weighted Returns

### 3.1 Notation

Trajectory $\tau = (s_0, a_0, r_1, ..., s_T)$ Discount $\gamma$. We define a causal weight for how $a_t$​ influenced outcome at step $k$:

$$
w_{t,k} \propto \max(0, I_{t \to k}) \quad \text{with} \quad \sum_{k \geq t} w_{t,k} = 1 \quad (\text{stability})
$$

and use it to compute a causality-weighted return for step $t$:

$$
G_{t}^{\text{causal}} = \sum_{k=t}^{t+H} w_{t,k} \cdot \gamma^{k-t} r_k + \gamma^{H+1} \cdot \bar{V}_{t+H+1}
$$

where:
* $H$ is a limited horizon
* $\bar{V}$ is a bootstrap value estimate - e.g., $max_a Q(s, a)$ or $V(s)$

### 3.2 Estimating $\hat{I}_t→k$​ (two plug-in estimators)

A. Model-free “delta-Q” (ultra-lightweight)

$$
\hat{I}_{t \to k} = | Q(s_t, a_t) - \mathbb{E}_{a' \sim \text{baseline}}[Q(s_t, a')] | \cdot \eta^{k-t}
$$

* Baseline can be uniform over actions or current policy.

* $\eta \in (0, 1)$ softly decays influence with temporal distance (keeps compute trivial).

* Pros: one line in tabular agents

* Cons: proxy for counterfactuals

B. Light model-based counterfactuals (recommended)

1. Learn a one-step dynamics head $g\theta(s, a) \rightarrow (\hat{r}, \hat{s}')$ alongside agent (tiny MLP or tabular simulator if known).

2. For each $t$, roll out $K$ short counterfactual branches from $s_t$​: one with the factual $a_t$​, others with alternative $\tilde{a}$.

3. Define:

    $$
    \hat{I}_{t \to k} = E[R_{t:k} \mid do(a_t)] - E_{\tilde{a}}[R_{t:k} \mid do(\tilde{a})]
    $$

    computed in the learned model (or exactly in tabular known MDPs).

4. Clamp negatives to 0 (causality for positive outcomes) and normalize across $k \ge t$.

    > Surveys characterize temporal credit as learning influence; our estimator directly instantiates that notion.

### 3.3 How to plug in (three simple variants)

* Q-Learning (tabular)

    $$
    Q(s_t, a_t) \leftarrow Q + \alpha (G_{t}^{\text{causal}} - Q(s_t, a_t))
    $$

* SARSA / SARSA(λ)

    Replace $\lambda$-decay with a causal trace $e_t(s, a) = \gamma\lambda e_{t - 1}(s, a) + 1_{s,a = s_t, a_t} \cdot c_t$, where $c_t = \Sigma_{k \ge t} w_{t, k}$. Then use usual TD error. (Directly contrasts time-decay traces.

* PPO/Actor-Critic

    Replace GAE’s $\lambda^{k - t}$ with $w_{t, k}$ or set $\tilde{\lambda}_{t, k} = \lambda w_{t, k} / \bar{w}_t$ (renormalized) to get Causal-GAE

3.4 Practical stabilizers

* Clip $w_{t, k} \in [0, w_{max}]$, softmax-normalize over $k$.

* Doubly-robust blend: $\Beta \cdot$ model-based $+ (1 - \Beta) \cdot$ delta-Q

* Keep horizon small (e.g., $H \in [10, 30]$), $K \in [2, 4]$ counterfactuals.

## 4. Experiments

### 4.1 Agents to benchmark (minimal & scalable)

* Tabular: Q-Learning, SARSA, SARSA(λ)

* Function approx: Linear Q (optional), DQN

* Policy-gradient: PPO (GAE)

### 4.2 Environments

* Dense/small: CartPole (sanity/learning speed).

* Sparse/structured: Taxi-v3 (pickup → dropoff), FrozenLake-8x8, MiniGrid-Key-Door, MountainCar.

* Stretch: Atari Montezuma’s first room (scripted exploration).

### 4.3 Baselines & comparators

* Vanilla versions of each agent (Q, SARSA, SARSA(λ), DQN, PPO+GAE).

* RUDDER-style comparison on one delayed-reward toy (if time), to position differences (redistribution vs weighting).

* COMA mention only for scope contrast (multi-agent vs ours).

### 4.4 Metrics

* Sample efficiency: steps to reach target return R∗R∗.

* AUC of learning curve; final return at fixed budget.

* Stability: variance across seeds (≥10).

* Interpretability: top-k wt,kwt,k​ events (e.g., “pick key” spikes in MiniGrid).

### 4.5 Ablations (show the mechanism matters)

* No-model delta-Q vs model-based counterfactuals.

* Replace wt,kwt,k​ with time-decay to quantify gain over λ.

* Normalize vs unnormalized weights; effect of horizon HH and KK.

* Clip on/off; doubly-robust blend $\beta$.

### 4.6 Hypotheses

* H1: CauCA-RL improves time-to-threshold on sparse-reward tasks vs λ/GAE.

* H2: Gains persist in tabular and deep settings (not a deep-only trick).

* H3: Learned weights align with human-interpretable pivotal actions (causal saliency).

## 5. Implementation plan (fast track)

* Week 1 – Tabular PoC

    * Implement delta-Q weights + causal traces for Q-Learning and SARSA on Taxi-v3 & FrozenLake-8x8.

    * Show clear speedup in time-to-success.

* Weeks 2–3 – Model-based counterfactuals

    * Tiny dynamics head gθgθ​ (shared across tasks) + short counterfactual rollouts.

    * Repeat tabular experiments and add DQN on MountainCar.

* Weeks 4–5 – PPO integration & MiniGrid

    * Swap λk−tλk−t in GAE for wt,kwt,k​ (Causal-GAE).

    * Run MiniGrid Key-Door; produce interpretability plots of wt,kwt,k​.

* Week 6 – Ablations + writeup figures

    * Sensitivity to H,K,βH,K,β; RUDDER-style toy to position differences.

## 6. Reporting & expected results (paper structure)

* **Title suggestion**: Causality-Weighted Credit Assignment Improves Sample Efficiency in Sparse-Reward RL

* Contributions:

    * A simple, general causal weighting mechanism for temporal credit assignment that plugs into tabular and deep RL.

    * Two practical estimators (model-free delta-Q, light model-based counterfactuals).

    * Consistent gains in sparse-reward domains, with interpretable causal attributions.

* Related work positioning:

    * We contrast with TD(λ)/eligibility traces (time-based recency), GAE (variance-reduction via temporal weighting), RUDDER (reward redistribution via contribution analysis), and COMA (agent-wise counterfactuals for multi-agent credit).

    * We align with surveys calling credit assignment an influence estimation problem and note that causal-RL work often targets modeling/exploration rather than in-policy temporal credit.

7) Pseudocode (agent-agnostic core)

    ```text
    for each episode:
    collect trajectory τ = (s0,a0,r1,...,sT)
    fit/update small dynamics head gθ(s,a)->(r̂, ŝ')

    for each t in [0..T]:
        # 1) estimate causal influence over a limited horizon H
        I = []  # size at most H
        # factual branch
        F = rollout_model(gθ, s_t, [a_t] + policy_actions, H)

        # K counterfactual branches with alternative actions at time t
        C_returns = []
        for k in 1..K:
        a_cf ~ baseline(s_t)              # e.g., uniform or policy
        Ck = rollout_model(gθ, s_t, [a_cf] + policy_actions, H)
        C_returns.append(Ck.cumulative_rewards_per_step)

        # difference-in-returns to form influence per future step
        for h in 0..H:
        delta = F.R[h] - mean_k(C_returns[k].R[h])
        I[h] = max(0, delta)

        # 2) normalize into weights over future steps
        w = softmax(I / temperature)  # ensures sum_h w[h] = 1

        # 3) compute causality-weighted return
        G_causal = sum_{h=0..H} w[h] * (γ^h * r_{t+h}) + γ^{H+1} * bootstrap(s_{t+H+1})

        # 4) plug into your learner
        update_agent_with_target(s_t, a_t, G_causal)
    ```

* Tabular shortcut (delta-Q):

    ```text
    I[h] = | Q(s_t, a_t) - mean_{a'} Q(s_t, a') | * η^h    # no model needed
    ```

## 8. Risks & mitigations

* Model bias → use small HH, few KK, doubly-robust blend ββ, and clip weights.

* Compute → cache one-step gθgθ​; reuse policy rollouts; vectorize counterfactuals.

* Noisy tasks → EMA-smooth weights across episodes.

## 9. Deliverables

* Open-source code with toggles: --cauca {off,deltaq,model}.

* Plots: learning curves, time-to-threshold bars, ablations, top-k causal spikes (per env).

* Short tech report with formalism + comparisons to λ/GAE/RUDDER/COMA/HER (2–6 pages).

## Sources for positioning and background

* Eligibility traces / TD(λ) overview.

* GAE (policy-gradient variance reduction via time-weights).

* RUDDER (return decomposition & reward redistribution for delayed rewards).

* COMA (counterfactual baseline for multi-agent credit).

* HER (sparse-reward goal relabeling).

    Surveys on temporal credit & causal RL (gap/opportunity we target).