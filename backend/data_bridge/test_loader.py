"""
Test script for the JSON data bridge
"""
import os
import sys
from pathlib import Path

# Add the project root to the path so we can import from data_bridge
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data_bridge.loader import JSONLoader
from data_bridge.validator import JSONValidator


def test_data_bridge():
    """Test the data bridge with existing JSON datasets"""
    print("Testing JSON Data Bridge...")
    
    # Initialize the loader
    loader = JSONLoader(input_directory="db")
    validator = JSONValidator()
    
    print("\n1. Loading and normalizing all JSON files in db/ directory...")
    
    # Load and normalize all JSON files
    sections, acts, cases = loader.load_and_normalize_directory()
    
    print(f"Loaded {len(sections)} sections")
    print(f"Loaded {len(acts)} acts") 
    print(f"Loaded {len(cases)} cases")
    
    print("\n2. Validating referential integrity...")
    
    # Validate referential integrity
    integrity_errors = validator.validate_referential_integrity(sections, acts, cases)
    if integrity_errors:
        print(f"Found {len(integrity_errors)} referential integrity errors:")
        # Show first 10 errors to see the pattern
        for error in integrity_errors[:10]:  
            print(f"  - {error.message}")
    else:
        print("✓ No referential integrity errors found")
    
    print("\n3. Checking for duplicate IDs...")
    
    # Check for duplicate IDs
    duplicate_errors = validator.validate_duplicate_ids(sections, acts, cases)
    if duplicate_errors:
        print(f"Found {len(duplicate_errors)} duplicate ID errors:")
        for error in duplicate_errors[:5]:  # Show first 5 errors
            print(f"  - {error.message}")
    else:
        print("✓ No duplicate ID errors found")
    
    print("\n4. Sample of normalized data...")
    
    # Show a sample of normalized sections
    print("\nSample sections (first 3):")
    for i, section in enumerate(sections[:3]):
        print(f"  {i+1}. ID: {section.section_id}, Number: {section.section_number}, "
              f"Act: {section.act_id}, Jurisdiction: {section.jurisdiction.value}")
        if section.metadata:
            print(f"     Metadata keys: {list(section.metadata.keys())}")
    
    # Show a sample of normalized acts
    print("\nSample acts (first 3):")
    for i, act in enumerate(acts[:3]):
        print(f"  {i+1}. ID: {act.act_id}, Name: {act.act_name}, "
              f"Year: {act.year}, Jurisdiction: {act.jurisdiction.value}")
        print(f"     Sections: {len(act.sections)} referenced")
        if act.metadata:
            print(f"     Metadata keys: {list(act.metadata.keys())}")
    
    # Show a sample of normalized cases (if any)
    if cases:
        print("\nSample cases (first 3):")
        for i, case in enumerate(cases[:3]):
            print(f"  {i+1}. ID: {case.case_id}, Title: {case.title}, "
                  f"Court: {case.court}, Jurisdiction: {case.jurisdiction.value}")
            if case.metadata:
                print(f"     Metadata keys: {list(case.metadata.keys())}")
    else:
        print("\nNo cases found in the datasets")
    
    print("\n5. Testing embedding-ready text extraction...")
    
    # Test embedding-ready text extraction
    embedding_texts = loader.get_all_embedding_texts(sections, acts, cases)
    print(f"Generated {len(embedding_texts)} embedding-ready text snippets")
    
    print("\nSample embedding texts (first 3):")
    for i, text in enumerate(embedding_texts[:3]):
        print(f"  {i+1}. {text[:100]}{'...' if len(text) > 100 else ''}")
    
    # Debug specific issue with indian_law_dataset
    print("\n6. Debugging specific file: indian_law_dataset.json...")
    specific_loader = JSONLoader()
    specific_sections, specific_acts, specific_cases = specific_loader.load_and_normalize_file("db/indian_law_dataset.json")
    
    print(f"  Loaded {len(specific_sections)} sections from indian_law_dataset.json")
    print(f"  Loaded {len(specific_acts)} acts from indian_law_dataset.json")
    
    # Check the first few sections
    for i, sec in enumerate(specific_sections[:5]):
        print(f"    Section {i+1}: ID={sec.section_id}, Act={sec.act_id}")
    
    # Check the acts
    for i, act in enumerate(specific_acts):
        print(f"    Act {i+1}: ID={act.act_id}, Sections count={len(act.sections)}")
        if act.sections:
            print(f"      First few sections: {act.sections[:3]}")
    
    print("\n✓ Data bridge test completed successfully!")
    print(f"\nSummary:")
    print(f"  - Sections: {len(sections)}")
    print(f"  - Acts: {len(acts)}")
    print(f"  - Cases: {len(cases)}")
    print(f"  - Integrity errors: {len(integrity_errors)}")
    print(f"  - Duplicate errors: {len(duplicate_errors)}")
    print(f"  - Embedding texts: {len(embedding_texts)}")


if __name__ == "__main__":
    test_data_bridge()