
import hashlib, random

def hash_trunc16(x):
    # use sha3_512 but truncate to 4 hex chars = 16 bits (unsafe)
    h = hashlib.sha3_512(str(x).encode()).hexdigest()
    return h[:4]   # 16 bits only -> collisions trivial

def gen_fib_trace(n):
    trace = [1,1]
    for i in range(2,n):
        trace.append(trace[-1] + trace[-2])
    return trace

def commit_trace(trace, hash_func=hash_trunc16):
    leaves = [hash_func(v) for v in trace]
    while len(leaves) > 1:
        if len(leaves) % 2 != 0:
            leaves.append(leaves[-1])
        leaves = [hash_func(leaves[i] + leaves[i+1]) for i in range(0,len(leaves),2)]
    return leaves[0], leaves  # also return final leaves for demo

if __name__ == "__main__":
    N = 10
    trace = gen_fib_trace(N)
    root, leaves = commit_trace(trace)
    print("VULN Root:", root)
    print("Leaves (truncated hashes):", leaves)
