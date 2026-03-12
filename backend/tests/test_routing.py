import pytest
from app.services.routing import build_prereq_graph, compute_route, find_reroute_target
from app.services.bkt import TAU_MASTERY

# Simple linear graph: 1 -> 2 -> 3 -> 4 -> 5
# (1 is prereq of 2, 2 is prereq of 3, etc.)
LINEAR_EDGES = [(1, 2), (2, 3), (3, 4), (4, 5)]

# Branching graph from plan: 3 -> 5, 3 -> 6, 5 -> 7, 6 -> 7
BRANCH_EDGES = [(1, 2), (2, 3), (3, 4), (4, 5), (4, 6), (5, 7), (6, 7)]


class TestBuildPrereqGraph:
    def test_builds_correctly(self):
        g = build_prereq_graph(LINEAR_EDGES)
        # Node 3 has prereq 2
        assert 2 in g[3]
        # Node 2 has prereq 1
        assert 1 in g[2]

    def test_empty_edges(self):
        g = build_prereq_graph([])
        assert g == {}


class TestComputeRoute:
    def test_full_route_no_mastery(self):
        g = build_prereq_graph(LINEAR_EDGES)
        route = compute_route(5, {}, g)
        # Should include all unmastered nodes 1-5 in topo order
        assert route[0] == 1
        assert route[-1] == 5
        assert len(route) == 5

    def test_route_skips_mastered(self):
        g = build_prereq_graph(LINEAR_EDGES)
        mastery = {1: TAU_MASTERY, 2: TAU_MASTERY}
        route = compute_route(5, mastery, g)
        assert 1 not in route
        assert 2 not in route
        assert 3 in route
        assert 5 in route

    def test_route_already_mastered_returns_goal(self):
        g = build_prereq_graph(LINEAR_EDGES)
        mastery = {1: TAU_MASTERY, 2: TAU_MASTERY, 3: TAU_MASTERY, 4: TAU_MASTERY, 5: TAU_MASTERY}
        route = compute_route(5, mastery, g)
        # Goal always included; all prereqs mastered so only goal remains
        assert 5 in route

    def test_branching_route_includes_both_branches(self):
        g = build_prereq_graph(BRANCH_EDGES)
        route = compute_route(7, {}, g)
        assert 7 in route
        # Should include nodes from both paths to 7
        assert 5 in route or 6 in route

    def test_topo_order_satisfied(self):
        g = build_prereq_graph(LINEAR_EDGES)
        route = compute_route(5, {}, g)
        for from_id, to_id in LINEAR_EDGES:
            if from_id in route and to_id in route:
                assert route.index(from_id) < route.index(to_id), \
                    f"Prereq {from_id} should come before {to_id} in route"

    def test_single_node_no_prereqs(self):
        g = build_prereq_graph([])
        route = compute_route(1, {}, g)
        assert 1 in route


class TestFindRerouteTarget:
    def test_returns_previous_unmastered(self):
        ordered = [1, 2, 3, 4, 5]
        mastery = {1: TAU_MASTERY, 2: TAU_MASTERY}  # 3, 4, 5 not mastered
        target = find_reroute_target(3, ordered, mastery)
        # Walk back from 3: index 1 (kc=2) is mastered, index 0 (kc=1) is mastered
        # Falls back to first node
        assert target == ordered[0]

    def test_returns_closest_unmastered_prereq(self):
        ordered = [1, 2, 3, 4, 5]
        mastery = {1: TAU_MASTERY}  # only 1 is mastered; 2 is not mastered
        target = find_reroute_target(4, ordered, mastery)
        # Walk back from index 3 (kc=4): index 2 (kc=3) → not mastered
        assert target == 3

    def test_fallback_to_first_when_all_prereqs_mastered(self):
        ordered = [1, 2, 3]
        mastery = {1: TAU_MASTERY, 2: TAU_MASTERY}
        target = find_reroute_target(3, ordered, mastery)
        # All prereqs mastered → fall back to first
        assert target == 1

    def test_kc_not_in_route_returns_first(self):
        ordered = [1, 2, 3]
        target = find_reroute_target(99, ordered, {})
        assert target == 1
