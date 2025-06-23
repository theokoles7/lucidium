# NSRL Hierarchical Predicate Discovery - Project Bible

## "Extract → Mine → Propose → Compose → Validate"

## Table of Contents
1. [Project Overview](#project-overview)
2. [Core Research Goal](#core-research-goal)
3. [Architectural Principles](#architectural-principles)
4. [Project Structure](#project-structure)
5. [Component Specifications](#component-specifications)
6. [Data Flow Architecture](#data-flow-architecture)
7. [Coding Standards](#coding-standards)
8. [Implementation Phases](#implementation-phases)
9. [Evaluation Framework](#evaluation-framework)
10. [Common Pitfalls](#common-pitfalls)
11. [Research Contribution](#research-contribution)

---

## Project Overview

### What We're Building
A neuro-symbolic reinforcement learning (NSRL) system that **automatically discovers hierarchical predicate structures** from raw experience data. The system learns to compose basic symbolic predicates (e.g., "near", "red") into meaningful higher-level concepts (e.g., "accessible", "goal_reachable") without human intervention.

### Why This Matters
- **Sample Efficiency**: Hierarchical predicates provide better state abstractions for RL
- **Transfer Learning**: Discovered hierarchies should generalize across related environments
- **Interpretability**: Symbolic predicates are human-readable, unlike pure neural representations
- **Automatic Discovery**: Removes the need for hand-crafted symbolic knowledge

### What Success Looks Like
1. System discovers meaningful composite predicates (validated against human intuition)
2. Discovered predicates improve RL sample efficiency compared to flat predicate spaces
3. Hierarchies transfer to new but related environments
4. Discovery process is automatic (no hand-coded target patterns)

---

## Core Research Goal

### Primary Research Question
**"Can an RL agent automatically discover hierarchical symbolic abstractions that improve learning efficiency and transfer capability?"**

### Specific Hypotheses to Test
1. **H1**: Statistical pattern mining can identify meaningful predicate co-occurrences
2. **H2**: Neural pattern proposal outperforms purely statistical methods
3. **H3**: Hierarchical predicates improve sample efficiency vs. flat predicate spaces
4. **H4**: Discovered hierarchies transfer to structurally similar environments
5. **H5**: Automatic discovery matches or exceeds hand-crafted hierarchies

### Success Metrics
- **Discovery Quality**: Semantic coherence, hierarchy depth, compression ratio
- **Learning Performance**: Sample efficiency, final performance, convergence speed
- **Transfer Capability**: Performance on unseen but related tasks
- **Scalability**: Discovery quality as environment complexity increases

---

## Architectural Principles

### 1. **Single Responsibility Principle**
- **RULE**: Each class has exactly one reason to change
- **IMPLEMENTATION**: One class per file, each class handles one specific aspect
- **RATIONALE**: Makes testing, debugging, and modification straightforward

### 2. **Separation of Concerns**
- **Perception**: Converting observations to symbols
- **Discovery**: Finding patterns and creating compositions
- **Learning**: RL with hierarchical state representations
- **Evaluation**: Measuring system performance

### 3. **Clear Data Interfaces**
- **RULE**: All data passed between components uses well-defined types
- **IMPLEMENTATION**: Strong typing with `@dataclass` and type hints
- **RATIONALE**: Prevents integration bugs and makes the system self-documenting

### 4. **Modular Pipeline Architecture**
- **RULE**: Each discovery component can be swapped independently
- **IMPLEMENTATION**: Abstract base classes with concrete implementations
- **RATIONALE**: Enables ablation studies and algorithm comparison

### 5. **Testability First**
- **RULE**: Every component can be unit tested in isolation
- **IMPLEMENTATION**: Dependency injection and mock-able interfaces
- **RATIONALE**: Research code must be reliable and debuggable

---

## Project Structure

```
nsrl_discovery/
├── README.md                     # Project overview and setup
├── requirements.txt              # Dependencies
├── setup.py                      # Package installation
├── pyproject.toml               # Build configuration
├── tests/                       # Unit and integration tests
│   ├── __init__.py
│   ├── test_core/
│   ├── test_perception/
│   ├── test_discovery/
│   ├── test_learning/
│   └── test_evaluation/
├── docs/                        # Documentation
│   ├── architecture.md
│   ├── api_reference.md
│   └── tutorials/
├── configs/                     # Experiment configurations
│   ├── default.yaml
│   ├── gridworld.yaml
│   └── continuous.yaml
├── experiments/                 # Experiment scripts
│   ├── __init__.py
│   ├── runner.py
│   ├── ablation_study.py
│   └── transfer_experiments.py
└── nsrl_discovery/              # Main package
    ├── __init__.py
    ├── core/                    # Fundamental data structures
    │   ├── __init__.py
    │   ├── predicate.py         # Predicate class
    │   ├── experience.py        # Experience data structure
    │   ├── hierarchy.py         # PredicateHierarchy manager
    │   └── patterns.py          # Pattern-related classes
    ├── perception/              # Observation → Symbol conversion
    │   ├── __init__.py
    │   ├── extractor.py         # BasicPredicateExtractor
    │   ├── grounding.py         # SymbolGrounder
    │   └── templates.py         # PredicateTemplate definitions
    ├── discovery/               # Pattern discovery and composition
    │   ├── __init__.py
    │   ├── pattern_miner.py     # StatisticalPatternMiner
    │   ├── neural_proposer.py   # NeuralPatternProposer
    │   ├── composer.py          # PredicateComposer
    │   ├── validator.py         # HierarchyValidator
    │   └── utils.py             # Discovery utilities
    ├── learning/                # RL with hierarchical predicates
    │   ├── __init__.py
    │   ├── agent.py             # NSRLAgent
    │   ├── policy.py            # HierarchicalPolicy
    │   ├── value.py             # HierarchicalValue
    │   └── replay_buffer.py     # ExperienceBuffer
    ├── evaluation/              # Metrics and benchmarks
    │   ├── __init__.py
    │   ├── metrics.py           # Discovery and performance metrics
    │   ├── benchmarks.py        # Standard test environments
    │   └── visualization.py     # Result plotting and analysis
    └── utils/                   # General utilities
        ├── __init__.py
        ├── logging.py           # Logging configuration
        ├── config.py            # Configuration management
        └── reproducibility.py   # Random seed management
```

### File Organization Principles
1. **One Class Per File**: Each `.py` file contains exactly one primary class
2. **Logical Grouping**: Related functionality grouped in packages
3. **Clear Dependencies**: Higher-level packages can import from lower-level ones
4. **No Circular Imports**: Dependency graph must be acyclic

---

## Component Specifications

### Core Components (`core/`)

#### `core/predicate.py`
```python
@dataclass(frozen=True)
class Predicate:
    """
    Atomic symbolic predicate representing a relationship or property.
    
    This is the fundamental unit of symbolic knowledge in our system.
    Predicates can be basic (extracted from observations) or composite
    (discovered through pattern mining and composition).
    
    Args:
        name: Predicate identifier (e.g., "near", "accessible")
        args: Tuple of argument strings (e.g., ("agent", "key"))
        confidence: Confidence score between 0.0 and 1.0
        level: Hierarchy level (0=basic, 1+=composite)
        source: How this predicate was created ("extracted", "composed")
        metadata: Additional information about predicate creation
    """
    name: str
    args: Tuple[str, ...]
    confidence: float = 1.0
    level: int = 0
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Key Methods**:
- `ground(bindings: Dict[str, str]) -> Predicate`: Apply variable substitutions
- `matches_pattern(pattern: str) -> bool`: Check if predicate matches a pattern template
- `get_variables() -> Set[str]`: Extract variable names from arguments
- `to_vector() -> np.ndarray`: Convert to neural network input representation

#### `core/experience.py`
```python
@dataclass
class Experience:
    """
    Single environment interaction containing observations and symbolic state.
    
    This is the primary data structure for learning and discovery. Each
    experience captures both the raw sensory information and the extracted
    symbolic representation at a particular time step.
    
    Args:
        obs: Raw observation from environment
        predicates: Extracted symbolic predicates for this state
        action: Action index taken by agent
        reward: Immediate reward received
        next_obs: Raw observation after action
        next_predicates: Symbolic predicates for next state
        done: Whether episode terminated
        episode_id: Unique identifier for episode
        step: Step number within episode
        metadata: Additional context information
    """
    obs: np.ndarray
    predicates: Set[Predicate]
    action: int
    reward: float
    next_obs: np.ndarray
    next_predicates: Set[Predicate]
    done: bool
    episode_id: str
    step: int
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### `core/hierarchy.py`
```python
class PredicateHierarchy:
    """
    Manages the discovered predicate hierarchy and composition rules.
    
    This class maintains the hierarchical structure of discovered predicates
    and provides methods for evaluating symbolic states at different levels
    of abstraction.
    
    Responsibilities:
    - Store predicates organized by hierarchy level
    - Evaluate observations to produce symbolic states
    - Manage composition rules for higher-level predicates
    - Provide efficient lookup and querying capabilities
    """
    
    def __init__(self):
        self.levels: Dict[int, Set[Predicate]] = defaultdict(set)
        self.composition_rules: Dict[str, CompositionRule] = {}
        self.predicate_lookup: Dict[str, Predicate] = {}
        self.evaluation_cache: Dict[str, Set[Predicate]] = {}
```

### Perception Components (`perception/`)

#### `perception/extractor.py`
```python
class BasicPredicateExtractor:
    """
    Converts raw observations into basic symbolic predicates.
    
    This is the bridge between continuous sensory input and discrete
    symbolic representation. It uses domain-specific extraction rules
    to identify when basic predicates hold in observations.
    
    Responsibilities:
    - Extract spatial relationships (near, above, left_of)
    - Extract object properties (color, shape, size)
    - Extract agent-specific predicates (has, can_see)
    - Handle different observation types (grid, image, vector)
    """
    
    def __init__(self, predicate_templates: Dict[str, PredicateTemplate]):
        self.templates = predicate_templates
        self.extractors = self._build_extractors()
        self.cache = {}
    
    def extract(self, obs: np.ndarray) -> Set[Predicate]:
        """
        Extract all basic predicates that hold in the observation.
        
        Args:
            obs: Raw observation array
            
        Returns:
            Set of basic predicates detected in observation
            
        Process:
        1. Apply each extraction rule to observation
        2. Collect positive detections
        3. Create Predicate objects with appropriate confidence
        4. Cache results for efficiency
        """
```

#### `perception/grounding.py`
```python
class SymbolGrounder:
    """
    Neural network that grounds symbolic predicates in observations.
    
    This component learns to evaluate whether arbitrary predicates
    (including newly discovered composite ones) hold in given observations.
    It's trained on basic predicate groundings and generalizes to compositions.
    
    Responsibilities:
    - Learn predicate grounding from basic predicates
    - Generalize to evaluate composite predicates
    - Provide confidence scores for predicate evaluations
    - Update representations based on successful compositions
    """
    
    def __init__(self, obs_dim: int, predicate_dim: int):
        self.grounding_network = self._build_network(obs_dim, predicate_dim)
        self.predicate_embeddings = {}
        self.training_data = []
```

### Discovery Components (`discovery/`)

#### `discovery/pattern_miner.py`
```python
class StatisticalPatternMiner:
    """
    Mines frequent co-occurrence patterns in predicate data.
    
    Uses classical association rule mining (Apriori algorithm) to find
    statistically significant predicate combinations. This provides the
    foundation for discovering meaningful composite predicates.
    
    Responsibilities:
    - Count predicate co-occurrences across experiences
    - Apply support and confidence thresholds
    - Generate candidate composition patterns
    - Handle temporal patterns (sequence mining)
    """
    
    def __init__(self, 
                 min_support: float = 0.1,
                 min_confidence: float = 0.7,
                 max_pattern_length: int = 3):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.max_pattern_length = max_pattern_length
        self.pattern_counts = defaultdict(int)
        self.total_transactions = 0
    
    def mine_patterns(self, experiences: List[Experience]) -> List[PredicatePattern]:
        """
        Mine frequent predicate patterns from experience data.
        
        Args:
            experiences: List of experience objects to analyze
            
        Returns:
            List of patterns meeting support/confidence criteria
            
        Algorithm:
        1. Extract predicate sets from experiences (transactions)
        2. Count all possible predicate combinations
        3. Filter by minimum support threshold
        4. Generate association rules and filter by confidence
        5. Return ranked patterns
        """
```

#### `discovery/neural_proposer.py`
```python
class NeuralPatternProposer:
    """
    Neural network that proposes promising predicate compositions.
    
    This component learns to suggest which predicate combinations
    are likely to be useful, going beyond simple statistical co-occurrence
    to consider semantic relationships and utility for the RL task.
    
    Architecture:
    - Predicate encoder: Maps predicates to embeddings
    - Context encoder: Captures current predicate context
    - Pattern decoder: Generates candidate compositions
    - Value network: Estimates composition utility
    """
    
    def __init__(self, 
                 predicate_vocab_size: int,
                 embedding_dim: int = 64,
                 hidden_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.predicate_encoder = PredicateEncoder(predicate_vocab_size, embedding_dim)
        self.context_encoder = ContextEncoder(embedding_dim, hidden_dim)
        self.pattern_decoder = PatternDecoder(hidden_dim, predicate_vocab_size)
        self.value_network = CompositionValueNetwork(hidden_dim)
        
    def propose_compositions(self, 
                           context_predicates: Set[Predicate],
                           experience_buffer: ExperienceBuffer,
                           num_proposals: int = 10) -> List[CandidateComposition]:
        """
        Generate promising predicate composition candidates.
        
        Args:
            context_predicates: Current set of available predicates
            experience_buffer: Recent experiences for context
            num_proposals: Number of candidates to generate
            
        Returns:
            Ranked list of composition candidates with utility scores
            
        Process:
        1. Encode current predicate context
        2. Sample composition candidates from learned distribution
        3. Score candidates using value network
        4. Return top-k candidates ranked by predicted utility
        """
```

#### `discovery/composer.py`
```python
class PredicateComposer:
    """
    Composes basic predicates into hierarchical composite predicates.
    
    Takes patterns from miners/proposers and creates actual composite
    predicates with proper semantics, argument handling, and composition rules.
    
    Responsibilities:
    - Determine composition type (AND, OR, SEQUENCE, etc.)
    - Handle argument unification across component predicates
    - Generate meaningful names for composite predicates
    - Create composition rules for hierarchy evaluation
    """
    
    def __init__(self):
        self.composition_templates = self._load_templates()
        self.naming_strategy = CompositeNamingStrategy()
        self.argument_unifier = ArgumentUnifier()
    
    def compose(self, pattern: PredicatePattern) -> Optional[CompositePredicateResult]:
        """
        Create composite predicate from a pattern.
        
        Args:
            pattern: Pattern specifying which predicates to compose
            
        Returns:
            CompositePredicateResult with new predicate and composition rule
            
        Process:
        1. Validate pattern for composability
        2. Determine appropriate composition semantics
        3. Unify arguments across component predicates
        4. Generate composite predicate name
        5. Create evaluation rule for the composition
        """
```

#### `discovery/validator.py`
```python
class HierarchyValidator:
    """
    Validates discovered predicates for quality and utility.
    
    Ensures that discovered composite predicates are logically sound,
    semantically meaningful, and provide utility for the RL task.
    
    Validation Criteria:
    - Logical consistency (no contradictions)
    - Semantic coherence (meaningful compositions)
    - Empirical utility (improves task performance)
    - Hierarchy constraints (depth limits, complexity bounds)
    """
    
    def __init__(self, 
                 max_hierarchy_depth: int = 5,
                 min_utility_threshold: float = 0.1,
                 coherence_threshold: float = 0.5):
        self.max_depth = max_hierarchy_depth
        self.min_utility = min_utility_threshold
        self.coherence_threshold = coherence_threshold
        self.validation_history = []
    
    def validate_composition(self, 
                           composite: Predicate,
                           supporting_evidence: List[Experience],
                           current_hierarchy: PredicateHierarchy) -> ValidationResult:
        """
        Comprehensive validation of a composite predicate candidate.
        
        Args:
            composite: Proposed composite predicate
            supporting_evidence: Experiences that support this composition
            current_hierarchy: Current predicate hierarchy
            
        Returns:
            ValidationResult with decision and detailed reasoning
            
        Validation Steps:
        1. Check logical consistency
        2. Verify hierarchy depth constraints
        3. Evaluate empirical utility
        4. Assess semantic coherence
        5. Check for redundancy with existing predicates
        """
```

### Learning Components (`learning/`)

#### `learning/agent.py`
```python
class NSRLAgent:
    """
    Main RL agent that integrates hierarchical predicate discovery.
    
    This is the central orchestrator that combines perception, discovery,
    and learning into a unified system. It manages the discovery pipeline
    and integrates discovered predicates into the RL process.
    
    Key Features:
    - Periodic predicate discovery
    - Dynamic network expansion for new predicates
    - Integration of symbolic and neural components
    - Experience collection and management
    """
    
    def __init__(self, 
                 obs_space: gym.Space,
                 action_space: gym.Space,
                 discovery_frequency: int = 100,
                 config: AgentConfig = None):
        
        # Core components
        self.extractor = BasicPredicateExtractor()
        self.hierarchy = PredicateHierarchy()
        self.policy = HierarchicalPolicy(action_space)
        self.value_function = HierarchicalValue()
        
        # Discovery pipeline
        self.pattern_miner = StatisticalPatternMiner()
        self.neural_proposer = NeuralPatternProposer()
        self.composer = PredicateComposer()
        self.validator = HierarchyValidator()
        
        # Experience management
        self.experience_buffer = ExperienceBuffer()
        self.discovery_frequency = discovery_frequency
        self.steps_since_discovery = 0
    
    def act(self, obs: np.ndarray) -> int:
        """
        Select action based on hierarchical predicate representation.
        
        Args:
            obs: Raw observation from environment
            
        Returns:
            Action index to execute
            
        Process:
        1. Extract/evaluate predicates from observation
        2. Feed hierarchical predicate state to policy
        3. Sample action from policy distribution
        4. Track experience for later learning
        """
    
    def update(self, experience: Experience) -> Dict[str, Any]:
        """
        Update agent with new experience and potentially discover predicates.
        
        Args:
            experience: Latest environment interaction
            
        Returns:
            Dictionary with update statistics and discoveries
            
        Process:
        1. Add experience to buffer
        2. Update policy and value networks
        3. Periodically run predicate discovery
        4. Integrate any new predicates into networks
        """
```

### Evaluation Components (`evaluation/`)

#### `evaluation/metrics.py`
```python
class DiscoveryMetrics:
    """
    Comprehensive metrics for evaluating predicate discovery quality.
    
    These metrics assess different aspects of the discovery process:
    - Structural properties of the hierarchy
    - Semantic quality of discovered predicates
    - Utility for the RL task
    - Efficiency of the discovery process
    """
    
    @staticmethod
    def hierarchy_depth(hierarchy: PredicateHierarchy) -> int:
        """Maximum depth of discovered hierarchy."""
        
    @staticmethod
    def compression_ratio(hierarchy: PredicateHierarchy) -> float:
        """Ratio of basic to total predicates (measures abstraction)."""
        
    @staticmethod
    def semantic_coherence(hierarchy: PredicateHierarchy, 
                          ground_truth: Optional[Dict] = None) -> float:
        """Measure semantic meaningfulness of compositions."""
        
    @staticmethod
    def discovery_efficiency(discovery_history: List[DiscoveryEvent]) -> float:
        """Predicates discovered per unit time/experience."""

class PerformanceMetrics:
    """
    Metrics for evaluating RL performance improvements from discovery.
    
    These metrics measure whether discovered predicates actually improve
    the RL agent's learning and performance.
    """
    
    @staticmethod
    def sample_efficiency_improvement(baseline_curve: List[float],
                                    discovery_curve: List[float]) -> float:
        """Improvement in sample efficiency compared to baseline."""
        
    @staticmethod
    def transfer_performance(source_hierarchy: PredicateHierarchy,
                           target_tasks: List[gym.Env]) -> Dict[str, float]:
        """Performance when transferring hierarchy to new tasks."""
```

---

## Data Flow Architecture

### Primary Data Flow
```
Raw Observation → BasicPredicateExtractor → Set[Predicate] → PredicateHierarchy
                                                                      ↓
Experience ← NSRLAgent ← HierarchicalPolicy ← Hierarchical State Representation
    ↓
ExperienceBuffer → PatternMiner → PredicatePattern → PredicateComposer
                       ↓                                    ↓
                NeuralProposer → CandidateComposition → CompositePredicateResult
                                                              ↓
                                                     HierarchyValidator
                                                              ↓
                                                     PredicateHierarchy (update)
```

### Key Data Structures Flow

1. **Observation Processing**:
   ```
   np.ndarray → BasicPredicateExtractor → Set[Predicate]
   ```

2. **Experience Collection**:
   ```
   (obs, action, reward, next_obs) → Experience → ExperienceBuffer
   ```

3. **Pattern Discovery**:
   ```
   List[Experience] → StatisticalPatternMiner → List[PredicatePattern]
                   → NeuralPatternProposer → List[CandidateComposition]
   ```

4. **Composition & Validation**:
   ```
   PredicatePattern → PredicateComposer → CompositePredicateResult
                                       → HierarchyValidator → ValidationResult
   ```

5. **Integration**:
   ```
   ValidatedComposite → PredicateHierarchy → HierarchicalPolicy/Value
   ```

### Critical Interfaces

#### `BasicPredicateExtractor.extract()`
- **Input**: `np.ndarray` (raw observation)
- **Output**: `Set[Predicate]` (basic predicates)
- **Contract**: Must handle all observation types consistently

#### `PatternMiner.mine_patterns()`
- **Input**: `List[Experience]` (recent experiences)
- **Output**: `List[PredicatePattern]` (statistical patterns)
- **Contract**: Patterns must meet minimum support/confidence

#### `NeuralProposer.propose_compositions()`
- **Input**: `Set[Predicate]` (context), `ExperienceBuffer`
- **Output**: `List[CandidateComposition]` (ranked proposals)
- **Contract**: Proposals must be valid predicate combinations

#### `PredicateComposer.compose()`
- **Input**: `PredicatePattern` or `CandidateComposition`
- **Output**: `Optional[CompositePredicateResult]`
- **Contract**: Must handle argument unification and naming

#### `HierarchyValidator.validate_composition()`
- **Input**: `CompositePredicateResult`, `List[Experience]`
- **Output**: `ValidationResult`
- **Contract**: Must prevent invalid additions to hierarchy

---

## Coding Standards

### Python Style Guidelines

#### Type Hints (MANDATORY)
```python
# ✅ CORRECT - Every function has complete type hints
def mine_patterns(self, experiences: List[Experience]) -> List[PredicatePattern]:
    """Mine frequent predicate patterns from experience data."""
    patterns: List[PredicatePattern] = []
    for exp in experiences:
        predicate_set: Set[Predicate] = exp.predicates
        # ... processing logic
    return patterns

# ❌ INCORRECT - Missing type hints
def mine_patterns(self, experiences):
    patterns = []
    for exp in experiences:
        # ... processing logic
    return patterns
```

#### Docstring Format (MANDATORY)
```python
def validate_composition(self, 
                        composite: Predicate,
                        supporting_evidence: List[Experience],
                        current_hierarchy: PredicateHierarchy) -> ValidationResult:
    """
    Comprehensive validation of a composite predicate candidate.
    
    This method evaluates whether a proposed composite predicate should be
    added to the hierarchy based on logical consistency, empirical utility,
    and semantic coherence criteria.
    
    Args:
        composite: The proposed composite predicate to validate. Must have
                  level > 0 and reference valid component predicates.
        supporting_evidence: List of experiences that provide evidence for
                           this composition. Should contain instances where
                           the component predicates co-occur.
        current_hierarchy: The existing predicate hierarchy that would receive
                         this composite. Used to check for redundancy and
                         consistency with existing predicates.
    
    Returns:
        ValidationResult object containing:
        - valid (bool): Whether the composition should be accepted
        - reason (str): Detailed explanation of the decision
        - confidence (float): Confidence in the validation decision
        - suggested_modifications (List[str]): Potential improvements if rejected
    
    Raises:
        ValueError: If composite.level <= 0 or component predicates not found
        TypeError: If supporting_evidence contains non-Experience objects
    
    Example:
        >>> composite = Predicate("accessible", ("agent", "key"), level=1)
        >>> evidence = [exp1, exp2, exp3]  # Experiences with near+unlocked
        >>> result = validator.validate_composition(composite, evidence, hierarchy)
        >>> if result.valid:
        ...     hierarchy.add_predicate(composite)
    """
    # Validation implementation...
```

#### Variable Documentation (MANDATORY)
```python
def discover_predicates(self) -> Dict[str, Predicate]:
    """Run the complete predicate discovery pipeline."""
    
    # Get recent experiences for pattern analysis
    recent_experiences: List[Experience] = self.experience_buffer.get_recent(1000)
    
    # Mine statistical patterns using co-occurrence analysis
    statistical_patterns: List[PredicatePattern] = self.pattern_miner.mine_patterns(
        experiences=recent_experiences
    )
    
    # Generate neural proposals based on learned preferences
    current_predicates: Set[Predicate] = self.hierarchy.get_active_predicates()
    neural_proposals: List[CandidateComposition] = self.neural_proposer.propose_compositions(
        context_predicates=current_predicates,
        experience_buffer=self.experience_buffer
    )
    
    # Combine and rank all candidate compositions
    all_candidates: List[Union[PredicatePattern, CandidateComposition]] = (
        statistical_patterns + neural_proposals
    )
    
    # Process each candidate through composition and validation
    newly_discovered: Dict[str, Predicate] = {}
    for candidate in all_candidates:
        # Attempt to create composite predicate from pattern
        composition_result: Optional[CompositePredicateResult] = self.composer.compose(candidate)
        
        if composition_result is not None:
            # Validate the proposed composition
            validation: ValidationResult = self.validator.validate_composition(
                composite=composition_result.predicate,
                supporting_evidence=recent_experiences,
                current_hierarchy=self.hierarchy
            )
            
            if validation.valid:
                # Add validated predicate to hierarchy and tracking
                self.hierarchy.add_predicate(
                    predicate=composition_result.predicate,
                    level=composition_result.predicate.level
                )
                newly_discovered[composition_result.predicate.name] = composition_result.predicate
    
    return newly_discovered
```

#### Error Handling Patterns
```python
# ✅ CORRECT - Specific exceptions with context
def extract_predicates(self, obs: np.ndarray) -> Set[Predicate]:
    """Extract basic predicates from observation."""
    if obs.shape != self.expected_obs_shape:
        raise ValueError(
            f"Observation shape {obs.shape} does not match expected shape "
            f"{self.expected_obs_shape}. Check environment compatibility."
        )
    
    try:
        predicates: Set[Predicate] = set()
        for extractor_name, extractor_fn in self.extractors.items():
            # Process each extractor with specific error context
            try:
                if extractor_fn(obs):
                    args: Tuple[str, ...] = self._get_args(obs, extractor_name)
                    predicates.add(Predicate(extractor_name, args))
            except Exception as e:
                # Log but don't fail completely for individual extractor errors
                logger.warning(
                    f"Extractor '{extractor_name}' failed on observation: {e}"
                )
                continue
        
        return predicates
        
    except Exception as e:
        raise RuntimeError(
            f"Predicate extraction failed completely: {e}. "
            f"Check observation format and extractor implementations."
        ) from e
```

#### Logging Standards
```python
import logging
from typing import Any, Dict

# Module-level logger configuration
logger = logging.getLogger(__name__)

class PredicateComposer:
    def compose(self, pattern: PredicatePattern) -> Optional[CompositePredicateResult]:
        """Create composite predicate from pattern."""
        
        # Log entry with context
        logger.debug(
            f"Composing pattern: {pattern.name} with {len(pattern.components)} components"
        )
        
        # Validation step with informative logging
        if not self._validate_pattern(pattern):
            logger.info(
                f"Pattern '{pattern.name}' failed validation. "
                f"Components: {[c.name for c in pattern.components]}"
            )
            return None
        
        # Successful composition
        composite: Predicate = self._create_composite(pattern)
        logger.info(
            f"Successfully composed '{composite.name}' from pattern '{pattern.name}'. "
            f"Level: {composite.level}, Components: {len(pattern.components)}"
        )
        
        return CompositePredicateResult(
            predicate=composite,
            composition_rule=self._create_rule(pattern),
            metadata={"pattern_source": pattern.source, "confidence": pattern.confidence}
        )
```

### Testing Standards (MANDATORY)

#### Unit Test Structure
```python
import pytest
import numpy as np
from unittest.mock import Mock, patch
from nsrl_discovery.core.predicate import Predicate
from nsrl_discovery.core.experience import Experience
from nsrl_discovery.discovery.pattern_miner import StatisticalPatternMiner

class TestStatisticalPatternMiner:
    """
    Comprehensive test suite for StatisticalPatternMiner.
    
    Tests cover normal operation, edge cases, error conditions,
    and performance characteristics.
    """
    
    @pytest.fixture
    def sample_experiences(self) -> List[Experience]:
        """Create standardized test experiences."""
        # Create realistic test data that covers common patterns
        obs: np.ndarray = np.zeros((10, 10))  # Grid world observation
        
        experiences: List[Experience] = [
            Experience(
                obs=obs,
                predicates={
                    Predicate("near", ("agent", "key")),
                    Predicate("unlocked", ("key",))
                },
                action=0,
                reward=1.0,
                next_obs=obs,
                next_predicates=set(),
                done=False,
                episode_id="test_episode_1",
                step=1
            ),
            # ... more test experiences
        ]
        return experiences
    
    @pytest.fixture
    def pattern_miner(self) -> StatisticalPatternMiner:
        """Create pattern miner with test configuration."""
        return StatisticalPatternMiner(
            min_support=0.3,
            min_confidence=0.7,
            max_pattern_length=2
        )
    
    def test_mine_patterns_normal_operation(self, 
                                          pattern_miner: StatisticalPatternMiner,
                                          sample_experiences: List[Experience]):
        """Test pattern mining under normal conditions."""
        # Execute pattern mining
        patterns: List[PredicatePattern] = pattern_miner.mine_patterns(sample_experiences)
        
        # Verify expected patterns are discovered
        assert len(patterns) > 0, "Should discover at least one pattern"
        
        # Check pattern structure
        for pattern in patterns:
            assert pattern.support >= pattern_miner.min_support
            assert pattern.confidence >= pattern_miner.min_confidence
            assert len(pattern.components) <= pattern_miner.max_pattern_length
    
    def test_mine_patterns_empty_input(self, pattern_miner: StatisticalPatternMiner):
        """Test behavior with empty experience list."""
        patterns: List[PredicatePattern] = pattern_miner.mine_patterns([])
        assert patterns == [], "Empty input should return empty patterns"
    
    def test_mine_patterns_insufficient_support(self, pattern_miner: StatisticalPatternMiner):
        """Test that patterns below support threshold are filtered out."""
        # Create experiences with rare patterns
        rare_experiences: List[Experience] = [/* single occurrence pattern */]
        
        patterns: List[PredicatePattern] = pattern_miner.mine_patterns(rare_experiences)
        
        # Should not discover patterns that don't meet support threshold
        assert len(patterns) == 0, "Rare patterns should be filtered out"
    
    @pytest.mark.performance
    def test_mine_patterns_performance(self, pattern_miner: StatisticalPatternMiner):
        """Test performance with large experience sets."""
        # Generate large test dataset
        large_experiences: List[Experience] = self._generate_large_dataset(10000)
        
        import time
        start_time: float = time.time()
        patterns: List[PredicatePattern] = pattern_miner.mine_patterns(large_experiences)
        end_time: float = time.time()
        
        # Performance requirements
        execution_time: float = end_time - start_time
        assert execution_time < 10.0, f"Pattern mining took {execution_time:.2f}s, should be < 10s"
```

#### Integration Test Structure
```python
class TestDiscoveryPipeline:
    """
    Integration tests for the complete discovery pipeline.
    
    These tests verify that components work together correctly
    and that the overall discovery process produces valid results.
    """
    
    @pytest.fixture
    def discovery_pipeline(self) -> Tuple[StatisticalPatternMiner, 
                                        NeuralPatternProposer,
                                        PredicateComposer,
                                        HierarchyValidator]:
        """Set up complete discovery pipeline."""
        miner = StatisticalPatternMiner(min_support=0.2, min_confidence=0.6)
        proposer = NeuralPatternProposer(predicate_vocab_size=50)
        composer = PredicateComposer()
        validator = HierarchyValidator(max_hierarchy_depth=3)
        
        return miner, proposer, composer, validator
    
    def test_end_to_end_discovery(self, discovery_pipeline, sample_environment_data):
        """Test complete discovery process from experiences to hierarchy."""
        miner, proposer, composer, validator = discovery_pipeline
        
        # Run complete pipeline
        statistical_patterns = miner.mine_patterns(sample_environment_data)
        neural_proposals = proposer.propose_compositions(
            context_predicates=set(),
            experience_buffer=ExperienceBuffer(sample_environment_data)
        )
        
        discovered_predicates: List[Predicate] = []
        
        # Process all candidates
        for candidate in statistical_patterns + neural_proposals:
            composition_result = composer.compose(candidate)
            if composition_result:
                validation = validator.validate_composition(
                    composition_result.predicate,
                    sample_environment_data,
                    PredicateHierarchy()
                )
                if validation.valid:
                    discovered_predicates.append(composition_result.predicate)
        
        # Verify meaningful discoveries
        assert len(discovered_predicates) > 0, "Should discover at least one valid predicate"
        
        # Check hierarchy properties
        max_level = max(p.level for p in discovered_predicates)
        assert max_level > 0, "Should discover hierarchical predicates"
        assert max_level <= 3, "Should respect depth constraints"
```

---

## Implementation Phases

### Phase 1: Core Foundation (Weeks 1-2)
**Goal**: Establish solid data structures and basic functionality

#### Week 1: Core Data Structures
- [ ] `core/predicate.py` - Complete Predicate class with all methods
- [ ] `core/experience.py` - Experience and ExperienceBuffer classes
- [ ] `core/hierarchy.py` - Basic PredicateHierarchy implementation
- [ ] Unit tests for all core classes
- [ ] Documentation for core interfaces

#### Week 2: Basic Perception
- [ ] `perception/extractor.py` - BasicPredicateExtractor for grid worlds
- [ ] `perception/templates.py` - PredicateTemplate definitions
- [ ] Simple test environment (GridWorld) for extraction testing
- [ ] Integration tests for observation → predicate conversion

**Deliverable**: Working system that converts observations to predicates

### Phase 2: Statistical Discovery (Weeks 3-4)
**Goal**: Implement and validate statistical pattern mining

#### Week 3: Pattern Mining
- [ ] `discovery/pattern_miner.py` - Complete StatisticalPatternMiner
- [ ] Support for different pattern types (co-occurrence, sequence)
- [ ] Comprehensive unit tests with edge cases
- [ ] Performance optimization and profiling

#### Week 4: Composition and Validation
- [ ] `discovery/composer.py` - PredicateComposer implementation
- [ ] `discovery/validator.py` - Basic HierarchyValidator
- [ ] Integration tests for pattern → predicate pipeline
- [ ] Validation of discovered predicates against known good examples

**Deliverable**: System discovers meaningful composite predicates from statistical patterns

### Phase 3: Neural Components (Weeks 5-7)
**Goal**: Add neural pattern proposal and grounding

#### Week 5: Neural Architecture
- [ ] `discovery/neural_proposer.py` - Basic neural architecture
- [ ] `perception/grounding.py` - SymbolGrounder implementation
- [ ] Training data generation and management
- [ ] Initial neural network training and validation

#### Week 6: Neural Integration
- [ ] Integration of neural proposals with statistical mining
- [ ] Joint training of grounding and proposal networks
- [ ] Hyperparameter tuning and optimization
- [ ] Performance comparison: neural vs. statistical only

#### Week 7: Advanced Neural Features
- [ ] Attention mechanisms for hierarchical reasoning
- [ ] Transfer learning capabilities
- [ ] Advanced composition strategies
- [ ] Ablation studies on neural components

**Deliverable**: Neural components that outperform statistical-only discovery

### Phase 4: RL Integration (Weeks 8-10)
**Goal**: Complete NSRL agent with discovery integration

#### Week 8: Basic RL Agent
- [ ] `learning/agent.py` - NSRLAgent with discovery integration
- [ ] `learning/policy.py` - HierarchicalPolicy implementation
- [ ] `learning/value.py` - HierarchicalValue function
- [ ] Basic RL training loop with predicate discovery

#### Week 9: Dynamic Network Expansion
- [ ] Online integration of discovered predicates
- [ ] Network architecture adaptation
- [ ] Experience replay with hierarchical states
- [ ] Stability and convergence analysis

#### Week 10: Performance Optimization
- [ ] Efficient discovery scheduling
- [ ] Memory management for large hierarchies
- [ ] Parallel discovery and learning
- [ ] Production-ready optimizations

**Deliverable**: Complete NSRL agent that learns and discovers simultaneously

### Phase 5: Evaluation and Validation (Weeks 11-12)
**Goal**: Comprehensive evaluation framework and results

#### Week 11: Evaluation Framework
- [ ] `evaluation/metrics.py` - Complete metrics implementation
- [ ] `evaluation/benchmarks.py` - Standard test environments
- [ ] Automated experiment runner and analysis
- [ ] Statistical significance testing

#### Week 12: Comprehensive Evaluation
- [ ] Ablation studies across all components
- [ ] Transfer learning experiments
- [ ] Scalability analysis
- [ ] Comparison with baselines and prior work

**Deliverable**: Publication-ready experimental results

---

## Evaluation Framework

### Discovery Quality Metrics

#### Structural Metrics
```python
def evaluate_hierarchy_structure(hierarchy: PredicateHierarchy) -> Dict[str, float]:
    """Evaluate structural properties of discovered hierarchy."""
    metrics = {
        "depth": max(hierarchy.levels.keys()) if hierarchy.levels else 0,
        "breadth": np.mean([len(preds) for preds in hierarchy.levels.values()]),
        "compression_ratio": len(hierarchy.levels[0]) / hierarchy.total_predicates(),
        "balance": calculate_hierarchy_balance(hierarchy),
    }
    return metrics
```

#### Semantic Coherence Metrics
```python
def evaluate_semantic_coherence(hierarchy: PredicateHierarchy,
                               ground_truth: Optional[Dict] = None) -> float:
    """
    Measure semantic meaningfulness of discovered compositions.
    
    If ground_truth is provided, compare against known good hierarchies.
    Otherwise, use heuristic measures of semantic coherence.
    """
    if ground_truth:
        return compute_hierarchy_similarity(hierarchy, ground_truth)
    else:
        return compute_intrinsic_coherence(hierarchy)
```

### Performance Improvement Metrics

#### Sample Efficiency
```python
def compute_sample_efficiency_improvement(baseline_rewards: List[float],
                                        discovery_rewards: List[float],
                                        convergence_threshold: float = 0.9) -> Dict[str, float]:
    """
    Compute improvement in sample efficiency due to predicate discovery.
    
    Returns:
        - episodes_to_convergence_improvement: Reduction in episodes needed
        - area_under_curve_improvement: Improvement in cumulative performance
        - final_performance_improvement: Improvement in asymptotic performance
    """
    baseline_convergence = find_convergence_point(baseline_rewards, convergence_threshold)
    discovery_convergence = find_convergence_point(discovery_rewards, convergence_threshold)
    
    return {
        "episodes_to_convergence_improvement": baseline_convergence - discovery_convergence,
        "area_under_curve_improvement": compute_auc_improvement(baseline_rewards, discovery_rewards),
        "final_performance_improvement": np.mean(discovery_rewards[-100:]) - np.mean(baseline_rewards[-100:])
    }
```

#### Transfer Performance
```python
def evaluate_transfer_performance(source_hierarchy: PredicateHierarchy,
                                target_environments: List[gym.Env],
                                num_episodes: int = 100) -> Dict[str, float]:
    """
    Evaluate how well discovered hierarchy transfers to new environments.
    
    Test hierarchy on structurally similar but different environments
    to measure generalization capability.
    """
    transfer_results = {}
    
    for env_name, env in target_environments.items():
        # Test hierarchy on new environment
        agent = NSRLAgent(env.observation_space, env.action_space)
        agent.hierarchy = source_hierarchy  # Use discovered hierarchy
        
        # Run evaluation episodes
        rewards = run_evaluation_episodes(agent, env, num_episodes)
        
        # Compare against baseline (no hierarchy)
        baseline_agent = NSRLAgent(env.observation_space, env.action_space)
        baseline_rewards = run_evaluation_episodes(baseline_agent, env, num_episodes)
        
        transfer_results[env_name] = {
            "performance_improvement": np.mean(rewards) - np.mean(baseline_rewards),
            "success_rate": np.mean(rewards > baseline_performance_threshold),
            "adaptation_speed": compute_adaptation_speed(rewards)
        }
    
    return transfer_results
```

### Experimental Design

#### Baseline Comparisons
1. **No Discovery Baseline**: Flat predicate space, no composition
2. **Hand-Crafted Hierarchy**: Expert-designed predicate hierarchy
3. **Random Composition**: Random predicate combinations as control
4. **Statistical Only**: Pattern mining without neural components
5. **Neural Only**: Neural proposals without statistical mining

#### Ablation Studies
```python
class AblationStudy:
    """Systematic ablation study framework."""
    
    def __init__(self, base_config: ExperimentConfig):
        self.base_config = base_config
        self.ablation_configs = self._generate_ablation_configs()
    
    def run_full_ablation(self) -> Dict[str, ExperimentResults]:
        """Run complete ablation study."""
        results = {}
        
        # Test each component combination
        for config_name, config in self.ablation_configs.items():
            print(f"Running ablation: {config_name}")
            
            agent = NSRLAgent(config)
            results[config_name] = self._run_experiment(agent, config)
        
        return results
    
    def _generate_ablation_configs(self) -> Dict[str, ExperimentConfig]:
        """Generate all ablation configurations."""
        configs = {
            "full_system": self.base_config,
            "no_neural_proposer": self.base_config.copy(neural_proposer=None),
            "no_statistical_miner": self.base_config.copy(statistical_miner=None),
            "no_validation": self.base_config.copy(validator=None),
            "shallow_hierarchy": self.base_config.copy(max_depth=2),
            "frequent_discovery": self.base_config.copy(discovery_frequency=50),
            "rare_discovery": self.base_config.copy(discovery_frequency=500),
        }
        return configs
```

---

## Common Pitfalls and Solutions

### Implementation Pitfalls

#### 1. **Circular Dependencies**
**Problem**: Core modules importing from discovery modules
```python
# ❌ INCORRECT - Creates circular dependency
# In core/hierarchy.py
from discovery.composer import PredicateComposer  # BAD!

class PredicateHierarchy:
    def add_predicate(self, predicate):
        # Using composer in core module
        composer = PredicateComposer()
```

**Solution**: Use dependency injection and clear layering
```python
# ✅ CORRECT - Hierarchy accepts composed predicates
# In core/hierarchy.py
class PredicateHierarchy:
    def add_predicate(self, predicate: Predicate, composition_rule: Optional[CompositionRule] = None):
        # Hierarchy just stores predicates, doesn't create them
        self.levels[predicate.level].add(predicate)
        if composition_rule:
            self.composition_rules[predicate.name] = composition_rule
```

#### 2. **Overly Complex Pattern Matching**
**Problem**: Trying to handle every possible pattern type in one class
```python
# ❌ INCORRECT - Monolithic pattern handling
class PatternMiner:
    def mine_patterns(self, experiences):
        # Handles co-occurrence, sequence, negation, temporal, etc.
        # 500+ lines of complex logic
```

**Solution**: Strategy pattern with specialized miners
```python
# ✅ CORRECT - Focused pattern miners
class CooccurrencePatternMiner(PatternMiner):
    def mine_patterns(self, experiences): 
        # Only handles co-occurrence patterns

class SequentialPatternMiner(PatternMiner):
    def mine_patterns(self, experiences):
        # Only handles sequential patterns

class CompositePatternMiner:
    def __init__(self):
        self.miners = [CooccurrencePatternMiner(), SequentialPatternMiner()]
    
    def mine_patterns(self, experiences):
        all_patterns = []
        for miner in self.miners:
            all_patterns.extend(miner.mine_patterns(experiences))
        return all_patterns
```

#### 3. **Inconsistent State Representation**
**Problem**: Different components using different predicate formats
```python
# ❌ INCORRECT - Inconsistent representations
extractor.extract(obs)  # Returns Set[Predicate]
miner.mine_patterns()   # Expects List[str]  
composer.compose()      # Returns Dict[str, Any]
```

**Solution**: Consistent data contracts throughout pipeline
```python
# ✅ CORRECT - Consistent interfaces
extractor.extract(obs) -> Set[Predicate]
miner.mine_patterns(experiences: List[Experience]) -> List[PredicatePattern]
composer.compose(pattern: PredicatePattern) -> Optional[CompositePredicateResult]
```

### Research Pitfalls

#### 1. **No Clear Baseline**
**Problem**: Can't demonstrate improvement without proper baseline
**Solution**: Always implement flat predicate space baseline first

#### 2. **Hand-Coded Target Patterns**
**Problem**: System only "discovers" pre-specified patterns
```python
# ❌ INCORRECT - Not really discovery
target_patterns = [
    "near(agent, key) AND unlocked(key) -> accessible(key)",
    "path_exists(A, B) AND safe(A, B) -> reachable(A, B)"
]
```

**Solution**: Emergent discovery from statistical/neural analysis
```python
# ✅ CORRECT - Emergent patterns
patterns = miner.discover_frequent_itemsets(experiences)  # Data-driven
proposals = neural_proposer.generate_candidates(context)  # Learned
```

#### 3. **No Performance Integration**
**Problem**: Discovered predicates don't actually help RL performance
**Solution**: Direct integration with policy/value networks and performance measurement

#### 4. **Evaluation on Toy Problems Only**
**Problem**: Only testing on 5x5 grid worlds
**Solution**: Scalability testing and multiple domain evaluation

---

## Research Contribution

### Novel Contributions

1. **Automatic Discovery**: System discovers hierarchical predicates without human specification of target patterns

2. **Neuro-Symbolic Integration**: Combines statistical pattern mining with neural pattern proposal

3. **Online Learning**: Discovery happens during RL training, not as preprocessing step

4. **Performance Validation**: Discovered predicates must demonstrably improve RL performance

5. **Transfer Capability**: Hierarchies discovered in one environment transfer to related environments

### Comparison to Prior Work

#### Traditional Symbolic AI
- **Limitation**: Requires hand-crafted knowledge bases
- **Our Contribution**: Automatic discovery from experience

#### Pure Neural RL
- **Limitation**: Lack of interpretability and transfer
- **Our Contribution**: Interpretable symbolic abstractions that transfer

#### Existing NSRL
- **Limitation**: Pre-specified symbolic knowledge or simple pattern matching
- **Our Contribution**: Sophisticated discovery with neural-statistical fusion

### Publication Strategy

#### Target Venues
- **Primary**: ICML, NeurIPS, ICLR (top-tier ML conferences)
- **Secondary**: AAAI, IJCAI (AI conferences with symbolic reasoning focus)
- **Domain-Specific**: CoRL (if robotics applications), AAMAS (if multi-agent)

#### Paper Structure
1. **Abstract**: Automatic hierarchical predicate discovery in NSRL
2. **Introduction**: Problem motivation and research questions
3. **Related Work**: Symbolic AI, NSRL, representation learning
4. **Method**: Architecture and discovery algorithm
5. **Experiments**: Ablation studies, transfer experiments, performance analysis
6. **Results**: Quantitative improvements and discovered hierarchies
7. **Discussion**: Implications and limitations
8. **Conclusion**: Contributions and future work

#### Key Experimental Results Needed
- **Discovery Quality**: Examples of meaningful discovered predicates
- **Performance Improvement**: Sample efficiency gains (20%+ improvement)
- **Transfer Results**: Performance maintenance across environments (>80% of original performance)
- **Scalability**: Successful discovery in complex environments (>10x10 grids, continuous spaces)
- **Ablation Studies**: Component contribution analysis

---

## Implementation Checklist

### Phase 1 Completion Criteria
- [ ] All core classes pass comprehensive unit tests
- [ ] Basic predicate extraction working on simple grid world
- [ ] Documentation covers all public interfaces
- [ ] Integration tests demonstrate observation → predicate conversion
- [ ] Performance benchmarks established for core operations

### Phase 2 Completion Criteria  
- [ ] Statistical pattern mining discovers known good patterns
- [ ] Composition creates valid hierarchical predicates
- [ ] Validation prevents obviously bad compositions
- [ ] End-to-end pipeline: experiences → discovered predicates
- [ ] Performance analysis shows reasonable computational costs

### Phase 3 Completion Criteria
- [ ] Neural components outperform statistical-only baseline
- [ ] Grounding network accurately evaluates predicate truth
- [ ] Joint training improves both components
- [ ] Neural proposals show semantic coherence
- [ ] Ablation studies demonstrate neural component value

### Phase 4 Completion Criteria
- [ ] Complete NSRL agent trains successfully
- [ ] Dynamic predicate integration maintains learning stability
- [ ] Discovered predicates improve RL performance metrics
- [ ] System scales to moderately complex environments
- [ ] Performance improvements are statistically significant

### Phase 5 Completion Criteria
- [ ] Comprehensive experimental evaluation complete
- [ ] Results demonstrate clear advantages over baselines
- [ ] Transfer experiments show generalization capability
- [ ] Statistical analysis confirms significance of results
- [ ] Paper draft ready for conference submission

---

**Remember**: This is a living document. Update it as the project evolves, but maintain consistency with the core architectural decisions. When in doubt, prioritize simplicity and modularity over premature optimization.

**For Students**: Read this document completely before contributing any code. Every piece of code should align with these principles and standards. When unsure, ask rather than guess.