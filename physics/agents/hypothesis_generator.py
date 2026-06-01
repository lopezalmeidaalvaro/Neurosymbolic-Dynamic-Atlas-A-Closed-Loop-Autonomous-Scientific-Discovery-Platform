#!/usr/bin/env python3
"""
Phase 2: Symbolic Hypothesis Generator Agent (HypoGen)
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import random
import re
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

class Hypothesis:
    def __init__(self, expression, confidence=0.5, metric_type="wormhole"):
        self.expression = expression
        self.confidence = confidence
        self.metric_type = metric_type

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        
    return previous_row[-1]

def similarity_score(s1, s2):
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2), 1)
    return 1.0 - (distance / max_len)

class HypothesisGenerator:
    """
    HypoGen Agent: Proposes symbolic mathematical ansatzes for metric shape functions
    using Context-Free Grammars (CFG) and Graph-Driven mutations.
    """
    def __init__(self, exploration_rate=0.4, similarity_threshold=0.85):
        self.exploration_rate = exploration_rate
        self.similarity_threshold = similarity_threshold
        
        # Define context-free grammar production rules
        self.grammar = {
            "Expr": [
                ["Term"],
                ["Expr", "+", "Term"],
                ["Expr", "-", "Term"]
            ],
            "Term": [
                ["Factor"],
                ["Term", "*", "Factor"],
                ["Term", "/", "Factor"]
            ],
            "Factor": [
                # Original basic factors
                ["Const"],
                ["Var"],
                ["tanh", "(", "Expr", ")"],
                ["exp", "(", "Expr", ")"],
                ["sin", "(", "Expr", ")"],
                ["(", "Expr", ")"],
                
                # Wormhole power laws and negative powers (A)
                ["pow", "(", "r", ",", "-1", ")"],
                ["pow", "(", "r", ",", "-2", ")"],
                ["pow", "(", "r", ",", "-3", ")"],
                ["pow", "(", "r", ",", "-4", ")"],
                ["r_0", "*", "pow", "(", "r_0", "/", "r", ",", "1", ")"],
                ["r_0", "*", "pow", "(", "r_0", "/", "r", ",", "2", ")"],
                ["r_0", "*", "pow", "(", "r_0", "/", "r", ",", "3", ")"],
                ["r_0", "*", "pow", "(", "r_0", "/", "r", ",", "4", ")"],
                ["Const", "*", "pow", "(", "r", ",", "-1.5", ")"],
                ["Const", "*", "pow", "(", "r", ",", "-2.5", ")"],
                
                # Warp tanh and sigmoid shapes (B)
                ["tanh", "(", "2.0", "*", "(", "r", "-", "0.5", ")", ")"],
                ["1.0", "-", "tanh", "(", "5.0", "*", "(", "r", "-", "0.5", ")", ")"],
                ["0.5", "*", "(", "1.0", "-", "tanh", "(", "12.0", "*", "(", "r", "-", "0.5", ")", ")", ")"],
                ["sigmoid", "(", "5.0", "*", "(", "r", "-", "0.5", ")", ")"],
                ["Const", "*", "tanh", "(", "3.0", "*", "(", "r", "-", "0.5", ")", ")", "+", "0.5"],
                
                # QG regularization shapes (C)
                ["pow", "(", "r", ",", "3", ")", "/", "(", "pow", "(", "r", ",", "3", ")", "+", "Const", ")"],
                ["pow", "(", "r", ",", "2", ")", "/", "(", "pow", "(", "r", ",", "2", ")", "+", "Const", ")"],
                ["pow", "(", "r", ",", "4", ")", "/", "(", "pow", "(", "r", ",", "4", ")", "+", "Const", ")"],
                ["1.0", "-", "exp", "(", "-", "pow", "(", "r", "/", "Const", ",", "2", ")", ")"],
                ["1.0", "-", "exp", "(", "-", "pow", "(", "r", "/", "Const", ",", "3", ")", ")"],
                
                # Mixed combinations (D)
                ["exp", "(", "-", "r", ")", "*", "tanh", "(", "r", ")"],
                ["pow", "(", "r", ",", "-2", ")", "/", "(", "1.0", "+", "r", ")"],
                ["tanh", "(", "r", ")", "/", "(", "1.0", "+", "pow", "(", "r", ",", "2", ")", ")"],
                ["(", "pow", "(", "r", ",", "-2", ")", "+", "Const", ")", "*", "exp", "(", "-", "2.0", "*", "r", ")"]
            ],
            "Const": [["0.5"], ["1.0"], ["1.5"], ["2.0"], ["3.0"], ["r_0"]],
            "Var": [["r"]]
        }

    def _generate_raw(self, symbol="Expr", depth=0, max_depth=3):
        """
        Recursively resolves the CFG grammar rules.
        """
        if depth >= max_depth:
            # Force terminal substitution to prevent stack overflows
            if symbol in ["Expr", "Term", "Factor"]:
                symbol = random.choice(["Const", "Var"])
                
        if symbol not in self.grammar:
            return symbol
            
        production = random.choice(self.grammar[symbol])
        result = []
        for sym in production:
            res = self._generate_raw(sym, depth + 1, max_depth)
            if res:
                result.append(res)
        return " ".join(result)

    def _clean_expression(self, expr):
        """
        Formats raw grammar strings into standard clean mathematical text.
        """
        expr = re.sub(r'\s+([\+\-\*/\(\),])\s+', r'\1', expr) # clean up commas too
        expr = expr.replace(" ( ", "(").replace(" ) ", ")")
        expr = expr.replace("tanh (", "tanh(").replace("exp (", "exp(").replace("sin (", "sin(").replace("sigmoid (", "sigmoid(").replace("pow (", "pow(")
        expr = re.sub(r'\s+', '', expr) # strip remaining spaces
        return expr

    def _mutate(self, base_expr):
        """
        Applies a random genetic mutation to a successful base expression.
        """
        # Mutate coefficients / constants
        mutated = base_expr
        constants = re.findall(r'[\d\.]+', base_expr)
        if constants:
            target = random.choice(constants)
            # Mutate slightly by multiplying by a factor in [0.7, 1.3]
            try:
                val = float(target)
                new_val = val * random.uniform(0.7, 1.3)
                mutated = mutated.replace(target, f"{new_val:.2f}", 1)
            except ValueError:
                pass
                
        # Mutate operators
        operators = ["+", "-", "*", "/"]
        for op in operators:
            if op in mutated and random.random() < 0.3:
                new_op = random.choice([o for o in operators if o != op])
                mutated = mutated.replace(op, new_op, 1)
                break
                
        return mutated

    def propose(self, context=None, metric_type="wormhole"):
        """
        Generates a novel Hypothesis. Balance exploration (CFG) vs exploitation (mutation).
        """
        if context is None:
            context = {"exploration_history": []}
            
        history = context.get("exploration_history", [])
        successful_eqs = [h["equation"] for h in history if "equation" in h]
        
        # Load from physical knowledge graph file if available
        kg_path = Path("physics/core/io/knowledge_graph.json")
        if kg_path.exists():
            try:
                import json
                with open(kg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for node in data.get("nodes", []):
                    if node.get("type") == "Success" and "equation" in node:
                        successful_eqs.append(node["equation"])
            except:
                pass

        # Dedicated logic for black holes to enforce physical regularizing boundary conditions f(0)=0, f(inf)=1
        if metric_type == "black_hole":
            templates = [
                "r**3 / (r**3 + {alpha})",
                "tanh(r**3 / {alpha})",
                "1.0 - exp(-r**3 / {alpha})",
                "r**3 / (r**3 + {alpha} * r_0)",
                "tanh(r**3 / ({alpha} * r_0**2))"
            ]
            attempts = 0
            while attempts < 50:
                attempts += 1
                alpha_val = random.choice([0.5, 1.0, 1.5, 2.0, 3.0])
                expr = random.choice(templates).format(alpha=alpha_val)
                
                is_novel = True
                for prev_eq in successful_eqs:
                    if similarity_score(expr, prev_eq) > self.similarity_threshold:
                        is_novel = False
                        break
                if is_novel:
                    return Hypothesis(expression=expr, confidence=0.75, metric_type="black_hole")
            # Fallback for regular black hole
            return Hypothesis(expression="r**3 / (r**3 + 1.0)", confidence=0.7, metric_type="black_hole")

        attempts = 0
        while attempts < 100:
            attempts += 1
            
            # Exploitation vs Exploration
            if successful_eqs and random.random() > self.exploration_rate:
                base = random.choice(successful_eqs)
                expr = self._mutate(base)
                conf = 0.85
            else:
                raw = self._generate_raw(max_depth=5)
                expr = self._clean_expression(raw)
                conf = 0.55
                
            # Novelty Check
            is_novel = True
            for prev_eq in successful_eqs:
                if similarity_score(expr, prev_eq) > self.similarity_threshold:
                    is_novel = False
                    break
                    
            if is_novel:
                return Hypothesis(expression=expr, confidence=conf, metric_type=metric_type)
                
        # Safeguard fallback
        return Hypothesis(expression="0.5*exp(-3.0*r**2)", confidence=0.5, metric_type=metric_type)

if __name__ == "__main__":
    print("[*] Levantando agente HypoGen...")
    generator = HypothesisGenerator()
    print("[+] Generador configurado con exito.")
    
    print("\n=== GENERANDO 10 HIPOTESIS NOVELES DE PRUEBA ===")
    mock_history = [{"equation": "b(r)=r_0*exp(-3.2*(r-0.5)^2)"}]
    context = {"exploration_history": mock_history}
    
    for i in range(10):
        hypo = generator.propose(context)
        print(f" -> Hipotesis {i+1:02d}: {hypo.expression:40s} | Confianza: {hypo.confidence:.2f}")
    print("================================================\n")
