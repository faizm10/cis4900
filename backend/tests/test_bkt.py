import pytest
from app.services.bkt import bkt_update, decide, TAU_MASTERY, TAU_LOW, K_REROUTE


# Standard parameters from literature
P_T = 0.1
P_G = 0.25
P_S = 0.1


class TestBktUpdate:
    def test_correct_increases_mastery(self):
        p_before = 0.3
        p_after = bkt_update(p_before, True, P_T, P_G, P_S)
        assert p_after > p_before

    def test_incorrect_decreases_or_holds_mastery(self):
        p_before = 0.5
        p_after = bkt_update(p_before, False, P_T, P_G, P_S)
        assert p_after <= p_before

    def test_correct_stays_in_range(self):
        p = bkt_update(0.1, True, P_T, P_G, P_S)
        assert 0.0 <= p <= 1.0

    def test_incorrect_stays_in_range(self):
        p = bkt_update(0.9, False, P_T, P_G, P_S)
        assert 0.0 <= p <= 1.0

    def test_high_prior_correct_approaches_mastery(self):
        p = 0.85
        for _ in range(5):
            p = bkt_update(p, True, P_T, P_G, P_S)
        assert p >= TAU_MASTERY

    def test_zero_prior_correct(self):
        p = bkt_update(0.0, True, P_T, P_G, P_S)
        assert p > 0.0

    def test_one_prior_incorrect(self):
        p = bkt_update(1.0, False, P_T, P_G, P_S)
        assert 0.0 <= p <= 1.0

    def test_multiple_correct_converges(self):
        p = 0.1
        for _ in range(20):
            p = bkt_update(p, True, 0.2, P_G, P_S)
        assert p >= 0.9

    def test_degenerate_parameters_no_crash(self):
        # p_g=0 and p_s=0 — denominator could be 0 for correct=True when p_l=1
        p = bkt_update(1.0, True, P_T, 0.0, 0.0)
        assert 0.0 <= p <= 1.0


class TestDecide:
    def test_advance_when_mastery_high(self):
        assert decide(TAU_MASTERY, 5) == "advance"
        assert decide(0.99, 1) == "advance"

    def test_reroute_when_low_mastery_and_enough_attempts(self):
        assert decide(TAU_LOW - 0.01, K_REROUTE) == "reroute"
        assert decide(0.1, 10) == "reroute"

    def test_remediate_when_low_mastery_but_few_attempts(self):
        assert decide(0.1, K_REROUTE - 1) == "remediate"

    def test_remediate_when_moderate_mastery(self):
        assert decide(0.6, 5) == "remediate"

    def test_boundary_mastery_threshold(self):
        assert decide(TAU_MASTERY, 1) == "advance"
        assert decide(TAU_MASTERY - 0.001, 5) == "remediate"

    def test_boundary_low_threshold(self):
        assert decide(TAU_LOW, K_REROUTE) == "remediate"  # TAU_LOW itself is not < TAU_LOW
        assert decide(TAU_LOW - 0.001, K_REROUTE) == "reroute"
