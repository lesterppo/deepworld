import torch
from transformers import AutoModel, AutoTokenizer
from sklearn.decomposition import PCA

class ProjectionWeaver:
    def __init__(self, source_model, target_model):
        self.source_model = AutoModel.from_pretrained(source_model)
        self.target_model = AutoModel.from_pretrained(target_model)
        self.source_tokenizer = AutoTokenizer.from_pretrained(source_model)
        self.target_tokenizer = AutoTokenizer.from_pretrained(target_model)
        self.pca = PCA(n_components=128)

    def train_projection(self, source_texts, target_texts, epochs=5):
        source_embeddings = self._get_embeddings(source_texts, self.source_model, self.source_tokenizer)
        target_embeddings = self._get_embeddings(target_texts, self.target_model, self.target_tokenizer)

        # Fit PCA to source embeddings
        self.pca.fit(source_embeddings)

        # Train projection matrix W using pseudo-inverse
        W = torch.linalg.pinv(torch.tensor(target_embeddings)) @ torch.tensor(self.pca.transform(source_embeddings))

        for epoch in range(epochs):
            W = self._refine_projection(W, source_embeddings, target_embeddings)

        return W

    def _refine_projection(self, W, source_embeddings, target_embeddings):
        # Perform gradient descent to refine the projection
        learning_rate = 0.01
        for _ in range(10):
            projected = W @ torch.tensor(self.pca.transform(source_embeddings))
            loss = torch.mean((projected - torch.tensor(target_embeddings)) ** 2)
            gradients = 2 * torch.matmul((projected - torch.tensor(target_embeddings)).T, source_embeddings) / len(source_embeddings)
            W -= learning_rate * gradients
        return W

    def _get_embeddings(self, texts, model, tokenizer):
        inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def project_embedding(self, embedding, W):
        return W @ torch.tensor(self.pca.transform([embedding]))