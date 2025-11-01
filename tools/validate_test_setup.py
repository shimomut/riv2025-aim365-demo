#!/usr/bin/env python3
"""
Validation script to ensure the testing framework is properly set up.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {str(e)}")
        return False


def check_file_exists(filepath, description):
    """Check if a file exists."""
    print(f"🔍 {description}...")
    if Path(filepath).exists():
        print(f"✅ {description} - OK")
        return True
    else:
        print(f"❌ {description} - MISSING: {filepath}")
        return False


def main():
    print("🧪 Validating HyperPod Testing Framework Setup")
    print("=" * 60)
    
    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    checks = []
    
    # Check required files
    checks.append(check_file_exists("tools/test_hyperpod_cluster.py", "Testing script exists"))
    checks.append(check_file_exists("Makefile", "Makefile exists"))
    checks.append(check_file_exists("FSDP/kubernetes/fsdp-hpto.yaml", "Job configuration exists"))
    checks.append(check_file_exists("doc/HYPERPOD_TESTING_GUIDE.md", "Testing guide exists"))
    
    # Check Python script is executable
    checks.append(run_command("python3 tools/test_hyperpod_cluster.py --help", "Testing script is executable"))
    
    # Check kubectl is available
    checks.append(run_command("kubectl version --client", "kubectl is available"))
    
    # Check make commands are available
    checks.append(run_command("make help", "Makefile commands are available"))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print("\n🚀 Ready to test! Try running:")
        print("   make validate-setup")
        print("   make test-quick")
        return 0
    else:
        print(f"❌ Some checks failed ({passed}/{total})")
        print("\n🔧 Please fix the issues above before testing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())