from mathematics.knowledge_base.library_manager import FormalKnowledgeBase
from mathematics.translator.registry import RuleRegistry
from mathematics.translator.rules import DoubleHadamardRule
from mathematics.translator.mapper import QuantumEquivalenceTranslator
from mathematics.verifier.runtime import LocalLeanRuntime
from mathematics.verifier.evaluator import ProofEvaluator
from mathematics.llm_translator.client import OpenAICompatibleClient
from mathematics.llm_translator.repair_loop import AutoFormalizationLoop
from mathematics.prover.mcts import MonteCarloTreeSearch
from mathematics.orchestrator.handlers import (
    DeterministicHandler,
    LLMHandler,
    MCTSHandler,
)
from mathematics.orchestrator.pipeline import DomainOrchestrator
from mathematics.engine import MathEngine


def bootstrap_math_engine(
    db_path: str,
    llm_api_url: str,
    llm_api_key: str,
    llm_model: str,
    lean_executable: str = "lean",
) -> MathEngine:
    """Bootstrap Composition Root that instantiates and wires all domain dependencies.

    Returns the initialized MathEngine Facade.
    """
    # 1. Instantiate SQLite Knowledge Base
    kb = FormalKnowledgeBase(db_path=db_path)

    # 2. Instantiate Rule Registry and Deterministic Translator
    registry = RuleRegistry()
    registry.register(DoubleHadamardRule())
    translator = QuantumEquivalenceTranslator(registry)

    # 3. Instantiate Verification Runtime and Evaluator
    runtime = LocalLeanRuntime(lean_executable=lean_executable, timeout_seconds=10.0)
    evaluator = ProofEvaluator(runtime)

    # 4. Instantiate LLM Client
    client = OpenAICompatibleClient(
        api_url=llm_api_url,
        api_key=llm_api_key,
        model_name=llm_model,
        timeout_seconds=30.0,
    )

    # 5. Instantiate LLM Auto-Repair Loop and MCTS Tree Search Prover
    repair_loop = AutoFormalizationLoop(client, evaluator)
    mcts = MonteCarloTreeSearch(client, evaluator)

    # 6. Instantiate Handlers
    deterministic_handler = DeterministicHandler(translator, evaluator)
    llm_handler = LLMHandler(repair_loop)
    mcts_handler = MCTSHandler(mcts, kb)

    # 7. Configure Chain of Responsibility Handlers: Deterministic -> LLM -> MCTS
    deterministic_handler.set_next(llm_handler)
    llm_handler.set_next(mcts_handler)

    # 8. Instantiate Domain Orchestrator
    orchestrator = DomainOrchestrator(deterministic_handler, kb)

    # 9. Return Facade Engine wrapper
    return MathEngine(orchestrator, kb)
