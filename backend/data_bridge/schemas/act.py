"""
Standard Act Object Schema
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Jurisdiction(Enum):
    IN = "IN"
    UK = "UK"
    UAE = "UAE"


@dataclass
class Act:
    """
    Standard normalized Act object schema:
    {
      "act_id": "string",
      "act_name": "string",
      "year": 0,
      "jurisdiction": "IN | UK | UAE",
      "sections": ["section_id"],
      "metadata": {}
    }
    """
    act_id: str
    act_name: str
    year: int
    jurisdiction: Jurisdiction
    sections: List[str]
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.sections is None:
            self.sections = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert Act object to dictionary with standard schema"""
        result = asdict(self)
        result["jurisdiction"] = self.jurisdiction.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Act':
        """Create Act object from dictionary"""
        jurisdiction_str = data.get("jurisdiction", "IN")
        if isinstance(jurisdiction_str, str):
            jurisdiction = Jurisdiction(jurisdiction_str)
        else:
            jurisdiction = jurisdiction_str
            
        return cls(
            act_id=data.get("act_id", ""),
            act_name=data.get("act_name", ""),
            year=data.get("year", 0),
            jurisdiction=jurisdiction,
            sections=data.get("sections", []),
            metadata=data.get("metadata", {})
        )