"""
Standard Section Object Schema
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Jurisdiction(Enum):
    IN = "IN"
    UK = "UK"
    UAE = "UAE"


@dataclass
class Section:
    """
    Standard normalized Section object schema:
    {
      "section_id": "string",
      "section_number": "string", 
      "text": "string",
      "act_id": "string",
      "jurisdiction": "IN | UK | UAE",
      "metadata": {}
    }
    """
    section_id: str
    section_number: str
    text: str
    act_id: str
    jurisdiction: Jurisdiction
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert Section object to dictionary with standard schema"""
        result = asdict(self)
        result["jurisdiction"] = self.jurisdiction.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Section':
        """Create Section object from dictionary"""
        jurisdiction_str = data.get("jurisdiction", "IN")
        if isinstance(jurisdiction_str, str):
            jurisdiction = Jurisdiction(jurisdiction_str)
        else:
            jurisdiction = jurisdiction_str
            
        return cls(
            section_id=data.get("section_id", ""),
            section_number=data.get("section_number", ""),
            text=data.get("text", ""),
            act_id=data.get("act_id", ""),
            jurisdiction=jurisdiction,
            metadata=data.get("metadata", {})
        )