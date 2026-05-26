import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import re

# Blocked list of phrases (case-insensitive check)
BLOCKED_PHRASES = [
    "theory of everything",
    "proof of quantum gravity",
    "discovered fundamental law",
    "real spacetime",
    "unified field theory",
    "quantum spacetime emergence proven",
    "hawking radiation confirmed",
    "holographic principle verified"
]

# Defendable replacements dictionary
REPLACEMENTS = {
    "emergent spacetime": "emergent network geometry in toy model",
    "entanglement creates curvature": "entanglement correlates with discrete curvature in this model",
    "theory of everything": "simplified toy-model representation",
    "proof of quantum gravity": "empirical representation correlation in toy models",
    "discovered fundamental law": "observed empirical relation in toys",
    "real spacetime": "simulated toy spacetime",
    "unified field theory": "toy-model coupling",
    "quantum spacetime emergence proven": "emergent network geometry observed in this simulation",
    "hawking radiation confirmed": "analog Hawking temperature signature observed",
    "holographic principle verified": "Ryu-Takayanagi area-entropy scaling observed in this toy network"
}

def sanitize_hypothesis(text: str) -> str:
    """
    Scans hypothesis text, replaces forbidden phrases with scientifically defendable ones,
    and prepends the '[MODEL-SPECIFIC OBSERVATION]:' tag if violations are detected.
    """
    if not text:
        return ""
    
    original_text = text
    has_blocked = False
    
    # 1. Check for blocked list violations
    text_lower = text.lower()
    for phrase in BLOCKED_PHRASES:
        if phrase in text_lower:
            has_blocked = True
            break
            
    # 2. Perform defendable replacements
    sanitized = text
    for target, replacement in REPLACEMENTS.items():
        # Match case-insensitively but preserve replacement
        pattern = re.compile(re.escape(target), re.IGNORECASE)
        sanitized, count = pattern.subn(replacement, sanitized)
        if count > 0:
            has_blocked = True

    # 3. Add model-specific observation tag if flagged
    if has_blocked:
        prefix = "[MODEL-SPECIFIC OBSERVATION]: "
        if not sanitized.startswith(prefix):
            sanitized = prefix + sanitized
            
    return sanitized

def validate_hypothesis_structure(hypothesis_dict: dict) -> tuple:
    """
    Validates that a hypothesis complies strictly with the rigid JSON template constraints:
    - hypothesis: string (max 200 characters)
    - equation: string (max 1 equation, LaTeX format)
    - variables: list (max 3 elements)
    - falsification_test: string with explicit numerical criterion
    - confidence_prior: float between 0 and 1
    
    Supports key fallback mapping to remain compatible with generic AutonomousScientist structures.
    Returns (is_valid, errors).
    """
    errors = []
    
    if not isinstance(hypothesis_dict, dict):
        return False, ["Input is not a dictionary / JSON object."]

    # 1. Fetch values with fallbacks
    hyp_text = hypothesis_dict.get("hypothesis") or hypothesis_dict.get("hypothesis_text")
    equation = hypothesis_dict.get("equation") or hypothesis_dict.get("prediction")
    variables = hypothesis_dict.get("variables") or hypothesis_dict.get("variables_involved")
    falsification = hypothesis_dict.get("falsification_test") or hypothesis_dict.get("falsification_criterion")
    confidence = hypothesis_dict.get("confidence_prior")
    
    # 2. Validate hypothesis text
    if not hyp_text:
        errors.append("Missing required field: 'hypothesis'")
    elif not isinstance(hyp_text, str):
        errors.append("'hypothesis' must be a string")
    elif len(hyp_text) > 200:
        errors.append(f"'hypothesis' text length ({len(hyp_text)}) exceeds maximum of 200 characters")
        
    # 3. Validate equation (LaTeX)
    if not equation:
        errors.append("Missing required field: 'equation'")
    elif not isinstance(equation, str):
        errors.append("'equation' must be a string")
    else:
        # Check LaTeX delimiters count (should contain at most 1 LaTeX equation)
        # We search for pairs of $ or $$ or math environments like \begin{equation}
        single_dollar_count = len(re.findall(r"(?<!\$)\$(?!\$)", equation))
        double_dollar_count = equation.count("$$")
        latex_env_count = len(re.findall(r"\\begin\{", equation))
        
        # If there are multiple pairs, that indicates multiple equations
        total_equations = double_dollar_count + (single_dollar_count // 2) + latex_env_count
        if total_equations > 1:
            errors.append(f"'equation' must contain at most ONE equation (detected {total_equations} equations)")
            
    # 4. Validate variables list
    if variables is None:
        errors.append("Missing required field: 'variables'")
    elif not isinstance(variables, list):
        errors.append("'variables' must be a list")
    elif len(variables) > 3:
        errors.append(f"'variables' list size ({len(variables)}) exceeds maximum of 3 elements")
    else:
        for idx, var in enumerate(variables):
            if not isinstance(var, str):
                errors.append(f"Variable at index {idx} is not a string")
                
    # 5. Validate falsification test
    if not falsification:
        errors.append("Missing required field: 'falsification_test'")
    elif not isinstance(falsification, str):
        errors.append("'falsification_test' must be a string")
    else:
        # Check for explicit numerical criterion (comparison operators, numeric patterns, or statistical keys)
        has_operator = any(op in falsification for op in ["<", ">", "=", "!=", "<=", ">="])
        has_number = bool(re.search(r"\d", falsification))
        has_metric = any(m in falsification.lower() for m in ["p-value", "p >", "p <", "r^2", "correlation", "wasserstein", "z-score", "chi"])
        
        if not (has_operator or has_number or has_metric):
            errors.append("'falsification_test' must specify an explicit quantitative numerical rejection criterion")
            
    # 6. Validate confidence prior
    if confidence is None:
        errors.append("Missing required field: 'confidence_prior'")
    else:
        try:
            val = float(confidence)
            if not (0.0 <= val <= 1.0):
                errors.append(f"'confidence_prior' value ({val}) must be between 0.0 and 1.0 inclusive")
        except (ValueError, TypeError):
            errors.append("'confidence_prior' must be a float / number")
            
    is_valid = len(errors) == 0
    return is_valid, errors

def reality_check(report_path: str) -> dict:
    """
    Scans a generated markdown discovery report, counts violations of forbidden phrases,
    and returns lists of violations and suggested replacements.
    """
    violations = []
    suggestions = []
    
    if not os.path.exists(report_path):
        return {"violations_count": 0, "violations": [], "suggestions": [f"Report file {report_path} not found."]}
        
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        content_lower = content.lower()
        
        # 1. Scan for forbidden phrases
        for phrase in BLOCKED_PHRASES:
            # Case-insensitive count
            matches = len(re.findall(re.escape(phrase), content_lower))
            if matches > 0:
                violations.append({
                    "phrase": phrase,
                    "count": matches
                })
                
        # 2. Scan for overinterpretations
        for target, replacement in REPLACEMENTS.items():
            matches = len(re.findall(re.escape(target), content_lower))
            if matches > 0:
                suggestions.append(f"Replace '{target}' with '{replacement}' ({matches} occurrences)")
                
    except Exception as e:
        suggestions.append(f"Error reading report file: {e}")
        
    violations_count = sum(v["count"] for v in violations)
    return {
        "violations_count": violations_count,
        "violations": violations,
        "suggestions": suggestions
    }

if __name__ == "__main__":
    print("Testing Scientific Guard...")
    
    # Test sanitization
    h1 = "This provides proof of quantum gravity and emergent spacetime in our real spacetime."
    print("Original Hypothesis: ", h1)
    print("Sanitized:           ", sanitize_hypothesis(h1))
    print("-" * 80)
    
    # Test structural validation
    valid_hyp = {
        "hypothesis": "The Betti-1 curvature exhibits a stable linear relationship with entanglement entropy.",
        "equation": "$S_{ent} \\approx \\beta \\cdot K_{betti} + \\alpha$",
        "variables": ["entropy", "curvature"],
        "falsification_test": "R^2 < 0.70",
        "confidence_prior": 0.85
    }
    is_v, errs = validate_hypothesis_structure(valid_hyp)
    print(f"Valid Hypothesis Check: is_valid={is_v}, errors={errs}")
    
    invalid_hyp = {
        "hypothesis_text": "This is way too long of a hypothesis. " * 10,  # exceeds 200 chars
        "prediction": "$S = A$ and also $S = k \\log(W)$",  # two equations
        "variables_involved": ["a", "b", "c", "d"],  # > 3 variables
        "falsification_criterion": "The metric looks bad",  # no quantitative criterion
        "confidence_prior": 1.5  # not in [0, 1]
    }
    is_v, errs = validate_hypothesis_structure(invalid_hyp)
    print(f"Invalid Hypothesis Check: is_valid={is_v}")
    print("Errors discovered:")
    for err in errs:
        print(f"  - {err}")
