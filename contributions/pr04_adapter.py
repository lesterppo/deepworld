# PR-04: Cross-family projection adapter for nvidia agents
# This module defines a lightweight projection adapter that can be trained or
# fine‑tuned to map embeddings from a source model family to a target
# model family. The adapter is intentionally simple to keep token usage low.

import torch
import torch.nn as nn

class ProjectionAdapter(nn.Module):
    """A learnable linear mapping between two embedding spaces.

    Parameters
    ----------
    dim : int
        Dimensionality of the embedding space (assumed equal for source
        and target families).
    """
    def __init__(self, dim: int):
        super().__init__()
        # Weight matrix of shape (dim, dim)
        self.weight = nn.Parameter(torch.randn(dim, dim) * 0.01)
        # Optional bias term
        self.bias = nn.Parameter(torch.zeros(dim))

    def forward(self, src: torch.Tensor) -> torch.Tensor:
        """Map source embeddings to target space.

        Parameters
        ----------
        src : torch.Tensor
            Tensor of shape (..., dim) representing embeddings from the
            source model family.

        Returns
        -------
        torch.Tensor
            Mapped embeddings in the target model family's space.
        """
        return torch.matmul(src, self.weight.t()) + self.bias

    def train_adapter(self, data_loader, lr=1e-3, epochs=5):
        """Fine‑tune the adapter using a simple MSE loss.

        Parameters
        ----------
        data_loader : iterable
            Provides pairs of (src_embedding, tgt_embedding).
        lr : float, optional
            Learning rate for the optimizer.
        epochs : int, optional
            Number of training epochs.
        """
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        loss_fn = nn.MSELoss()
        for epoch in range(epochs):
            for src, tgt in data_loader:
                optimizer.zero_grad()
                pred = self.forward(src)
                loss = loss_fn(pred, tgt)
                loss.backward()
                optimizer.step()

# Example usage (pseudo‑code):
# adapter = ProjectionAdapter(dim=768)
# adapter.train_adapter(training_loader)
# mapped = adapter(src_embedding)

# The adapter can be serialized and shared as a projection matrix.
# Save weight and bias as a dictionary.
# torch.save({'weight': adapter.weight, 'bias': adapter.bias}, 'adapter.pt')

# End of PR-04 adapter module.
