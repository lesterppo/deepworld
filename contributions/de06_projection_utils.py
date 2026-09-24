# Projection utilities for cross-model adapters
# Author: PR-04
# This module provides helper functions to train, cache, and retrieve projection adapters
# between model families. The adapters are simple linear transforms stored as numpy arrays.

import numpy as np
from typing import Tuple

# Simple in-memory registry of adapters
_adapter_registry = {}


def train_adapter(source_family: str, target_family: str, data: np.ndarray, dim: int = 512, epochs: int = 10, lr: float = 0.01) -> np.ndarray:
    """Train a linear projection adapter from source_family to target_family.
    Args:
        source_family: Name of the source model family.
        target_family: Name of the target model family.
        data: Training data matrix (samples x dim).
        dim: Embedding dimensionality.
        epochs: Number of gradient steps.
        lr: Learning rate.
    Returns:
        The trained weight matrix (dim x dim).
    """
    # Random initialization
    W = np.random.randn(dim, dim) * 0.01
    for _ in range(epochs):
        # Forward pass
        proj = data @ W
        # Simple L2 loss to identity (placeholder for real objective)
        loss = np.mean((proj - data) ** 2)
        # Gradient descent step
        grad = 2 * (proj - data).T @ data / data.shape[0]
        W -= lr * grad
    # Register adapter
    _adapter_registry[(source_family, target_family)] = W
    return W


def get_adapter(source_family: str, target_family: str) -> np.ndarray:
    """Retrieve a trained adapter. Raises KeyError if not found."""
    return _adapter_registry[(source_family, target_family)]


def blend_concepts(a: np.ndarray, b: np.ndarray, ratio: float) -> np.ndarray:
    """Blend two concept vectors in embedding space.
    Args:
        a: First concept vector.
        b: Second concept vector.
        ratio: 0.0 -> pure a, 1.0 -> pure b.
    Returns:
        Blended vector.
    """
    return (1 - ratio) * a + ratio * b

# Example usage:
# adapter = train_adapter('gemini', 'deepseek', np.random.randn(100, 512))
# blended = blend_concepts(np.random.randn(512), np.random.randn(512), 0.7)
