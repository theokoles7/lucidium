# NSRL Hierarchical Predicate Discovery - Clean Architecture

## Project Structure
```
nsrl_discovery/
├── core/
│   ├── __init__.py
│   ├── predicate.py          # Basic Predicate class
│   ├── experience.py         # Experience data structure
│   └── hierarchy.py          # PredicateHierarchy manager
├── perception/
│   ├── __init__.py
│   ├── extractor.py          # BasicPredicateExtractor
│   └── grounding.py          # SymbolGrounder
├── discovery/
│   ├── __init__.py
│   ├── pattern_miner.py      # StatisticalPatternMiner
│   ├── neural_proposer.py    # NeuralPatternProposer
│   ├── composer.py           # PredicateComposer
│   └── validator.py          # HierarchyValidator
├── learning/
│   ├── __init__.py
│   ├── agent.py              # NSRLAgent
│   ├── policy.py             # HierarchicalPolicy
│   └── value.py              # HierarchicalValue
├── evaluation/
│   ├── __init__.py
│   ├── metrics.py            # Discovery & Performance metrics
│   └── benchmarks.py         # Standard test environments
└── experiments/
    ├── __init__.py
    ├── runner.py             # ExperimentRunner
    └── configs/              # Experiment configurations
```

## Core Data Flow

```
Raw Observations → BasicPredicateExtractor → Predicate Set
                                                    ↓
Experience Buffer ← NSRLAgent ← HierarchicalPolicy ← PredicateHierarchy
       ↓                                                    ↑
StatisticalPatternMiner → NeuralPatternProposer → PredicateComposer
                                                           ↓
                                              HierarchyValidator
```

---

## Component Specifications

### 1. Core Components

#### `core/predicate.py`
```python
@dataclass(frozen=True)
class Predicate:
    """Atomic symbolic predicate"""
    name: str
    args: Tuple[str, ...]
    confidence: float = 1.0
    level: int = 0  # Hierarchy level (0=basic, 1+=composite)
    
    def ground(self, bindings: Dict[str, str]) -> 'Predicate': ...
    def matches_pattern(self, pattern: str) -> bool: ...
```

#### `core/experience.py`
```python
@dataclass
class Experience:
    """Single environment interaction"""
    obs: np.ndarray                    # Raw observation
    predicates: Set[Predicate]         # Extracted symbolic state
    action: int                        # Action taken
    reward: float                      # Immediate reward
    next_obs: np.ndarray              # Next observation
    next_predicates: Set[Predicate]    # Next symbolic state
    done: bool                         # Episode termination
    
class ExperienceBuffer:
    """Manages experience storage and retrieval"""
    def add(self, experience: Experience) -> None: ...
    def sample(self, batch_size: int) -> List[Experience]: ...
    def get_recent(self, n: int) -> List[Experience]: ...
```

#### `core/hierarchy.py`
```python
class PredicateHierarchy:
    """Manages the discovered predicate hierarchy"""
    def __init__(self):
        self.levels: Dict[int, Set[Predicate]] = defaultdict(set)
        self.composition_rules: Dict[str, CompositionRule] = {}
    
    def add_predicate(self, predicate: Predicate, level: int) -> None: ...
    def get_active_predicates(self, level: int = None) -> Set[Predicate]: ...
    def evaluate_state(self, obs: np.ndarray) -> Set[Predicate]: ...
```

### 2. Perception Components

#### `perception/extractor.py`
```python
class BasicPredicateExtractor:
    """Converts raw observations to basic symbolic predicates"""
    def __init__(self, predicate_vocab: Dict[str, PredicateTemplate]):
        self.vocab = predicate_vocab
        self.extractors = self._build_extractors()
    
    def extract(self, obs: np.ndarray) -> Set[Predicate]:
        """Extract basic predicates from observation"""
        predicates = set()
        for name, extractor_fn in self.extractors.items():
            if extractor_fn(obs):
                predicates.add(Predicate(name, self._get_args(obs, name)))
        return predicates
    
    def _build_extractors(self) -> Dict[str, Callable]: ...
```

#### `perception/grounding.py`
```python
class SymbolGrounder:
    """Grounds symbolic predicates in neural representations"""
    def __init__(self):
        self.grounding_network = self._build_network()
    
    def ground_predicate(self, predicate: Predicate, obs: np.ndarray) -> float:
        """Return confidence that predicate holds in observation"""
        return self.grounding_network(predicate.to_vector(), obs)
    
    def update_grounding(self, experiences: List[Experience]) -> None: ...
```

### 3. Discovery Components

#### `discovery/pattern_miner.py`
```python
class StatisticalPatternMiner:
    """Mines frequent predicate co-occurrence patterns"""
    def __init__(self, min_support: float = 0.1, min_confidence: float = 0.7):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.pattern_counts = defaultdict(int)
    
    def mine_patterns(self, experiences: List[Experience]) -> List[PredicatePattern]:
        """Find statistically significant predicate patterns"""
        # Count co-occurrences
        for exp in experiences:
            for combo in self._get_combinations(exp.predicates):
                self.pattern_counts[combo] += 1
        
        # Filter by support/confidence
        return self._filter_patterns()
    
    def _get_combinations(self, predicates: Set[Predicate]) -> List[Tuple]: ...
    def _filter_patterns(self) -> List[PredicatePattern]: ...
```

#### `discovery/neural_proposer.py`
```python
class NeuralPatternProposer:
    """Neural network that proposes candidate compositions"""
    def __init__(self, embedding_dim: int = 64):
        self.predicate_encoder = PredicateEncoder(embedding_dim)
        self.pattern_decoder = PatternDecoder(embedding_dim)
        self.value_network = CompositionValueNetwork()
    
    def propose_compositions(self, 
                           context_predicates: Set[Predicate],
                           experience_buffer: ExperienceBuffer) -> List[CandidateComposition]:
        """Propose promising predicate compositions"""
        # Encode current predicate context
        context_embedding = self.predicate_encoder(context_predicates)
        
        # Generate candidate compositions
        candidates = self.pattern_decoder(context_embedding)
        
        # Score candidates by predicted utility
        scored_candidates = []
        for candidate in candidates:
            utility = self.value_network(candidate, context_embedding)
            scored_candidates.append(CandidateComposition(candidate, utility))
        
        return sorted(scored_candidates, key=lambda x: x.utility, reverse=True)
    
    def update(self, successful_compositions: List[CompositionOutcome]) -> None: ...
```

#### `discovery/composer.py`
```python
class PredicateComposer:
    """Composes basic predicates into hierarchical structures"""
    def __init__(self):
        self.composition_templates = self._load_templates()
    
    def compose(self, pattern: PredicatePattern) -> Optional[Predicate]:
        """Create composite predicate from pattern"""
        if not self._validate_pattern(pattern):
            return None
        
        # Determine composition type (AND, OR, SEQUENCE, etc.)
        comp_type = self._infer_composition_type(pattern)
        
        # Create composite predicate
        composite = Predicate(
            name=self._generate_name(pattern),
            args=self._merge_args(pattern.predicates),
            level=max(p.level for p in pattern.predicates) + 1
        )
        
        return composite
    
    def _validate_pattern(self, pattern: PredicatePattern) -> bool: ...
    def _infer_composition_type(self, pattern: PredicatePattern) -> CompositionType: ...
```

#### `discovery/validator.py`
```python
class HierarchyValidator:
    """Validates discovered predicates and manages hierarchy quality"""
    def __init__(self, max_hierarchy_depth: int = 5):
        self.max_depth = max_hierarchy_depth
        self.validation_metrics = ValidationMetrics()
    
    def validate_composition(self, 
                           composite: Predicate,
                           supporting_evidence: List[Experience]) -> ValidationResult:
        """Validate that a composite predicate is useful"""
        
        # Check logical consistency
        if not self._check_logical_consistency(composite):
            return ValidationResult(False, "Logical inconsistency")
        
        # Check hierarchy depth
        if composite.level > self.max_depth:
            return ValidationResult(False, "Exceeds max depth")
        
        # Check empirical utility
        utility_score = self._compute_utility(composite, supporting_evidence)
        if utility_score < 0.1:  # Configurable threshold
            return ValidationResult(False, f"Low utility: {utility_score}")
        
        return ValidationResult(True, f"Valid (utility: {utility_score})")
    
    def _check_logical_consistency(self, predicate: Predicate) -> bool: ...
    def _compute_utility(self, predicate: Predicate, evidence: List[Experience]) -> float: ...
```

### 4. Learning Components

#### `learning/agent.py`
```python
class NSRLAgent:
    """Main RL agent with hierarchical predicate discovery"""
    def __init__(self, 
                 obs_space: gym.Space,
                 action_space: gym.Space,
                 discovery_freq: int = 100):
        
        self.extractor = BasicPredicateExtractor()
        self.hierarchy = PredicateHierarchy()
        self.policy = HierarchicalPolicy(action_space)
        self.value_fn = HierarchicalValue()
        
        # Discovery components
        self.pattern_miner = StatisticalPatternMiner()
        self.neural_proposer = NeuralPatternProposer()
        self.composer = PredicateComposer()
        self.validator = HierarchyValidator()
        
        self.experience_buffer = ExperienceBuffer()
        self.discovery_freq = discovery_freq
        self.steps = 0
    
    def act(self, obs: np.ndarray) -> int:
        """Select action based on hierarchical predicate state"""
        predicates = self.hierarchy.evaluate_state(obs)
        return self.policy.select_action(predicates)
    
    def update(self, experience: Experience) -> None:
        """Update agent with new experience"""
        self.experience_buffer.add(experience)
        
        # Update policy/value networks
        self._update_networks()
        
        # Periodic predicate discovery
        if self.steps % self.discovery_freq == 0:
            self._discover_predicates()
        
        self.steps += 1
    
    def _discover_predicates(self) -> None:
        """Run predicate discovery pipeline"""
        recent_experiences = self.experience_buffer.get_recent(1000)
        
        # 1. Mine statistical patterns
        statistical_patterns = self.pattern_miner.mine_patterns(recent_experiences)
        
        # 2. Generate neural proposals
        neural_proposals = self.neural_proposer.propose_compositions(
            self.hierarchy.get_active_predicates(),
            self.experience_buffer
        )
        
        # 3. Combine and compose
        all_candidates = statistical_patterns + [p.pattern for p in neural_proposals]
        for pattern in all_candidates:
            composite = self.composer.compose(pattern)
            if composite:
                # 4. Validate
                validation = self.validator.validate_composition(composite, recent_experiences)
                if validation.valid:
                    self.hierarchy.add_predicate(composite, composite.level)
                    self._expand_networks(composite)
```

#### `learning/policy.py`
```python
class HierarchicalPolicy:
    """Policy network that operates on hierarchical predicate space"""
    def __init__(self, action_space: gym.Space):
        self.action_space = action_space
        self.networks = {}  # One network per hierarchy level
        self.attention = HierarchyAttention()
    
    def select_action(self, predicates: Set[Predicate]) -> int:
        """Select action using hierarchical predicate representation"""
        # Group predicates by level
        by_level = self._group_by_level(predicates)
        
        # Compute attention weights across levels
        attention_weights = self.attention(by_level)
        
        # Weighted combination of level-specific policies
        action_logits = self._combine_policies(by_level, attention_weights)
        
        return self._sample_action(action_logits)
    
    def update(self, experiences: List[Experience]) -> None: ...
    def expand_for_predicate(self, new_predicate: Predicate) -> None: ...
```

### 5. Evaluation Components

#### `evaluation/metrics.py`
```python
class DiscoveryMetrics:
    """Metrics for evaluating predicate discovery quality"""
    
    @staticmethod
    def hierarchy_depth(hierarchy: PredicateHierarchy) -> int:
        """Maximum depth of discovered hierarchy"""
        return max(hierarchy.levels.keys()) if hierarchy.levels else 0
    
    @staticmethod
    def compression_ratio(hierarchy: PredicateHierarchy) -> float:
        """Ratio of basic to total predicates"""
        basic_count = len(hierarchy.levels[0])
        total_count = sum(len(preds) for preds in hierarchy.levels.values())
        return basic_count / total_count if total_count > 0 else 0
    
    @staticmethod
    def semantic_coherence(hierarchy: PredicateHierarchy, 
                          ground_truth: Optional[Dict] = None) -> float:
        """Measure semantic coherence of hierarchy"""
        # Implementation depends on domain and ground truth availability
        pass
    
    @staticmethod
    def transfer_utility(source_hierarchy: PredicateHierarchy,
                        target_env: gym.Env) -> float:
        """Measure how well hierarchy transfers to new environment"""
        pass

class PerformanceMetrics:
    """Metrics for evaluating RL performance improvements"""
    
    @staticmethod
    def sample_efficiency(learning_curves: List[float]) -> float: ...
    
    @staticmethod
    def final_performance(rewards: List[float]) -> float: ...
    
    @staticmethod
    def convergence_speed(learning_curves: List[float]) -> int: ...
```

### 6. Experiment Runner

#### `experiments/runner.py`
```python
class ExperimentRunner:
    """Orchestrates experiments and comparisons"""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.results = ExperimentResults()
    
    def run_ablation_study(self) -> Dict[str, Any]:
        """Run ablation study comparing different components"""
        results = {}
        
        # Baseline: No hierarchy discovery
        results['baseline'] = self._run_baseline()
        
        # Statistical mining only
        results['statistical_only'] = self._run_with_statistical_mining()
        
        # Neural proposals only  
        results['neural_only'] = self._run_with_neural_proposals()
        
        # Full system
        results['full_system'] = self._run_full_system()
        
        return results
    
    def run_transfer_experiment(self, 
                               source_envs: List[gym.Env],
                               target_envs: List[gym.Env]) -> Dict[str, Any]:
        """Test predicate hierarchy transfer across environments"""
        pass
    
    def run_scalability_test(self, env_sizes: List[int]) -> Dict[str, Any]:
        """Test how discovery scales with environment complexity"""
        pass
```

---

## Key Architectural Principles

### 1. **Single Responsibility**
- Each class has one clear purpose
- Easy to test in isolation
- Simple to modify/extend

### 2. **Clear Data Flow**
- Observations → Predicates → Patterns → Compositions → Validation → Integration
- Each step is explicit and debuggable

### 3. **Modular Discovery Pipeline**
- Statistical and neural components are separate
- Can easily swap different discovery algorithms
- Clear interfaces between components

### 4. **Separation of Concerns**
- Perception: Raw obs → symbols
- Discovery: Pattern mining + composition
- Learning: RL with hierarchical states
- Evaluation: Metrics and benchmarks

### 5. **Testability**
- Each component can be unit tested
- Mock interfaces for integration testing
- Clear success/failure criteria

This architecture maintains your preference for modularity while ensuring each file has a single, clear responsibility. The big picture is the discovery pipeline, but each component is focused and maintainable.