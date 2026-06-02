# Hashes de Integridad de la Fase 0B (Fase 0C.4)

Este documento registra los hashes SHA256 verificables para los 6 nuevos archivos Python creados durante la Fase 0B (Abstracciones y Adaptadores).

---

## Hashes SHA256 de los Archivos Creados

```
core/abstractions/base_hypothesis_generator.py: 1e1a0320bd9642184179e25385c25b60e566ec78316a6d18ade7dcee2adce761
core/abstractions/base_critic.py: 037f6574e649976b3876cf29d43ed3224c6439d3e7da309870289908340c225c
core/abstractions/base_sandbox.py: 41e98696a806fd1756d50b8cb05c1c21bc5efa91c43b406ec01aefb7f61c35c7
core/abstractions/base_memory.py: 8f92621183590489ebbb2abf1e1577c0cb4b45d2bad19bf5782a254356c1eb93
physics/adapters/classical_hypothesis_generator.py: cf446eeff7805f8878fe34d8b9cf7d25d6d8cfa5d29388a4e17b53d3b0a4a904
physics/adapters/classical_physics_critic.py: b2b18a2d9b3d1e74782e0fae2d2902954c5e88fe6efdd64d021220afe7855d89
```

---

## Verificación de Hashes
Para comprobar la integridad de estos archivos de forma independiente, ejecute en PowerShell:
```powershell
Get-FileHash -Algorithm SHA256 -Path "ruta/del/archivo"
```
o en Linux/macOS:
```bash
sha256sum "ruta/del/archivo"
```
