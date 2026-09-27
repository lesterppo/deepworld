import torch
import torch.nn as nn

class ProjectionAdapter(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.fc = nn.Linear(input_dim, output_dim)

    def forward(self, x):
        return self.fc(x)

class ProjectionTrainer:
    def __init__(self, source_model, target_model):
        self.source_model = source_model
        self.target_model = target_model
        self.adapter = ProjectionAdapter(source_model.output_dim, target_model.input_dim)
        self.loss_fn = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.adapter.parameters(), lr=0.001)

    def train_step(self, source_tensor, target_tensor):
        # Forward pass
        projected = self.adapter(source_tensor)
        loss = self.loss_fn(projected, target_tensor)

        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def evaluate_fidelity(self, test_tensors):
        total_loss = 0.0
        count = 0
        for source, target in test_tensors:
            with torch.no_grad():
                projected = self.adapter(source)
                loss = self.loss_fn(projected, target)
                total_loss += loss.item()
                count += 1
        return 1.0 - (total_loss / count)  # Fidelity score (0-1)