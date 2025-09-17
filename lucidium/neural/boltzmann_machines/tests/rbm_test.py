"""# lucidium.neural.boltzmann-machines.tests.rbm_test

Restricted Boltzmann Machine Test Suite.
"""

from pytest                                 import fixture, FixtureRequest
from torch                                  import all as t_all, allclose, device as t_device,  \
                                                   dtype as t_dtype, equal, float32, float64,   \
                                                   isfinite, manual_seed, no_grad, rand, Tensor
from torch.cuda                             import is_available
from torch.nn.functional                    import linear, softplus
from torch.optim                            import Adam

from lucidium.neural.boltzmann_machines.rbm import RBM

# FIXTURES =========================================================================================

@fixture(params = [float32, float64], scope = "module")
def dtype(request: FixtureRequest) -> t_dtype:
    """# Get Data Type."""
    return request.param

@fixture(scope = "module")
def device() -> t_device:
    """# Get Device."""
    return t_device("cuda") if is_available() else t_device("cpu")

@fixture()
def small_rbm(
    dtype:  t_dtype,
    device: t_device
) -> RBM:
    """# Create Small RBM."""
    return  RBM(
                visible_nodes = 6,
                hidden_nodes =  4,
                gibbs_steps =   3,
                weight_scale =  1e-2,
                device =        device,
                dtype =         dtype,
            )

@fixture()
def toy_batch(
    dtype:  t_dtype,
    device: t_device
) -> Tensor:
    """# Create Dummy Batch."""
    # Seed torch.
    manual_seed(0)
    
    # Provide dummy sample.
    return (rand(8, 6, device = device, dtype = dtype) > 0.5).to(dtype)

# INTERFACE & SHAPES ===============================================================================

def test_forward_shapes(
    small_rbm:  RBM,
    toy_batch:  Tensor
) -> None:
    """# Test Contrastive Divergence Output Shapes."""
    # Get contrastive divergence output.
    v_data, v_model, p_v =  small_rbm(toy_batch)
    
    # Validate output shapes.
    assert v_data.shape  == toy_batch.shape,\
        f"Visible data batch shape {v_data.shape} expected to be {toy_batch.shape}"
        
    assert v_model.shape == toy_batch.shape,\
        f"Visible model batch shape {v_data.shape} expected to be {toy_batch.shape}"
        
    assert p_v.shape     == toy_batch.shape,\
        f"Probabilities shape {v_data.shape} expected to be {toy_batch.shape}"

def test_sampling_outputs_binary(
    small_rbm:  RBM,
    toy_batch:  Tensor
) -> None:
    """# Test Elements of Sampling Output."""
    # With no gradient...
    with no_grad():
        
        # Perform on Gibbs step.
        _, h =      small_rbm._visible_to_hidden_(visible_batch = toy_batch)
        p_v, v =    small_rbm._hidden_to_visible_(hidden_batch = h)
        
    # Ensure that all elements are binary.
    assert t_all((v == 0) | (v == 1)),      "Values of binary visible sample found not to be binary"
    assert t_all((p_v >= 0) & (p_v <= 1)),  "Probability values found to be outside of range [0, 1]"


# FREE ENERGY ======================================================================================

def test_free_energy_matches_closed_form(
    small_rbm:  RBM,
    toy_batch:  Tensor
) -> None:
    """# Test Free Energy Calculation."""
    # Compute free energy using RBM.
    fe_api:         Tensor =    small_rbm.free_energy(toy_batch)

    # Compute free energy manually.
    hidden_pre:     Tensor =    linear(
                                    input =     toy_batch,
                                    weight =    small_rbm._weights_,
                                    bias =      small_rbm._hidden_bias_
                                )
    softplus_sum:   Tensor =    softplus(input = hidden_pre).sum(dim=1)
    vbias_term:     Tensor =    toy_batch.mv(small_rbm._visible_bias_)
    fe_manual:      Tensor =    (-softplus_sum - vbias_term).mean()

    # Ensure that calculations match.
    assert  allclose(
                input = fe_api,
                other = fe_manual,
                atol =  1e-7 if toy_batch.dtype == float64 else 1e-5
            ), "Free energy calculation regression detected"


# GRADIENTS & TRAINING =============================================================================

def test_cd_backward_and_grads(
    small_rbm:  RBM,
    toy_batch:  Tensor
) -> None:
    """# Test Back Propagation & Gradients."""
    # Get predictions & targets.
    v_data, v_model, _ =    small_rbm(toy_batch)
    
    # Calculate loss.
    loss = small_rbm.cd_loss(v_data, v_model)

    # For each parameter...
    for p in small_rbm.parameters():
        
        # Zero out gradients.
        if p.grad is not None: p.grad.zero_()
        
    # Back propagation.
    loss.backward()

    # Gather parameters.
    grads:  Tensor =        [p.grad for p in small_rbm.parameters() if p.requires_grad]
    
    # Ensure that at least some parameters received gradients.
    assert any(g is not None for g in grads),                       \
        "No gradients found on RBM parameters"
        
    # Ensure that no gradients vanished/exploded.
    assert all(isfinite(g).all() for g in grads if g is not None),  \
        "Vanishing/exploding gradients detected"

def test_one_step_of_optimization_reduces_cd_loss(
    small_rbm:  RBM,
    toy_batch:  Tensor
) -> None:
    # Initialize optimizer.
    opt:    Adam =  Adam(params = small_rbm.parameters(), lr = 5e-2)

    # Without gradients...
    with no_grad():
        
        # Get predictions/targets.
        v_data0, v_model0, _ =  small_rbm(toy_batch)
        
        # Calculate loss.
        loss0:  Tensor =        small_rbm.cd_loss(v_data0, v_model0)

    # Get predictions/targets with gradients enabled.
    v_data, v_model, _ =    small_rbm(toy_batch)
    
    # Calculate loss.
    loss:   Tensor =        small_rbm.cd_loss(v_data, v_model)
    
    # Reset gradients.
    opt.zero_grad()
    
    # Back propagation.
    loss.backward()
    
    # Update weights.
    opt.step()

    # Without gradients...
    with no_grad():
        
        # Re-measure (not guaranteed strictly monotonic every single step, but usually decreases).
        v_data2, v_model2, _ =  small_rbm(toy_batch)
        loss2:  Tensor =        small_rbm.cd_loss(v_data2, v_model2)

    # Allow some tolerance; check "non-increase" to reduce flakiness on tiny batches.
    assert loss2 <= loss0 + 1e-6, \
        f"Loss did not decrease: before={loss0.item():.6f}, after={loss2.item():.6f}"

# REPRODUCIBILITY ==================================================================================

def test_seeding_reproducibility(
    dtype:  t_dtype,
    device: t_device
) -> None:
    """# Test Reproducibility."""
    # Initialize two RBMs for comparison.
    manual_seed(123)
    rbm1:   RBM =   RBM(visible_nodes=6, hidden_nodes=4, gibbs_steps=2, device=device, dtype=dtype)
    manual_seed(123)
    rbm2:   RBM =   RBM(visible_nodes=6, hidden_nodes=4, gibbs_steps=2, device=device, dtype=dtype)

    # For each parameter pair between RBMs...
    for p1, p2 in zip(rbm1.parameters(), rbm2.parameters()):
        
        # Parameters should match exactly if seeded identically before construction.
        assert allclose(p1, p2), f"Parameters differ between RBMs: {p1} != {p2}"

    # Create samples.
    manual_seed(123)
    x:  Tensor =    (rand(5, 6, device=device, dtype=dtype) > 0.5).to(dtype)
    manual_seed(123)
    y:  Tensor =    (rand(5, 6, device=device, dtype=dtype) > 0.5).to(dtype)

    # Ensure that output matches.
    assert equal(x, y), f"Sample data batches do not match"
    
    # Make forward passes through each RBM.
    manual_seed(123)
    out1 = rbm1(x)
    manual_seed(123)
    out2 = rbm2(y)
    
    # For each vector in outputs...
    for a, b in zip(out1, out2):
        
        # Ensure output matches.
        assert allclose(a, b), "RBM outputs do not match"


# DEVICE & TYPE HANDLING ===========================================================================

def test_device_and_dtype_consistency(
    small_rbm:  RBM,
    toy_batch:  Tensor,
    dtype:      t_dtype,
    device:     t_device
) -> None:
    # For each parameter in RBM...
    for p in small_rbm.parameters():
        
        # Ensure parameters live on the intended device/dtype.
        assert p.device == device
        assert p.dtype  == dtype

    # Make a forward pass through RBM and record output.
    v_data, v_model, p_v = small_rbm(toy_batch)
    
    # Ensure that output tensors are of proper type and on correct device.
    assert v_data.device  == device, f"Visible data batch device expected to be {device}, got {v_data.device}"
    assert v_model.device == device, f"Visible model batch device expected to be {device}, got {v_model.device}"
    assert p_v.device     == device, f"Probabilities batch device expected to be {device}, got {p_v.device}"
    assert v_data.dtype   == dtype,  f"Visible data batch dtype expected to be {dtype}, got {v_data.device}"
    assert v_model.dtype  == dtype,  f"Visible modelbatch dtype expected to be {dtype}, got {v_model.device}"
    assert p_v.dtype      == dtype,  f"Probabilities batch dtype expected to be {dtype}, got {p_v.device}"


# PROBABILITY BOUNDS ===============================================================================

def test_probability_bounds(
    small_rbm:  RBM,
    toy_batch:  Tensor
) -> None:
    """# Test Probability Bounds."""
    # Get probabilities of hidden nodes.
    p_h, h = small_rbm._visible_to_hidden_(visible_batch = toy_batch)
    
    # Ensure that all values are in range [0, 1].
    assert t_all((p_h >= 0) & (p_h <= 1)),  \
        f"Visible probabilities found to be outside of range [0, 1]"
    
    # Get probabilities of visible nodes.
    p_v, v = small_rbm._hidden_to_visible_(hidden_batch = h)
    
    # Ensure that all values are in range [0, 1].
    assert t_all((p_v >= 0) & (p_v <= 1)),  \
        f"Hidden probabilities found to be outside of range [0, 1]"
