"""Basic unit tests for the BI Documentation Tool"""

import unittest
import tempfile
import json
from pathlib import Path

from bidoc.json_generator import JSONGenerator
from bidoc.markdown_generator import MarkdownGenerator
from bidoc.ai_summary import AISummary
from bidoc.test_data import create_sample_powerbi_metadata, create_sample_tableau_metadata


class TestJSONGenerator(unittest.TestCase):
    """Test JSON output generation"""
    
    def setUp(self):
        self.generator = JSONGenerator()
    
    def test_powerbi_json_generation(self):
        """Test JSON generation for Power BI metadata"""
        metadata = create_sample_powerbi_metadata()
        json_output = self.generator.generate(metadata)
        
        # Verify it's valid JSON
        parsed = json.loads(json_output)
        
        # Check structure
        self.assertEqual(parsed['type'], 'Power BI')
        self.assertIn('tables', parsed)
        self.assertIn('measures', parsed)
        self.assertIn('generation_info', parsed)
    
    def test_tableau_json_generation(self):
        """Test JSON generation for Tableau metadata"""
        metadata = create_sample_tableau_metadata()
        json_output = self.generator.generate(metadata)
        
        # Verify it's valid JSON
        parsed = json.loads(json_output)
        
        # Check structure
        self.assertEqual(parsed['type'], 'Tableau')
        self.assertIn('data_sources', parsed)
        self.assertIn('worksheets', parsed)
        self.assertIn('generation_info', parsed)
    
    def test_json_validation(self):
        """Test JSON validation"""
        valid_json = '{"test": "value"}'
        invalid_json = '{"test": value}'
        
        self.assertTrue(self.generator.validate_json(valid_json))
        self.assertFalse(self.generator.validate_json(invalid_json))


class TestMarkdownGenerator(unittest.TestCase):
    """Test Markdown output generation"""
    
    def setUp(self):
        self.generator = MarkdownGenerator()
    
    def test_powerbi_markdown_generation(self):
        """Test Markdown generation for Power BI metadata"""
        metadata = create_sample_powerbi_metadata()
        markdown_output = self.generator.generate(metadata)
        
        # Check for key sections
        self.assertIn('# Documentation for', markdown_output)
        self.assertIn('## Data Sources', markdown_output)
        self.assertIn('## Tables and Fields', markdown_output)
        self.assertIn('## Measures', markdown_output)
        self.assertIn('Total Sales', markdown_output)  # Sample measure
    
    def test_tableau_markdown_generation(self):
        """Test Markdown generation for Tableau metadata"""
        metadata = create_sample_tableau_metadata()
        markdown_output = self.generator.generate(metadata)
        
        # Check for key sections
        self.assertIn('# Documentation for', markdown_output)
        self.assertIn('## Data Sources', markdown_output)
        self.assertIn('## Worksheets', markdown_output)
        self.assertIn('## Dashboards', markdown_output)
        self.assertIn('Superstore', markdown_output)  # Sample data source


class TestAISummary(unittest.TestCase):
    """Test AI summary generation"""
    
    def setUp(self):
        self.ai_summary = AISummary()
    
    def test_powerbi_static_summary(self):
        """Test static summary generation for Power BI"""
        metadata = create_sample_powerbi_metadata()
        summary = self.ai_summary.generate_summary(metadata)
        
        self.assertIn('Power BI report', summary)
        self.assertIn('data tables', summary)
        self.assertIn('DAX measures', summary)
    
    def test_tableau_static_summary(self):
        """Test static summary generation for Tableau"""
        metadata = create_sample_tableau_metadata()
        summary = self.ai_summary.generate_summary(metadata)
        
        self.assertIn('Tableau workbook', summary)
        self.assertIn('data sources', summary)
        self.assertIn('worksheets', summary)
    
    def test_complexity_assessment(self):
        """Test complexity assessment"""
        powerbi_metadata = create_sample_powerbi_metadata()
        tableau_metadata = create_sample_tableau_metadata()
        
        powerbi_complexity = self.ai_summary._assess_powerbi_complexity(powerbi_metadata)
        tableau_complexity = self.ai_summary._assess_tableau_complexity(tableau_metadata)
        
        self.assertIn(powerbi_complexity, ['Low', 'Medium', 'High'])
        self.assertIn(tableau_complexity, ['Low', 'Medium', 'High'])


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow from metadata to output files"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            # Test Power BI workflow
            powerbi_metadata = create_sample_powerbi_metadata()
            
            # Add AI summary
            ai_summary = AISummary()
            powerbi_metadata['ai_summary'] = ai_summary.generate_summary(powerbi_metadata)
            
            # Generate outputs
            json_gen = JSONGenerator()
            markdown_gen = MarkdownGenerator()
            
            json_output = json_gen.generate(powerbi_metadata)
            markdown_output = markdown_gen.generate(powerbi_metadata)
            
            # Write files
            json_file = output_dir / 'test_powerbi.json'
            markdown_file = output_dir / 'test_powerbi.md'
            
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_output)
            
            # Verify files exist and have content
            self.assertTrue(json_file.exists())
            self.assertTrue(markdown_file.exists())
            self.assertGreater(json_file.stat().st_size, 0)
            self.assertGreater(markdown_file.stat().st_size, 0)
            
            # Verify JSON is valid
            with open(json_file, 'r', encoding='utf-8') as f:
                parsed_json = json.load(f)
                self.assertEqual(parsed_json['type'], 'Power BI')


if __name__ == '__main__':
    unittest.main()
