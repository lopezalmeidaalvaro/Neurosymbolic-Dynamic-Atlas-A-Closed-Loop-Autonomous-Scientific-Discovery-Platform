import math
import copy
from typing import Any, List, Dict, Optional
from quantum.interfaces import BaseMemory
from quantum.knowledge.context_schema import Context

class QuantumMemory(BaseMemory):
    """
    Capa de memoria semántica temporal para el dominio cuántico.
    Almacena hipótesis y resultados en memoria (sin persistencia).
    """

    def __init__(self):
        self._store = {}
        self.current_context: Optional[Context] = None
        self.allow_cross_context = True

    def set_current_context(self, context: Context) -> None:
        """
        Establece el contexto activo para la recuperación del conocimiento.
        """
        self.current_context = context

    def store(self, key: str, value: Any, *args, **kwargs) -> None:
        """
        Almacena un elemento en memoria.
        """
        self._store[key] = value

    def retrieve(self, key: str, *args, **kwargs) -> Any:
        """
        Recupera un elemento de la memoria. Devuelve None si no se encuentra.
        """
        return self._store.get(key, None)

    def query_patterns(self, task: str = None) -> List[Dict[str, Any]]:
        """
        Consulta patrones descubiertos de forma queryable.
        Si se proporciona 'task', filtra los patrones asociados a esa tarea.
        """
        if task:
            return self.retrieve(f"quantum:distillation:task:{task}:patterns") or []
        else:
            return self.retrieve("quantum:distillation:patterns") or []

    def query_scaffolds(self) -> List[Dict[str, Any]]:
        """
        Consulta scaffolds compuestos.
        """
        return self.retrieve("quantum:distillation:scaffolds") or []

    def get_knowledge_graph(self) -> Dict[str, Any]:
        """
        Retorna la representación actual del grafo de conocimiento.
        """
        return self.retrieve("quantum:distillation:knowledge_graph") or {"nodes": {}, "edges": []}

    def retrieve_patterns(self, context: Context, allow_cross_context: bool = True) -> List[Dict[str, Any]]:
        """
        Algoritmo de recuperación condicional basado en la similitud del contexto actual
        y la puntuación de calidad (P_convergence, survival_probability, mean_delta_score).
        """
        patterns = self.query_patterns() or []
        retrieved = []

        for p in patterns:
            # Migration/compatibility: check for context field
            p_context_data = p.get("context")
            if p_context_data is None:
                # Legacy pattern: no context
                if not allow_cross_context:
                    continue
                similarity = 0.5
            else:
                # Reconstruct Context object
                if isinstance(p_context_data, dict):
                    p_context = Context.from_dict(p_context_data)
                elif isinstance(p_context_data, Context):
                    p_context = p_context_data
                else:
                    p_context = Context(task_name="unknown", qubit_count=0, converged=False)
                
                # Check task_name and qubit_count match
                if p_context.task_name == context.task_name and p_context.qubit_count == context.qubit_count:
                    similarity = 1.0
                else:
                    if not allow_cross_context:
                        continue
                    # Soft context matching
                    if p_context.qubit_count == context.qubit_count:
                        similarity = 0.5
                    elif p_context.task_name == context.task_name:
                        similarity = 0.2
                    else:
                        similarity = 0.1

            # Calculate Quality Score
            p_conv = p.get("P_convergence", p.get("avg_score", 0.0))
            surv_prob = p.get("survival_probability", 0.5)
            mean_delta = p.get("mean_delta_score", 0.0)

            quality_score = max(1e-4, p_conv * surv_prob * math.exp(mean_delta))
            score = quality_score * similarity

            if score > 0 or similarity > 0:
                p_copy = copy.deepcopy(p)
                p_copy["weight"] = score
                p_copy["retrieval_score"] = score
                retrieved.append(p_copy)

        # Sort descending by score
        retrieved.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return retrieved

    def get_active_patterns(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de patrones activos.
        Si hay un contexto establecido, usa retrieve_patterns.
        De lo contrario, usa el fallback de filtrado basado en la valoración de calidad.
        """
        if self.current_context is not None:
            return self.retrieve_patterns(self.current_context, allow_cross_context=getattr(self, "allow_cross_context", True))

        # Fallback para compatibilidad con código antiguo
        patterns = self.query_patterns() or []
        causal_records = self.retrieve("quantum:distillation:causal_records") or []
        knowledge_graph = self.get_knowledge_graph() or {"nodes": {}, "edges": []}
        has_evidence = len(causal_records) > 0 or len(knowledge_graph.get("nodes", {})) > 0
        
        active_patterns = []
        
        if not has_evidence:
            for p in patterns:
                freq = p.get("frequency", 1)
                if freq < 10:
                    confidence_factor = freq / 10.0
                else:
                    confidence_factor = 1.0 + math.log10(freq / 10.0)
                
                avg_score = p.get("avg_score", 0.0)
                weight = max(1e-4, avg_score) * confidence_factor
                
                pat_copy = copy.deepcopy(p)
                pat_copy["weight"] = weight
                active_patterns.append(pat_copy)
            return active_patterns
            
        # Avoid circular dependency if loaded early
        from quantum.knowledge.pattern_valuation import PatternValuationEngine
        valuation_engine = PatternValuationEngine(self)
        evaluated = valuation_engine.evaluate_patterns()
        
        pattern_map = {p["representation"]: p for p in patterns if "representation" in p}
        
        for rep, ev in evaluated.items():
            if ev["category"] in ("TOXIC", "NOISE/JUNK"):
                continue
                
            orig_pat = pattern_map.get(rep)
            if not orig_pat:
                continue
                
            freq = ev["frequency"]
            if freq < 10:
                confidence_factor = freq / 10.0
            else:
                confidence_factor = 1.0 + math.log10(freq / 10.0)
                
            p_conv = ev["P_convergence"]
            survival_prob = ev["survival_probability"]
            
            base_weight = p_conv * survival_prob
            if base_weight == 0.0:
                base_weight = 1e-4
                
            weight = base_weight * confidence_factor
            
            pat_copy = copy.deepcopy(orig_pat)
            pat_copy["weight"] = weight
            active_patterns.append(pat_copy)
            
        return active_patterns

    def get_active_scaffolds(self, context: Optional[Context] = None, threshold: float = 0.75) -> List[Dict[str, Any]]:
        """
        Retorna la lista de scaffolds activos que son compatibles con el contexto.
        """
        ctx = context or self.current_context
        scaffolds = self.query_scaffolds()
        if ctx is None:
            return scaffolds
            
        from quantum.memory.context_compatibility import ContextCompatibilityEngine
        engine = ContextCompatibilityEngine()
        active = []
        for s in scaffolds:
            s_ctx = s.get("context")
            if s_ctx:
                score = engine.calculate_compatibility(s_ctx, ctx)
                if score >= threshold:
                    s_copy = copy.deepcopy(s)
                    s_copy["compatibility_score"] = score
                    
                    # selection weight = quality_score * compatibility_score * scaffold_confidence
                    p_conv = s.get("P_convergence", 0.0)
                    surv_prob = s.get("survival_probability", 0.5)
                    mean_delta = s.get("mean_delta_score", 0.0)
                    quality_score = max(1e-4, p_conv * surv_prob * math.exp(mean_delta))
                    
                    s_copy["weight"] = quality_score * score * s.get("confidence_score", 0.1)
                    active.append(s_copy)
        return active
