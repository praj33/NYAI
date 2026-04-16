"""
Standard Case Object Schema
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Jurisdiction(Enum):
    IN = "IN"
    UK = "UK"
    UAE = "UAE"


@dataclass
class Case:
    """
    Standard normalized Case object schema:
    {
      "case_id": "string",
      "title": "string",
      "court": "string",
      "jurisdiction": "IN | UK | UAE",
      "citations": [],
      "summary": "string",
      "referenced_sections": ["section_id"],
      "metadata": {}
    }
    """
    case_id: str
    title: str
    court: str
    jurisdiction: Jurisdiction
    citations: List[str]
    summary: str
    referenced_sections: List[str]
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.citations is None:
            self.citations = []
        if self.referenced_sections is None:
            self.referenced_sections = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert Case object to dictionary with standard schema"""
        result = asdict(self)
        result["jurisdiction"] = self.jurisdiction.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Case':
        """Create Case object from dictionary"""
        jurisdiction_str = data.get("jurisdiction", "IN")
        if isinstance(jurisdiction_str, str):
            jurisdiction = Jurisdiction(jurisdiction_str)
        else:
            jurisdiction = jurisdiction_str
            
        return cls(
            case_id=data.get("case_id", ""),
            title=data.get("title", ""),
            court=data.get("court", ""),
            jurisdiction=jurisdiction,
            citations=data.get("citations", []),
            summary=data.get("summary", ""),
            referenced_sections=data.get("referenced_sections", []),
            metadata=data.get("metadata", {})
        )