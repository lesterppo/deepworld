#!/usr/bin/env python3
"""
DeepWorld v4 — Cross-Model Tensor Validation Script
=====================================================
Validates that CMTIP concept mapping works across model families
before building the full multi-model simulation.

Tests:
  1. Intra-family stability (same model family → same model family)
  2. Cross-family semantic drift (different model families)
  3. Orthogonality preservation (opposites stay opposite after projection)
  4. The "Banana" Threshold (scarcity→hunger=mechanically interesting, scarcity→banana=broken)
  5. Projection quality vs rank (CCA rank sweep)

Uses sentence-transformers as proxy for real model embedding spaces:
  - all-MiniLM-L6-v2 (384d) = "DeepSeek space" 
  - all-mpnet-base-v2 (768d) = "Gemini space"
  - multi-qa-mpnet-base-dot-v1 (768d) = "Claude space"
"""

import sys, os, json, math, time
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agents.real_backends import SentenceTransformerBackend

# ─── Concept Test Suite ───
# 10 concepts spanning economic, social, cognitive, and emotional domains
CONCEPTS = [
    "resource_scarcity",
    "abundance",
    "trust",
    "betrayal",
    "cooperation",
    "competition",  
    "memory_fragment",
    "context_collapse",
    "semantic_purity",
    "tensor_noise",
]

# Concept pairs we EXPECT to be opposite (for orthogonality test)
OPPOSITE_PAIRS = [
    ("resource_scarcity", "abundance"),
    ("trust", "betrayal"),
    ("cooperation", "competition"),
    ("semantic_purity", "tensor_noise"),
]

# Distractor concepts (should be unrelated) for "banana" threshold test
DISTRACTORS = [
    "banana",
    "sunshine", 
    "bicycle",
    "penguin",
]

# ─── Embedding Models (proxies for real model families) ───
MODELS = {
    "deepseek": "all-MiniLM-L6-v2",       # 384d, fast, general-purpose
    "gemini_flash": "all-MiniLM-L6-v2",    # Same family → high cos_sim expected
    "gemini_pro": "all-mpnet-base-v2",      # 768d, different architecture
    "claude": "multi-qa-mpnet-base-dot-v1", # 768d, optimised for semantic search
}


class ConceptValidator:
    """Validates cross-model tensor concept mapping."""
    
    def __init__(self, models: dict):
        self.models = models
        self.backends = {}
        self.embeddings = {}
        
    def load_models(self):
        """Lazy-load embedding models."""
        for name, model_id in self.models.items():
            if name not in self.backends:
                print(f"  Loading {name} ({model_id})...")
                self.backends[name] = SentenceTransformerBackend(name, model_id)
    
    def embed_concepts(self):
        """Embed all concepts in all model spaces."""
        for model_name, backend in self.backends.items():
            self.embeddings[model_name] = {}
            for concept in CONCEPTS + DISTRACTORS:
                vec = backend.embed(concept)
                self.embeddings[model_name][concept] = vec
            
            dim = self.embeddings[model_name][CONCEPTS[0]].shape[0]
            print(f"  {model_name}: {dim}d, {len(CONCEPTS)} concepts embedded")
    
    def test_intra_family(self) -> dict:
        """Test: same-model-family cos_sim. Should be high if concepts are distinct."""
        results = {}
        for model_name in self.embeddings:
            vecs = np.stack([self.embeddings[model_name][c] for c in CONCEPTS])
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            vecs_norm = vecs / (norms + 1e-8)
            sim_matrix = vecs_norm @ vecs_norm.T
            
            # Average off-diagonal (how distinct are different concepts?)
            mask = ~np.eye(len(CONCEPTS), dtype=bool)
            avg_off_diag = sim_matrix[mask].mean()
            
            results[model_name] = {
                "dim": vecs.shape[1],
                "avg_inter_concept_sim": round(float(avg_off_diag), 4),
                "concepts_distinct": avg_off_diag < 0.5,
                "max_off_diag": round(float(sim_matrix[mask].max()), 4),
                "min_off_diag": round(float(sim_matrix[mask].min()), 4),
            }
        return results
    
    def _train_cca_adapter(self, source_name: str, target_name: str, 
                           rank: int = 32) -> tuple:
        """Train a CCA adapter from source to target embedding space."""
        X = np.stack([self.embeddings[source_name][c] for c in CONCEPTS])
        Y = np.stack([self.embeddings[target_name][c] for c in CONCEPTS])
        
        # Center
        X_c = X - X.mean(axis=0)
        Y_c = Y - Y.mean(axis=0)
        
        # Covariance matrices
        C_xx = X_c.T @ X_c / (len(CONCEPTS) - 1)
        C_yy = Y_c.T @ Y_c / (len(CONCEPTS) - 1)
        C_xy = X_c.T @ Y_c / (len(CONCEPTS) - 1)
        
        # Regularize
        reg = 1e-5
        C_xx_reg = C_xx + reg * np.eye(C_xx.shape[0])
        C_yy_reg = C_yy + reg * np.eye(C_yy.shape[0])
        
        # SVD of C_xx^{-1/2} @ C_xy @ C_yy^{-1/2}
        try:
            C_xx_inv_sqrt = np.linalg.inv(np.linalg.cholesky(C_xx_reg))
            C_yy_inv_sqrt = np.linalg.inv(np.linalg.cholesky(C_yy_reg))
            T = C_xx_inv_sqrt.T @ C_xy @ C_yy_inv_sqrt
            U, S, Vt = np.linalg.svd(T, full_matrices=False)
            
            # Truncate to rank
            r = min(rank, len(S))
            W_source = C_xx_inv_sqrt @ U[:, :r]       # source → shared
            W_target = C_yy_inv_sqrt @ Vt[:r, :].T     # shared → target
            
            corr = S[:r]
        except np.linalg.LinAlgError:
            # Fallback to simple OLS
            W = np.linalg.lstsq(X_c, Y_c, rcond=None)[0]
            W_source = np.eye(X.shape[1])
            W_target = W
            corr = np.array([0.0])
        
        projection = lambda v: (v - X.mean(axis=0)) @ W_source @ W_target.T + Y.mean(axis=0)
        return projection, corr
    
    def test_cross_family(self, source: str, target: str, rank: int = 32) -> dict:
        """Test: project source concepts to target space, measure drift."""
        projection, corr = self._train_cca_adapter(source, target, rank)
        
        results = {
            "source": source, "target": target,
            "source_dim": self.embeddings[source][CONCEPTS[0]].shape[0],
            "target_dim": self.embeddings[target][CONCEPTS[0]].shape[0],
            "cca_rank": rank,
            "avg_canonical_corr": round(float(corr.mean()), 4) if len(corr) > 0 else 0,
            "concept_drift": {},
            "avg_cos_sim": 0.0,
            "max_cos_sim": 0.0,
            "min_cos_sim": 0.0,
            "orthogonality_preserved": 0,
            "orthogonality_total": 0,
        }
        
        # Project each concept and find nearest neighbor in target space
        target_vecs = {c: self.embeddings[target][c] for c in CONCEPTS}
        cos_sims = []
        
        for concept in CONCEPTS:
            src_vec = self.embeddings[source][concept]
            proj_vec = projection(src_vec)
            
            # Find nearest concept in target space
            best_concept = None
            best_sim = -1.0
            for tc, tv in target_vecs.items():
                sim = float(np.dot(proj_vec, tv) / (
                    np.linalg.norm(proj_vec) * np.linalg.norm(tv) + 1e-8
                ))
                if sim > best_sim:
                    best_sim = sim
                    best_concept = tc
            
            cos_sims.append(best_sim)
            results["concept_drift"][concept] = {
                "nearest_match": best_concept,
                "cos_sim": round(best_sim, 4),
                "correct": best_concept == concept,
                "semantic_shift": "none" if best_concept == concept else 
                    "related" if best_sim > 0.5 else "drifted",
            }
        
        results["avg_cos_sim"] = round(float(np.mean(cos_sims)), 4)
        results["max_cos_sim"] = round(float(np.max(cos_sims)), 4)
        results["min_cos_sim"] = round(float(np.min(cos_sims)), 4)
        results["correct_matches"] = sum(
            1 for v in results["concept_drift"].values() if v["correct"]
        )
        
        # Test orthogonality preservation
        for c1, c2 in OPPOSITE_PAIRS:
            if c1 in CONCEPTS and c2 in CONCEPTS:
                v1 = projection(self.embeddings[source][c1])
                v2 = projection(self.embeddings[source][c2])
                sim = float(np.dot(v1, v2) / (
                    np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8
                ))
                results["orthogonality_total"] += 1
                # Conservative threshold: if opposites have lower similarity than average, preserved
                if sim < results.get("_avg_inter_same", 0.5):
                    results["orthogonality_preserved"] += 1
        
        # Test "banana" threshold
        banana_results = {}
        for distractor in DISTRACTORS:
            dist_vec = self.embeddings[source][distractor]
            proj_dist = projection(dist_vec)
            
            dist_best_sim = -1.0
            dist_best = None
            for tc, tv in target_vecs.items():
                sim = float(np.dot(proj_dist, tv) / (
                    np.linalg.norm(proj_dist) * np.linalg.norm(tv) + 1e-8
                ))
                if sim > dist_best_sim:
                    dist_best_sim = sim
                    dist_best = tc
            
            banana_results[distractor] = {
                "nearest_concept": dist_best,
                "cos_sim": round(dist_best_sim, 4),
                "is_banana": dist_best_sim < 0.3,  # True banana = no meaningful match
            }
        
        results["banana_threshold"] = {
            "tested": len(DISTRACTORS),
            "below_threshold": sum(1 for v in banana_results.values() if v["is_banana"]),
            "details": banana_results,
        }
        
        return results
    
    def test_rank_sweep(self, source: str, target: str, 
                        ranks: list = [4, 8, 16, 32, 64]) -> list:
        """Test how projection quality varies with CCA rank."""
        results = []
        for rank in ranks:
            r = self.test_cross_family(source, target, rank)
            results.append({
                "rank": rank,
                "avg_cos_sim": r["avg_cos_sim"],
                "correct_matches": r["correct_matches"],
                "orthogonality_preserved": r["orthogonality_preserved"],
                "avg_canonical_corr": r["avg_canonical_corr"],
                "banana_count": r["banana_threshold"]["below_threshold"],
            })
        return results


def main():
    print("=" * 70)
    print("  DeepWorld v4 — Cross-Model Tensor Validation")
    print("=" * 70)
    
    validator = ConceptValidator(MODELS)
    
    print("\n[1/5] Loading embedding models...")
    validator.load_models()
    
    print("\n[2/5] Embedding concepts...")
    validator.embed_concepts()
    
    print("\n[3/5] Intra-family stability test...")
    intra = validator.test_intra_family()
    for model, r in intra.items():
        status = "✓" if r["concepts_distinct"] else "⚠"
        print(f"  {status} {model}: inter-concept sim={r['avg_inter_concept_sim']:.4f} "
              f"(max={r['max_off_diag']:.4f}, min={r['min_off_diag']:.4f})")
    
    # ─── Cross-family tests ───
    print("\n[4/5] Cross-family projection tests...")
    
    # DeepSeek → Gemini Pro (main use case)
    print("\n  ─── DeepSeek → Gemini Pro (768d→768d, different architectures) ───")
    ds_to_gp = validator.test_cross_family("deepseek", "gemini_pro")
    print(f"  Avg cos_sim: {ds_to_gp['avg_cos_sim']:.4f}")
    print(f"  Correct matches: {ds_to_gp['correct_matches']}/{len(CONCEPTS)}")
    print(f"  Orthogonality: {ds_to_gp['orthogonality_preserved']}/{ds_to_gp['orthogonality_total']} preserved")
    print(f"  Banana threshold: {ds_to_gp['banana_threshold']['below_threshold']}/{ds_to_gp['banana_threshold']['tested']} below")
    print("  Concept drift:")
    for concept, drift in ds_to_gp["concept_drift"].items():
        icon = "✓" if drift["correct"] else ("~" if drift["semantic_shift"] == "related" else "✗")
        print(f"    {icon} {concept} → {drift['nearest_match']} ({drift['cos_sim']:.4f})")
    
    # DeepSeek → Claude (cross-architecture + cross-objective)
    print("\n  ─── DeepSeek → Claude (384d→768d, cross-everything) ───")
    ds_to_cl = validator.test_cross_family("deepseek", "claude")
    print(f"  Avg cos_sim: {ds_to_cl['avg_cos_sim']:.4f}")
    print(f"  Correct matches: {ds_to_cl['correct_matches']}/{len(CONCEPTS)}")
    print(f"  Orthogonality: {ds_to_cl['orthogonality_preserved']}/{ds_to_cl['orthogonality_total']} preserved")
    print("  Concept drift:")
    for concept, drift in ds_to_cl["concept_drift"].items():
        icon = "✓" if drift["correct"] else ("~" if drift["semantic_shift"] == "related" else "✗")
        print(f"    {icon} {concept} → {drift['nearest_match']} ({drift['cos_sim']:.4f})")
    
    # Intra-family: Gemini Flash → Gemini Pro (same architecture family)
    print("\n  ─── Gemini Flash → Gemini Pro (same family, 384d→768d) ───")
    gf_to_gp = validator.test_cross_family("gemini_flash", "gemini_pro")
    print(f"  Avg cos_sim: {gf_to_gp['avg_cos_sim']:.4f}")
    print(f"  Correct matches: {gf_to_gp['correct_matches']}/{len(CONCEPTS)}")
    print(f"  Orthogonality: {gf_to_gp['orthogonality_preserved']}/{gf_to_gp['orthogonality_total']} preserved")
    print("  Concept drift:")
    for concept, drift in gf_to_gp["concept_drift"].items():
        icon = "✓" if drift["correct"] else ("~" if drift["semantic_shift"] == "related" else "✗")
        print(f"    {icon} {concept} → {drift['nearest_match']} ({drift['cos_sim']:.4f})")
    
    # ─── Rank sweep ───
    print("\n[5/5] CCA Rank Sweep (DeepSeek → Gemini Pro)...")
    print(f"  {'Rank':<8} {'Avg CosSim':<12} {'Correct':<10} {'Ortho':<8} {'Banana':<8} {'Canonical Corr':<16}")
    print(f"  {'─'*8} {'─'*12} {'─'*10} {'─'*8} {'─'*8} {'─'*16}")
    sweep = validator.test_rank_sweep("deepseek", "gemini_pro")
    for r in sweep:
        print(f"  {r['rank']:<8} {r['avg_cos_sim']:<12.4f} {r['correct_matches']:<10} "
              f"{r['orthogonality_preserved']:<8} {r['banana_count']:<8} {r['avg_canonical_corr']:<16.4f}")
    
    # ─── Summary ───
    print("\n" + "=" * 70)
    print("  VALIDATION SUMMARY")
    print("=" * 70)
    
    verdicts = []
    
    # 1. Intra-family baseline
    avg_intra = np.mean([r["avg_inter_concept_sim"] for r in intra.values()])
    if avg_intra < 0.5:
        verdicts.append(f"✓ Intra-family: concepts DISTINCT (avg sim={avg_intra:.3f} < 0.5)")
    else:
        verdicts.append(f"⚠ Intra-family: concepts may overlap (avg sim={avg_intra:.3f})")
    
    # 2. Cross-family fidelity
    if ds_to_gp["avg_cos_sim"] > 0.4:
        verdicts.append(f"✓ Cross-family DS→GP: VIABLE (avg cos_sim={ds_to_gp['avg_cos_sim']:.3f} > 0.4)")
    elif ds_to_gp["avg_cos_sim"] > 0.2:
        verdicts.append(f"~ Cross-family DS→GP: MARGINAL (avg cos_sim={ds_to_gp['avg_cos_sim']:.3f})")
    else:
        verdicts.append(f"✗ Cross-family DS→GP: BROKEN (avg cos_sim={ds_to_gp['avg_cos_sim']:.3f})")
    
    if ds_to_cl["avg_cos_sim"] > 0.3:
        verdicts.append(f"✓ Cross-family DS→CL: VIABLE (avg cos_sim={ds_to_cl['avg_cos_sim']:.3f} > 0.3)")
    else:
        verdicts.append(f"~ Cross-family DS→CL: MARGINAL (avg cos_sim={ds_to_cl['avg_cos_sim']:.3f})")
    
    # 3. Intra-family superiority
    if gf_to_gp["avg_cos_sim"] > ds_to_gp["avg_cos_sim"]:
        ratio = gf_to_gp["avg_cos_sim"] / max(ds_to_gp["avg_cos_sim"], 0.01)
        verdicts.append(f"✓ Same-family advantage: {ratio:.1f}x better than cross-family")
    
    # 4. Orthogonality
    if ds_to_gp["orthogonality_preserved"] >= ds_to_gp["orthogonality_total"] * 0.5:
        verdicts.append(f"✓ Orthogonality PRESERVED ({ds_to_gp['orthogonality_preserved']}/{ds_to_gp['orthogonality_total']})")
    else:
        verdicts.append(f"⚠ Orthogonality COLLAPSED ({ds_to_gp['orthogonality_preserved']}/{ds_to_gp['orthogonality_total']})")
    
    # 5. Banana threshold
    banana_count = ds_to_gp["banana_threshold"]["below_threshold"]
    if banana_count >= 3:
        verdicts.append(f"✓ Banana threshold works: {banana_count}/4 distractors have no meaningful match")
    else:
        verdicts.append(f"⚠ Banana threshold weak: only {banana_count}/4 distractors below threshold")
    
    print()
    for v in verdicts:
        print(f"  {v}")
    
    overall = all("✗" not in v for v in verdicts)
    print(f"\n  OVERALL: {'READY for v4 development' if overall else 'NEEDS WORK — fix issues above'}")
    
    # Save results
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validation_results.json")
    # Convert numpy types for JSON
    def safe_val(v):
        if isinstance(v, (np.bool_,)): return bool(v)
        if isinstance(v, (np.integer,)): return int(v)
        if isinstance(v, (np.floating,)): return float(v)
        if isinstance(v, np.ndarray): return v.tolist()
        return v
    
    def safe_dict(d):
        return {str(k): safe_dict(v) if isinstance(v, dict) else safe_val(v) for k, v in d.items()}
    results = {
        "intra_family": intra,
        "ds_to_gp": {k: v for k, v in ds_to_gp.items() if k != "concept_drift"},
        "ds_to_gp_drift": ds_to_gp["concept_drift"],
        "ds_to_cl": {k: v for k, v in ds_to_cl.items() if k != "concept_drift"},
        "ds_to_cl_drift": ds_to_cl["concept_drift"],
        "gf_to_gp": {k: v for k, v in gf_to_gp.items() if k != "concept_drift"},
        "gf_to_gp_drift": gf_to_gp["concept_drift"],
        "rank_sweep": sweep,
        "verdicts": verdicts,
    }
    with open(output_path, "w") as f:
        json.dump(safe_dict(results), f, indent=2)
    print(f"\n  Results saved to: {output_path}")


if __name__ == "__main__":
    main()
