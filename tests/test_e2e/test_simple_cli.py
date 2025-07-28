#!/usr/bin/env python3
"""
Simple CLI test to validate the framework.

This test creates an isolated database and tests basic CLI commands.
"""

import os
import subprocess
import tempfile
from pathlib import Path


def run_cli_command(args, db_path, project_root):
    """Run a CLI command with an isolated database."""
    cmd = ["poetry", "run", "python", "-m", "domotix.cli.main"] + args
    env = {**os.environ, "DOMOTIX_DB_PATH": db_path}

    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def main():
    """Simple CLI test."""
    print("🚀 Simple CLI test...")

    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    project_root = Path(__file__).parent.parent.parent

    try:
        # Test 1: List devices (empty database)
        print("📋 Test: List devices (empty database)")
        return_code, stdout, stderr = run_cli_command(
            ["device-list"], db_path, project_root
        )
        print(f"Return code: {return_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")

        if return_code == 0 and "No device registered" in stdout:
            print("✅ device-list test passed")
        else:
            print("❌ device-list test failed")
            return False

        # Test 2: Create a light
        print("\n💡 Test: Create a light")
        return_code, stdout, stderr = run_cli_command(
            ["device-add", "light", "Test Lampe", "--location", "Test"],
            db_path,
            project_root,
        )
        print(f"Return code: {return_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")

        if return_code == 0 and "created" in stdout:
            print("✅ device-add test passed")
        else:
            print("❌ device-add test failed")
            return False

        # Test 3: List devices (with 1 light)
        print("\n📋 Test: List devices (with 1 light)")
        return_code, stdout, stderr = run_cli_command(
            ["device-list"], db_path, project_root
        )
        print(f"Return code: {return_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")

        if return_code == 0 and "Test Lampe" in stdout:
            print("✅ device-list with data test passed")
        else:
            print("❌ device-list with data test failed")
            return False

        print("\n🎉 All basic CLI tests passed!")
        return True

    finally:
        # Cleanup
        try:
            os.unlink(db_path)
        except OSError:
            ...


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
