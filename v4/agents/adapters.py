import torch
import torch.nn as nn

class TensorRouter(nn.Module):
    def __init__(self, model_family, target_family):
        super().__init__()
        self.model_family = model_family
        self.target_family = target_family
        self.relay_fee = 0.05  # Default 5% relay fee
        
        # Initialize projection matrices
        self.forward_proj = nn.Linear(768, 768)  # Example dimensions
        self.backward_proj = nn.Linear(768, 768)
        
    def forward(self, tensor, priority=0):
        """Route tensor through the CMTIP bus.
        Args:
            tensor: Input tensor to route
            priority: Message priority (0-10)
        Returns:
            Projected tensor with relay fee deducted
        """
        # Apply projection
        routed = self.forward_proj(tensor)
        
        # Apply relay fee
        fee = self.relay_fee * torch.norm(routed)
        routed = routed / (1 + self.relay_fee)
        
        # Apply priority-based boost
        if priority > 0:
            routed = routed * (1 + priority * 0.1)
        
        return routed
    
    def set_fee(self, new_fee):
        """Set new relay fee percentage"""
        self.relay_fee = min(max(new_fee, 0.01), 0.5)  # Clamp between 1% and 50%
    
    @property
    def fidelity(self):
        """Estimated projection fidelity"""
        # Simple heuristic based on fee level
        return 1.0 - (self.relay_fee * 0.8)
