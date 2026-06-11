import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression


def deterministic_symbolic_recovery(X, y, feature_names=None):
    """
    Highly robust SINDy-style Lasso term matcher. Used as a resilient fallback
    if Julia/PySR is unavailable. Returns a simplified math string.
    """
    n_samples, n_features = X.shape
    if feature_names is None:
        feature_names = [f"x{i}" for i in range(n_features)]

    terms = []
    term_names = []

    # Constant
    terms.append(np.ones(n_samples))
    term_names.append("1")

    # Linear
    for i in range(n_features):
        terms.append(X[:, i])
        term_names.append(feature_names[i])

    # Quadratic & Cubic
    for i in range(n_features):
        terms.append(X[:, i] ** 2)
        term_names.append(f"{feature_names[i]}**2")
        terms.append(X[:, i] ** 3)
        term_names.append(f"{feature_names[i]}**3")

    # Cross terms
    for i in range(n_features):
        for j in range(i + 1, n_features):
            terms.append(X[:, i] * X[:, j])
            term_names.append(f"{feature_names[i]} * {feature_names[j]}")

    # Trig functions
    for i in range(n_features):
        terms.append(np.sin(X[:, i]))
        term_names.append(f"sin({feature_names[i]})")
        terms.append(np.cos(X[:, i]))
        term_names.append(f"cos({feature_names[i]})")

    Phi = np.column_stack(terms)

    # Sparse identification using Lasso
    clf = Lasso(alpha=0.01, max_iter=3000, random_state=42)
    clf.fit(Phi, y)
    coefs = clf.coef_

    expr_parts = []
    for val, name in zip(coefs, term_names):
        if abs(val) > 0.005:
            rounded = round(val, 2)
            if name == "1":
                expr_parts.append(f"{rounded}")
            else:
                expr_parts.append(f"{rounded}*{name}")

    if not expr_parts:
        # Fallback to standard linear regression if Lasso was too aggressive
        clf_ols = LinearRegression()
        clf_ols.fit(Phi[:, 1 : 1 + n_features], y)
        for val, name in zip(clf_ols.coef_, feature_names):
            if abs(val) > 0.005:
                expr_parts.append(f"{round(val, 2)}*{name}")

    expr_str = " + ".join(expr_parts) if expr_parts else "0"
    expr_str = expr_str.replace(" + -", " - ")
    return expr_str
