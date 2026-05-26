import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import subprocess
import sys
import importlib
import socket

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def check_and_install(package, import_name):
    """
    Checks if a package is installed. If not, installs it via pip.
    """
    print(f"Checking package '{package}'...")
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, "__version__", "unknown")
        print(f"  Package '{package}' is already installed (version: {version})")
        return True, version
    except ImportError:
        print(f"  Package '{package}' is not installed. Installing via pip...")
        try:
            cmd = [sys.executable, "-m", "pip", "install", package]
            subprocess.check_call(cmd)
            module = importlib.import_module(import_name)
            version = getattr(module, "__version__", "unknown")
            print(f"  Successfully installed '{package}' (version: {version})")
            return True, version
        except Exception as e:
            print(f"  [ERROR] Failed to install '{package}': {e}")
            return False, str(e)


def print_neo4j_installation_guide():
    """
    Prints a friendly, detailed Neo4j local setup guide for Windows.
    """
    print("\n" + "=" * 70)
    print("NEO4J GRAPH DATABASE LOCAL INSTALLATION GUIDE:")
    print("=" * 70)
    print("Para habilitar la memoria cientifica de Fase 3, se requiere Neo4j:")
    print("1. Descarga Neo4j Desktop desde: https://neo4j.com/download/")
    print("2. Instala e inicia la aplicacion Neo4j Desktop.")
    print("3. Crea un nuevo 'Project' y añade una base de datos local (Local DBMS).")
    print("4. Configura el DBMS local con los siguientes valores:")
    print("     - Versión: 5.x o la mas reciente disponible")
    print("     - Database Name: neo4j")
    print("     - Password: password  (o la contraseña que prefieras)")
    print("5. Haz clic en 'Start' para arrancar la base de datos.")
    print("6. La base de datos estara disponible en bolt://localhost:7687")
    print("=" * 70 + "\n")


def test_neo4j_connection(
    uri="bolt://localhost:7687", user="neo4j", password="password"
):
    """
    Attempts to connect to Neo4j and execute a simple test query.
    """
    print(f"Testing Neo4j connection at '{uri}'...")
    try:
        from neo4j import GraphDatabase

        # Perform a quick socket check to avoid hanging if the server is completely down
        host = "localhost"
        port = 7687
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((host, port))
            sock.close()
        except Exception:
            print(
                f"  [CONNECTION TIMEOUT] Socket connection failed on host {host}:{port}."
            )
            return False, "Neo4j local server is not listening on port 7687."

        # Actual driver connection test
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 AS val")
            record = result.single()
            if record and record["val"] == 1:
                print(
                    "  [SUCCESS] Successfully connected to Neo4j and executed 'RETURN 1'!"
                )
                driver.close()
                return True, "Connected successfully"
        driver.close()
        return False, "Failed to fetch correct response."
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        return False, str(e)


def main():
    print("=" * 60)
    print("STARTING FASE 3 ENVIRONMENT SETUP")
    print("=" * 60)

    dependencies = [
        ("neo4j>=5.0", "neo4j"),
        ("networkx", "networkx"),
        ("matplotlib", "matplotlib"),
    ]

    success_list = []
    failed_list = []

    for pkg, imp_name in dependencies:
        success, info = check_and_install(pkg, imp_name)
        if success:
            success_list.append((pkg, info))
        else:
            failed_list.append((pkg, info))

    print("\n" + "=" * 60)
    print("INSTALLATION SUMMARY:")
    print("=" * 60)
    for pkg, ver in success_list:
        print(f"  - {pkg}: INSTALLED (version: {ver})")
    for pkg, err in failed_list:
        print(f"  - {pkg}: FAILED ({err})")

    print("\n" + "=" * 60)
    print("CHECKING NEO4J SERVER STATUS:")
    print("=" * 60)

    # Check status with command line (optional fallback check)
    try:
        # On Windows, we can query tasklist or services, but socket/bolt driver is much more reliable
        res = subprocess.run(
            ["neo4j", "status"], capture_output=True, text=True, timeout=5
        )
        print("Neo4j status command output:")
        print(res.stdout or res.stderr or "No output.")
    except Exception:
        print(
            "Neo4j CLI command is not available in PATH (normal if installing via Desktop app)."
        )

    # Main driver connection test
    connected, conn_msg = test_neo4j_connection()

    print("\n" + "=" * 60)
    if not failed_list:
        if connected:
            print("Entorno de Fase 3 verificado - Neo4j ONLINE")
        else:
            print("Entorno de Fase 3 verificado - Neo4j OFFLINE (Librerías listas)")
            print_neo4j_installation_guide()
    else:
        failed_names = [f[0] for f in failed_list]
        print(f"Algunas dependencias fallaron: {failed_names}")
    print("=" * 60)


if __name__ == "__main__":
    main()
