#!/usr/bin/env python3
"""
Test CLI simple pour valider le framework.

Ce test crée une base de données isolée et teste les commandes CLI de base.
"""

import os
import subprocess
import tempfile
from pathlib import Path


def run_cli_command(args, db_path, project_root):
    """Execute une commande CLI avec une base de données isolée."""
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
    """Test CLI simple."""
    print("🚀 Test CLI simple...")

    # Créer une base de données temporaire
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    project_root = Path(__file__).parent.parent.parent

    try:
        # Test 1: Lister les dispositifs (base vide)
        print("📋 Test: Liste des dispositifs (base vide)")
        return_code, stdout, stderr = run_cli_command(
            ["device-list"], db_path, project_root
        )
        print(f"Return code: {return_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")

        if return_code == 0 and "Aucun dispositif enregistré" in stdout:
            print("✅ Test device-list réussi")
        else:
            print("❌ Test device-list échoué")
            return False

        # Test 2: Créer une lampe
        print("\n💡 Test: Création d'une lampe")
        return_code, stdout, stderr = run_cli_command(
            ["device-add", "light", "Test Lampe", "--location", "Test"],
            db_path,
            project_root,
        )
        print(f"Return code: {return_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")

        if return_code == 0 and "créée" in stdout:
            print("✅ Test device-add réussi")
        else:
            print("❌ Test device-add échoué")
            return False

        # Test 3: Lister les dispositifs (avec 1 lampe)
        print("\n📋 Test: Liste des dispositifs (avec 1 lampe)")
        return_code, stdout, stderr = run_cli_command(
            ["device-list"], db_path, project_root
        )
        print(f"Return code: {return_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")

        if return_code == 0 and "Test Lampe" in stdout:
            print("✅ Test device-list avec donnée réussi")
        else:
            print("❌ Test device-list avec donnée échoué")
            return False

        print("\n🎉 Tous les tests CLI de base sont réussis !")
        return True

    finally:
        # Nettoyer
        try:
            os.unlink(db_path)
        except OSError:
            ...


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
