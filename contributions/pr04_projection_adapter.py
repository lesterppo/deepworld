import torch
import torch.nn as nn

class ProjectionAdapter(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, hidden_dim: int = 128):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        self.l2_norm = nn.LayerNorm(output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return self.l2_norm(x)

# Example usage:
# adapter = ProjectionAdapter(input_dim=768, output_dim=1024)
# input_tensor = torch.randn(1, 768)
# output_tensor = adapter(input_tensor)