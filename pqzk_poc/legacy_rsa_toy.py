# legacy_rsa_toy.py
from Crypto.Util.number import inverse
import math

# choose tiny primes (for demo only)
p = 3
q = 5
N = p * q
phi = (p-1)*(q-1)
e = 3  # choose e coprime to phi(=8) -> 3 ok
d = inverse(e, phi)

def rsa_sign(m):
    # message m as small integer
    return pow(m, d, N)

def rsa_verify(m, s):
    return pow(s, e, N) == (m % N)

if __name__ == "__main__":
    m = 7
    s = rsa_sign(m)
    print("N =", N, "e=", e, "d=", d)
    print("message", m, "signature", s, "verify?", rsa_verify(m,s))
