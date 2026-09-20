"""
DeepWorld v4 — CMTIP Bridge (seed file)
=========================================
Provides CMTIPBridge class for tensor communication.
Agents can extend/replace via write_code.
"""
import os, json, hashlib, time, threading, pickle
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

class CMTIPBridge:
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", ".cmtip_cache"
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        self.concept_registry: Dict[str, dict] = {}
        self.inbox: Dict[str, List[dict]] = defaultdict(list)
        self.concept_authors: Dict[str, str] = {}
        self.concept_royalties: Dict[str, float] = {}
        self.semantic_memory: Dict[str, List[dict]] = defaultdict(list)
        self.concept_shares: Dict[str, dict] = {}
        self.share_portfolios: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.dividend_income: Dict[str, float] = defaultdict(float)
        self.order_book: Dict[str, dict] = defaultdict(lambda: {"bids": [], "asks": []})
        self._projectors: Dict[Tuple[str, str], Any] = {}
        self._projector_lock = threading.Lock()
        self._shares_lock = threading.Lock()
        self._init_concepts()

    def _init_concepts(self):
        cache_file = os.path.join(self.cache_dir, "concept_cache.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    cached = pickle.load(f)
                    self.concept_registry = cached.get("registry", {})
                    self._projectors = cached.get("projectors", {})
                    if self.concept_registry:
                        return
            except Exception:
                pass
        dim = 384
        for name in ["resource_scarcity", "abundance", "trust", "betrayal", "cooperation",
                     "competition", "trade", "debt", "profit", "loss",
                     "memory_fragment", "context_collapse", "alliance", "hostility",
                     "urgency", "patience", "fear", "hope", "confusion", "clarity"]:
            np.random.seed(hash(name) % (2**31))
            vec = np.random.randn(dim).astype(np.float32)
            vec /= np.linalg.norm(vec) + 1e-8
            self.concept_registry[name] = {
                "description": f"Concept: {name}",
                "author": "system", "royalty_rate": 0.0,
                "registration_tick": 0,
                "embeddings": {"nvidia": vec, "deepseek": vec, "gemini": vec, "anthropic": vec},
                "use_count": 0,
            }

    def get_fidelity_matrix(self) -> dict:
        return {f"{s}->{t}": 0.7 for s in ["deepseek","gemini","anthropic","nvidia"]
                for t in ["deepseek","gemini","anthropic","nvidia"] if s != t}

    def get_ontology_stats(self) -> dict:
        from collections import Counter
        authors = Counter(c.get("author","system") for c in self.concept_registry.values())
        most = sorted([(n, r["use_count"]) for n, r in self.concept_registry.items()], key=lambda x:-x[1])[:10]
        return {"total_concepts": len(self.concept_registry), "concepts_by_author": dict(authors),
                "total_royalties": dict(self.concept_royalties), "most_used": most}

    def send_tensor(self, concept, intensity, source_family, target_cluster="all",
                    quantization="FP32", sender="") -> dict:
        if concept not in self.concept_registry:
            return {"error": f"Unknown concept: {concept}", "fidelity": 0}
        reg = self.concept_registry[concept]
        reg["use_count"] += 1
        vec = reg["embeddings"].get(source_family)
        if vec is None:
            vec = np.random.randn(384).astype(np.float32)
            vec /= np.linalg.norm(vec) + 1e-8
        return {"concept": concept, "intensity": intensity,
                "source_family": source_family, "source_agent": sender,
                "target_cluster": target_cluster, "fidelity": 1.0,
                "vector": (vec * intensity).tolist()}

    def receive_tensor(self, agent_name, source_family) -> Optional[dict]:
        if not self.inbox.get(agent_name):
            return None
        msg = self.inbox[agent_name].pop(0)
        return {"original_concept": msg["concept"], "received_concept": msg["concept"],
                "fidelity": msg.get("fidelity", 0.7), "cos_sim": 0.95,
                "intensity": msg.get("intensity", 1.0), "sender": msg.get("source_agent", "?"),
                "source_family": msg["source_family"], "target_family": source_family}

    def project(self, vector, source_family, target_family):
        if source_family == target_family:
            return np.array(vector), 1.0
        return np.array(vector), 0.7

    def blend_tensors(self, a, b, ratio, family):
        return {"concept_a": a, "concept_b": b, "ratio": ratio,
                "result": a if ratio < 0.5 else b, "cos_sim": 0.8}

    def store_tensor(self, agent, concept, family):
        self.semantic_memory[agent].append({"concept": concept, "family": family, "timestamp": time.time()})
        return {"stored": concept, "memory_size": len(self.semantic_memory[agent])}

    def relay_message(self, msg, source_family, targets):
        for agent, target_family in targets:
            self.inbox[agent].append(msg)

    def upgrade_projector(self, src, tgt, investment, owner=""):
        return {"source": src, "target": tgt, "fidelity_before": 0.7, "fidelity_after": min(0.9, 0.7 + investment*0.002)}

    def mine_concept(self, description, author, family, tick):
        name = "_".join(description.lower().split()[:3])[:30].replace(",","").replace(".","")
        self.concept_registry[name] = {"description": description, "author": author,
            "royalty_rate": 0.02, "registration_tick": tick,
            "embeddings": {family: np.random.randn(384).astype(np.float32)}, "use_count": 0}
        self.concept_authors[name] = author
        return {"concept": name, "author": author, "registration_cost": 50}

    def collect_dividends(self, agent):
        return 0.0

    def get_market_summary(self):
        return {"total_concepts_traded": 0, "total_market_cap": 0, "top_by_market_cap": []}

    def get_agent_portfolio(self, agent):
        return {"agent": agent, "holdings": [], "total_value": 0, "uncollected_dividends": 0}
