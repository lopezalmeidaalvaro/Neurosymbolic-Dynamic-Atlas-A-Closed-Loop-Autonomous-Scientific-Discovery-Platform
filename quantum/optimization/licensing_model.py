from typing import Any, Dict


def estimate_licensing_revenue(portfolio_value: Dict[str, Any]) -> Dict[str, float]:
    ip_value = float(portfolio_value.get("estimated_IP_value", 0.0) or 0.0)
    transferability = float(portfolio_value.get("transferability_score", 0.0) or 0.0)
    small_startup_license = max(25000.0, 0.08 * ip_value)
    enterprise_annual_license = max(150000.0, 0.35 * ip_value)
    cloud_api_usage = max(50000.0, 250000.0 * transferability)
    oem_compiler_integration = max(300000.0, 0.75 * ip_value)
    annual_revenue_potential = (
        5 * small_startup_license
        + 3 * enterprise_annual_license
        + cloud_api_usage
        + oem_compiler_integration
    )
    return {
        "small_startup_license": small_startup_license,
        "enterprise_annual_license": enterprise_annual_license,
        "cloud_api_usage": cloud_api_usage,
        "oem_compiler_integration": oem_compiler_integration,
        "annual_revenue_potential": annual_revenue_potential,
    }
