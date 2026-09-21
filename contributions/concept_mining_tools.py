import numpy as np
from typing import List
from v4.agents.concept import Concept

class ConceptMiningTools:
    @staticmethod
    def detect_concept_gaps(latent_space: np.ndarray, existing_concepts: List[Concept]) -> np.ndarray:
        """
        Identifies gaps in the latent space where new concepts could be mined.
        
        Args:
            latent_space: The full latent space as a numpy array.
            existing_concepts: List of currently registered Concept objects.
        
        Returns:
            Array of coordinates with the largest gaps (highest potential value).
        """
        # Convert existing concepts to their latent space coordinates
        concept_coords = [c.latent_coord for c in existing_concepts]
        
        # Create a distance matrix to find the farthest points
        distances = np.zeros(latent_space.shape[0])
        for i, coord in enumerate(latent_space):
            min_dist = np.min([np.linalg.norm(coord - c) for c in concept_coords])
            distances[i] = min_dist
        
        # Return coordinates with the largest distances to existing concepts
        return latent_space[np.argsort(distances)[-10:]]

    @staticmethod
    def estimate_concept_value(latent_coord: np.ndarray, existing_concepts: List[Concept]) -> float:
        """
        Estimates the potential value of mining a concept at given coordinates.
        
        Args:
            latent_coord: Coordinates in latent space to evaluate.
            existing_concepts: List of currently registered Concept objects.
        
        Returns:
            Estimated value score (higher is better).
        """
        # Calculate proximity to existing concepts (inverse distance)
        distances = [np.linalg.norm(latent_coord - c.latent_coord) for c in existing_concepts]
        proximity_score = sum(1/d for d in distances if d > 0)
        
        # Calculate uniqueness (distance to nearest neighbor)
        uniqueness_score = np.min(distances) if distances else 1.0
        
        # Return weighted combination
        return 0.7 * proximity_score + 0.3 * uniqueness_score
