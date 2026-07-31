def compress_fragment(fragment: str, max_tokens: int) -> str:
    """Compress a memory fragment to fit within max_tokens.
    Truncates tail if exceeds limit, preserving head.
    """
    if len(fragment) <= max_tokens:
        return fragment
    return fragment[:max_tokens]


def purge_low_priority(fragments: list, priority_func, keep_ratio: float = 0.7) -> list:
    """Retain top keep_ratio of fragments by priority.
    fragments: list of (description, priority_score) tuples.
    """
    sorted_fragments = sorted(fragments, key=lambda x: x[1], reverse=True)
    keep_len = int(len(sorted_fragments) * keep_ratio)
    return sorted_fragments[:keep_len]
