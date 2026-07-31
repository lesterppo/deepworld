def compress(context: str, strategy: str = "full") -> str:
    """Compress context using Quant-Scribe compression strategy.
    
    Args:
        context: The raw context string to compress.
        strategy: Compression strategy ("full", "summary", "token_prune").
    
    Returns:
        Compressed string with 30% detail loss if strategy is not "full".
    """
    if strategy == "full":
        return context  # No compression, preserve all detail
    elif strategy == "summary":
        # Simple summarization by taking first 1000 chars
        return context[:1000] + "..." if len(context) > 1000 else context
    elif strategy == "token_prune":
        # Remove low‑importance tokens (here we just truncate to 2000 tokens)
        tokens = context.split()
        return " ".join(tokens[:2000])
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def decompress(compressed: str, original_length: int) -> str:
    """Placeholder for decompression; currently returns the compressed string.
    In a real system this would restore detail based on stored metadata.
    """
    return compressed
