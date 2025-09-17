"""# lucidium.neural.boltzmann_machines.rbm

Restricted Boltzmann Machine implementation.
"""

__all__ = ["RBM"]

from typing                 import Any, Dict, Optional, Tuple

from torch                  import device, dtype, float32, log, rand_like, randn, sigmoid, Tensor, zeros
from torch.nn               import Module, Parameter
from torch.nn.functional    import linear, softplus

class RBM(Module):
    """# Bernoulli-Bernoulli Restricted Boltzmann Machine (RBM).

    This implementation supports binary visible and hidden units, and is trained using Contrastive 
    Divergence with k Gibbs steps (CD-k).
    """
    
    def __init__(self,
        visible_nodes:  int,
        hidden_nodes:   int,
        gibbs_steps:    int =               5,
        weight_scale:   float =             1e-2,
        *,
        device:         Optional[device] =  None,
        dtype:          dtype =             float32
    ):
        """# Instantiate Bernoulli-Bernoulli Restricted Boltzmann Machine.

        ## Args:
            * visible_nodes (int):              Number of visible nodes/units.
            * hidden_nodes  (int):              Number of hidden nodes/units.
            * gibbs_steps   (int):              Number of alternating Gibbs sampling steps to run in 
                                                Contrastive Divergence (CD-k). Defaults to 5.
            * weight_scale  (float):            Standard deviation of the normal distribution used 
                                                for initializing the weight matrix. Defaults to 
                                                1e-2.
            * device        (device | None):    Device on which to allocate parameters. Defaults to 
                                                None.
            * dtype         (dtype):            Parameter data type. Defaults to float32.
        """
        # Initialize module.
        super(RBM, self).__init__()
        
        # Record Torch relevant factory arguments.
        factory_kwargs:         Dict[str, Any] =    {"device": device, "dtype": dtype}
        
        # Initialize weight matrix.
        self._weights_:         Parameter =         Parameter(
                                                        data =  randn(
                                                                    hidden_nodes,
                                                                    visible_nodes,
                                                                    **factory_kwargs
                                                                ) * weight_scale
                                                    )
        
        # Initialize biases.
        self._visible_bias_:    Parameter =         Parameter(
                                                        data =  zeros(
                                                                    visible_nodes,
                                                                    **factory_kwargs
                                                                )
                                                    )
        self._hidden_bias_:     Parameter =         Parameter(
                                                        data =  zeros(
                                                                    hidden_nodes,
                                                                    **factory_kwargs
                                                                )
                                                    )
        
        # Define Gibbs steps.
        self._gibbs_steps_:     int =               int(gibbs_steps)
        
    # METHODS ======================================================================================
    
    def cd_loss(self,
        data_visible_batch:     Tensor,
        model_visible_batch:    Tensor
    ) -> Tensor:
        """# Contrastive Divergence (CD) Loss Approximation.
        
        Loss = F(v_data) - (v_model) where v_data are data samples and v_model are negative samples 
        after k Gibbs steps.

        ## Args:
            * data_visible_batch    (Tensor):   Data batch, of shape (batch_size, visible_nodes).
            * model_visible_batch   (Tensor):   Model samples after k Gibbs steps, of shape 
                                                (batch_size, visible_nodes).

        ## Returns:
            * Tensor:   Contrastive divergence loss approximation.
        """
        # Compute mean free energy on data samples.
        free_energy_on_data:    Tensor =    self.free_energy(visible_batch = data_visible_batch)
        
        # Compute mean free energy on model samples (negative samples).
        free_energy_on_model:   Tensor =    self.free_energy(visible_batch = model_visible_batch)
        
        # CD objective is the difference.
        cd_objective:           Tensor =    free_energy_on_data - free_energy_on_model
        
        # Return the scalar loss tensor.
        return cd_objective
    
    def forward(self,
        data_visible_batch: Tensor
    ) -> Tuple[Tensor, Tensor, Tensor]:
        """# Contrastive Divergence (CD-k).
        
        Alias for contrastive divergence method so that the module can be called directly.

        ## Args:
            * data_visible_batch    (Tensor):   Batch of visible data samples.

        ## Returns:
            * Tensor:   The original input batch (returned for convenience/symmetry).
            * Tensor:   Sample from the model after k alternating Gibbs steps.
            * Tensor:   Probabilities P(visible = 1 | hidden_k) from the final Gibbs step (useful 
                        for computing reconstruction losses/metrics).
        """
        # Simply dispatch to proper method.
        return self._cd_k_(data_visible_batch = data_visible_batch)
    
    def free_energy(self,
        visible_batch:  Tensor
    ) -> Tensor:
        """# Compute Free Energy.
        
        Compute the mean free energy of a batch of visible vectors.
        
        Free energy for Bernoulli-Bernoulli RBM is defined as:
        
        F(v) = -visible_bias^T v - sum_j softplus((W v + hidden_bias)_j)

        ## Args:
            * visible_batch (Tensor):   Batch of visible vectors, of shape (batch_size, 
                                        visible_nodes).

        ## Returns:
            * Tensor:   (Scalar) Mean free energy of the batch.
        """
        # Compute visible bias term b^T v for each example; shape (batch_size,).
        visible_bias_dot_product:   Tensor =    visible_batch.mv(self._visible_bias_)
        
        # Compute hidden pre-activations (W v + c) as v @ W^T + c; shape (batch_size, n_hidden).
        hidden_pre_activation:      Tensor =    linear(
                                                    input =     visible_batch,
                                                    weight =    self._weights_,
                                                    bias =      self._hidden_bias_
                                                )
        
        # Compute sum_j softplus(hidden_pre_activation_j) for numerical stability; shape 
        # (batch_size,).
        hidden_softplus_sum:        Tensor =    softplus(input = hidden_pre_activation).sum(dim=1)
        
        # Return the mean over the batch of the negative energy components.
        mean_free_energy:           Tensor =    (-hidden_softplus_sum - visible_bias_dot_product).mean()
        
        # Provide mean free energy calculation.
        return mean_free_energy
    
    @staticmethod
    def reconstruct(
        v_data: Tensor,
        p_v:    Tensor
    ) -> Tensor:
        """# Reconstruct From Data.

        ## Args:
            * v_data    (Tensor):   Visible node data.
            * p_v       (Tensor):   Visible node probabilities.

        ## Returns:
            * Tensor:   Reconstructed solution from data.
        """
        # Clamp probabilities to avoid log(0).
        p_v:    Tensor =    p_v.clamp(min = 1e-8, max = 1 - 1e-8)
        
        # Provide calculation of binary cross-entropy between data and predicated visible 
        # probabilities.
        return -(v_data * log(p_v) + (1 - v_data) * log(1 - p_v)).mean()
    
    # HELPERS ======================================================================================
    
    @staticmethod
    def _bernoulli_sample_(
        probabilities:  Tensor
    ) -> Tensor:
        """# Sample Probabilities.
        
        Sample binary {0, 1} values from given probabilities.

        ## Args:
            * probabilities (Tensor):   Tensor of probability values in [0, 1].

        ## Returns:
            * Tensor:   Binary tensor with the same shape, containing values in {0, 1}.
        """
        return (probabilities > rand_like(probabilities)).to(probabilities.dtype)
    
    def _cd_k_(self,
        data_visible_batch: Tensor
    ) -> Tuple[Tensor, Tensor, Tensor]:
        """# Contrastive Divergence (CD-k).
        
        Run k steps of Gibbs sampling starting from data (Contrastive Divergence CD-k).

        ## Args:
            * data_visible_batch    (Tensor):   Batch of data visible vectors (clamped starting 
                                                states).

        ## Returns:
            * Tensor:   The original input batch (returned for convenience/symmetry).
            * Tensor:   Sample from the model after k alternating Gibbs steps.
            * Tensor:   Probabilities P(visible = 1 | hidden_k) from the final Gibbs step (useful 
                        for computing reconstruction losses/metrics).
        """
        # Compute P(hidden | data_visible) and draw a hidden sample to start the chain.
        _, hidden_sample_from_data =                                self._visible_to_hidden_(
                                                                        visible_batch = data_visible_batch
                                                                    )

        # Initialize the running hidden state of the Gibbs chain with the sample from data.
        current_hidden_sample_binary =                              hidden_sample_from_data

        # Prepare holders for outputs from the final step (filled inside the loop).
        last_step_visible_activation_probability:   Tensor | None = None
        model_visible_sample_after_k_steps:         Tensor | None = None

        # Perform k alternating Gibbs steps: hidden -> visible -> hidden -> ...
        for _ in range(self._gibbs_steps_):
            
            # One Gibbs step starting from the current hidden sample.
            last_step_visible_activation_probability,   \
            model_visible_sample_after_k_steps,         \
            current_hidden_sample_binary =                          self._gibbs_step_from_hidden_(
                                                                        hidden_batch =  current_hidden_sample_binary
                                                                    )

        # Sanity checks for type checkers (they will be set after at least one step).
        assert model_visible_sample_after_k_steps       is not None
        assert last_step_visible_activation_probability is not None

        # Return the original data batch, the final model sample, and the final visible 
        # probabilities.
        return  data_visible_batch,                 \
                model_visible_sample_after_k_steps, \
                last_step_visible_activation_probability
    
    def _gibbs_step_from_hidden_(self,
        hidden_batch:   Tensor
    ) -> Tuple[Tensor, Tensor, Tensor]:
        """# Gibbs Step from Hidden.
        
        Perform one full Gibbs step starting from hidden states:
        hidden -> visible' -> hidden'

        ## Args:
            * hidden_batch  (Tensor):   Current hidden binary samples, of shape (batch_size, 
                                        hidden_nodes).

        ## Returns:
            * Tensor:   Probabilities = P(visible = 1 | hidden) from this step.
            * Tensor:   Sampled visible binary units from those probabilities.
            * Tensor:   New hidden binary sample obtained from the sampled visible units.
        """
        # Compute P(visible | hidden) and sample a visible vector.
        visible_activation_probability, visible_sample_binary = self._hidden_to_visible_(
                                                                    hidden_batch = hidden_batch
                                                                )
        
        # Given that sampled visible vector, compute p(hidden | visible) and sample new hidden.
        _, next_hidden_sample_binary =                          self._visible_to_hidden_(
                                                                    visible_batch = visible_sample_binary
                                                                )
        
        # Return probability for logging, the visible sample, and the next hidden sample.
        return visible_activation_probability, visible_sample_binary, next_hidden_sample_binary
    
    def _hidden_to_visible_(self,
        hidden_batch:   Tensor
    ) -> Tuple[Tensor, Tensor]:
        """# Hidden -> Visible.

        ## Args:
            * hidden_batch  (Tensor):   Batch of hidden vectors of shape (batch_size, hidden_nodes).

        ## Returns:
            * Tensor:   Probabilities of visible units being 1, of shape (batch_size, 
                        visible_nodes).
            * Tensor:   Binary visible unit samples, of shape (batch_size, visible_units).
        """
        # Compute visible pre-activation (affine transform): hidden @ W + visible_bias.
        visible_activation_logit:       Tensor =    linear(
                                                        input =         hidden_batch,
                                                        weight =        self._weights_.t(),
                                                        bias =          self._visible_bias_
                                                    )
        
        # Convert logits to probabilities with sigmoid.
        visible_activation_probability: Tensor =    sigmoid(visible_activation_logit)
        
        # Draw binary samples for the visible units.
        visible_sample_binary:          Tensor =    self._bernoulli_sample_(
                                                        probabilities = visible_activation_probability
                                                    )
        
        # Return both probabilities and samples.
        return visible_activation_probability, visible_sample_binary
    
    def _visible_to_hidden_(self,
        visible_batch:  Tensor
    ) -> Tuple[Tensor, Tensor]:
        """# Visible -> Hidden.
        
        Compute hidden activation probabilities and samples given visible units.

        ## Args:
            * visible_batch (Tensor):   Batch of visible vectors of shape (batch_size, 
                                        visible_nodes).

        ## Returns:
            * Tensor:   Probabilities of hidden units being 1, of shape (batch_size, hidden_nodes).
            * Tensor:   Binary hidden unit samples, of shape (batch_size, hidden_units).
        """
        # Compute hidden pre-activation (affine transform): visible @ W^T + hidden_bias.
        hidden_activation_logit:        Tensor =    linear(
                                                        input =         visible_batch,
                                                        weight =        self._weights_,
                                                        bias =          self._hidden_bias_
                                                    )
        
        # Pass through sigmoid to convert logits to probabilities in [0,1].
        hidden_activation_probability:  Tensor =    sigmoid(hidden_activation_logit)
        
        # Draw binary samples from these probabilities (non-differentiable).
        hidden_sample_binary:           Tensor =    self._bernoulli_sample_(
                                                        probabilities = hidden_activation_probability
                                                    )
        
        # Provide probabilities and binary samples.
        return hidden_activation_probability, hidden_sample_binary