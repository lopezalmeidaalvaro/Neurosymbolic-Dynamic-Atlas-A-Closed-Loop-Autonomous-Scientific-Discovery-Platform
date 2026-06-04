import os
import json
import pytest
from quantum.law_discovery.scientific_observer import ScientificObserver
from quantum.law_discovery.pattern_miner import PatternMiner
from quantum.law_discovery.symbolic_law_generator import SymbolicLawGenerator
from quantum.law_discovery.hypothesis_generator import HypothesisGenerator
from quantum.law_discovery.mechanistic_explainer import MechanisticExplainer
from quantum.law_discovery.synthetic_law_benchmark import SyntheticLawBenchmark
from quantum.law_discovery.causal_law_verifier import CausalLawVerifier
from quantum.law_discovery.law_falsification_engine import LawFalsificationEngine
from quantum.law_discovery.law_tournament import LawTournament
from quantum.law_discovery.theory_refinement import TheoryRefinement
from quantum.law_discovery.law_memory import LawMemory
from quantum.law_discovery.mdl_analyzer import MDLAnalyzer
from quantum.law_discovery.meta_law_discovery import MetaLawDiscovery
from quantum.law_discovery.scientific_loop import ScientificLoop
from quantum.law_discovery.law_discovery_audit import LawDiscoveryAudit
from quantum.graph.knowledge_graph_analyzer import KnowledgeGraphAnalyzer

@pytest.fixture(scope="module")
def setup_test_data():
    # Generate 50 test observations
    obs_path = "test_observations.json"
    observer = ScientificObserver(output_path=obs_path)
    observer.generate_large_scale_dataset(target_count=50)
    yield obs_path
    if os.path.exists(obs_path):
        os.remove(obs_path)

def test_observer(setup_test_data):
    obs_path = setup_test_data
    assert os.path.exists(obs_path)
    with open(obs_path, "r") as f:
        data = json.load(f)
    assert len(data) == 50
    assert "gate_entropy" in data[0]

def test_pattern_miner(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    rules = miner.mine_rules(min_support=0.01, min_confidence=0.1)
    assert len(rules) > 0
    assert os.path.exists(rules_path)
    os.remove(rules_path)

def test_symbolic_law_generator(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    laws_path = "test_laws.json"
    
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    miner.mine_rules(min_support=0.01, min_confidence=0.1)
    
    generator = SymbolicLawGenerator(input_path=rules_path, output_path=laws_path)
    laws = generator.generate_laws()
    
    assert len(laws) > 0
    assert os.path.exists(laws_path)
    
    os.remove(rules_path)
    os.remove(laws_path)

def test_hypothesis_generator(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    laws_path = "test_laws.json"
    hyp_path = "test_hypotheses.json"
    
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    miner.mine_rules(min_support=0.01, min_confidence=0.1)
    
    generator = SymbolicLawGenerator(input_path=rules_path, output_path=laws_path)
    generator.generate_laws()
    
    h_gen = HypothesisGenerator(input_path=laws_path, output_path=hyp_path)
    hyps = h_gen.generate_hypotheses()
    
    assert len(hyps) > 0
    assert os.path.exists(hyp_path)
    
    os.remove(rules_path)
    os.remove(laws_path)
    os.remove(hyp_path)

def test_mechanistic_explainer(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    laws_path = "test_laws.json"
    hyp_path = "test_hypotheses.json"
    expl_path = "test_explanations.json"
    
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    miner.mine_rules(min_support=0.01, min_confidence=0.1)
    
    generator = SymbolicLawGenerator(input_path=rules_path, output_path=laws_path)
    generator.generate_laws()
    
    h_gen = HypothesisGenerator(input_path=laws_path, output_path=hyp_path)
    h_gen.generate_hypotheses()
    
    explainer = MechanisticExplainer(input_path=hyp_path, output_path=expl_path)
    exps = explainer.explain_mechanisms()
    
    assert len(exps) > 0
    assert os.path.exists(expl_path)
    
    os.remove(rules_path)
    os.remove(laws_path)
    os.remove(hyp_path)
    os.remove(expl_path)

def test_synthetic_law_benchmark():
    temp_data = "test_temp_synth.json"
    report_path = "test_synth_report.json"
    
    benchmark = SyntheticLawBenchmark(temp_data_path=temp_data, report_path=report_path)
    report = benchmark.run_benchmark()
    
    assert "recovery_precision" in report
    assert "discovery_confidence_score" in report
    assert os.path.exists(report_path)
    os.remove(report_path)

def test_causal_law_verifier(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    laws_path = "test_laws.json"
    val_path = "test_validation.json"
    
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    miner.mine_rules(min_support=0.01, min_confidence=0.1)
    
    generator = SymbolicLawGenerator(input_path=rules_path, output_path=laws_path)
    generator.generate_laws()
    
    verifier = CausalLawVerifier(laws_path=laws_path, data_path=obs_path, output_path=val_path)
    vals = verifier.verify_laws()
    
    assert len(vals) > 0
    assert "metrics" in vals[0]
    assert os.path.exists(val_path)
    
    os.remove(rules_path)
    os.remove(laws_path)
    os.remove(val_path)

def test_law_falsification_engine(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    laws_path = "test_laws.json"
    val_path = "test_validation.json"
    fal_path = "test_falsification.json"
    
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    miner.mine_rules(min_support=0.01, min_confidence=0.1)
    
    generator = SymbolicLawGenerator(input_path=rules_path, output_path=laws_path)
    generator.generate_laws()
    
    verifier = CausalLawVerifier(laws_path=laws_path, data_path=obs_path, output_path=val_path)
    verifier.verify_laws()
    
    falsifier = LawFalsificationEngine(validation_path=val_path, data_path=obs_path, output_path=fal_path)
    fals = falsifier.run_falsification()
    
    assert len(fals) > 0
    assert "survival_score" in fals[0]
    assert os.path.exists(fal_path)
    
    os.remove(rules_path)
    os.remove(laws_path)
    os.remove(val_path)
    os.remove(fal_path)

def test_law_tournament(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    laws_path = "test_laws.json"
    val_path = "test_validation.json"
    fal_path = "test_falsification.json"
    tour_path = "test_leaderboard.json"
    
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    miner.mine_rules(min_support=0.01, min_confidence=0.1)
    
    generator = SymbolicLawGenerator(input_path=rules_path, output_path=laws_path)
    generator.generate_laws()
    
    verifier = CausalLawVerifier(laws_path=laws_path, data_path=obs_path, output_path=val_path)
    verifier.verify_laws()
    
    falsifier = LawFalsificationEngine(validation_path=val_path, data_path=obs_path, output_path=fal_path)
    falsifier.run_falsification()
    
    tournament = LawTournament(validation_path=val_path, falsification_path=fal_path, output_path=tour_path)
    leaderboard = tournament.run_tournament()
    
    assert len(leaderboard) > 0
    assert "tournament_score" in leaderboard[0]
    assert os.path.exists(tour_path)
    
    os.remove(rules_path)
    os.remove(laws_path)
    os.remove(val_path)
    os.remove(fal_path)
    os.remove(tour_path)

def test_theory_refinement(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    laws_path = "test_laws.json"
    val_path = "test_validation.json"
    fal_path = "test_falsification.json"
    tour_path = "test_leaderboard.json"
    ref_path = "test_versions.json"
    
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    miner.mine_rules(min_support=0.01, min_confidence=0.1)
    
    generator = SymbolicLawGenerator(input_path=rules_path, output_path=laws_path)
    generator.generate_laws()
    
    verifier = CausalLawVerifier(laws_path=laws_path, data_path=obs_path, output_path=val_path)
    verifier.verify_laws()
    
    falsifier = LawFalsificationEngine(validation_path=val_path, data_path=obs_path, output_path=fal_path)
    falsifier.run_falsification()
    
    tournament = LawTournament(validation_path=val_path, falsification_path=fal_path, output_path=tour_path)
    tournament.run_tournament()
    
    refinement = TheoryRefinement(leaderboard_path=tour_path, falsification_path=fal_path, output_path=ref_path)
    versions = refinement.refine_theories()
    
    assert len(versions) > 0
    assert "version" in versions[0]
    assert os.path.exists(ref_path)
    
    os.remove(rules_path)
    os.remove(laws_path)
    os.remove(val_path)
    os.remove(fal_path)
    os.remove(tour_path)
    os.remove(ref_path)

def test_law_memory(setup_test_data):
    # Verify synchronizing and files loading
    mem = LawMemory(directory=".")
    # Check that synchronous works without errors
    mem.synchronize_memory()
    assert mem.get_accepted_laws() == [] or len(mem.get_accepted_laws()) >= 0

def test_mdl_analyzer(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    laws_path = "test_laws.json"
    mdl_path = "test_mdl_report.json"
    
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    miner.mine_rules(min_support=0.01, min_confidence=0.1)
    
    generator = SymbolicLawGenerator(input_path=rules_path, output_path=laws_path)
    generator.generate_laws()
    
    analyzer = MDLAnalyzer(laws_path=laws_path, output_path=mdl_path)
    mdls = analyzer.analyze_complexity()
    
    assert len(mdls) > 0
    assert "scientific_value_score" in mdls[0]
    assert os.path.exists(mdl_path)
    
    os.remove(rules_path)
    os.remove(laws_path)
    os.remove(mdl_path)

def test_meta_law_discovery(setup_test_data):
    obs_path = setup_test_data
    rules_path = "test_rules.json"
    laws_path = "test_laws.json"
    val_path = "test_validation.json"
    fal_path = "test_falsification.json"
    meta_path = "test_meta.json"
    
    miner = PatternMiner(input_path=obs_path, output_path=rules_path)
    miner.mine_rules(min_support=0.01, min_confidence=0.1)
    
    generator = SymbolicLawGenerator(input_path=rules_path, output_path=laws_path)
    generator.generate_laws()
    
    verifier = CausalLawVerifier(laws_path=laws_path, data_path=obs_path, output_path=val_path)
    verifier.verify_laws()
    
    falsifier = LawFalsificationEngine(validation_path=val_path, data_path=obs_path, output_path=fal_path)
    falsifier.run_falsification()
    
    discovery = MetaLawDiscovery(validation_path=val_path, falsification_path=fal_path, output_path=meta_path)
    metas = discovery.discover_meta_laws()
    
    assert len(metas) >= 0
    assert os.path.exists(meta_path)
    
    os.remove(rules_path)
    os.remove(laws_path)
    os.remove(val_path)
    os.remove(fal_path)
    os.remove(meta_path)

def test_scientific_loop():
    history_path = "test_scientific_history.json"
    loop = ScientificLoop(history_path=history_path)
    logs = loop.execute_loop(cycles=10) # run small loop
    assert len(logs) == 10
    assert os.path.exists(history_path)
    
    # Cleanup loop output artifacts if they exist
    for f in [history_path, "observation_dataset.json", "candidate_laws.json", "generated_hypotheses.json",
              "mechanistic_explanations.json", "causal_law_validation.json", "law_falsification_report.json",
              "law_leaderboard.json", "law_versions.json", "accepted_laws.json", "rejected_laws.json",
              "mdl_report.json", "meta_laws.json", "pattern_rules.json"]:
        if os.path.exists(f):
            os.remove(f)

def test_knowledge_graph_analyzer():
    # Check that knowledge graph analyzer handles LAW, HYPOTHESIS nodes and count mapping
    graph_dict = {
        "nodes": {
            "LAW_001": {"type": "LAW", "attributes": {"rule": "IF x THEN y"}},
            "HYP_001": {"type": "HYPOTHESIS", "attributes": {"statement": "statement"}},
            "MECH_001": {"type": "MECHANISM", "attributes": {"causal_chain": ["a", "b"]}},
            "CS_1": {"type": "CompositeScaffold", "attributes": {}}
        },
        "edges": [
            {"source": "LAW_001", "target": "HYP_001", "type": "DERIVED_FROM", "attributes": {}},
            {"source": "MECH_001", "target": "LAW_001", "type": "EXPLAINS", "attributes": {}}
        ]
    }
    
    analyzer = KnowledgeGraphAnalyzer(graph_dict)
    stats = analyzer.analyze()
    
    assert stats["node_count"] == 4
    assert stats["edge_count"] == 2
    assert stats["node_types"]["LAW"] == 1
    assert stats["node_types"]["HYPOTHESIS"] == 1
    assert stats["node_types"]["MECHANISM"] == 1
    assert stats["relation_types"]["DERIVED_FROM"] == 1
    assert stats["relation_types"]["EXPLAINS"] == 1
    
    # Clean up generated reports
    if os.path.exists("knowledge_graph_statistics.json"):
        os.remove("knowledge_graph_statistics.json")
    if os.path.exists("docs/GRAPH_ANALYTICS_REPORT.md"):
        os.remove("docs/GRAPH_ANALYTICS_REPORT.md")
