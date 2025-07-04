#!/usr/bin/env python3
"""
Development script for testing the BI Documentation Tool
Run this script to test the tool with sample data
"""

import sys
import tempfile
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bidoc.test_data import create_sample_powerbi_metadata, create_sample_tableau_metadata
from bidoc.markdown_generator import MarkdownGenerator
from bidoc.json_generator import JSONGenerator
from bidoc.ai_summary import AISummary


def main():
    """Run development tests"""
    
    print("🚀 BI Documentation Tool - Development Test")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("dev_output")
    output_dir.mkdir(exist_ok=True)
    
    # Test Power BI processing
    print("\n📊 Testing Power BI processing...")
    test_powerbi(output_dir)
    
    # Test Tableau processing
    print("\n📈 Testing Tableau processing...")
    test_tableau(output_dir)
    
    print(f"\n✅ Test complete! Check outputs in: {output_dir.absolute()}")


def test_powerbi(output_dir: Path):
    """Test Power BI metadata processing"""
    
    # Create sample metadata
    metadata = create_sample_powerbi_metadata()
    
    # Add AI summary
    ai_summary = AISummary()
    metadata['ai_summary'] = ai_summary.generate_summary(metadata)
    
    # Generate outputs
    json_gen = JSONGenerator()
    markdown_gen = MarkdownGenerator()
    
    json_output = json_gen.generate(metadata)
    markdown_output = markdown_gen.generate(metadata)
    
    # Write files
    json_file = output_dir / 'sample_powerbi.json'
    markdown_file = output_dir / 'sample_powerbi.md'
    
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(json_output)
    
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(markdown_output)
    
    print(f"   ✓ Generated: {json_file}")
    print(f"   ✓ Generated: {markdown_file}")


def test_tableau(output_dir: Path):
    """Test Tableau metadata processing"""
    
    # Create sample metadata
    metadata = create_sample_tableau_metadata()
    
    # Add AI summary
    ai_summary = AISummary()
    metadata['ai_summary'] = ai_summary.generate_summary(metadata)
    
    # Generate outputs
    json_gen = JSONGenerator()
    markdown_gen = MarkdownGenerator()
    
    json_output = json_gen.generate(metadata)
    markdown_output = markdown_gen.generate(metadata)
    
    # Write files
    json_file = output_dir / 'sample_tableau.json'
    markdown_file = output_dir / 'sample_tableau.md'
    
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(json_output)
    
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(markdown_output)
    
    print(f"   ✓ Generated: {json_file}")
    print(f"   ✓ Generated: {markdown_file}")


if __name__ == "__main__":
    main()
