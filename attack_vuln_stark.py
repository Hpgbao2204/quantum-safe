# attack_vuln_stark.py
# Brute-force attack against vuln_stark.py (truncated hash) to forge a trace leaf
# Runs classical brute-force to find an alternative value for one leaf that keeps the same Merkle root.

import hashlib, random, itertools
from vuln_stark import gen_fib_trace, hash_trunc16, commit_trace

def build_merkle_from_leaves(leaves, hash_func=hash_trunc16):
    L = list(leaves)
    while len(L) > 1:
        if len(L) % 2 != 0:
            L.append(L[-1])
        L = [hash_func(L[i]+L[i+1]) for i in range(0, len(L), 2)]
    return L[0]

def recompute_root_with_new_leaf(trace, leaf_index, new_value):
    # recompute leaves 111 from trace but replace leaf_index raw value with new_value (string/number)
    leaves = [hash_trunc16(v) for v in trace]
    leaves[leaf_index] = hash_trunc16(new_value)
    return build_merkle_from_leaves(leaves), leaves

if __name__ == "__main__":
    N = 10
    trace = gen_fib_trace(N)
    orig_root, _ = commit_trace(trace)
    print("Original vulnerable root:", orig_root)

    # choose index to attack
    idx = 3
    print("Attacking leaf index", idx, "original value", trace[idx])

    # brute force small integers to find collision
    max_try = 200000
    found = None
    for cand in range(0, max_try):
        new_root, _ = recompute_root_with_new_leaf(trace, idx, cand)
        if new_root == orig_root:
            found = cand
            print("Found collision! candidate:", cand)
            break

    if not found:
        print("No collision found in range 0..", max_try)
