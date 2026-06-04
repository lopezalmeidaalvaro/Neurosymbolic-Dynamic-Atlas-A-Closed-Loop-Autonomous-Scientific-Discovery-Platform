import os
import sys
from typing import Dict, Any

from quantum.external_audit.forensic_export_engine import ForensicExportEngine
from quantum.external_audit.chain_of_custody import ChainOfCustodyVerifier
from quantum.external_audit.hostile_leakage_audit import HostileLeakageAudit
from quantum.external_audit.circular_validation_audit import CircularValidationAudit
from quantum.external_audit.red_team_reimplementation import RedTeamReimplementation
from quantum.external_audit.double_blind_reproduction import DoubleBlindReproduction
from quantum.external_audit.adversarial_model_tournament import AdversarialModelTournament
from quantum.external_audit.external_hardware_challenge import ExternalHardwareChallenge
from quantum.external_audit.independent_physics_review import IndependentPhysicsReview
from quantum.external_audit.external_review_panel import ExternalReviewPanel
from quantum.external_audit.meta_reproduction_engine import MetaReproductionEngine
from quantum.external_audit.external_epistemic_verdict import ExternalEpistemicVerdict

def run_full_external_audit(project_root: str) -> str:
    print("=" * 60)
    print("  PHASE X -- EXTERNAL PEER AUDIT & REPLICATION ENGINE")
    print("=" * 60)

    # 1. Forensic Export
    print("\n[XA] Running Forensic Export...")
    exporter = ForensicExportEngine(project_root)
    manifest = exporter.generate_manifest()
    print(f"     Manifest generated with {len(manifest['records'])} entries.")

    # 2. Chain of Custody
    print("\n[XB] Verifying Chain of Custody...")
    verifier = ChainOfCustodyVerifier(project_root, manifest)
    coc_res = verifier.verify()
    print(f"     Chain of custody: {coc_res['verdict']}")

    # 3. Hostile Leakage
    print("\n[XC] Auditing for Hostile Data Leakage...")
    leakage_audit = HostileLeakageAudit(project_root)
    leak_res = leakage_audit.run_leakage_audit()
    print(f"     Leakage score: {leak_res['leakage_score'] * 100:.2f}% (Status: {leak_res['status']})")

    # 4. Circular Validation
    print("\n[XD] Checking Circular Validation Risks...")
    circ_audit = CircularValidationAudit(project_root)
    circ_res = circ_audit.audit_circular_validation()
    print(f"     Circular validation status: {circ_res['status']}")

    # 5. Red Team Reimplementation
    print("\n[XE] Running Red Team Reimplementation challenge...")
    red_team = RedTeamReimplementation(project_root)
    rt_res = red_team.run_reimplementation()
    print(f"     Reimplementation equivalence: {rt_res['equivalence_rate'] * 100:.2f}% (Status: {rt_res['status']})")

    # 6. Double Blind
    print("\n[XF] Conducting Double Blind reproduction analysis...")
    double_blind = DoubleBlindReproduction(project_root)
    db_res = double_blind.run_double_blind()
    print(f"     Double blind agreement: {db_res['prediction_agreement'] * 100:.2f}%")

    # 7. Adversarial Model Tournament
    print("\n[XG] Staging Adversarial Model Tournament...")
    tournament = AdversarialModelTournament(project_root)
    tourney_res = tournament.run_tournament()
    print(f"     Adversarial tournament win rate: {tourney_res['win_rate'] * 100:.2f}%")

    # 8. External Hardware Challenge
    print("\n[XH] Staging External Hardware Challenge...")
    hw_challenge = ExternalHardwareChallenge(project_root)
    hw_res = hw_challenge.run_hardware_challenge()
    print(f"     External hardware replication rate: {hw_res['replication_rate'] * 100:.2f}%")

    # 9. Independent Physics Review
    print("\n[XI] Conducting Independent Physics Review...")
    phys_review = IndependentPhysicsReview(project_root)
    phys_res = phys_review.run_review()
    print(f"     Physics review survival rate: {phys_res['survival_rate'] * 100:.2f}%")

    # 10. Peer Review Panel Simulation
    print("\n[XJ] Convening External Review Panel...")
    panel_input = {
        "leakage_score": leak_res["leakage_score"],
        "checksum_integrity": 1.0 if coc_res["checksum_integrity"] else 0.0,
        "red_team_equivalence": rt_res["equivalence_rate"],
        "double_blind_agreement": db_res["prediction_agreement"],
        "external_hardware_replication": hw_res["replication_rate"],
        "independent_physics_survival": phys_res["survival_rate"]
    }
    panel = ExternalReviewPanel(project_root)
    panel_res = panel.evaluate_panel(panel_input)
    print(f"     External Review Panel score: {panel_res['panel_score']:.2f}%")

    # 11. Meta-Reproduction Analysis
    print("\n[XK] Executing Meta-Reproduction Stability Audit...")
    meta_engine = MetaReproductionEngine(project_root)
    meta_res = meta_engine.run_meta_analysis()
    print(f"     Meta-reproduction stability rate: {meta_res['meta_reproduction_rate'] * 100:.2f}%")

    # 12. Final Verdict Decision
    print("\n[XL] Issuing Epistemic Verdict Verdict...")
    verdict_engine = ExternalEpistemicVerdict(project_root)
    aggregated = {
        "leakage_score": leak_res["leakage_score"],
        "checksum_integrity": coc_res["checksum_integrity"],
        "red_team_equivalence": rt_res["equivalence_rate"],
        "double_blind_agreement": db_res["prediction_agreement"],
        "external_hardware_replication": hw_res["replication_rate"],
        "adversarial_tournament_win_rate": tourney_res["win_rate"],
        "independent_physics_survival": phys_res["survival_rate"],
        "external_review_score": panel_res["panel_score"],
        "meta_reproduction_rate": meta_res["meta_reproduction_rate"]
    }
    final_verdict = verdict_engine.evaluate_verdict(aggregated)

    print("\n" + "=" * 60)
    print("  PHASE X -- EXTERNAL PEER AUDIT COMPLETE")
    print("=" * 60)
    print(f"  Leakage score:                  {leak_res['leakage_score']*100:.2f}%")
    print(f"  Checksum Integrity:             {'100.00%' if coc_res['checksum_integrity'] else 'FAILED'}")
    print(f"  Red Team Equivalence:           {rt_res['equivalence_rate']*100:.2f}%")
    print(f"  Double Blind Agreement:         {db_res['prediction_agreement']*100:.2f}%")
    print(f"  External Hardware Replication:  {hw_res['replication_rate']*100:.2f}%")
    print(f"  Adversarial Tournament Win:     {tourney_res['win_rate']*100:.2f}%")
    print(f"  Independent Physics Survival:   {phys_res['survival_rate']*100:.2f}%")
    print(f"  External Review Panel Score:    {panel_res['panel_score']:.2f}%")
    print(f"  Meta-Reproduction Rate:         {meta_res['meta_reproduction_rate']*100:.2f}%")
    print("  ----------------------------------------------------------")
    print(f"  FINAL PEER AUDIT VERDICT:       {final_verdict}")
    print("=" * 60)

    return final_verdict

if __name__ == "__main__":
    import os
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    verdict = run_full_external_audit(root)
    if verdict == "EXTERNALLY_AUDITED_NEW_PHYSICS_CANDIDATE":
        sys.exit(0)
    else:
        sys.exit(1)
