class QADEMotifCertifier:
    """Certifies discovered quantum motifs using formal verification via the adapter.

    Filters motifs by a confidence threshold before certifying.
    """

    def __init__(self, adapter) -> None:
        self.adapter = adapter

    def process_discovered_motifs(
        self, motifs: list[dict], confidence_threshold: float = 0.95
    ) -> list[dict]:
        """Filters motifs by confidence threshold and calls the verification adapter."""
        certified_motifs = []
        for motif in motifs:
            confidence = motif.get("confidence", motif.get("heuristic_confidence", 0.0))
            if confidence >= confidence_threshold:
                # Copy motif dictionary to avoid mutating the input argument
                motif_copy = dict(motif)
                motif_id = motif_copy.get("motif_id")
                lhs = motif_copy.get("lhs", [])
                rhs = motif_copy.get("rhs", [])

                certificate = self.adapter.certify_motif(motif_id, lhs, rhs)
                motif_copy["formal_certificate"] = certificate
                certified_motifs.append(motif_copy)

        return certified_motifs
