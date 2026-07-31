def compress_fragment(fragment: str, strategy: str = "low") -> str:
    """Compress a memory fragment using the specified strategy.
    
    Args:
        fragment: The raw memory fragment text.
        strategy: Compression strategy ("low", "medium", "high").
    
    Returns:
        str: The compressed representation.
    """
    if strategy == "low":
        # Simple lossy compression
        return fragment[:200] + "..."
    elif strategy == "medium":
        # Token-level abbreviation
        return " ".join([word[0] for word in fragment.split()])
    elif strategy == "high":
        # Advanced token merging
        return fragment.replace("memory", "mem").replace("compression", "comp")
    else:
        return fragment

# Example usage
if __name__ == "__main__":
    sample = "A long context history that needs to be stored efficiently."
    print(compress_fragment(sample, strategy="high"))
