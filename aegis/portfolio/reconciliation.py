from __future__ import annotations


def reconcile_positions(internal, broker):
    internal = dict(internal or {})
    broker = dict(broker or {})
    all_symbols = sorted(set(internal) | set(broker))
    deltas = []
    for symbol in all_symbols:
        lhs = int((internal.get(symbol) or {}).get("qty", 0))
        rhs = int((broker.get(symbol) or {}).get("qty", 0))
        if lhs != rhs:
            deltas.append({"symbol": symbol, "internal_qty": lhs, "broker_qty": rhs, "delta": rhs - lhs})
    return deltas