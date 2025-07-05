# Integration Hooks and Extensibility Guide

This document outlines how to integrate the BI Documentation Tool with enterprise data management platforms, wikis, and other systems.

## 🔗 Overview

The BI Documentation Tool is designed with extensibility in mind, providing multiple integration points for enterprise workflows:

- **JSON Output**: Machine-readable metadata for programmatic consumption
- **CLI Interface**: Easy automation via scripts and CI/CD pipelines  
- **Docker Support**: Container-based deployment for enterprise environments
- **Configuration Files**: Centralized settings management via TOML
- **Exit Codes**: Proper error handling for automated workflows

## 🛠️ Integration Patterns

### 1. Ataccama DGC Integration

**Use Case**: Integrate BI documentation into Ataccama Data Governance Center for centralized metadata management.

**Implementation Approach**:

```python
# Example: Post-processing script for Ataccama integration
import json
import requests
from pathlib import Path

def upload_to_ataccama(metadata_file, ataccama_endpoint, auth_token):
    """Upload BI metadata to Ataccama DGC via REST API"""
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        bi_metadata = json.load(f)
    
    # Transform to Ataccama schema
    ataccama_payload = {
        "assetType": "business_intelligence",
        "assetName": bi_metadata["file_info"]["name"],
        "metadata": {
            "tables": bi_metadata["tables"],
            "measures": bi_metadata["measures"],
            "data_sources": bi_metadata["data_sources"]
        },
        "tags": ["power_bi", "tableau", "automated_documentation"]
    }
    
    response = requests.post(
        f"{ataccama_endpoint}/api/v1/assets",
        json=ataccama_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    return response.status_code == 201

# Integration workflow
def bi_to_ataccama_workflow(bi_file_path):
    # Generate documentation
    os.system(f"python -m bidoc -i '{bi_file_path}' -o './temp_output' -f json")
    
    # Upload to Ataccama
    json_file = Path("./temp_output") / f"{Path(bi_file_path).stem}.json"
    upload_to_ataccama(json_file, ATACCAMA_ENDPOINT, AUTH_TOKEN)
```

**Recommended Ataccama Mapping**:

- BI files → Business Intelligence Assets
- Tables → Data Entities  
- Measures → Business Rules/Calculations
- Data Sources → Data Source Assets
- Relationships → Lineage Information

### 2. Confluence Documentation Portal

**Use Case**: Automatically publish BI documentation to Confluence wikis for team collaboration.

**Implementation Approach**:

```python
# Example: Confluence integration script
from atlassian import Confluence
import markdown

def publish_to_confluence(markdown_file, confluence_url, username, api_token, space_key):
    """Publish Markdown documentation to Confluence"""
    
    confluence = Confluence(
        url=confluence_url,
        username=username,
        password=api_token
    )
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert Markdown to Confluence storage format
    html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
    
    # Create/update page
    page_title = f"BI Documentation: {Path(markdown_file).stem}"
    
    existing_page = confluence.get_page_by_title(space_key, page_title)
    
    if existing_page:
        confluence.update_page(
            page_id=existing_page['id'],
            title=page_title,
            body=html_content
        )
    else:
        confluence.create_page(
            space=space_key,
            title=page_title,
            body=html_content,
            parent_id=None
        )

# Automated workflow
def bi_to_confluence_workflow(bi_files, confluence_config):
    for bi_file in bi_files:
        # Generate documentation
        os.system(f"python -m bidoc -i '{bi_file}' -o './docs_output' -f markdown")
        
        # Publish to Confluence
        markdown_file = Path("./docs_output") / f"{Path(bi_file).stem}.md"
        publish_to_confluence(markdown_file, **confluence_config)
```

### 3. SharePoint Integration

**Use Case**: Upload documentation to SharePoint document libraries with metadata tagging.

**Implementation Approach**:

```python
# Example: SharePoint integration
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext

def upload_to_sharepoint(docs_folder, sharepoint_url, username, password, library_name):
    """Upload BI documentation to SharePoint with metadata"""
    
    auth_context = AuthenticationContext(sharepoint_url)
    auth_context.acquire_token_for_user(username, password)
    
    ctx = ClientContext(sharepoint_url, auth_context)
    
    for doc_file in Path(docs_folder).glob("*.md"):
        with open(doc_file, 'rb') as f:
            file_content = f.read()
        
        # Upload file
        target_file = ctx.web.get_folder_by_server_relative_url(library_name).upload_file(
            doc_file.name, file_content
        ).execute_query()
        
        # Set metadata
        target_file.set_property("DocumentType", "BI Documentation")
        target_file.set_property("GeneratedBy", "BI Documentation Tool")
        target_file.set_property("LastGenerated", datetime.now().isoformat())
        target_file.update()
        ctx.execute_query()
```

### 4. Microsoft Purview Integration

**Use Case**: Register BI assets and lineage information in Microsoft Purview for enterprise data governance.

**Implementation Approach**:

```python
# Example: Microsoft Purview integration
from azure.purview.catalog import PurviewCatalogClient
from azure.identity import DefaultAzureCredential

def register_with_purview(metadata_file, purview_endpoint):
    """Register BI metadata with Microsoft Purview"""
    
    credential = DefaultAzureCredential()
    client = PurviewCatalogClient(endpoint=purview_endpoint, credential=credential)
    
    with open(metadata_file, 'r') as f:
        bi_metadata = json.load(f)
    
    # Create BI asset entity
    bi_asset = {
        "typeName": "powerbi_report",
        "attributes": {
            "qualifiedName": bi_metadata["file_info"]["path"],
            "name": bi_metadata["file_info"]["name"],
            "description": f"Auto-generated documentation from {bi_metadata['file_info']['name']}",
            "tables": len(bi_metadata["tables"]),
            "measures": len(bi_metadata["measures"])
        }
    }
    
    client.entity.create_or_update(entity=bi_asset)
```

## 🔄 CI/CD Integration Patterns

### GitHub Actions Workflow

```yaml
# .github/workflows/bi-documentation.yml
name: BI Documentation Generation

on:
  push:
    paths:
      - 'bi-files/**/*.pbix'
      - 'bi-files/**/*.twb'
      - 'bi-files/**/*.twbx'

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
          
      - name: Generate BI Documentation
        run: |
          python -m bidoc -i "bi-files/" -o "docs/" -f all --verbose
          
      - name: Deploy to Confluence
        run: |
          python scripts/confluence_deploy.py --docs-dir docs/
        env:
          CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
          CONFLUENCE_TOKEN: ${{ secrets.CONFLUENCE_TOKEN }}
          
      - name: Commit documentation
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/
          git commit -m "Auto-update BI documentation" || exit 0
          git push
```

### Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - bi-files/*

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'
  displayName: 'Use Python 3.11'

- script: |
    pip install -r requirements.txt
    pip install -e .
  displayName: 'Install dependencies'

- script: |
    python -m bidoc -i "bi-files/" -o "$(Build.ArtifactStagingDirectory)/docs" -f all
  displayName: 'Generate BI Documentation'

- task: PublishBuildArtifacts@1
  inputs:
    PathtoPublish: '$(Build.ArtifactStagingDirectory)/docs'
    ArtifactName: 'bi-documentation'
  displayName: 'Publish Documentation Artifacts'
```

## 📊 Data Catalog Integrations

### Apache Atlas Integration

```python
def register_with_atlas(metadata_file, atlas_endpoint, auth):
    """Register BI metadata with Apache Atlas"""
    
    atlas_client = AtlasClient(atlas_endpoint, auth)
    
    with open(metadata_file, 'r') as f:
        bi_metadata = json.load(f)
    
    # Create BI report entity
    bi_entity = {
        "typeName": "bi_report",
        "attributes": {
            "qualifiedName": bi_metadata["file_info"]["path"],
            "name": bi_metadata["file_info"]["name"],
            "owner": "BI Documentation Tool",
            "createTime": datetime.now().timestamp(),
            "tables": [table["name"] for table in bi_metadata["tables"]]
        }
    }
    
    atlas_client.entity.create(bi_entity)
```

### DataHub Integration

```python
def push_to_datahub(metadata_file, datahub_gms_url):
    """Push BI metadata to LinkedIn DataHub"""
    
    from datahub.emitter.rest_emitter import DatahubRestEmitter
    from datahub.metadata.com.linkedin.pegasus2avro.dataset import DatasetProperties
    
    emitter = DatahubRestEmitter(gms_server=datahub_gms_url)
    
    with open(metadata_file, 'r') as f:
        bi_metadata = json.load(f)
    
    # Create dataset metadata
    dataset_properties = DatasetProperties(
        name=bi_metadata["file_info"]["name"],
        description=f"BI Report: {bi_metadata['file_info']['name']}",
        customProperties={
            "tool": "BI Documentation Tool",
            "file_type": bi_metadata["file_info"]["type"],
            "tables_count": str(len(bi_metadata["tables"])),
            "measures_count": str(len(bi_metadata["measures"]))
        }
    )
    
    emitter.emit_metadata(dataset_properties)
```

## 🔧 Custom Hook Development

### Creating Custom Output Processors

```python
# Example: Custom processor for internal systems
class CustomOutputProcessor:
    def __init__(self, config):
        self.config = config
    
    def process_metadata(self, metadata_dict):
        """Process extracted metadata for custom system"""
        
        # Transform metadata to custom format
        custom_format = {
            "system_id": self.config.get("system_id"),
            "timestamp": datetime.now().isoformat(),
            "source": metadata_dict["file_info"]["path"],
            "entities": self._transform_entities(metadata_dict),
            "relationships": self._extract_relationships(metadata_dict)
        }
        
        return custom_format
    
    def _transform_entities(self, metadata):
        entities = []
        
        # Process tables
        for table in metadata["tables"]:
            entities.append({
                "type": "table",
                "name": table["name"],
                "fields": table["fields"],
                "source_system": "BI Tool"
            })
        
        # Process measures
        for measure in metadata["measures"]:
            entities.append({
                "type": "calculation",
                "name": measure["name"],
                "expression": measure["expression"],
                "table": measure["table"]
            })
        
        return entities

# Usage in post-processing script
def run_custom_processor(bi_output_dir):
    processor = CustomOutputProcessor(config)
    
    for json_file in Path(bi_output_dir).glob("*.json"):
        with open(json_file, 'r') as f:
            metadata = json.load(f)
        
        custom_output = processor.process_metadata(metadata)
        
        # Send to custom system
        send_to_internal_system(custom_output)
```

## 📋 Best Practices

### 1. Error Handling and Monitoring

```python
import logging
import sys

def robust_integration_workflow(bi_files, integration_configs):
    """Robust integration with proper error handling"""
    
    success_count = 0
    error_count = 0
    
    for bi_file in bi_files:
        try:
            # Generate documentation
            result = subprocess.run([
                "python", "-m", "bidoc", 
                "-i", str(bi_file), 
                "-o", "./output", 
                "-f", "all"
            ], capture_output=True, text=True, check=True)
            
            # Process integrations
            for integration_name, config in integration_configs.items():
                try:
                    process_integration(bi_file, integration_name, config)
                    logging.info(f"✓ {integration_name} integration successful for {bi_file}")
                except Exception as e:
                    logging.error(f"✗ {integration_name} integration failed for {bi_file}: {e}")
                    error_count += 1
            
            success_count += 1
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Documentation generation failed for {bi_file}: {e.stderr}")
            error_count += 1
        except Exception as e:
            logging.error(f"Unexpected error processing {bi_file}: {e}")
            error_count += 1
    
    logging.info(f"Integration complete: {success_count} successful, {error_count} errors")
    
    # Exit with appropriate code for CI/CD
    sys.exit(1 if error_count > 0 else 0)
```

### 2. Configuration Management

```python
# integration_config.py
INTEGRATION_CONFIGS = {
    "confluence": {
        "enabled": True,
        "url": os.getenv("CONFLUENCE_URL"),
        "username": os.getenv("CONFLUENCE_USER"),
        "token": os.getenv("CONFLUENCE_TOKEN"),
        "space_key": "BITOOLS",
        "parent_page": "BI Documentation"
    },
    "sharepoint": {
        "enabled": False,
        "site_url": os.getenv("SHAREPOINT_URL"),
        "library": "BI Documentation",
        "folder": "Auto Generated"
    },
    "ataccama": {
        "enabled": True,
        "endpoint": os.getenv("ATACCAMA_ENDPOINT"),
        "auth_token": os.getenv("ATACCAMA_TOKEN"),
        "project_id": "bi_governance"
    }
}
```

### 3. Scheduling and Automation

```python
# Example: Automated daily processing
import schedule
import time

def daily_bi_documentation_job():
    """Daily automated BI documentation generation and distribution"""
    
    # Scan for new/updated BI files
    bi_files = scan_for_bi_files("//shared/bi_reports/")
    
    if bi_files:
        logging.info(f"Found {len(bi_files)} BI files to process")
        robust_integration_workflow(bi_files, INTEGRATION_CONFIGS)
    else:
        logging.info("No BI files found for processing")

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(daily_bi_documentation_job)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

## 🚀 Getting Started

1. **Identify Integration Points**: Determine which systems you need to integrate with
2. **Review Output Formats**: Examine the JSON and Markdown outputs to understand available metadata
3. **Develop Integration Scripts**: Create custom scripts using the patterns above
4. **Test Integration**: Start with a small set of BI files to validate the workflow
5. **Automate**: Implement CI/CD pipelines for production deployment
6. **Monitor**: Set up logging and monitoring for integration health

## 📞 Support

For integration assistance or custom development:

- **GitHub Issues**: Report integration bugs or request new integration examples
- **Discussions**: Share integration patterns with the community
- **Custom Development**: Contact for enterprise integration consulting

---

*This integration guide is actively maintained. Contributions and real-world integration examples are welcome!*
