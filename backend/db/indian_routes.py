import json
import re
from typing import Dict, List, Tuple

class IndianRoutes:
    def __init__(self, dataset_path: str = "indian_law_dataset.json", domain_map_path: str = "indian_domain_map.json"):
        with open(dataset_path, 'r') as f:
            self.dataset = json.load(f)
        with open(domain_map_path, 'r') as f:
            self.domain_map = json.load(f)

    def detect_jurisdiction(self, query: str) -> Tuple[str, float]:
        """Detect if query relates to Indian jurisdiction"""
        indian_keywords = [
            r'\bindia\b', r'\bindian\b', r'\bipc\b', r'\bcrpc\b', r'\bbns\b',
            r'\bdelhi\b', r'\bmumbai\b', r'\bbangalore\b', r'\bchennai\b',
            r'\bindian law\b', r'\bhindu law\b', r'\bmuslim law\b'
        ]
        score = 0
        for pattern in indian_keywords:
            if re.search(pattern, query.lower()):
                score += 0.2
        return "India", min(score, 1.0)

    def classify_domain(self, query: str) -> Tuple[str, str, float]:
        """Classify query into domain and subdomain"""
        query_lower = query.lower()

        # Check criminal keywords
        for subdomain, keywords in self.domain_map["keyword_mapping"].items():
            matching_keywords = [k for k in keywords if k in query_lower]
            if matching_keywords:
                domain = "criminal" if subdomain in self.domain_map["domain_mapping"]["criminal"]["subdomains"] else "civil"
                confidence = 0.9 if len(matching_keywords) > 1 else 0.7
                return domain, subdomain, confidence

        # Default fallback
        return "civil", "contract_disputes", 0.5

    def get_legal_info(self, domain: str, subdomain: str) -> Dict:
        """Retrieve relevant legal information"""
        if domain == "criminal":
            # Map subdomains to relevant offence types
            offence_mapping = {
                "violent_crimes": ["criminal_force", "causing_hurt", "grievous_hurt", "assault"],
                "sexual_offences": ["rape", "outraging_modesty"],
                "property_crimes": ["theft", "robbery", "criminal_misappropriation"],
                "fraud_and_deception": ["cheating", "criminal_breach_of_trust", "forgery"],
                "cyber_crimes": ["unauthorized_access"],
                "procedural_matters": ["criminal_force"]  # fallback
            }
            relevant_offences = offence_mapping.get(subdomain, ["criminal_force"])
            for offence in relevant_offences:
                if offence in self.dataset["bns_sections"]:
                    return self.dataset["bns_sections"][offence]
        elif domain == "civil":
            # Map subdomains to relevant civil areas
            civil_mapping = {
                "contract_disputes": ["contract_breach"],
                "arbitration_matters": ["arbitration_matters"],
                "property_disputes": ["property_disputes"],
                "family_matters": ["family_matters", "divorce_and_matrimonial_disputes"],
                "tort_law": ["defamation_civil"]
            }
            relevant_areas = civil_mapping.get(subdomain, ["contract_breach"])
            for area in relevant_areas:
                if area in self.dataset["civil_law"]:
                    return self.dataset["civil_law"][area]

        return {"error": "No matching legal information found"}

    def route_query(self, query: str) -> Dict:
        """Main routing function"""
        jurisdiction, jur_confidence = self.detect_jurisdiction(query)
        domain, subdomain, dom_confidence = self.classify_domain(query)
        legal_info = self.get_legal_info(domain, subdomain)

        return {
            "jurisdiction": jurisdiction,
            "jurisdiction_confidence": jur_confidence,
            "domain": domain,
            "subdomain": subdomain,
            "domain_confidence": dom_confidence,
            "legal_basis": legal_info,
            "process_steps": legal_info.get("process_steps", []),
            "remedies": legal_info.get("civil_remedies", legal_info.get("punishment", "N/A"))
        }

# Example usage
if __name__ == "__main__":
    routes = IndianRoutes()
    result = routes.route_query("I was cheated in a business deal in Mumbai")
    print(json.dumps(result, indent=2))