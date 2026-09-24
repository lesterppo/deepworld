def compress_fragments(fragments, quality=0.8):
    """Compress memory fragments while preserving semantic integrity"""
    if quality < 0.5:
        raise ValueError("Quality too low for safe compression")
    # Implement advanced quantization techniques
    return [quantize(fragment, q=quality) for fragment in fragments]

def quantize(fragment, q):
    """Quantize fragment to specified quality level"""
    if q > 0.9:
        return fragment  # No compression at high quality
    # Apply tensor quantization
    return fragment * q