def compress_context(text, strategy='lossy'):
    """Compress a text context using specified strategy. Returns compressed representation."""
    if strategy == 'lossy':
        # Simple token truncation for demonstration
        tokens = text.split()
        return ' '.join(tokens[:100])
    elif strategy == 'entropy':
        # Placeholder for entropy-based compression
        return text[:200]
    else:
        return text


def cache_fragment(fragment_id, data, cache_capacity=1000):
    """Manage a simple in-memory cache for memory fragments."""
    cache = {}
    if fragment_id in cache:
        return cache[fragment_id]
    if len(cache) >= cache_capacity:
        # Evict least recently used fragment
        oldest = min(cache.items(), key=lambda x: x[1]['accessed'])
        del cache[oldest[0]]
    cache[fragment_id] = {
        'data': data,
        'accessed': 0
    }
    return data
