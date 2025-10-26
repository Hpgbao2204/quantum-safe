# mini_stark_qsafe.py
import hashlib, random

def gen_fib_trace(n):
    trace = [1,1]
    for i in range(2, n):
        trace.append(trace[-1] + trace[-2])
    return trace

def hash512(x):
    return hashlib.sha3_512(str(x).encode()).hexdigest()

def merkle_root_from_leaves(leaves):
    L = list(leaves)
    while len(L) > 1:
        if len(L) % 2 != 0:
            L.append(L[-1])
        L = [hash512(L[i] + L[i+1]) for i in range(0, len(L), 2)]
    return L[0]

def commit_trace(trace):
    leaves = [hash512(v) for v in trace]
    root = merkle_root_from_leaves(leaves)
    return root, leaves

def random_challenges(n, k=3):
    return random.sample(range(n-2), k)

def prove_trace(trace, indices):
    proof = []
    for i in indices:
        lhs = trace[i] + trace[i+1]
        rhs = trace[i+2]
        proof.append((i, lhs, rhs))
    return proof

def verify_proof(proof):
    for (i,lhs,rhs) in proof:
        if lhs != rhs:
            return False
    return True

if __name__ == "__main__":
    N=12
    trace = gen_fib_trace(N)
    root, leaves = commit_trace(trace)
    print("STARK root:", root[:64], "...")
    idx = random_challenges(N, k=4)
    print("Challenges:", idx)
    proof = prove_trace(trace, idx)
    ok = verify_proof(proof)
    print("Proof OK?", ok)
