"""Security utilities for safe file handling and archive processing."""

import os
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List, Optional, Union

# Security constants
MAX_ARCHIVE_SIZE = 100 * 1024 * 1024  # 100MB max archive size
MAX_EXTRACTED_SIZE = 500 * 1024 * 1024  # 500MB max extracted content
MAX_FILES_IN_ARCHIVE = 1000  # Maximum number of files in archive
ALLOWED_EXTENSIONS = {".twb", ".tds", ".pbix", ".twbx", ".tdsx"}


class SecurityError(Exception):
    """Base exception for security-related errors."""
    pass


class PathTraversalError(SecurityError):
    """Raised when path traversal attack is detected."""
    pass


class FileSizeLimitError(SecurityError):
    """Raised when file size exceeds limits."""
    pass


class ZipBombError(SecurityError):
    """Raised when zip bomb attack is detected."""
    pass


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    Validate that a file path is safe and accessible.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Validated Path object
        
    Raises:
        SecurityError: If path is unsafe
    """
    path = Path(file_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if not path.is_file():
        raise SecurityError(f"Path is not a file: {path}")
    
    # Check file size
    file_size = path.stat().st_size
    if file_size > MAX_ARCHIVE_SIZE:
        raise FileSizeLimitError(
            f"File size ({file_size}) exceeds maximum allowed size ({MAX_ARCHIVE_SIZE})"
        )
    
    return path


def validate_archive_member(member: zipfile.ZipInfo, extract_to: Path) -> None:
    """
    Validate that an archive member is safe to extract.
    
    Args:
        member: ZipInfo object for the archive member
        extract_to: Directory where file will be extracted
        
    Raises:
        PathTraversalError: If path traversal is detected
        FileSizeLimitError: If file is too large
    """
    # Check for path traversal attempts
    if os.path.isabs(member.filename) or ".." in member.filename:
        raise PathTraversalError(
            f"Path traversal attempt detected in: {member.filename}"
        )
    
    # Construct the full extraction path
    full_path = (extract_to / member.filename).resolve()
    
    # Ensure the resolved path is still within the extraction directory
    if not str(full_path).startswith(str(extract_to.resolve())):
        raise PathTraversalError(
            f"Path traversal attempt detected: {member.filename} -> {full_path}"
        )
    
    # Check uncompressed size
    if member.file_size > MAX_EXTRACTED_SIZE:
        raise FileSizeLimitError(
            f"Uncompressed file size ({member.file_size}) exceeds limit ({MAX_EXTRACTED_SIZE})"
        )


def validate_archive_contents(archive_path: Path) -> List[zipfile.ZipInfo]:
    """
    Validate archive contents for security issues.
    
    Args:
        archive_path: Path to the archive file
        
    Returns:
        List of validated ZipInfo objects
        
    Raises:
        SecurityError: If archive contains security issues
    """
    try:
        with zipfile.ZipFile(archive_path, "r") as zip_file:
            members = zip_file.infolist()
            
            # Check number of files
            if len(members) > MAX_FILES_IN_ARCHIVE:
                raise ZipBombError(
                    f"Archive contains too many files ({len(members)} > {MAX_FILES_IN_ARCHIVE})"
                )
            
            total_uncompressed_size = 0
            total_compressed_size = 0
            
            for member in members:
                # Validate each member
                temp_dir = Path(tempfile.gettempdir())
                validate_archive_member(member, temp_dir)
                
                total_uncompressed_size += member.file_size
                total_compressed_size += member.compress_size
            
            # Check for zip bomb (high compression ratio)
            if total_compressed_size > 0:
                compression_ratio = total_uncompressed_size / total_compressed_size
                if compression_ratio > 100:  # More than 100:1 compression ratio
                    raise ZipBombError(
                        f"Suspicious compression ratio detected: {compression_ratio:.1f}:1"
                    )
            
            # Check total uncompressed size
            if total_uncompressed_size > MAX_EXTRACTED_SIZE:
                raise FileSizeLimitError(
                    f"Total uncompressed size ({total_uncompressed_size}) "
                    f"exceeds limit ({MAX_EXTRACTED_SIZE})"
                )
            
            return members
            
    except zipfile.BadZipFile as e:
        raise SecurityError(f"Invalid or corrupted archive: {e}")


@contextmanager
def secure_temp_directory() -> Generator[Path, None, None]:
    """
    Create a secure temporary directory with guaranteed cleanup.
    
    Yields:
        Path to the temporary directory
    """
    temp_dir = None
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix="bidoc_secure_"))
        yield temp_dir
    finally:
        # Ensure cleanup even if an exception occurs
        if temp_dir and temp_dir.exists():
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except Exception as cleanup_error:
                # Log cleanup failure but don't raise
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to cleanup temporary directory {temp_dir}: {cleanup_error}")


def safe_extract_archive_member(
    zip_file: zipfile.ZipFile, 
    member: zipfile.ZipInfo, 
    extract_to: Path,
    allowed_extensions: Optional[set] = None
) -> Path:
    """
    Safely extract a single member from an archive.
    
    Args:
        zip_file: Open ZipFile object
        member: ZipInfo for the member to extract
        extract_to: Directory to extract to
        allowed_extensions: Set of allowed file extensions
        
    Returns:
        Path to the extracted file
        
    Raises:
        SecurityError: If extraction is unsafe
    """
    # Validate the member
    validate_archive_member(member, extract_to)
    
    # Check file extension if specified
    if allowed_extensions:
        file_ext = Path(member.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise SecurityError(
                f"File extension '{file_ext}' not in allowed extensions: {allowed_extensions}"
            )
    
    # Extract the file
    zip_file.extract(member, extract_to)
    
    extracted_path = extract_to / member.filename
    return extracted_path.resolve()


def find_archive_members_by_extension(
    archive_path: Path, 
    extensions: List[str]
) -> List[zipfile.ZipInfo]:
    """
    Find archive members with specific extensions.
    
    Args:
        archive_path: Path to the archive
        extensions: List of file extensions to find (e.g., ['.twb', '.tds'])
        
    Returns:
        List of matching ZipInfo objects
    """
    validate_file_path(archive_path)
    members = validate_archive_contents(archive_path)
    
    matching_members = []
    for member in members:
        file_ext = Path(member.filename).suffix.lower()
        if file_ext in extensions:
            matching_members.append(member)
    
    return matching_members