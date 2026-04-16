"""
JSON schema & integrity validator for legal datasets
"""
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from .schemas.section import Section
from .schemas.act import Act
from .schemas.case import Case


@dataclass
class ValidationError:
    """Represents a validation error with structured information"""
    field: str
    error_type: str
    message: str
    value: Any = None
    path: Optional[str] = None


class JSONValidator:
    """Validates JSON datasets against required schemas and integrity rules"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
    
    def validate_section(self, section_data: Dict[str, Any], path: str = "") -> bool:
        """Validate a section object against the standard schema"""
        self.errors = []
        required_fields = ["section_id", "section_number", "text", "act_id", "jurisdiction"]
        
        # Check required fields
        for field in required_fields:
            if field not in section_data:
                self.errors.append(ValidationError(
                    field=field,
                    error_type="MISSING_FIELD",
                    message=f"Required field '{field}' is missing",
                    path=path
                ))
        
        # Validate data types
        if "section_id" in section_data and not isinstance(section_data["section_id"], str):
            self.errors.append(ValidationError(
                field="section_id",
                error_type="INVALID_TYPE",
                message="section_id must be a string",
                value=section_data["section_id"],
                path=path
            ))
        
        if "section_number" in section_data and not isinstance(section_data["section_number"], str):
            self.errors.append(ValidationError(
                field="section_number",
                error_type="INVALID_TYPE",
                message="section_number must be a string",
                value=section_data["section_number"],
                path=path
            ))
        
        if "text" in section_data and not isinstance(section_data["text"], str):
            self.errors.append(ValidationError(
                field="text",
                error_type="INVALID_TYPE",
                message="text must be a string",
                value=section_data["text"],
                path=path
            ))
        
        if "act_id" in section_data and not isinstance(section_data["act_id"], str):
            self.errors.append(ValidationError(
                field="act_id",
                error_type="INVALID_TYPE",
                message="act_id must be a string",
                value=section_data["act_id"],
                path=path
            ))
        
        if "jurisdiction" in section_data:
            if not isinstance(section_data["jurisdiction"], str) or \
               section_data["jurisdiction"] not in ["IN", "UK", "UAE"]:
                self.errors.append(ValidationError(
                    field="jurisdiction",
                    error_type="INVALID_TYPE",
                    message="jurisdiction must be one of: IN, UK, UAE",
                    value=section_data["jurisdiction"],
                    path=path
                ))
        
        return len(self.errors) == 0
    
    def validate_act(self, act_data: Dict[str, Any], path: str = "") -> bool:
        """Validate an act object against the standard schema"""
        self.errors = []
        required_fields = ["act_id", "act_name", "year", "jurisdiction", "sections"]
        
        # Check required fields
        for field in required_fields:
            if field not in act_data:
                self.errors.append(ValidationError(
                    field=field,
                    error_type="MISSING_FIELD",
                    message=f"Required field '{field}' is missing",
                    path=path
                ))
        
        # Validate data types
        if "act_id" in act_data and not isinstance(act_data["act_id"], str):
            self.errors.append(ValidationError(
                field="act_id",
                error_type="INVALID_TYPE",
                message="act_id must be a string",
                value=act_data["act_id"],
                path=path
            ))
        
        if "act_name" in act_data and not isinstance(act_data["act_name"], str):
            self.errors.append(ValidationError(
                field="act_name",
                error_type="INVALID_TYPE",
                message="act_name must be a string",
                value=act_data["act_name"],
                path=path
            ))
        
        if "year" in act_data and not isinstance(act_data["year"], int):
            self.errors.append(ValidationError(
                field="year",
                error_type="INVALID_TYPE",
                message="year must be an integer",
                value=act_data["year"],
                path=path
            ))
        
        if "jurisdiction" in act_data:
            if not isinstance(act_data["jurisdiction"], str) or \
               act_data["jurisdiction"] not in ["IN", "UK", "UAE"]:
                self.errors.append(ValidationError(
                    field="jurisdiction",
                    error_type="INVALID_TYPE",
                    message="jurisdiction must be one of: IN, UK, UAE",
                    value=act_data["jurisdiction"],
                    path=path
                ))
        
        if "sections" in act_data and not isinstance(act_data["sections"], list):
            self.errors.append(ValidationError(
                field="sections",
                error_type="INVALID_TYPE",
                message="sections must be a list",
                value=act_data["sections"],
                path=path
            ))
        
        return len(self.errors) == 0
    
    def validate_case(self, case_data: Dict[str, Any], path: str = "") -> bool:
        """Validate a case object against the standard schema"""
        self.errors = []
        required_fields = ["case_id", "title", "court", "jurisdiction", "citations", "summary", "referenced_sections"]
        
        # Check required fields
        for field in required_fields:
            if field not in case_data:
                self.errors.append(ValidationError(
                    field=field,
                    error_type="MISSING_FIELD",
                    message=f"Required field '{field}' is missing",
                    path=path
                ))
        
        # Validate data types
        if "case_id" in case_data and not isinstance(case_data["case_id"], str):
            self.errors.append(ValidationError(
                field="case_id",
                error_type="INVALID_TYPE",
                message="case_id must be a string",
                value=case_data["case_id"],
                path=path
            ))
        
        if "title" in case_data and not isinstance(case_data["title"], str):
            self.errors.append(ValidationError(
                field="title",
                error_type="INVALID_TYPE",
                message="title must be a string",
                value=case_data["title"],
                path=path
            ))
        
        if "court" in case_data and not isinstance(case_data["court"], str):
            self.errors.append(ValidationError(
                field="court",
                error_type="INVALID_TYPE",
                message="court must be a string",
                value=case_data["court"],
                path=path
            ))
        
        if "jurisdiction" in case_data:
            if not isinstance(case_data["jurisdiction"], str) or \
               case_data["jurisdiction"] not in ["IN", "UK", "UAE"]:
                self.errors.append(ValidationError(
                    field="jurisdiction",
                    error_type="INVALID_TYPE",
                    message="jurisdiction must be one of: IN, UK, UAE",
                    value=case_data["jurisdiction"],
                    path=path
                ))
        
        if "citations" in case_data and not isinstance(case_data["citations"], list):
            self.errors.append(ValidationError(
                field="citations",
                error_type="INVALID_TYPE",
                message="citations must be a list",
                value=case_data["citations"],
                path=path
            ))
        
        if "summary" in case_data and not isinstance(case_data["summary"], str):
            self.errors.append(ValidationError(
                field="summary",
                error_type="INVALID_TYPE",
                message="summary must be a string",
                value=case_data["summary"],
                path=path
            ))
        
        if "referenced_sections" in case_data and not isinstance(case_data["referenced_sections"], list):
            self.errors.append(ValidationError(
                field="referenced_sections",
                error_type="INVALID_TYPE",
                message="referenced_sections must be a list",
                value=case_data["referenced_sections"],
                path=path
            ))
        
        return len(self.errors) == 0
    
    def validate_referential_integrity(self, sections: List[Section], acts: List[Act], cases: List[Case]) -> List[ValidationError]:
        """Validate referential integrity between different objects"""
        errors = []
        
        # Check that sections reference valid acts
        for section in sections:
            act_exists = any(act.act_id == section.act_id for act in acts)
            if not act_exists:
                errors.append(ValidationError(
                    field="act_id",
                    error_type="INVALID_REFERENCE",
                    message=f"Section {section.section_id} references non-existent act {section.act_id}",
                    value=section.act_id
                ))
        
        # Check that cases reference valid sections
        for case in cases:
            for section_id in case.referenced_sections:
                section_exists = any(section.section_id == section_id for section in sections)
                if not section_exists:
                    errors.append(ValidationError(
                        field="referenced_sections",
                        error_type="INVALID_REFERENCE",
                        message=f"Case {case.case_id} references non-existent section {section_id}",
                        value=section_id
                    ))
        
        return errors
    
    def validate_duplicate_ids(self, sections: List[Section], acts: List[Act], cases: List[Case]) -> List[ValidationError]:
        """Detect duplicate IDs within each entity type"""
        errors = []
        
        # Check for duplicate section IDs
        section_ids = [s.section_id for s in sections]
        unique_section_ids = set()
        for section_id in section_ids:
            if section_id in unique_section_ids:
                errors.append(ValidationError(
                    field="section_id",
                    error_type="DUPLICATE_ID",
                    message=f"Duplicate section ID found: {section_id}",
                    value=section_id
                ))
            else:
                unique_section_ids.add(section_id)
        
        # Check for duplicate act IDs
        act_ids = [a.act_id for a in acts]
        unique_act_ids = set()
        for act_id in act_ids:
            if act_id in unique_act_ids:
                errors.append(ValidationError(
                    field="act_id",
                    error_type="DUPLICATE_ID",
                    message=f"Duplicate act ID found: {act_id}",
                    value=act_id
                ))
            else:
                unique_act_ids.add(act_id)
        
        # Check for duplicate case IDs
        case_ids = [c.case_id for c in cases]
        unique_case_ids = set()
        for case_id in case_ids:
            if case_id in unique_case_ids:
                errors.append(ValidationError(
                    field="case_id",
                    error_type="DUPLICATE_ID",
                    message=f"Duplicate case ID found: {case_id}",
                    value=case_id
                ))
            else:
                unique_case_ids.add(case_id)
        
        return errors
    
    def get_validation_errors(self) -> List[ValidationError]:
        """Return the list of validation errors from the last validation"""
        return self.errors.copy()