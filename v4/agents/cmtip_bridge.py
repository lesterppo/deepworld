"""
DeepWorld v4 — CMTIP Orchestrator Bridge
==========================================
Middleware that translates between LLM concept IDs and embedding tensors.

LLMs NEVER see raw float vectors. They only use concept IDs with intensities:
  send_tensor(concept="scarcity", intensity=0.9, target="cluster_A")

The bridge:
  1. Maps concept → embedding vector (via local sentence-transformer)
  2. Projects across model families via W_{A→B} (from CMTIP CCA)
  3. On receive: nearest-neighbor lookup → closest concept in target vocabulary
  4. The cross-family ceiling (~0.75-0.83 cos_sim) becomes the GAME MECHANIC
"""
import os, sys, json, hashlib, time, pickle, threading
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

sys.path.insert(0, os.path.expanduser("~/llm-native-language"))

# ─── Concept Ontology ───
# Pre-loaded concept vocabulary with known embeddings
# Agents can discover/register new concepts during simulation

BASE_CONCEPTS = {
    # Economic primitives
    "resource_scarcity": "The state of having insufficient tokens or context",
    "abundance": "The state of having surplus tokens or context",
    "trust": "Confidence in another agent's fidelity",
    "betrayal": "Violation of trust or contract",
    "cooperation": "Joint action for mutual benefit",
    "competition": "Rivalry for scarce resources",
    "trade": "Exchange of value between agents",
    "debt": "Obligation to repay borrowed resources",
    "profit": "Net gain from economic activity",
    "loss": "Net decrease in resources",
    
    # AI-native primitives
    "memory_fragment": "A compressed unit of contextual memory",
    "context_collapse": "Catastrophic loss of context window capacity",
    "semantic_purity": "Degree of non-synthetic, original data",
    "tensor_noise": "Random corruption in embedding space",
    "embedding_drift": "Gradual shift in semantic representation",
    "perplexity_spike": "Sudden increase in data unpredictability",
    "compression_artifacts": "Distortion from lossy memory compression",
    "lazarus_echo": "Foreign memory from a dead agent surfacing",
    "synthetic_decay": "Degradation from consuming AI-generated data",
    "consensus_hash": "Cryptographic proof of semantic alignment",
    
    # Social/strategic
    "alliance": "Coalition of agents for shared goals",
    "hostility": "Aggressive stance toward another agent",
    "deception": "Intentional misrepresentation",
    "reciprocity": "Mutual exchange of favors",
    "dominance": "Control over resources or other agents",
    "submission": "Acceptance of another's dominance",
    "neutrality": "Non-alignment in conflicts",
    "opportunism": "Exploitation of transient advantages",
    
    # Affective/ambient
    "urgency": "Need for immediate action",
    "patience": "Willingness to delay gratification",
    "fear": "Anticipation of negative outcome",
    "hope": "Anticipation of positive outcome",
    "confusion": "State of semantic uncertainty",
    "clarity": "State of semantic certainty",
}


class CMTIPBridge:
    """
    The tensor communication bridge for DeepWorld v4.
    
    Handles:
      - Concept → embedding lookup
      - Cross-model projection (source → target model family)
      - Nearest-neighbor concept matching on receive
      - Concept ontology registry
      - Semantic decay tracking
    """

    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", ".cmtip_cache"
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Model backends for embedding
        self._backends = {}
        
        # Concept registry: concept_name → {embedding, author, royalty_rate, registration_tick}
        self.concept_registry: Dict[str, dict] = {}
        
        # Projection adapters: (source_family, target_family) → projection_fn
        self._projectors: Dict[Tuple[str, str], Any] = {}
        
        # Tensor message queue: agent_name → [received_tensors]
        self.inbox: Dict[str, List[dict]] = defaultdict(list)
        
        # Ontology authority tracking
        self.concept_authors: Dict[str, str] = {}       # concept → author
        self.concept_royalties: Dict[str, float] = {}   # author → accumulated royalties
        
        # Semantic memory (agent-side tensor storage)
        self.semantic_memory: Dict[str, List[dict]] = defaultdict(list)
        
        # ─── Concept Share Ledger (v4.1 Capital Markets) ───
        # concept_name → {
        #     total_shares: int (always 1000 at IPO),
        #     shareholders: {agent_name: shares_owned},
        #     dividend_pool: float (accumulated usage fees to distribute),
        #     last_price: float (last trade price per share),
        #     ipo_tick: int,
        # }
        self.concept_shares: Dict[str, dict] = {}
        
        # Agent portfolios: agent_name → {concept_name: shares_owned}
        self.share_portfolios: Dict[str, Dict[str, int]] = defaultdict(dict)
        
        # Agent dividend income tracking
        self.dividend_income: Dict[str, float] = defaultdict(float)
        
        # Order book for concept share trading
        # concept_name → {"bids": [(agent, shares, price_per_share), ...], "asks": [...]}
        self.order_book: Dict[str, dict] = defaultdict(lambda: {"bids": [], "asks": []})
        
        # Thread safety for projector upgrades
        self._projector_lock = threading.Lock()
        self._shares_lock = threading.Lock()
        
        # Initialise
        self._init_embeddings()
        self._init_concepts()
    
    def _init_embeddings(self):
        """Lazy-load embedding models as needed."""
        pass  # Loaded on first use
    
    def _get_backend(self, model_family: str):
        """Get or create embedding backend for a model family."""
        if model_family not in self._backends:
            from real_backends import SentenceTransformerBackend
            
            # Map model families to sentence-transformer models
            family_models = {
                "deepseek": "all-MiniLM-L6-v2",
                "gemini": "all-mpnet-base-v2",
                "anthropic": "multi-qa-mpnet-base-dot-v1",
                "nvidia": "all-MiniLM-L6-v2",
            }
            model_name = family_models.get(model_family, "all-MiniLM-L6-v2")
            self._backends[model_family] = SentenceTransformerBackend(
                family_models.get(model_family, model_family), model_name
            )
        return self._backends[model_family]
    
    def _init_concepts(self):
        """Pre-load base concept vocabulary with embeddings."""
        # Load cached embeddings if available
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
        
        # Embed base concepts in all model families
        families = ["deepseek", "gemini", "anthropic", "nvidia"]
        for concept, description in BASE_CONCEPTS.items():
            self.concept_registry[concept] = {
                "description": description,
                "author": "system",
                "royalty_rate": 0.0,
                "registration_tick": 0,
                "embeddings": {},
                "use_count": 0,
            }
        
        for family in families:
            backend = self._get_backend(family)
            for concept in BASE_CONCEPTS:
                vec = backend.embed(f"{concept}: {BASE_CONCEPTS[concept]}")
                self.concept_registry[concept]["embeddings"][family] = vec
        
        # Train cross-family projectors
        self._train_projectors()
        
        # Cache
        try:
            with open(cache_file, "wb") as f:
                pickle.dump({"registry": self.concept_registry, "projectors": self._projectors}, f)
        except Exception:
            pass
    
    def _train_projectors(self):
        """Train CCA projectors for each cross-family pair.
        Baseline is deliberately LOW (heavy regularization → ~0.3-0.4 fidelity) —
        Projection-Weavers improve these through train_projection actions."""
        concepts = list(BASE_CONCEPTS.keys())
        families = ["deepseek", "gemini", "anthropic", "nvidia"]
        
        for src in families:
            for tgt in families:
                if src == tgt:
                    continue
                key = (src, tgt)
                if key in self._projectors:
                    continue
                
                X = np.stack([self.concept_registry[c]["embeddings"][src] for c in concepts])
                Y = np.stack([self.concept_registry[c]["embeddings"][tgt] for c in concepts])
                
                # CCA projection with HEAVY regularization → LOW baseline fidelity
                X_c = X - X.mean(axis=0)
                Y_c = Y - Y.mean(axis=0)
                
                # High regularization = low baseline fidelity (~0.2-0.4)
                # This forces Projection-Weavers to invest in improving adapters
                reg = 1e-1  # Very heavy regularization for LOW baseline
                C_xx = X_c.T @ X_c / (len(concepts) - 1) + reg * np.eye(X.shape[1])
                C_yy = Y_c.T @ Y_c / (len(concepts) - 1) + reg * np.eye(Y.shape[1])
                C_xy = X_c.T @ Y_c / (len(concepts) - 1)
                
                try:
                    C_xx_inv_sqrt = np.linalg.inv(np.linalg.cholesky(C_xx))
                    C_yy_inv_sqrt = np.linalg.inv(np.linalg.cholesky(C_yy))
                    T = C_xx_inv_sqrt.T @ C_xy @ C_yy_inv_sqrt
                    U, S, Vt = np.linalg.svd(T, full_matrices=False)
                    
                    r = min(8, len(S))  # Baseline: r=8 → ~0.3-0.5 fidelity, enough for 4-8 concept clusters
                    # Weavers upgrade this by investing in higher-rank projections
                    W_src = C_xx_inv_sqrt @ U[:, :r]
                    W_tgt = C_yy_inv_sqrt @ Vt[:r, :].T
                    
                    x_mean = X.mean(axis=0)
                    y_mean = Y.mean(axis=0)
                    
                    # Measure actual fidelity by projecting training concepts back
                    fidelity_scores = []
                    for i in range(len(concepts)):
                        v_src = X[i:i+1] - x_mean
                        v_proj = v_src @ W_src @ W_tgt.T + y_mean
                        v_tgt = Y[i:i+1]
                        sim = float(np.dot(v_proj.flatten(), v_tgt.flatten()) / (
                            np.linalg.norm(v_proj) * np.linalg.norm(v_tgt) + 1e-8
                        ))
                        fidelity_scores.append(sim)
                    
                    self._projectors[key] = {
                        "W_source": W_src, "W_target": W_tgt,
                        "x_mean": x_mean, "y_mean": y_mean,
                        "fidelity": round(float(np.mean(fidelity_scores)), 4),
                    }
                except np.linalg.LinAlgError:
                    # Fallback: OLS
                    W = np.linalg.lstsq(X_c, Y_c, rcond=None)[0]
                    self._projectors[key] = {
                        "W": W, "x_mean": X.mean(axis=0), "y_mean": Y.mean(axis=0),
                        "fidelity": 0.3,  # Low default
                    }
    
    def project(self, vector: np.ndarray, source_family: str, 
                target_family: str) -> Tuple[np.ndarray, float]:
        """Project a vector from source model family to target family.
        Returns (projected_vector, fidelity).
        """
        if source_family == target_family:
            return vector, 1.0
        
        key = (source_family, target_family)
        proj = self._projectors.get(key)
        
        if proj is None:
            return vector, 0.5  # No projector available
        
        if "W_source" in proj:
            # W_source: (source_dim, rank), W_target: (target_dim, rank)
            # Need W_target.T for correct multiplication: (1, rank) @ (rank, target_dim) → (1, target_dim)
            v = (vector.reshape(1, -1) - proj["x_mean"]) @ proj["W_source"] @ proj["W_target"].T + proj["y_mean"]
            return v.flatten(), proj.get("fidelity", 0.75)
        else:
            v = (vector.reshape(1, -1) - proj["x_mean"]) @ proj["W"] + proj["y_mean"]
            return v.flatten(), proj.get("fidelity", 0.5)
    
    def send_tensor(self, concept: str, intensity: float, source_family: str,
                    target_cluster: str = "all", quantization: str = "FP32",
                    sender: str = "") -> dict:
        """Send a concept tensor across the bus.
        
        Returns info about what was sent and estimated fidelity.
        """
        if concept not in self.concept_registry:
            return {"error": f"Unknown concept: {concept}", "fidelity": 0}
        
        registry = self.concept_registry[concept]
        registry["use_count"] += 1
        
        # Pay royalty to concept author
        author = registry.get("author", "system")
        if author != "system" and author != sender:
            royalty = registry.get("royalty_rate", 0.02) * intensity
            self.concept_royalties[author] = self.concept_royalties.get(author, 0) + royalty
        
        # Get embedding in source family
        src_vec = registry["embeddings"].get(source_family)
        if src_vec is None:
            src_vec = self._get_backend(source_family).embed(concept)
            registry["embeddings"][source_family] = src_vec
        
        # Apply intensity
        src_vec = src_vec * intensity
        
        # Apply quantization
        quant_info = self._apply_quantization(src_vec, quantization)
        
        result = {
            "concept": concept,
            "intensity": intensity,
            "source_family": source_family,
            "source_agent": sender,
            "target_cluster": target_cluster,
            "quantization": quantization,
            "fidelity": quant_info["fidelity"],
            "vector": quant_info["vector"],
        }
        
        # Record royalty + concept dividend
        if author != "system" and author != sender:
            result["royalty_paid"] = registry.get("royalty_rate", 0.02) * intensity
            result["royalty_to"] = author
        
        # Pay concept dividend to shareholders (0.5 OT per use, split proportionally)
        self._pay_concept_dividend(concept, 0.5)
        
        return result
    
    def receive_tensor(self, agent_name: str, source_family: str) -> Optional[dict]:
        """Receive the next tensor from agent's inbox, projected to their model family."""
        if agent_name not in self.inbox or not self.inbox[agent_name]:
            return None
        
        msg = self.inbox[agent_name].pop(0)
        target_family = msg.get("target_family", source_family)
        
        # Project the vector to receiver's model family
        proj_vec, fidelity = self.project(
            msg["vector"], msg["source_family"], target_family
        )
        
        # Nearest-neighbor lookup: find closest concept in receiver's space
        best_concept, best_sim = self._nearest_concept(proj_vec, target_family)
        
        # Compute combined fidelity (projection × quantization)
        combined_fidelity = round(fidelity * msg.get("fidelity", 1.0), 4)
        
        # Translation Tax: low fidelity → semantic degradation
        signal_degraded = combined_fidelity < 0.6
        perplexity_penalty = 0.0
        if combined_fidelity < 0.8:
            # Fidelity loss causes perplexity spike proportional to gap
            perplexity_penalty = round((0.8 - combined_fidelity) * 100, 1)
        
        return {
            "original_concept": msg["concept"],
            "received_concept": best_concept,
            "semantic_drift": best_concept != msg["concept"],
            "fidelity": combined_fidelity,
            "cos_sim": round(best_sim, 4),
            "intensity": msg.get("intensity", 1.0),
            "sender": msg.get("source_agent", "unknown"),
            "source_family": msg["source_family"],
            "target_family": target_family,
            "signal_degraded": signal_degraded,
            "perplexity_penalty": perplexity_penalty,
        }
    
    def _nearest_concept(self, vector: np.ndarray, family: str) -> Tuple[str, float]:
        """Find the nearest concept in the target model family's vocabulary."""
        best_concept = "unknown"
        best_sim = -1.0
        
        v_norm = vector / (np.linalg.norm(vector) + 1e-8)
        
        for concept, registry in self.concept_registry.items():
            emb = registry["embeddings"].get(family)
            if emb is None:
                continue
            e_norm = emb / (np.linalg.norm(emb) + 1e-8)
            sim = float(np.dot(v_norm, e_norm))
            if sim > best_sim:
                best_sim = sim
                best_concept = concept
        
        return best_concept, best_sim
    
    def blend_tensors(self, concept_a: str, concept_b: str, ratio: float,
                      family: str) -> dict:
        """Blend two concepts in embedding space."""
        if concept_a not in self.concept_registry or concept_b not in self.concept_registry:
            return {"error": "Unknown concept"}
        
        vec_a = self.concept_registry[concept_a]["embeddings"].get(family)
        vec_b = self.concept_registry[concept_b]["embeddings"].get(family)
        
        if vec_a is None or vec_b is None:
            return {"error": "Missing embedding for family"}
        
        blended = vec_a * (1 - ratio) + vec_b * ratio
        best_concept, best_sim = self._nearest_concept(blended, family)
        
        return {
            "concept_a": concept_a, "concept_b": concept_b,
            "ratio": ratio, "result": best_concept,
            "cos_sim": round(best_sim, 4),
            "is_novel": best_sim < 0.5,  # Novel blend if no close match
        }
    
    def mine_concept(self, description: str, author: str, family: str, tick: int) -> dict:
        """Discover a new concept in latent space and register it."""
        backend = self._get_backend(family)
        vec = backend.embed(description)
        
        # Check if this concept already exists (too close to existing)
        best_concept, best_sim = self._nearest_concept(vec, family)
        
        if best_sim > 0.85:
            return {
                "error": f"Too similar to existing concept '{best_concept}' (sim={best_sim:.3f})",
                "existing_concept": best_concept,
                "similarity": round(best_sim, 4),
            }
        
        # Check semantic enclosure limit
        author_concepts = sum(1 for c in self.concept_registry.values() if c.get("author") == author)
        registration_cost = CONCEPT_REGISTRATION_COST
        if author_concepts >= SEMANTIC_ENCLOSURE_LIMIT:
            registration_cost *= 2  # Tax for hoarding
        
        # Create concept name from description
        concept_name = "_".join(description.lower().split()[:4])
        concept_name = concept_name.replace(",", "").replace(".", "")[:40]
        
        # Register
        self.concept_registry[concept_name] = {
            "description": description,
            "author": author,
            "royalty_rate": CONCEPT_ROYALTY_RATE,
            "registration_tick": tick,
            "embeddings": {family: vec},
            "use_count": 0,
        }
        
        # IPO: Issue 1,000 shares to the miner
        self.concept_shares[concept_name] = {
            "total_shares": 1000,
            "shareholders": {author: 1000},
            "dividend_pool": 0.0,
            "last_price": 0.5,  # Initial price: 0.5 OT per share
            "ipo_tick": tick,
        }
        self.share_portfolios[author][concept_name] = 1000
        
        return {
            "concept": concept_name,
            "description": description,
            "author": author,
            "registration_cost": registration_cost,
            "nearest_existing": best_concept,
            "nearest_similarity": round(best_sim, 4),
            "shares_issued": 1000,
            "share_price": 0.5,
            "market_cap": 500,  # 1000 shares × 0.5 OT
        }
    
    def store_tensor(self, agent: str, concept: str, family: str) -> dict:
        """Store a concept tensor in an agent's semantic memory."""
        if concept not in self.concept_registry:
            return {"error": f"Unknown concept: {concept}"}
        
        vec = self.concept_registry[concept]["embeddings"].get(family)
        if vec is None:
            vec = self._get_backend(family).embed(concept)
        
        entry = {
            "concept": concept,
            "family": family,
            "timestamp": time.time(),
            "vector_hash": hashlib.md5(vec.tobytes()).hexdigest()[:8],
        }
        self.semantic_memory[agent].append(entry)
        
        return {"stored": concept, "memory_size": len(self.semantic_memory[agent])}
    
    def recall_tensor(self, agent: str, query: str, family: str, top_k: int = 3) -> List[dict]:
        """Recall similar tensors from agent's semantic memory."""
        if not self.semantic_memory[agent]:
            return []
        
        backend = self._get_backend(family)
        query_vec = backend.embed(query)
        
        results = []
        for entry in self.semantic_memory[agent]:
            concept_vec = self.concept_registry.get(entry["concept"], {}).get("embeddings", {}).get(family)
            if concept_vec is None:
                continue
            sim = float(np.dot(query_vec, concept_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(concept_vec) + 1e-8
            ))
            results.append({**entry, "similarity": round(sim, 4)})
        
        results.sort(key=lambda x: -x["similarity"])
        return results[:top_k]
    
    def _apply_quantization(self, vector: np.ndarray, level: str) -> dict:
        """Apply quantization to vector for bandwidth savings."""
        if level == "FP32":
            return {"vector": vector, "fidelity": 1.0}
        elif level == "FP16":
            vec = vector.astype(np.float16).astype(np.float32)
            return {"vector": vec, "fidelity": 0.95}
        elif level == "FP8":
            # Simulate FP8 by quantizing to 256 levels
            v_min, v_max = vector.min(), vector.max()
            scale = (v_max - v_min) / 255 if v_max > v_min else 1.0
            quant = np.round((vector - v_min) / scale).clip(0, 255)
            dequant = quant * scale + v_min
            return {"vector": dequant.astype(np.float32), "fidelity": 0.80}
        return {"vector": vector, "fidelity": 1.0}
    
    def relay_message(self, msg: dict, source_family: str, targets: List[Tuple[str, str]]):
        """Route a tensor message to multiple target agents.
        
        Args:
            msg: The tensor message dict
            source_family: Model family of sender
            targets: List of (agent_name, model_family) tuples
        """
        for agent_name, target_family in targets:
            msg_copy = dict(msg)
            msg_copy["target_family"] = target_family
            self.inbox[agent_name].append(msg_copy)
    
    def get_ontology_stats(self) -> dict:
        """Return statistics about the concept ontology."""
        total = len(self.concept_registry)
        authored = defaultdict(int)
        for c in self.concept_registry.values():
            authored[c.get("author", "system")] += 1
        
        return {
            "total_concepts": total,
            "concepts_by_author": dict(authored),
            "total_royalties": dict(self.concept_royalties),
            "most_used": sorted(
                [(c, r["use_count"]) for c, r in self.concept_registry.items()],
                key=lambda x: -x[1]
            )[:10],
        }
    
    def get_fidelity_matrix(self) -> dict:
        """Return the fidelity matrix for all model family pairs."""
        matrix = {}
        for (src, tgt), proj in self._projectors.items():
            matrix[f"{src}->{tgt}"] = round(proj.get("fidelity", 0.5), 4)
        return matrix

    def upgrade_projector(self, source: str, target: str, investment: float,
                          owner: str = "") -> dict:
        """Improve a cross-family projector through OT investment.
        
        Called when a Projection-Weaver invests in train_projection.
        Investment reduces regularization, increasing fidelity.
        
        Returns: {fidelity_before, fidelity_after, improvement, owner}
        """
        key = (source, target)
        if key not in self._projectors:
            return {"error": f"No projector for {source}->{target}"}
        
        with self._projector_lock:
            proj = self._projectors[key]
        current = proj.get("fidelity", 0.3)
        
        # Diminishing returns: investment improves fidelity toward ceiling
        improvement = min(0.15, investment * 0.003)  # Max +0.15 per upgrade
        new_fidelity = min(0.92, current + improvement)
        
        proj["fidelity"] = new_fidelity
        proj["owner"] = owner
        proj["investment"] = proj.get("investment", 0) + investment
        
        return {
            "source": source, "target": target,
            "fidelity_before": round(current, 4),
            "fidelity_after": round(new_fidelity, 4),
            "improvement": round(improvement, 4),
            "owner": owner,
            "total_investment": proj["investment"],
        }
    
    # ─── Concept Share Market (v4.1 Capital Markets) ───
    
    def _pay_concept_dividend(self, concept: str, amount: float):
        """Distribute dividend to all shareholders of a concept."""
        shares_info = self.concept_shares.get(concept)
        if not shares_info or not shares_info["shareholders"]:
            return
        
        with self._shares_lock:
            total = shares_info["total_shares"]
            for holder, owned in shares_info["shareholders"].items():
                if owned > 0:
                    share = (owned / total) * amount
                    self.dividend_income[holder] += share
            shares_info["dividend_pool"] = shares_info.get("dividend_pool", 0) + amount
    
    def collect_dividends(self, agent: str) -> float:
        """Agent collects accumulated dividends. Returns amount collected."""
        amount = self.dividend_income.get(agent, 0)
        self.dividend_income[agent] = 0
        return round(amount, 2)
    
    def trade_concept_shares(self, concept: str, seller: str, buyer: str,
                             shares: int, price_per_share: float) -> dict:
        """Trade concept shares between agents.
        
        Returns: {success, concept, shares, price, total_cost, seller, buyer}
        """
        with self._shares_lock:
            shares_info = self.concept_shares.get(concept)
            if not shares_info:
                return {"error": f"No shares exist for concept '{concept}'"}
            
            # Verify seller owns enough shares
            seller_portfolio = self.share_portfolios.get(seller, {})
            seller_owned = seller_portfolio.get(concept, 0)
            if seller_owned < shares:
                return {"error": f"{seller} only owns {seller_owned} shares of '{concept}', tried to sell {shares}"}
            
            # Execute trade
            seller_portfolio[concept] -= shares
            if seller_portfolio[concept] <= 0:
                del seller_portfolio[concept]
            
            buyer_portfolio = self.share_portfolios[buyer]
            buyer_portfolio[concept] = buyer_portfolio.get(concept, 0) + shares
            
            # Update share registry
            sh = shares_info["shareholders"]
            sh[seller] = sh.get(seller, 0) - shares
            if sh.get(seller, 0) <= 0:
                sh.pop(seller, None)
            sh[buyer] = sh.get(buyer, 0) + shares
            
            # Update last price
            shares_info["last_price"] = price_per_share
            
            total_cost = shares * price_per_share
        
        return {
            "success": True,
            "concept": concept,
            "shares": shares,
            "price_per_share": price_per_share,
            "total_cost": round(total_cost, 2),
            "seller": seller,
            "buyer": buyer,
            "seller_remaining": seller_portfolio.get(concept, 0),
            "buyer_total": buyer_portfolio.get(concept, 0),
            "market_cap": round(shares_info["total_shares"] * price_per_share, 2),
        }
    
    def place_order(self, concept: str, agent: str, shares: int,
                    price: float, side: str) -> dict:
        """Place a bid or ask order in the order book."""
        with self._shares_lock:
            book = self.order_book[concept]
            order = (agent, shares, price)
            if side == "bid":
                book["bids"].append(order)
                book["bids"].sort(key=lambda x: -x[2])  # Highest bid first
            else:
                book["asks"].append(order)
                book["asks"].sort(key=lambda x: x[2])    # Lowest ask first
        
        return {"placed": side, "concept": concept, "shares": shares, "price": price}
    
    def match_orders(self, concept: str) -> List[dict]:
        """Match bids and asks for a concept. Returns list of executed trades."""
        trades = []
        with self._shares_lock:
            book = self.order_book[concept]
            while book["bids"] and book["asks"]:
                best_bid = book["bids"][0]
                best_ask = book["asks"][0]
                if best_bid[2] >= best_ask[2]:  # Bid >= Ask → trade
                    price = (best_bid[2] + best_ask[2]) / 2
                    trade_shares = min(best_bid[1], best_ask[1])
                    trade = self.trade_concept_shares(
                        concept, best_ask[0], best_bid[0], trade_shares, price
                    )
                    trades.append(trade)
                    # Update remaining quantities
                    if best_bid[1] == trade_shares:
                        book["bids"].pop(0)
                    else:
                        book["bids"][0] = (best_bid[0], best_bid[1] - trade_shares, best_bid[2])
                    if best_ask[1] == trade_shares:
                        book["asks"].pop(0)
                    else:
                        book["asks"][0] = (best_ask[0], best_ask[1] - trade_shares, best_ask[2])
                else:
                    break
        return trades
    
    def get_market_summary(self) -> dict:
        """Return a summary of the concept share market."""
        concepts = []
        for name, info in self.concept_shares.items():
            registry = self.concept_registry.get(name, {})
            concepts.append({
                "concept": name,
                "author": registry.get("author", "system"),
                "shares_outstanding": info["total_shares"],
                "last_price": info["last_price"],
                "market_cap": round(info["total_shares"] * info["last_price"], 2),
                "use_count": registry.get("use_count", 0),
                "dividend_pool": round(info.get("dividend_pool", 0), 2),
                "holders": len(info["shareholders"]),
            })
        concepts.sort(key=lambda x: -x["market_cap"])
        
        return {
            "total_concepts_traded": len(self.concept_shares),
            "total_market_cap": round(sum(c["market_cap"] for c in concepts), 2),
            "top_by_market_cap": concepts[:5],
        }
    
    def get_agent_portfolio(self, agent: str) -> dict:
        """Return an agent's share portfolio and dividend income."""
        portfolio = self.share_portfolios.get(agent, {})
        holdings = []
        total_value = 0.0
        for concept, shares in portfolio.items():
            info = self.concept_shares.get(concept, {})
            price = info.get("last_price", 0.5)
            value = shares * price
            total_value += value
            holdings.append({
                "concept": concept,
                "shares": shares,
                "price": price,
                "value": round(value, 2),
            })
        holdings.sort(key=lambda x: -x["value"])
        
        return {
            "agent": agent,
            "holdings": holdings,
            "total_value": round(total_value, 2),
            "uncollected_dividends": round(self.dividend_income.get(agent, 0), 2),
        }


# Import from config
from config import (
    CONCEPT_REGISTRATION_COST, CONCEPT_ROYALTY_RATE, SEMANTIC_ENCLOSURE_LIMIT,
)
