"""Unit tests for the migration apply pipeline — pure helpers only.

Database-backed integration tests (savepoint rollback, idempotency,
end-to-end import round-trip) require the project conftest and a live
test Postgres; they live in the api/ test suite.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.migration.apply import _remap_attributes, _topo_sort


@dataclass
class _FakeStaged:
    source_id: str
    parent_source_id: str | None = None


def test_topo_sort_orders_parents_before_children() -> None:
    a = _FakeStaged("a")  # root
    b = _FakeStaged("b", parent_source_id="a")
    c = _FakeStaged("c", parent_source_id="b")
    out = _topo_sort([c, b, a])  # type: ignore[list-item]
    order = [r.source_id for r in out]
    assert order.index("a") < order.index("b") < order.index("c")


def test_topo_sort_unknown_parent_schedules_immediately() -> None:
    # Parent is not in the staged set — should not block the child.
    orphan = _FakeStaged("only", parent_source_id="external-parent")
    out = _topo_sort([orphan])  # type: ignore[list-item]
    assert [r.source_id for r in out] == ["only"]


def test_topo_sort_cycle_keeps_all_rows() -> None:
    # a ↔ b cycle; both depend on each other. The function must not
    # drop rows on cycle — it appends them in arrival order and logs.
    a = _FakeStaged("a", parent_source_id="b")
    b = _FakeStaged("b", parent_source_id="a")
    out = _topo_sort([a, b])  # type: ignore[list-item]
    assert {r.source_id for r in out} == {"a", "b"}


def test_topo_sort_preserves_arrival_order_among_siblings() -> None:
    a = _FakeStaged("a")
    b = _FakeStaged("b")  # also a root
    c = _FakeStaged("c", parent_source_id="a")
    d = _FakeStaged("d", parent_source_id="b")
    out = _topo_sort([a, b, c, d])  # type: ignore[list-item]
    order = [r.source_id for r in out]
    # All roots scheduled first; among siblings the input order is kept.
    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("d")
    assert order.index("a") < order.index("b")


def test_remap_attributes_passes_unmapped_keys_through() -> None:
    out = _remap_attributes(
        {"criticality": "high", "vendorName": "Acme"},
        {"criticality": "businessCriticality"},
    )
    assert out == {"businessCriticality": "high", "vendorName": "Acme"}


def test_remap_attributes_drops_skip_targets() -> None:
    out = _remap_attributes(
        {"criticality": "high", "noise": "ignore me"},
        {"noise": "__skip__"},
    )
    assert out == {"criticality": "high"}


def test_remap_attributes_empty_mapping_is_identity() -> None:
    src = {"a": 1, "b": "x"}
    assert _remap_attributes(src, {}) == src


def test_remap_attributes_collision_last_write_wins() -> None:
    # Two source keys mapped onto the same TEA key — Python dict
    # iteration order makes the *later* one win, which matches the
    # docstring contract. We don't promise which one, but we promise
    # the dict ends up with exactly one entry under the target key.
    out = _remap_attributes(
        {"a": 1, "b": 2},
        {"a": "merged", "b": "merged"},
    )
    assert list(out.keys()) == ["merged"]
