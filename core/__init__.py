import os
import sys

# Ensure this package can find submodules from other directories named 'core'
__path__ = [os.path.dirname(os.path.abspath(__file__))]

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for domain in ["physics", "satellite", "satellite", "quantum"]:
    domain_core = os.path.join(base_dir, domain, "core")
    if os.path.exists(domain_core):
        if domain_core not in __path__:
            __path__.append(domain_core)
