import re
from typing import Dict, List, Any, Optional
from procedures.loader import procedure_loader

def enrich_response(base_response: Dict[str, Any], query_text: str, domain: str, statutes: List[Dict], jurisdiction: str = "IN") -> Dict[str, Any]:
    """Enrich response with timeline, glossary, and evidence_requirements"""
    
    # Set timeline if not present
    if "timeline" not in base_response:
        base_response["timeline"] = _get_timeline_defaults(domain, jurisdiction)
    
    # Set glossary if not present
    if "glossary" not in base_response:
        base_response["glossary"] = _get_glossary_defaults(statutes)
    
    # Set evidence_requirements if not present
    if "evidence_requirements" not in base_response:
        base_response["evidence_requirements"] = _get_evidence_defaults(domain, jurisdiction)
    
    return base_response

def _get_timeline_defaults(domain: str, jurisdiction: str = "IN") -> List[Dict[str, str]]:
    """Get default timeline based on domain and jurisdiction"""
    # Map jurisdiction codes to country names
    jurisdiction_map = {'IN': 'india', 'UK': 'uk', 'UAE': 'uae', 'KSA': 'ksa'}
    country = jurisdiction_map.get(jurisdiction, 'india').lower()
    
    # Map domain to procedure domain
    domain_map = {'terrorism': 'criminal', 'consumer': 'consumer_commercial'}
    procedure_domain = domain_map.get(domain.lower(), domain.lower())
    
    # Try to get from procedure loader
    procedure = procedure_loader.get_procedure(country, procedure_domain)
    if procedure and "procedure" in procedure and "steps" in procedure["procedure"]:
        steps = procedure["procedure"]["steps"]
        timeline = []
        for i, step in enumerate(steps[:4]):
            timeline.append({
                "step": step.get("title", f"Step {i+1}"),
                "eta": "Varies"
            })
        return timeline
    return []

def _get_glossary_defaults(statutes: List[Dict]) -> List[Dict[str, str]]:
    """Generate glossary from statutes"""
    glossary = []
    seen = set()

    def _add_term(term: str, definition: str) -> None:
        if term in seen:
            return
        glossary.append({"term": term, "definition": definition})
        seen.add(term)
    
    for statute in statutes:
        title = statute.get('title', '') if isinstance(statute, dict) else getattr(statute, 'title', '')
        text = statute.get('text', '') if isinstance(statute, dict) else getattr(statute, 'text', '')
        combined = f"{title} {text}".lower()

        if "murder" in combined:
            _add_term("Murder", "Intentional killing with intent to cause death")
        if "extortion" in combined:
            _add_term("Extortion", "Obtaining property by threat or force")
        if "rape" in combined or "sexual" in combined:
            _add_term("Sexual Assault", "Non-consensual sexual act")
        if "theft" in combined:
            _add_term("Theft", "Dishonestly taking movable property")
        if "fir" in combined:
            _add_term("FIR", "First Information Report filed with police")
        if "charge sheet" in combined or "chargesheet" in combined:
            _add_term("Charge Sheet", "Police report submitted to court after investigation")
    
    return glossary

def _get_evidence_defaults(domain: str, jurisdiction: str = "IN") -> List[str]:
    """Get default evidence requirements based on domain and jurisdiction"""
    # Map jurisdiction codes to country names
    jurisdiction_map = {'IN': 'india', 'UK': 'uk', 'UAE': 'uae', 'KSA': 'ksa'}
    country = jurisdiction_map.get(jurisdiction, 'india').lower()
    
    # Map domain to procedure domain
    domain_map = {'terrorism': 'criminal', 'consumer': 'consumer_commercial'}
    procedure_domain = domain_map.get(domain.lower(), domain.lower())
    
    # Try to get from procedure loader
    procedure = procedure_loader.get_procedure(country, procedure_domain)
    if procedure and "procedure" in procedure and "documents_required" in procedure["procedure"]:
        return procedure["procedure"]["documents_required"]
    return []
