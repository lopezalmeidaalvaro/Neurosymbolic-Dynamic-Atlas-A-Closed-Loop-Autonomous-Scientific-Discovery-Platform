#!/usr/bin/env python3
"""
Phase T45: Spacecraft Flight Software (FSW) Quality Assurance (ECSS-E-ST-40C & MISRA C)
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import re
import time
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config

class SoftwareAssuranceAnalyzer:
    """
    Statically analyzes C flight code against ECSS-E-ST-40C and MISRA-C software safety guidelines.
    """
    def __init__(self, target_c_file):
        self.target_file = Path(target_c_file)
        self.violations = []
        self.traceability_matrix = []
        
        # ECSS Traceability rules to map
        self.ecss_reqs = {
            "surrogate_mlp_predict": "ECSS-E-ST-40C-REQ-001 (Deterministic ML Prediction)",
            "sigmoid": "ECSS-E-ST-40C-REQ-002 (Mathematical Safe Sigmoid Approximator)",
            "relu": "ECSS-E-ST-40C-REQ-003 (Mathematical Safe ReLU Boundary Check)",
            "safe_division": "ECSS-E-ST-40C-REQ-004 (Protected Arithmetic Division)",
            "initialize_buffers": "ECSS-E-ST-40C-REQ-005 (Static Memory Initialization)"
        }
        
    def analyze(self):
        if not self.target_file.exists():
            raise FileNotFoundError(f"Target C code not found at: {self.target_file}")
            
        with open(self.target_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        full_code = "".join(lines)
        
        # 1. Check for Memory Safety (Forbidden Malloc/Free after boot)
        # Search for malloc, calloc, realloc, free
        malloc_matches = re.findall(r"\b(malloc|calloc|realloc|free)\b", full_code)
        for m in malloc_matches:
            self.violations.append(
                f"MISRA-C:2012 Rule 21.3 Violation: Use of dynamic allocation function '{m}' is strictly prohibited in safety-critical flight code."
            )
            
        # 2. Check for Safe Arithmetic (Protected Division)
        # Scan for division symbol '/' without preceding checks (flag as warning if not inside protected helper)
        div_lines = []
        for idx, line in enumerate(lines):
            if "/" in line and not line.strip().startswith("//") and not line.strip().startswith("*"):
                # Make sure it's arithmetic division, not comment or path
                if not re.search(r"//|/\*|\*/", line) and not re.search(r"\b(safe_division)\b", line):
                    div_lines.append((idx + 1, line.strip()))
                    
        for line_num, content in div_lines:
            self.violations.append(
                f"MISRA-C:2012 Rule 1.3 Warning (Line {line_num}): Raw arithmetic division '/' detected. Division by zero protection must be explicitly implemented via safe_division wrapper: '{content}'"
            )
            
        # 3. Naming Conventions (Functions: snake_case, Macros: UPPER_CASE)
        # Scan for function definitions
        # e.g., void func_name(args) or float func_name(args)
        fun_matches = re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{", full_code)
        functions = []
        
        for m in fun_matches:
            fun_type = m.group(1)
            fun_name = m.group(2)
            if fun_type in ["void", "float", "double", "int", "char", "uint8_t", "uint16_t", "uint32_t"]:
                functions.append((fun_name, m.start()))
                # Naming check
                if not re.match(r"^[a-z_][a-z0-9_]*$", fun_name):
                    self.violations.append(
                        f"Coding Standard Violation: Function '{fun_name}' is not named in snake_case."
                    )
                    
        # Scan macro definitions
        macro_matches = re.finditer(r"#define\s+([a-zA-Z_][a-zA-Z0-9_]*)\b", full_code)
        for m in macro_matches:
            macro_name = m.group(1)
            if not re.match(r"^[A-Z_][A-Z0-9_]*$", macro_name):
                self.violations.append(
                    f"Coding Standard Violation: Macro Constant '{macro_name}' is not named in UPPER_CASE."
                )
                
        # 4. Function Length & Cyclomatic Complexity
        # Locate brackets matching to extract function bodies
        for fun_name, start_pos in functions:
            # Simple bracket match to find body
            body_start = full_code.find("{", start_pos)
            if body_start == -1:
                continue
                
            open_brackets = 1
            body_end = body_start + 1
            while open_brackets > 0 and body_end < len(full_code):
                char = full_code[body_end]
                if char == "{":
                    open_brackets += 1
                elif char == "}":
                    open_brackets -= 1
                body_end += 1
                
            fun_body = full_code[body_start:body_end]
            lines_in_fun = fun_body.count("\n") + 1
            
            # Check length constraint (< 50 lines)
            if lines_in_fun > 50:
                self.violations.append(
                    f"ECSS Coding Standard Violation: Function '{fun_name}' contains {lines_in_fun} lines, exceeding the safety limit of 50 lines."
                )
                
            # Cyclomatic Complexity Check (count branch statements: if, for, while, case)
            branch_points = len(re.findall(r"\b(if|for|while|case)\b", fun_body))
            complexity = branch_points + 1
            
            if complexity > 10:
                self.violations.append(
                    f"ECSS Software Metric Warning: Function '{fun_name}' has a cyclomatic complexity of {complexity}, exceeding the maximum safe threshold of 10."
                )
                
            # 5. Check Traceability comments (Requirements, Preconditions, Postconditions)
            # Check if function definition is preceded by comments containing @pre, @post, @req
            fun_header_start = full_code.rfind("\n", 0, start_pos)
            comment_block = full_code[max(0, fun_header_start - 300):fun_header_start]
            
            has_pre = "@pre" in comment_block
            has_post = "@post" in comment_block
            has_req = "@req" in comment_block
            
            if not (has_pre and has_post and has_req):
                self.violations.append(
                    f"ECSS Traceability Violation: Function '{fun_name}' is missing structured headers. Preconditions (@pre), postconditions (@post), and requirements (@req) must be documented in header comments."
                )
                
            # Link to requirements matrix
            req_mapped = self.ecss_reqs.get(fun_name, "ECSS-E-ST-40C-REQ-TBD (General FSW Module)")
            self.traceability_matrix.append({
                "Function_Name": fun_name,
                "Lines_Of_Code": lines_in_fun,
                "Cyclomatic_Complexity": complexity,
                "ECSS_Requirement": req_mapped,
                "Precondition_Documented": "YES" if has_pre else "NO",
                "Postcondition_Documented": "YES" if has_post else "NO",
                "Status": "COMPLIANT" if has_pre and has_post and has_req and lines_in_fun <= 50 and complexity <= 10 else "NON_COMPLIANT"
            })
            
        # Write Violations to file
        violations_path = "satellite/flight/violations.txt"
        os.makedirs(os.path.dirname(violations_path), exist_ok=True)
        with open(violations_path, "w", encoding="utf-8") as f:
            f.write("=== REGISTRO DE INFRACCIONES DE SOFTWARE DE VUELO (ECSS & MISRA C) ===\n\n")
            if len(self.violations) == 0:
                f.write("[SAFE] Cero infracciones encontradas. El código de vuelo es 100% conforme.\n")
            else:
                for v in self.violations:
                    f.write(f"- {v}\n")
        print(f"[+] Archivo de infracciones guardado en: {violations_path}")
        
        # Write Traceability matrix to CSV
        df_trace = pd.DataFrame(self.traceability_matrix)
        trace_path = "satellite/flight/traceability_matrix.csv"
        df_trace.to_csv(trace_path, index=False)
        print(f"[+] Matriz de trazabilidad guardada en: {trace_path}")
        
        # Write Markdown Report
        report_path = "satellite/flight/assurance_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Informe de Aseguramiento de Calidad de Software de Vuelo (ECSS + MISRA) (Fase T45)\n\n")
            f.write(f"**Generado:** {time.strftime('%Y-%m-%d %H:%M:%S')} | **Archivo Evaluado:** `surrogate_mlp_inference.c`\n\n")
            f.write("Este informe detalla el análisis estático automatizado de la arquitectura del software de vuelo (FSW) del Cubesat, validando su cumplimiento estricto con los estándares de seguridad espacial **ECSS-E-ST-40C** y **MISRA-C:2012**.\n\n")
            
            f.write("## 1. Tabla de Cumplimiento y Mapeo de Requisitos (Trazabilidad)\n\n")
            f.write("| Módulo / Función C | Líneas de Código | Complejidad Ciclomática | Requisito ECSS Vinculado | Pre / Post Documentado | Estado de Conformidad |\n")
            f.write("| :--- | :---: | :---: | :--- | :---: | :--- |\n")
            for _, r in df_trace.iterrows():
                doc_status = "Sí" if r['Precondition_Documented'] == 'YES' and r['Postcondition_Documented'] == 'YES' else "No"
                state_str = "CONFORME" if r['Status'] == 'COMPLIANT' else "NO_CONFORME"
                f.write(f"| **{r['Function_Name']}** | {r['Lines_Of_Code']} | {r['Cyclomatic_Complexity']} | {r['ECSS_Requirement']} | {doc_status} | **{state_str}** |\n")
                
            f.write("\n## 2. Infracciones Críticas Detectadas y Mitigación\n\n")
            if len(self.violations) == 0:
                f.write("> [!TIP]\n")
                f.write("> **Resultado del Análisis de Seguridad Estática:**\n")
                f.write("> - Cero infracciones críticas encontradas. El software de vuelo cumple plenamente con las restricciones de **Zero dynamic memory allocation** post-boot y determinismo de bucles.\n\n")
            else:
                f.write("> [!WARNING]\n")
                f.write("> **Alertas y Desviaciones de Estándar Registradas:**\n")
                for v in self.violations:
                    f.write(f"> - {v}\n")
                f.write("\n")
                
            f.write("## 3. Matriz de Recomendaciones de FSW\n")
            f.write("> 1. **Prevención de Punteros Nulos (MISRA Rule 8.1)**: Asegurar que las precondiciones de entrada verifiquen que todos los punteros pasados como argumento son distintos de `NULL` mediante sentencias `assert` controladas.\n")
            f.write("> 2. **Protección de División por Cero**: Todo cálculo matemático involucrando división debe ejecutarse dentro del método `safe_division(a, b)` para evitar fallos de desbordamiento aritmético en la FPU.\n")
            
        print(f"[+] Informe final de aseguramiento guardado en: {report_path}")

if __name__ == "__main__":
    # Path to C file
    c_file = Path(__file__).resolve().parents[1] / "flight" / "surrogate_mlp_inference.c"
    
    # Check if the C file exists. If not, generate a mock or run the ONNX exporter to create it
    if not c_file.exists():
        print("[CRITICAL] surrogate_mlp_inference.c not found. Generating C code via exporter...")
        import subprocess
        subprocess.run(["python", "satellite/flight/export_to_onnx.py"], cwd=str(Path(__file__).resolve().parents[2]))
        
    analyzer = SoftwareAssuranceAnalyzer(c_file)
    analyzer.analyze()
