#!/usr/bin/env python3
"""
BI Documentation Tool - Comprehensive Demo Script

This script demonstrates the complete functionality of the BI Documentation Tool
using real PowerBI and Tableau sample files, showcasing:

1. Metadata extraction from PowerBI (.pbix) files
2. Metadata extraction from Tableau (.twbx) files  
3. Professional Markdown generation with formatted DAX
4. Complete JSON output with all metadata fields
5. Error handling and missing metadata marking as "Not available"
6. Performance optimization features
7. Enterprise integration capabilities

Run with: python demo.py
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any

def setup_demo_logging():
    """Setup enhanced logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('demo_run.log')
        ]
    )
    return logging.getLogger(__name__)

def analyze_output_quality(output_path: Path, file_type: str) -> Dict[str, Any]:
    """Analyze the quality and completeness of generated documentation"""
    
    md_file = output_path / f"{output_path.stem}.md"
    json_file = output_path / f"{output_path.stem}.json"
    
    analysis = {
        "files_generated": [],
        "markdown_analysis": {},
        "json_analysis": {},
        "metadata_completeness": {},
        "dax_formatting_quality": {},
        "issues_found": []
    }
    
    # Check if files were generated
    if md_file.exists():
        analysis["files_generated"].append("markdown")
        
        # Analyze markdown content
        md_content = md_file.read_text(encoding='utf-8')
        analysis["markdown_analysis"] = {
            "line_count": len(md_content.split('\n')),
            "word_count": len(md_content.split()),
            "has_dax_code_blocks": "```dax" in md_content,
            "has_m_code_blocks": "```m" in md_content,
            "measures_documented": md_content.count("### ") - md_content.count("### Page:"),
            "tables_documented": md_content.count("| Field Name |"),
            "not_available_count": md_content.count("not available")
        }
        
        # Check for common issues
        if "None" in md_content:
            analysis["issues_found"].append("Found 'None' values instead of 'not available'")
        if "```dax\n\n```" in md_content:
            analysis["issues_found"].append("Found empty DAX code blocks")
            
    if json_file.exists():
        analysis["files_generated"].append("json")
        
        # Analyze JSON content
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
            analysis["json_analysis"] = {
                "total_sections": len(json_data.keys()),
                "has_generation_info": "generation_info" in json_data,
                "data_sources_count": len(json_data.get("data_sources", [])),
                "tables_count": len(json_data.get("tables", [])),
                "measures_count": len(json_data.get("measures", [])),
                "relationships_count": len(json_data.get("relationships", []))
            }
            
            # Check metadata completeness
            if file_type == "Power BI":
                expected_sections = [
                    "model_info", "data_sources", "tables", "relationships", 
                    "measures", "calculated_columns", "visualizations", "power_query"
                ]
            else:
                expected_sections = [
                    "workbook_info", "data_sources", "worksheets", "dashboards", 
                    "parameters", "calculated_fields"
                ]
                
            analysis["metadata_completeness"] = {
                "expected_sections": len(expected_sections),
                "present_sections": sum(1 for section in expected_sections if section in json_data),
                "missing_sections": [section for section in expected_sections if section not in json_data]
            }
            
        except json.JSONDecodeError as e:
            analysis["issues_found"].append(f"Invalid JSON generated: {str(e)}")
    
    return analysis

def demonstrate_powerbi_extraction(logger):
    """Demonstrate PowerBI file extraction with real files"""
    logger.info("=" * 60)
    logger.info("DEMONSTRATION: PowerBI File Processing")
    logger.info("=" * 60)
    
    # Find PowerBI sample files
    samples_dir = Path("samples/power_bi")
    if not samples_dir.exists():
        logger.error(f"Samples directory not found: {samples_dir}")
        return
        
    pbix_files = list(samples_dir.glob("*.pbix"))
    if not pbix_files:
        logger.error("No PowerBI sample files found")
        return
        
    logger.info(f"Found {len(pbix_files)} PowerBI sample files:")
    for file in pbix_files:
        logger.info(f"  - {file.name} ({file.stat().st_size / 1024:.1f} KB)")
    
    # Process each file
    demo_output = Path("demo_output")
    demo_output.mkdir(exist_ok=True)
    
    for pbix_file in pbix_files[:2]:  # Process first 2 files for demo
        logger.info(f"\nProcessing: {pbix_file.name}")
        start_time = time.time()
        
        try:
            # Import and use the actual parser
            from bidoc.pbix_parser import PowerBIParser
            from bidoc.markdown_generator import MarkdownGenerator
            from bidoc.json_generator import JSONGenerator
            
            # Parse the file
            parser = PowerBIParser()
            metadata = parser.parse(pbix_file)
            
            # Generate outputs
            base_name = pbix_file.stem
            
            # Generate Markdown
            md_gen = MarkdownGenerator()
            markdown_content = md_gen.generate(metadata)
            md_file = demo_output / f"{base_name}.md"
            md_file.write_text(markdown_content, encoding='utf-8')
            
            # Generate JSON
            json_gen = JSONGenerator()
            json_content = json_gen.generate(metadata)
            json_file = demo_output / f"{base_name}.json"
            json_file.write_text(json_content, encoding='utf-8')
            
            processing_time = time.time() - start_time
            
            # Analyze output quality
            analysis = analyze_output_quality(demo_output / base_name, "Power BI")
            
            logger.info(f"✅ Successfully processed in {processing_time:.2f}s")
            logger.info(f"   Generated: {', '.join(analysis['files_generated'])}")
            logger.info(f"   Markdown: {analysis['markdown_analysis'].get('line_count', 0)} lines")
            logger.info(f"   JSON: {analysis['json_analysis'].get('total_sections', 0)} sections")
            logger.info(f"   Measures documented: {analysis['markdown_analysis'].get('measures_documented', 0)}")
            logger.info(f"   Tables documented: {analysis['markdown_analysis'].get('tables_documented', 0)}")
            
            if analysis['issues_found']:
                logger.warning(f"   Issues found: {len(analysis['issues_found'])}")
                for issue in analysis['issues_found']:
                    logger.warning(f"     - {issue}")
            else:
                logger.info("   ✅ No quality issues detected")
                
        except Exception as e:
            logger.error(f"❌ Failed to process {pbix_file.name}: {str(e)}")

def demonstrate_tableau_extraction(logger):
    """Demonstrate Tableau file extraction with real files"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATION: Tableau File Processing")
    logger.info("=" * 60)
    
    # Find Tableau sample files
    samples_dir = Path("samples/Tableau")
    if not samples_dir.exists():
        logger.warning(f"Tableau samples directory not found: {samples_dir}")
        return
        
    twbx_files = list(samples_dir.glob("*.twbx"))
    if not twbx_files:
        logger.warning("No Tableau sample files found")
        return
        
    logger.info(f"Found {len(twbx_files)} Tableau sample files:")
    for file in twbx_files:
        logger.info(f"  - {file.name} ({file.stat().st_size / 1024:.1f} KB)")
    
    # Process first file for demo
    demo_output = Path("demo_output")
    demo_output.mkdir(exist_ok=True)
    
    for twbx_file in twbx_files[:1]:  # Process first file for demo
        logger.info(f"\nProcessing: {twbx_file.name}")
        start_time = time.time()
        
        try:
            # Import and use the actual parser
            from bidoc.tableau_parser import TableauParser
            from bidoc.markdown_generator import MarkdownGenerator
            from bidoc.json_generator import JSONGenerator
            
            # Parse the file
            parser = TableauParser()
            metadata = parser.parse(twbx_file)
            
            # Generate outputs
            base_name = twbx_file.stem
            
            # Generate Markdown
            md_gen = MarkdownGenerator()
            markdown_content = md_gen.generate(metadata)
            md_file = demo_output / f"{base_name}.md"
            md_file.write_text(markdown_content, encoding='utf-8')
            
            # Generate JSON
            json_gen = JSONGenerator()
            json_content = json_gen.generate(metadata)
            json_file = demo_output / f"{base_name}.json"
            json_file.write_text(json_content, encoding='utf-8')
            
            processing_time = time.time() - start_time
            
            # Analyze output quality
            analysis = analyze_output_quality(demo_output / base_name, "Tableau")
            
            logger.info(f"✅ Successfully processed in {processing_time:.2f}s")
            logger.info(f"   Generated: {', '.join(analysis['files_generated'])}")
            logger.info(f"   Markdown: {analysis['markdown_analysis'].get('line_count', 0)} lines")
            logger.info(f"   JSON: {analysis['json_analysis'].get('total_sections', 0)} sections")
            
            if analysis['issues_found']:
                logger.warning(f"   Issues found: {len(analysis['issues_found'])}")
                for issue in analysis['issues_found']:
                    logger.warning(f"     - {issue}")
            else:
                logger.info("   ✅ No quality issues detected")
                
        except Exception as e:
            logger.error(f"❌ Failed to process {twbx_file.name}: {str(e)}")

def demonstrate_dax_formatting(logger):
    """Demonstrate DAX formatting capabilities"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATION: DAX Formatting Features")
    logger.info("=" * 60)
    
    from bidoc.dax_formatter import DAXFormatter
    
    formatter = DAXFormatter()
    
    # Sample DAX expressions to format
    sample_expressions = [
        "calculate(sum(sales[amount]),filter(sales,sales[date]>=date(2020,1,1)))",
        "if(isblank(related(customer[country])),'Unknown',related(customer[country]))",
        "var CurrentYear = year(today()) return calculate([Total Sales],filter(all('Date'),'Date'[Year] = CurrentYear))",
        "sumx(filter(sales,sales[product]='Widget'),sales[amount]*sales[quantity])"
    ]
    
    for i, expression in enumerate(sample_expressions, 1):
        logger.info(f"\nSample {i} - Original:")
        logger.info(f"  {expression}")
        
        formatted = formatter.format(expression)
        logger.info(f"Sample {i} - Formatted:")
        logger.info(f"  {formatted}")

def demonstrate_cli_features(logger):
    """Demonstrate CLI capabilities"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATION: CLI Features")
    logger.info("=" * 60)
    
    logger.info("Available CLI commands:")
    logger.info("  bidoc --help                    # Show help")
    logger.info("  bidoc -i file.pbix -o docs/     # Process single file")
    logger.info("  bidoc -i *.pbix -o docs/ -f all # Process multiple files")
    logger.info("  bidoc -i file.pbix --verbose    # Verbose output")
    logger.info("  bidoc -i file.pbix --log-file   # Save logs to file")
    logger.info("  bidoc -i file.pbix --with-summary # Include AI summary")

def generate_demo_summary(logger):
    """Generate a summary of the demo results"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO SUMMARY")
    logger.info("=" * 60)
    
    demo_output = Path("demo_output")
    if not demo_output.exists():
        logger.warning("No demo output directory found")
        return
    
    generated_files = list(demo_output.iterdir())
    markdown_files = [f for f in generated_files if f.suffix == '.md']
    json_files = [f for f in generated_files if f.suffix == '.json']
    
    logger.info(f"Total files generated: {len(generated_files)}")
    logger.info(f"  Markdown files: {len(markdown_files)}")
    logger.info(f"  JSON files: {len(json_files)}")
    
    if markdown_files:
        logger.info("\nGenerated Markdown files:")
        for md_file in markdown_files:
            size_kb = md_file.stat().st_size / 1024
            logger.info(f"  - {md_file.name} ({size_kb:.1f} KB)")
    
    if json_files:
        logger.info("\nGenerated JSON files:")
        for json_file in json_files:
            size_kb = json_file.stat().st_size / 1024
            logger.info(f"  - {json_file.name} ({size_kb:.1f} KB)")
    
    logger.info(f"\nDemo output available in: {demo_output.absolute()}")
    logger.info("✅ Demo completed successfully!")

def main():
    """Main demo function"""
    logger = setup_demo_logging()
    
    logger.info("🚀 Starting BI Documentation Tool Comprehensive Demo")
    logger.info(f"Demo started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Demonstrate PowerBI extraction
        demonstrate_powerbi_extraction(logger)
        
        # Demonstrate Tableau extraction
        demonstrate_tableau_extraction(logger)
        
        # Demonstrate DAX formatting
        demonstrate_dax_formatting(logger)
        
        # Demonstrate CLI features
        demonstrate_cli_features(logger)
        
        # Generate summary
        generate_demo_summary(logger)
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()