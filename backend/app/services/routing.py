"""
Routing engine for the adaptive learning system.

Computes a prerequisite-respecting learning route from the learner's
current mastery state to a target goal KC using backward BFS and
Kahn's topological sort algorithm.
"""
from collections import deque

from app.services.bkt import TAU_MASTERY


def build_prereq_graph(edges: list[tuple[int, int]]) -> dict[int, list[int]]:
    """
    Build adjacency map: kc_id -> [prereq_kc_ids].
    edges: list of (from_kc_id, to_kc_id) where from is prereq of to.
    """
    graph: dict[int, list[int]] = {}
    for from_id, to_id in edges:
        if to_id not in graph:
            graph[to_id] = []
        graph[to_id].append(from_id)
        if from_id not in graph:
            graph[from_id] = []
    return graph


def compute_route(
    goal_kc_id: int,
    mastery_map: dict[int, float],
    prereq_graph: dict[int, list[int]],
) -> list[int]:
    """
    Compute an ordered list of KCs to study, from first unmet prerequisite to goal.

    Args:
        goal_kc_id: target KC the learner wants to reach
        mastery_map: {kc_id: p_mastery} for all KCs the learner has attempted
        prereq_graph: {kc_id: [prereq_kc_id, ...]} adjacency

    Returns:
        Ordered list of unmastered KC IDs (topological order, goal last).
        If goal is already mastered, returns [goal_kc_id].
    """
    # Step 1: Backward BFS from goal — collect all ancestor KCs (including goal)
    visited: set[int] = set()
    queue: deque[int] = deque([goal_kc_id])
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for prereq in prereq_graph.get(node, []):
            if prereq not in visited:
                queue.append(prereq)

    # Step 2: Filter to unmastered KCs; always include goal even if mastered
    def is_mastered(kc_id: int) -> bool:
        return mastery_map.get(kc_id, 0.0) >= TAU_MASTERY

    unmastered: set[int] = {kc for kc in visited if not is_mastered(kc) or kc == goal_kc_id}

    # If everything is mastered except the goal, ensure goal is included
    if goal_kc_id not in unmastered:
        unmastered.add(goal_kc_id)

    # Step 3: Topological sort (Kahn's algorithm) on the unmastered subgraph
    # Build in-degree and forward edges within the subgraph
    in_degree: dict[int, int] = {kc: 0 for kc in unmastered}
    forward: dict[int, list[int]] = {kc: [] for kc in unmastered}

    for kc in unmastered:
        for prereq in prereq_graph.get(kc, []):
            if prereq in unmastered:
                in_degree[kc] += 1
                forward[prereq].append(kc)

    # Kahn's BFS
    ready: deque[int] = deque([kc for kc in unmastered if in_degree[kc] == 0])
    ordered: list[int] = []
    while ready:
        node = ready.popleft()
        ordered.append(node)
        for successor in forward[node]:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                ready.append(successor)

    # If topological sort is incomplete (cycle detected), fall back to visited order
    if len(ordered) < len(unmastered):
        ordered = list(unmastered)

    return ordered


def find_reroute_target(
    current_kc_id: int,
    ordered_kc_ids: list[int],
    mastery_map: dict[int, float],
) -> int:
    """
    Walk backward from current KC in the ordered route.
    Return the closest unmastered KC (first ancestor that is not yet mastered).
    Falls back to the first KC on the route.
    """
    try:
        idx = ordered_kc_ids.index(current_kc_id)
    except ValueError:
        return ordered_kc_ids[0] if ordered_kc_ids else current_kc_id

    for i in range(idx - 1, -1, -1):
        kc = ordered_kc_ids[i]
        if mastery_map.get(kc, 0.0) < TAU_MASTERY:
            return kc

    return ordered_kc_ids[0]
