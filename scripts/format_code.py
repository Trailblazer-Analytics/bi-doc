#!/usr/bin/env python3
"""Code formatting and quality check script for BI Documentation Tool.

This script provides a consistent way to format code and run quality checks
across the entire codebase. It serves as a wrapper around the various tools
configured in pyproject.toml and pre-commit-config.yaml.

Usage:
    python scripts/format_code.py --check      # Check only, don't modify
    python scripts/format_code.py --fix        # Format and fix issues
    python scripts/format_code.py --all        # Run all checks and formatting
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class CodeFormatter:
    """Code formatting and quality checker."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.bidoc_dir = project_root / "bidoc"
        self.tests_dir = project_root / "tests"
        
    def run_command(self, cmd: List[str], description: str) -> bool:
        """Run a command and return success status."""
        print(f"Running {description}...")
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"✅ {description} passed")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                print(f"❌ {description} failed")
                if result.stdout.strip():
                    print("STDOUT:", result.stdout)
                if result.stderr.strip():
                    print("STDERR:", result.stderr)
                return False
                
        except FileNotFoundError:
            print(f"❌ {description} failed - tool not installed")
            return False
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed - command returned non-zero exit status {e.returncode}")
            if e.output:
                print("OUTPUT:", e.output)
            if e.stderr:
                print("STDERR:", e.stderr)
            return False
    
    def format_with_black(self, check_only: bool = False) -> bool:
        """Format code with Black."""
        cmd = ["python", "-m", "black"]
        if check_only:
            cmd.extend(["--check", "--diff"])
        cmd.extend(["--line-length=88", str(self.bidoc_dir), str(self.tests_dir)])
        
        return self.run_command(cmd, "Black formatting")
    
    def sort_imports(self, check_only: bool = False) -> bool:
        """Sort imports with isort."""
        cmd = ["python", "-m", "isort"]
        if check_only:
            cmd.append("--check-only")
        cmd.extend([
            "--profile=black", 
            "--line-length=88",
            str(self.bidoc_dir), 
            str(self.tests_dir)
        ])
        
        return self.run_command(cmd, "Import sorting (isort)")
    
    def lint_with_ruff(self, fix: bool = False) -> bool:
        """Lint code with Ruff."""
        cmd = ["python", "-m", "ruff", "check"]
        if fix:
            cmd.append("--fix")
        cmd.extend([str(self.bidoc_dir), str(self.tests_dir)])
        
        return self.run_command(cmd, "Linting (Ruff)")
    
    def type_check(self) -> bool:
        """Type check with MyPy."""
        cmd = ["python", "-m", "mypy", str(self.bidoc_dir)]
        return self.run_command(cmd, "Type checking (MyPy)")
    
    def security_check(self) -> bool:
        """Security check with Bandit."""
        cmd = [
            "python", "-m", "bandit", 
            "-r", str(self.bidoc_dir),
            "-f", "json",
            "--exclude", str(self.tests_dir)
        ]
        return self.run_command(cmd, "Security check (Bandit)")
    
    def run_tests(self) -> bool:
        """Run tests with pytest."""
        cmd = [
            "python", "-m", "pytest", 
            str(self.tests_dir),
            "-v", 
            "--tb=short"
        ]
        return self.run_command(cmd, "Unit tests (pytest)")
    
    def run_coverage(self) -> bool:
        """Run tests with coverage."""
        cmd = [
            "python", "-m", "pytest",
            "--cov=bidoc",
            "--cov-report=term-missing",
            "--cov-report=html",
            str(self.tests_dir)
        ]
        return self.run_command(cmd, "Test coverage")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Code formatting and quality checks for BI Documentation Tool"
    )
    parser.add_argument(
        "--check", 
        action="store_true",
        help="Check formatting and code quality without making changes"
    )
    parser.add_argument(
        "--fix",
        action="store_true", 
        help="Format code and fix auto-fixable issues"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all checks and formatting (implies --fix)"
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip running tests"
    )
    
    args = parser.parse_args()
    
    # Default to check mode if no args provided
    if not any([args.check, args.fix, args.all]):
        args.check = True
    
    project_root = Path(__file__).parent.parent
    formatter = CodeFormatter(project_root)
    
    results = []
    
    print("🔍 BI Documentation Tool - Code Quality Check")
    print("=" * 50)
    
    if args.all or args.fix:
        # Format and fix mode
        results.append(formatter.format_with_black(check_only=False))
        results.append(formatter.sort_imports(check_only=False))
        results.append(formatter.lint_with_ruff(fix=True))
    elif args.check:
        # Check only mode
        results.append(formatter.format_with_black(check_only=True))
        results.append(formatter.sort_imports(check_only=True))
        results.append(formatter.lint_with_ruff(fix=False))
    
    # Always run type checking and security checks
    results.append(formatter.type_check())
    results.append(formatter.security_check())
    
    # Run tests unless explicitly skipped
    if not args.no_tests:
        results.append(formatter.run_tests())
        if args.all:
            results.append(formatter.run_coverage())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} checks passed!")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} of {total} checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()