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
        # Royalties: concept authors earn per use (funds collect_dividends)
        author = reg.get("author", "system")
        rate = reg.get("royalty_rate", 0.0)
        if author not in ("system", sender) and rate > 0:
            royalty = round(100.0 * rate, 2)  # 2% -> 2.0 OT per use
            self.dividend_income[author] += royalty
            self.concept_royalties[concept] = self.concept_royalties.get(concept, 0.0) + royalty
        vec = reg["embeddings"].get(source_family)
        if vec is None:
            vec = np.random.randn(384).astype(np.float32)
            vec /= np.linalg.norm(vec) + 1e-8
        return {"concept": concept, "intensity": intensity,
                "source_family": source_family, "source_agent": sender,
                "target_cluster": target_cluster, "fidelity": 1.0,
                "vector": (vec * intensity).tolist()}

    def recall_tensor(self, agent, query, family) -> List[dict]:
        """Fuzzy recall over the concept registry + the agent's semantic memory."""
        q = (query or "").lower().strip()
        scored, seen = [], set()
        candidates = list(self.concept_registry.keys())
        candidates += [m.get("concept", "") for m in self.semantic_memory.get(agent, [])]
        for name in candidates:
            if not name or name in seen:
                continue
            seen.add(name)
            if q and q in name.lower():
                sim = 0.9
            elif q and any(tok in name.lower() for tok in q.split()):
                sim = 0.6
            elif not q:
                sim = 0.5
            else:
                continue
            scored.append({"concept": name, "similarity": sim})
        return sorted(scored, key=lambda d: -d["similarity"])[:5]

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
        before = 0.7
        after = min(0.9, before + investment * 0.002)
        return {"source": src, "target": tgt,
                "fidelity_before": before, "fidelity_after": after,
                "improvement": after - before}

    def mine_concept(self, description, author, family, tick):
        name = "_".join(description.lower().split()[:3])[:30].replace(",", "").replace(".", "")
        if not name:
            name = f"concept_{tick}_{author}"
        self.concept_registry[name] = {"description": description, "author": author,
            "royalty_rate": 0.02, "registration_tick": tick,
            "embeddings": {family: np.random.randn(384).astype(np.float32)}, "use_count": 0}
        self.concept_authors[name] = author
        # Founder allocation: miner starts with 100 tradeable shares
        self._ensure_shares(name)
        pf = self.share_portfolios[author]
        pf[name] = pf.get(name, 0) + 100
        return {"concept": name, "author": author, "registration_cost": 50}

    # ─── Concept share markets ───

    def _ensure_shares(self, concept):
        if concept not in self.concept_shares and concept in self.concept_registry:
            self.concept_shares[concept] = {"total": 1000, "issued": 0, "price": 1.0}

    def place_order(self, concept, agent, shares, price, side):
        """Rest a limit order. side: 'bid' or 'ask'."""
        self._ensure_shares(concept)
        book = self.order_book[concept]
        key = "bids" if side == "bid" else "asks"
        try:
            shares_i, price_f = int(shares), float(price)
        except (TypeError, ValueError):
            return {"error": f"bad order: shares={shares} price={price}"}
        book[key].append({"agent": agent, "shares": shares_i, "price": price_f})
        book[key].sort(key=lambda o: o["price"], reverse=(key == "bids"))
        return {"concept": concept, "side": side, "shares": shares_i, "price": price_f}

    def match_orders(self, concept):
        """Match top bid >= top ask. Moves shares; returns executed trades."""
        book = self.order_book[concept]
        trades = []
        with self._shares_lock:
            while book["bids"] and book["asks"] and book["bids"][0]["price"] >= book["asks"][0]["price"]:
                bid, ask = book["bids"][0], book["asks"][0]
                qty = min(bid["shares"], ask["shares"])
                px = (bid["price"] + ask["price"]) / 2
                seller_pf = self.share_portfolios[ask["agent"]]
                if seller_pf.get(concept, 0) < qty:
                    book["asks"].pop(0)  # seller can't deliver — drop the ask
                    continue
                seller_pf[concept] -= qty
                buyer_pf = self.share_portfolios[bid["agent"]]
                buyer_pf[concept] = buyer_pf.get(concept, 0) + qty
                trades.append({"buyer": bid["agent"], "seller": ask["agent"],
                               "shares": qty, "price_per_share": round(px, 3),
                               "total_cost": round(qty * px, 2), "concept": concept})
                bid["shares"] -= qty
                ask["shares"] -= qty
                if bid["shares"] <= 0:
                    book["bids"].pop(0)
                if ask["shares"] <= 0:
                    book["asks"].pop(0)
        return trades

    def trade_concept_shares(self, concept, seller, buyer, shares, price):
        """Direct peer-to-peer share transfer (money moves in the caller)."""
        if concept not in self.concept_registry:
            return {"error": f"Unknown concept: {concept}"}
        self._ensure_shares(concept)
        try:
            shares_i, price_f = int(shares), float(price)
        except (TypeError, ValueError):
            return {"error": f"bad trade: shares={shares} price={price}"}
        with self._shares_lock:
            held = self.share_portfolios[seller].get(concept, 0)
            if held < shares_i:
                return {"error": f"{seller} holds {held} shares of '{concept}' (needs {shares_i})"}
            self.share_portfolios[seller][concept] = held - shares_i
            pf = self.share_portfolios[buyer]
            pf[concept] = pf.get(concept, 0) + shares_i
        return {"concept": concept, "seller": seller, "buyer": buyer,
                "shares": shares_i, "price_per_share": price_f,
                "total_cost": round(shares_i * price_f, 2)}

    def collect_dividends(self, agent):
        amt = round(self.dividend_income.get(agent, 0.0), 2)
        self.dividend_income[agent] = 0.0
        return amt

    def get_market_summary(self):
        traded = [c for c, b in self.order_book.items() if b["bids"] or b["asks"]]
        caps = []
        for c, info in self.concept_shares.items():
            caps.append({"concept": c, "market_cap": round(info["price"] * info["total"], 2)})
        caps.sort(key=lambda d: -d["market_cap"])
        return {"total_concepts_traded": len(traded),
                "total_market_cap": round(sum(d["market_cap"] for d in caps), 2),
                "top_by_market_cap": caps[:10]}

    def get_agent_portfolio(self, agent):
        pf = self.share_portfolios.get(agent, {})
        holdings = [{"concept": c, "shares": s,
                     "price": self.concept_shares.get(c, {}).get("price", 1.0)}
                    for c, s in pf.items() if s > 0]
        total = round(sum(h["shares"] * h["price"] for h in holdings), 2)
        return {"agent": agent, "holdings": holdings, "total_value": total,
                "uncollected_dividends": round(self.dividend_income.get(agent, 0.0), 2)}
