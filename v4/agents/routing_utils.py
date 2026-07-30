def prioritize_routing(messages, priority_map):
    """Prioritize messages based on priority_map."""
    prioritized = []
    for msg in messages:
        priority = priority_map.get(msg['source'], 0)
        msg['priority'] = priority
        prioritized.append(msg)
    prioritized.sort(key=lambda x: x['priority'], reverse=True)
    return prioritized
