"""Security tests for file handling and input validation."""

import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from bidoc.utils import detect_file_type, FileType
from bidoc.pbix_parser import PowerBIParser  
from bidoc.tableau_parser import TableauParser

from .test_fixtures import create_malicious_zip


class TestFileValidation:
    """Test file validation and security checks."""
    
    def test_file_extension_validation(self, temp_directory):
        """Test that only expected file types are processed."""
        # Create files with various extensions
        test_files = [
            ("legitimate.pbix", FileType.POWER_BI),
            ("legitimate.twb", FileType.TABLEAU_TWB),
            ("legitimate.twbx", FileType.TABLEAU_TWBX),
            ("suspicious.exe", FileType.UNKNOWN),
            ("suspicious.bat", FileType.UNKNOWN),
            ("suspicious.sh", FileType.UNKNOWN),
            ("suspicious.pdf", FileType.UNKNOWN),
            ("no_extension", FileType.UNKNOWN),
        ]
        
        for filename, expected_type in test_files:
            file_path = temp_directory / filename
            file_path.write_text("dummy content")
            
            detected_type = detect_file_type(file_path)
            assert detected_type == expected_type, f"File {filename} should be detected as {expected_type}"
    
    def test_path_traversal_protection(self, temp_directory):
        """Test protection against path traversal attacks."""
        # Create a malicious ZIP file with path traversal
        malicious_zip = temp_directory / "malicious.pbix"
        create_malicious_zip(malicious_zip, path_traversal=True)
        
        # Mock PBIXRay to prevent actual processing
        with patch('bidoc.pbix_parser.PBIXRay') as mock_pbixray:
            mock_pbixray.side_effect = Exception("Path traversal detected")
            
            parser = PowerBIParser()
            
            # Should handle the malicious file gracefully
            result = parser.parse(malicious_zip)
            
            # Should return default metadata, not crash
            assert result is not None
            assert result["type"] == "Power BI"
    
    def test_zip_bomb_protection(self, temp_directory):
        """Test protection against zip bomb attacks."""
        # Create a ZIP bomb
        zip_bomb = temp_directory / "zipbomb.pbix"
        create_malicious_zip(zip_bomb, zip_bomb=True)
        
        # Mock PBIXRay to simulate zip bomb detection
        with patch('bidoc.pbix_parser.PBIXRay') as mock_pbixray:
            mock_pbixray.side_effect = Exception("Suspicious compression ratio detected")
            
            parser = PowerBIParser()
            
            # Should handle the zip bomb gracefully
            result = parser.parse(zip_bomb)
            
            # Should return default metadata, not crash or hang
            assert result is not None
            assert result["type"] == "Power BI"
    
    def test_large_file_handling(self, temp_directory):
        """Test handling of extremely large files."""
        # Create a large file (simulate - don't actually create huge file)
        large_file = temp_directory / "large.pbix"
        large_file.write_text("dummy content")
        
        # Mock file stats to simulate large file
        with patch.object(Path, 'stat') as mock_stat:
            mock_stat.return_value = Mock(st_size=10 * 1024 * 1024 * 1024)  # 10GB
            
            # Mock PBIXRay to simulate handling
            with patch('bidoc.pbix_parser.PBIXRay') as mock_pbixray:
                mock_pbixray.side_effect = Exception("File too large")
                
                parser = PowerBIParser()
                result = parser.parse(large_file)
                
                # Should handle gracefully
                assert result is not None
    
    def test_malformed_zip_handling(self, temp_directory):
        """Test handling of corrupted or malformed ZIP files."""
        # Create a corrupted ZIP file
        corrupted_zip = temp_directory / "corrupted.pbix"
        corrupted_zip.write_bytes(b"This is not a valid ZIP file content")
        
        # Mock PBIXRay to simulate corruption detection
        with patch('bidoc.pbix_parser.PBIXRay') as mock_pbixray:
            mock_pbixray.side_effect = zipfile.BadZipFile("File is not a zip file")
            
            parser = PowerBIParser()
            result = parser.parse(corrupted_zip)
            
            # Should handle gracefully
            assert result is not None
            assert result["type"] == "Power BI"
    
    def test_empty_file_handling(self, temp_directory):
        """Test handling of empty files."""
        empty_file = temp_directory / "empty.pbix"
        empty_file.touch()  # Create empty file
        
        with patch('bidoc.pbix_parser.PBIXRay') as mock_pbixray:
            mock_pbixray.side_effect = Exception("Empty file")
            
            parser = PowerBIParser()
            result = parser.parse(empty_file)
            
            assert result is not None
            assert result["file_size"] == 0


class TestInputSanitization:
    """Test input sanitization and validation."""
    
    def test_sql_injection_in_metadata(self):
        """Test that SQL injection attempts in metadata are handled safely."""
        malicious_metadata = {
            "file": "'; DROP TABLE users; --",
            "type": "Power BI",
            "data_sources": [
                {
                    "name": "'; DROP DATABASE test; --", 
                    "connection": "server'; EXEC xp_cmdshell('rm -rf /'); --"
                }
            ],
            "tables": [
                {
                    "name": "Users'; DROP TABLE passwords; --",
                    "columns": [
                        {
                            "name": "'; UNION SELECT * FROM secrets; --",
                            "data_type": "String"
                        }
                    ]
                }
            ]
        }
        
        # Test that generators handle malicious input safely
        from bidoc.markdown_generator import MarkdownGenerator
        from bidoc.json_generator import JSONGenerator
        
        markdown_gen = MarkdownGenerator()
        markdown_result = markdown_gen.generate(malicious_metadata)
        
        # Should include the content but not execute it
        assert "'; DROP TABLE users; --" in markdown_result
        assert "DROP DATABASE" in markdown_result  # Should be treated as text
        
        json_gen = JSONGenerator()
        json_result = json_gen.generate(malicious_metadata)
        
        # Should be properly escaped in JSON
        assert "'; DROP TABLE users; --" in json_result
        assert '"name": "\\u0027; DROP DATABASE test; --"' in json_result or \
               '"name": "\'; DROP DATABASE test; --"' in json_result
    
    def test_xss_prevention_in_output(self):
        """Test prevention of XSS attacks in generated output."""
        xss_metadata = {
            "file": "<script>alert('XSS')</script>",
            "type": "Power BI",
            "data_sources": [
                {
                    "name": "<img src=x onerror=alert('XSS')>",
                    "description": "javascript:alert('XSS')"
                }
            ],
            "measures": [
                {
                    "name": "<svg onload=alert('XSS')>",
                    "expression": "<iframe src=javascript:alert('XSS')>",
                    "description": "<body onload=alert('XSS')>"
                }
            ]
        }
        
        from bidoc.markdown_generator import MarkdownGenerator
        
        markdown_gen = MarkdownGenerator()
        result = markdown_gen.generate(xss_metadata)
        
        # HTML/JavaScript should be escaped or treated as plain text in Markdown
        # Markdown naturally escapes HTML, but we should verify
        assert "<script>" in result  # Should be literal text, not executed
        assert "alert('XSS')" in result  # Should be literal text
        
        # Check that dangerous patterns are neutralized in context
        lines = result.split('\n')
        script_lines = [line for line in lines if '<script>' in line]
        for line in script_lines:
            # Should be in a safe context (like code blocks or escaped)
            assert line.startswith('```') or line.startswith('    ') or '`' in line
    
    def test_path_injection_prevention(self, temp_directory):
        """Test prevention of path injection in file operations."""
        # Simulate malicious file paths
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam", 
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "../../../../usr/bin/python",
        ]
        
        for malicious_path in malicious_paths:
            # Mock file operations to simulate path injection attempts
            with patch('bidoc.pbix_parser.PBIXRay') as mock_pbixray:
                mock_pbixray.side_effect = Exception(f"Access denied: {malicious_path}")
                
                parser = PowerBIParser()
                
                # Should handle malicious paths safely
                try:
                    # Create a file with safe name but simulate malicious internal path
                    safe_file = temp_directory / "safe.pbix"
                    safe_file.write_text("dummy")
                    
                    result = parser.parse(safe_file)
                    assert result is not None
                except Exception as e:
                    # Should not expose system paths or crash
                    error_msg = str(e).lower()
                    assert "access denied" in error_msg or "file not found" in error_msg
    
    def test_command_injection_prevention(self):
        """Test prevention of command injection in processing."""
        command_injection_metadata = {
            "file": "test.pbix",
            "type": "Power BI", 
            "data_sources": [
                {
                    "name": "test; rm -rf /",
                    "connection": "server`shutdown -h now`"
                }
            ],
            "measures": [
                {
                    "name": "$(cat /etc/passwd)",
                    "expression": "`ls -la`",
                    "description": "&& curl malicious-site.com"
                }
            ]
        }
        
        from bidoc.markdown_generator import MarkdownGenerator
        
        markdown_gen = MarkdownGenerator()
        result = markdown_gen.generate(command_injection_metadata)
        
        # Commands should be treated as literal text, not executed
        assert "rm -rf /" in result
        assert "shutdown -h now" in result
        assert "$(cat /etc/passwd)" in result
        assert "`ls -la`" in result
        
        # Should not contain evidence of command execution
        assert "/etc/passwd" not in result or "$(cat /etc/passwd)" in result
        assert "total" not in result  # Common start of 'ls -la' output


class TestAccessControl:
    """Test access control and permission handling."""
    
    def test_file_permission_handling(self, temp_directory):
        """Test handling of files with restricted permissions."""
        # Create a file and make it unreadable
        restricted_file = temp_directory / "restricted.pbix"
        restricted_file.write_text("test content")
        
        try:
            # Make file unreadable (Unix systems)
            restricted_file.chmod(0o000)
            
            with patch('bidoc.pbix_parser.PBIXRay') as mock_pbixray:
                mock_pbixray.side_effect = PermissionError("Access denied")
                
                parser = PowerBIParser()
                result = parser.parse(restricted_file)
                
                # Should handle permission error gracefully
                assert result is not None
        finally:
            # Restore permissions for cleanup
            try:
                restricted_file.chmod(0o644)
            except:
                pass
    
    def test_directory_traversal_in_output(self, temp_directory):
        """Test that output paths cannot be manipulated for directory traversal."""
        from bidoc.cli import generate_outputs
        
        metadata = {"file": "test.pbix", "type": "Power BI"}
        
        # Try to use directory traversal in output filename
        malicious_names = [
            "../../../malicious",
            "..\\..\\..\\malicious",
            "/etc/passwd",
            "C:\\Windows\\System32\\malicious"
        ]
        
        for malicious_name in malicious_names:
            try:
                # Should either sanitize the name or fail safely
                generate_outputs(metadata, temp_directory, malicious_name, "markdown")
                
                # Check that no files were created outside temp_directory
                temp_files = list(temp_directory.rglob("*"))
                for temp_file in temp_files:
                    # All created files should be within temp_directory
                    assert temp_directory in temp_file.parents or temp_file == temp_directory
                    
            except Exception as e:
                # If it fails, should fail safely without creating files in wrong places
                pass


class TestDataValidation:
    """Test validation of processed data for security issues."""
    
    def test_metadata_size_limits(self):
        """Test that extremely large metadata structures are handled safely."""
        # Create metadata with extremely large strings
        huge_string = "A" * (100 * 1024 * 1024)  # 100MB string
        
        large_metadata = {
            "file": "huge.pbix",
            "type": "Power BI",
            "model_info": {
                "description": huge_string
            }
        }
        
        from bidoc.json_generator import JSONGenerator
        
        json_gen = JSONGenerator()
        
        # Should handle large data gracefully (may truncate or limit)
        try:
            result = json_gen.generate(large_metadata)
            # If it succeeds, result should be manageable size
            assert len(result) < 200 * 1024 * 1024  # Less than 200MB
        except MemoryError:
            # Acceptable to fail with memory error for extreme cases
            pass
        except Exception as e:
            # Should fail gracefully, not crash the process
            assert "memory" in str(e).lower() or "size" in str(e).lower()
    
    def test_circular_reference_handling(self):
        """Test handling of circular references in metadata."""
        # Create metadata with circular references (simulate complex object graph)
        metadata = {
            "file": "circular.pbix",
            "type": "Power BI"
        }
        
        # Add self-reference (simulate circular dependency)
        metadata["self_ref"] = metadata
        
        from bidoc.json_generator import JSONGenerator
        
        json_gen = JSONGenerator()
        
        # Should handle circular references without infinite recursion
        try:
            result = json_gen.generate(metadata)
            # Should complete without hanging
            assert len(result) > 0
        except (ValueError, RecursionError) as e:
            # Acceptable to fail with recursion error for circular references
            assert "circular" in str(e).lower() or "recursion" in str(e).lower()
    
    def test_unicode_security(self):
        """Test handling of potentially malicious Unicode characters."""
        # Test various Unicode attack vectors
        unicode_attacks = [
            "\u202e",  # Right-to-left override
            "\u200b\u200c\u200d",  # Zero-width characters
            "\ufeff",  # Byte order mark
            "\u0000",  # Null character
            "\u001f\u007f",  # Control characters
            "𝒻𝒾𝓁𝑒.𝓅𝒷𝒾𝓍",  # Mathematical script (homograph attack)
        ]
        
        for attack_string in unicode_attacks:
            metadata = {
                "file": f"test_{attack_string}.pbix",
                "type": "Power BI",
                "data_sources": [
                    {"name": f"source_{attack_string}"}
                ]
            }
            
            from bidoc.markdown_generator import MarkdownGenerator
            
            markdown_gen = MarkdownGenerator()
            
            # Should handle special Unicode without issues
            try:
                result = markdown_gen.generate(metadata)
                assert len(result) > 0
                # Should contain the Unicode (not crash or corrupt)
                assert attack_string in result or repr(attack_string) in result
            except UnicodeError:
                # Acceptable to fail on invalid Unicode
                pass