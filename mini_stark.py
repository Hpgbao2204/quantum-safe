# mini_stark_qsafe.py
# Simple, educational mini-STARK: Fibonacci trace + Merkle-like commit using SHA3-512

import hashlib, random

def gen_fib_trace(n):
    trace = [1,1]
    for i in range(2,n):
        trace.append(trace[-1] + trace[-2])
    return trace

def hash512(x):
    return hashlib.sha3_512(str(x).encode()).hexdigest()

def commit_trace(trace, hash_func=hash512):
    leaves = [hash_func(v) for v in trace]
    while len(leaves) > 1:
        if len(leaves) % 2 != 0:
            leaves.append(leaves[-1])
        leaves = [hash_func(leaves[i] + leaves[i+1]) for i in range(0,len(leaves),2)]
    return leaves[0]

def random_challenges(n, k=3):
    return random.sample(range(n-2), k)

def prove(trace, indices):
    proof = []
    for i in indices:
        lhs = trace[i] + trace[i+1]
        rhs = trace[i+2]
        proof.append((i,lhs,rhs))
    return proof

def verify(proof):
    for (i,lhs,rhs) in proof:
        if lhs != rhs:
            return False
    return True

if __name__ == "__main__":
    N=10
    trace = gen_fib_trace(N)
    root = commit_trace(trace)
    print("Root:", root[:32], "...")
    idx = random_challenges(N)
    proof = prove(trace, idx)
    ok = verify(proof)
    print("Proof ok:", ok, " challenges:", idx)
