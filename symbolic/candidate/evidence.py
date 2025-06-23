"""# lucidium.symbolic.candidate.Evidence

Manage evidence collection and storage for composition candidates.
"""

from typing import Any, Dict, List

class Evidence():
    """# Evidence (Manager).
    
    Manages the collection and storage of evidence for composition candidates.
    
    Tracks both positive evidence (when patterns hold and lead to good outcomes) and negative 
    evidence (when patterns fail or mislead).
    """
    
    def __init__(self):
        """# Instantiate Evidence Manager."""
        # Initialize instance lists.
        self._positive_instances_:  List[Dict[str, Any]] =  []
        self._negative_instances_:  List[Dict[str, Any]] =  []
        
        
    # PROPERTIES ===================================================================================
    
    @property
    def negative_instances(self) -> List[Dict[str, Any]]:
        """# Negative Instances.

        ## Returns:
            * List[Dict[str, Any]]: List of negative evidence towards candidate.
        """
        return self._negative_instances_
    
    @property
    def positive_instances(self) -> List[Dict[str, Any]]:
        """# Positive Instances.

        ## Returns:
            * List[Dict[str, Any]]: List of positive evidence towards candidate.
        """
        return self._positive_instances_
    
    @property
    def summary(self) -> Dict[str, Any]:
        """# Summary.

        ## Returns:
            * Dict[str, Any]:   Summary statistics about collected evidence.
        """
        return  {
                    "negative":         len(self.negative_instances),
                    "negative_ratio":   (
                                            len(self.negative_instances) / self.total_evidence_count
                                            if self.total_evidence_count > 0
                                            else 0.0
                                        ),
                    "positive":         len(self.positive_instances),
                    "positive_ratio":   (
                                            len(self.positive_instances) / self.total_evidence_count
                                            if self.total_evidence_count > 0
                                            else 0.0
                                        ),
                    "total":            self.total_evidence_count
                }
    
    @property
    def total_evidence_count(self) -> int:
        """# Total Evidence Count.

        ## Returns:
            * int:  Total of negative + positive evidence.
        """
        return len(self.negative_instances) + len(self.positive_instances)
    
        
    # METHODS ======================================================================================
        
    def add_negative_instance(self,
        instance:   Dict[str, Any]
    ) -> None:
        """# Add Negative Instance.
        
        Negative evidence comes from situations where:
            * The component predicates were true but the outcome was poor.
            * The composition would have led to incorrect decisions.
            * The pattern appeared spurious or misleading.

        ## Args:
            * instance  (Dict[str, Any]):   Dictionary containing evidence data.
        """
        self._negative_instances_.append(instance)
        
    def add_positive_instance(self,
        instance:   Dict[str, Any]
    ) -> None:
        """# Add Positive Instance.
        
        Positive evidence comes from situations where:
            * The component predicates were all true.
            * The resulting action/outcome was successful.
            * The composition would have been useful for decision-making.

        ## Args:
            * instance  (Dict[str, Any]):   Dictionary containing evidence data.
        """
        self._positive_instances_.append(instance)