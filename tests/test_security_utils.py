"""Tests for security utilities"""

import os
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from bidoc.security_utils import (
    FileSizeLimitError,
    PathTraversalError,
    SecurityError,
    ZipBombError,
    find_archive_members_by_extension,
    safe_extract_archive_member,
    secure_temp_directory,
    validate_archive_contents,
    validate_archive_member,
    validate_file_path,
)


class TestValidateFilePath:
    """Tests for file path validation"""

    def test_valid_file_path(self, tmp_path):
        """Test validation of a valid file path"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        result = validate_file_path(test_file)
        assert result == test_file.resolve()

    def test_nonexistent_file(self, tmp_path):
        """Test validation fails for nonexistent file"""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError):
            validate_file_path(test_file)

    def test_directory_path(self, tmp_path):
        """Test validation fails for directory path"""
        with pytest.raises(SecurityError, match="Path is not a file"):
            validate_file_path(tmp_path)

    def test_file_too_large(self, tmp_path):
        """Test validation fails for oversized file"""
        test_file = tmp_path / "large.txt"
        test_file.write_text("x" * 1000)  # Small file for testing
        
        # Mock the MAX_ARCHIVE_SIZE to be very small
        with patch('bidoc.security_utils.MAX_ARCHIVE_SIZE', 100):
            with pytest.raises(FileSizeLimitError):
                validate_file_path(test_file)


class TestValidateArchiveMember:
    """Tests for archive member validation"""

    def test_valid_member(self, tmp_path):
        """Test validation of a valid archive member"""
        member = Mock()
        member.filename = "normal_file.txt"
        member.file_size = 1000
        
        # Should not raise any exception
        validate_archive_member(member, tmp_path)

    def test_path_traversal_dotdot(self, tmp_path):
        """Test detection of path traversal with .."""
        member = Mock()
        member.filename = "../../../etc/passwd"
        member.file_size = 1000
        
        with pytest.raises(PathTraversalError, match="Path traversal attempt detected"):
            validate_archive_member(member, tmp_path)

    def test_path_traversal_absolute(self, tmp_path):
        """Test detection of absolute path traversal"""
        member = Mock()
        member.filename = "/etc/passwd"
        member.file_size = 1000
        
        with pytest.raises(PathTraversalError, match="Path traversal attempt detected"):
            validate_archive_member(member, tmp_path)

    def test_file_too_large(self, tmp_path):
        """Test detection of oversized archive member"""
        member = Mock()
        member.filename = "large_file.txt"
        member.file_size = 1000 * 1024 * 1024  # 1GB
        
        with pytest.raises(FileSizeLimitError):
            validate_archive_member(member, tmp_path)

    def test_path_traversal_resolved_outside(self, tmp_path):
        """Test detection of path traversal that resolves outside extraction directory"""
        # Create a subdirectory structure
        sub_dir = tmp_path / "subdir"
        sub_dir.mkdir()
        
        member = Mock()
        member.filename = "subdir/../../outside.txt"
        member.file_size = 1000
        
        with pytest.raises(PathTraversalError):
            validate_archive_member(member, sub_dir)


class TestValidateArchiveContents:
    """Tests for archive content validation"""

    def test_valid_archive(self, tmp_path):
        """Test validation of a valid archive"""
        # Create a test archive
        archive_path = tmp_path / "test.zip"
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
        
        members = validate_archive_contents(archive_path)
        assert len(members) == 2
        assert members[0].filename in ["file1.txt", "file2.txt"]

    def test_zip_bomb_compression_ratio(self, tmp_path):
        """Test detection of zip bomb with high compression ratio"""
        archive_path = tmp_path / "zipbomb.zip"
        
        # Create a zip with very high compression ratio
        with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            # Create a highly compressible content (lots of zeros)
            large_content = "0" * (10 * 1024 * 1024)  # 10MB of zeros
            zf.writestr("bomb.txt", large_content)
        
        with pytest.raises(ZipBombError, match="Suspicious compression ratio"):
            validate_archive_contents(archive_path)

    def test_too_many_files(self, tmp_path):
        """Test detection of archive with too many files"""
        archive_path = tmp_path / "manyfiles.zip"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            # Mock MAX_FILES_IN_ARCHIVE to be very small for testing
            with patch('bidoc.security_utils.MAX_FILES_IN_ARCHIVE', 3):
                for i in range(5):  # Create more files than allowed
                    zf.writestr(f"file{i}.txt", f"content{i}")
        
        with patch('bidoc.security_utils.MAX_FILES_IN_ARCHIVE', 3):
            with pytest.raises(ZipBombError, match="too many files"):
                validate_archive_contents(archive_path)

    def test_total_size_too_large(self, tmp_path):
        """Test detection of archive with total uncompressed size too large"""
        archive_path = tmp_path / "largetotal.zip"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            # Mock MAX_EXTRACTED_SIZE to be small for testing
            with patch('bidoc.security_utils.MAX_EXTRACTED_SIZE', 1000):
                zf.writestr("file1.txt", "x" * 600)
                zf.writestr("file2.txt", "x" * 600)  # Total > 1000
        
        with patch('bidoc.security_utils.MAX_EXTRACTED_SIZE', 1000):
            with pytest.raises(FileSizeLimitError, match="Total uncompressed size"):
                validate_archive_contents(archive_path)


class TestSecureTempDirectory:
    """Tests for secure temporary directory context manager"""

    def test_temp_directory_creation_and_cleanup(self):
        """Test that temporary directory is created and cleaned up"""
        temp_path = None
        
        with secure_temp_directory() as temp_dir:
            temp_path = temp_dir
            assert temp_dir.exists()
            assert temp_dir.is_dir()
            assert "bidoc_secure_" in temp_dir.name
            
            # Create a test file
            test_file = temp_dir / "test.txt"
            test_file.write_text("test")
            assert test_file.exists()
        
        # Directory should be cleaned up after exiting context
        assert not temp_path.exists()

    def test_temp_directory_cleanup_on_exception(self):
        """Test that temporary directory is cleaned up even when exception occurs"""
        temp_path = None
        
        try:
            with secure_temp_directory() as temp_dir:
                temp_path = temp_dir
                assert temp_dir.exists()
                
                # Create a test file
                test_file = temp_dir / "test.txt"
                test_file.write_text("test")
                assert test_file.exists()
                
                # Raise an exception
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Directory should still be cleaned up
        assert not temp_path.exists()


class TestSafeExtractArchiveMember:
    """Tests for safe archive member extraction"""

    def test_safe_extraction(self, tmp_path):
        """Test safe extraction of a valid archive member"""
        # Create test archive
        archive_path = tmp_path / "test.zip"
        test_content = "test file content"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("test.txt", test_content)
        
        # Extract safely
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()
        
        with zipfile.ZipFile(archive_path, 'r') as zf:
            member = zf.infolist()[0]
            extracted_path = safe_extract_archive_member(
                zf, member, extract_dir, allowed_extensions={".txt"}
            )
            
            assert extracted_path.exists()
            assert extracted_path.read_text() == test_content

    def test_forbidden_extension(self, tmp_path):
        """Test rejection of forbidden file extensions"""
        # Create test archive with .exe file
        archive_path = tmp_path / "test.zip"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("malware.exe", "fake exe content")
        
        # Try to extract with restricted extensions
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()
        
        with zipfile.ZipFile(archive_path, 'r') as zf:
            member = zf.infolist()[0]
            with pytest.raises(SecurityError, match="not in allowed extensions"):
                safe_extract_archive_member(
                    zf, member, extract_dir, allowed_extensions={".txt", ".twb"}
                )


class TestFindArchiveMembersByExtension:
    """Tests for finding archive members by extension"""

    def test_find_matching_extensions(self, tmp_path):
        """Test finding members with matching extensions"""
        # Create test archive with multiple file types
        archive_path = tmp_path / "test.zip"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("workbook.twb", "tableau workbook")
            zf.writestr("data.csv", "csv data")
            zf.writestr("config.tds", "tableau data source")
            zf.writestr("readme.txt", "readme text")
        
        # Find Tableau files
        matching_members = find_archive_members_by_extension(
            archive_path, [".twb", ".tds"]
        )
        
        assert len(matching_members) == 2
        filenames = [member.filename for member in matching_members]
        assert "workbook.twb" in filenames
        assert "config.tds" in filenames
        assert "data.csv" not in filenames
        assert "readme.txt" not in filenames

    def test_no_matching_extensions(self, tmp_path):
        """Test when no members match the specified extensions"""
        # Create test archive with non-matching files
        archive_path = tmp_path / "test.zip"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("data.csv", "csv data")
            zf.writestr("readme.txt", "readme text")
        
        # Look for Tableau files
        matching_members = find_archive_members_by_extension(
            archive_path, [".twb", ".tds"]
        )
        
        assert len(matching_members) == 0

    def test_case_insensitive_matching(self, tmp_path):
        """Test that extension matching is case insensitive"""
        # Create test archive with uppercase extensions
        archive_path = tmp_path / "test.zip"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("workbook.TWB", "tableau workbook uppercase")
            zf.writestr("data.TDS", "tableau data source uppercase")
        
        # Find with lowercase extensions
        matching_members = find_archive_members_by_extension(
            archive_path, [".twb", ".tds"]
        )
        
        assert len(matching_members) == 2
        filenames = [member.filename for member in matching_members]
        assert "workbook.TWB" in filenames
        assert "data.TDS" in filenames