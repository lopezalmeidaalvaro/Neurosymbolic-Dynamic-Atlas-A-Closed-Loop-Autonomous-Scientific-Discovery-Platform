import os
import sys

ALLOWED_FOLDERS = {
    ".github",
    ".agent",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".vscode",
    ".idea",
    "quantum",
    "physics",
    "satellite",
    "mathematics",
    "core",
    "dashboard",
    "docs",
    "papers",
    "tests",
    "config",
}

ALLOWED_FILES = {
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "pyproject.toml",
    "requirements.txt",
    ".gitignore",
    ".pre-commit-config.yaml",
    "LEAN4_AUDIT_REPORT.md",
    "LEAN4_INSTALLATION_REPORT.md",
    "QFT_ROUTING_FIX_REPORT.md",
    "QFT_FIX_EQUIVALENCE_VERIFICATION.md",
}

def check_root():
    # Use the parent directory of core/scripts/ as root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    offending_paths = []
    
    for entry in os.listdir(project_root):
        path = os.path.join(project_root, entry)
        if os.path.isdir(path):
            if entry not in ALLOWED_FOLDERS:
                offending_paths.append(entry + "/")
        else:
            if entry not in ALLOWED_FILES:
                offending_paths.append(entry)
                
    if offending_paths:
        print("ERROR: Repository root polluted.\n")
        print("Unexpected entries:")
        for path in offending_paths:
            print(f"  - {path}")
        print("\nPlease move files/folders into their owning domain.")
        sys.exit(1)
    else:
        print("SUCCESS: Repository root is clean.")
        sys.exit(0)

if __name__ == "__main__":
    check_root()
