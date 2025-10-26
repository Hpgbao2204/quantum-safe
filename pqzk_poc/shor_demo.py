# shor_demo.py - Educational Shor's Algorithm Implementation
import math
import random
import time
from fractions import Fraction

def gcd(a, b):
    """Calculate the greatest common divisor."""
    while b:
        a, b = b, a % b
    return a

def mod_exp(base, exp, mod):
    """Compute (base^exp) mod mod efficiently."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result

def find_period_classical(a, N):
    """Find the period of a^x mod N classically."""
    for r in range(1, N):
        if mod_exp(a, r, N) == 1:
            return r
    return None

def continued_fraction_convergents(x, max_denominator=1000):
    """Get convergents of continued fraction expansion."""
    convergents = []
    a = int(x)
    convergents.append(Fraction(a))
    
    if x == a:
        return convergents
    
    x = x - a
    prev_h, prev_k = a, 1
    h, k = a * int(1/x) + 1, int(1/x)
    
    convergents.append(Fraction(h, k))
    
    while k < max_denominator:
        x = 1/x - int(1/x)
        if abs(x) < 1e-15:
            break
        
        a = int(1/x)
        new_h = a * h + prev_h
        new_k = a * k + prev_k
        
        if new_k > max_denominator:
            break
            
        convergents.append(Fraction(new_h, new_k))
        prev_h, prev_k = h, k
        h, k = new_h, new_k
    
    return convergents

def shor_educational(N, verbose=True):
    """Educational implementation of Shor's algorithm."""
    if verbose:
        print(f"Running Shor's algorithm to factor N = {N}")
    
    # Step 1: Check if N is even
    if N % 2 == 0:
        if verbose:
            print("N is even, trivial factorization")
        return [2, N // 2]
    
    # Step 2: Check if N is a perfect power
    for k in range(2, int(math.log2(N)) + 1):
        root = round(N ** (1/k))
        if root ** k == N:
            if verbose:
                print(f"N is a perfect power: {root}^{k}")
            return [root, N // root]
    
    # Step 3: Main Shor's algorithm loop
    max_attempts = 10
    for attempt in range(max_attempts):
        if verbose:
            print(f"\nAttempt {attempt + 1}:")
        
        # Choose random a
        a = random.randint(2, N - 1)
        g = gcd(a, N)
        
        if g > 1:
            if verbose:
                print(f"Lucky! gcd({a}, {N}) = {g}")
            return [g, N // g]
        
        if verbose:
            print(f"Chosen a = {a}")
        
        # Find period (classically for demo)
        period = find_period_classical(a, N)
        
        if period is None:
            if verbose:
                print("Could not find period")
            continue
            
        if verbose:
            print(f"Period r = {period}")
        
        # Check if period is even
        if period % 2 == 1:
            if verbose:
                print("Period is odd, trying again")
            continue
        
        # Compute a^(r/2) mod N
        half_period_power = mod_exp(a, period // 2, N)
        
        if half_period_power == N - 1:
            if verbose:
                print("a^(r/2) ≡ -1 (mod N), trying again")
            continue
        
        # Extract factors
        factor1 = gcd(half_period_power - 1, N)
        factor2 = gcd(half_period_power + 1, N)
        
        if 1 < factor1 < N:
            if verbose:
                print(f"Success! Found factors: {factor1} × {N // factor1}")
            return [factor1, N // factor1]
        
        if 1 < factor2 < N:
            if verbose:
                print(f"Success! Found factors: {factor2} × {N // factor2}")
            return [factor2, N // factor2]
    
    if verbose:
        print(f"Failed to factor {N} after {max_attempts} attempts")
    return []

def factor_N(N):
    """Main factoring function compatible with original interface."""
    factors = shor_educational(N, verbose=True)
    
    # Create a simple result object
    class ShorResult:
        def __init__(self, factors):
            self.factors = factors
    
    return ShorResult(factors)

def demo_quantum_advantage():
    """Demonstrate the theoretical quantum advantage."""
    print("\n" + "="*60)
    print("Quantum vs Classical Complexity Comparison")
    print("="*60)
    
    bit_sizes = [8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    
    print("Bit Size\tClassical (trial div)\tQuantum (Shor's)\tSpeedup")
    print("-" * 65)
    
    for bits in bit_sizes:
        # Use logarithmic scale to avoid overflow
        log_classical = 0.5 * bits * math.log10(2)  # log10(sqrt(2^bits))
        quantum_ops = bits ** 3   # Shor's complexity O(log^3 N)
        log_quantum = math.log10(quantum_ops)
        log_speedup = log_classical - log_quantum
        
        if log_classical < 100:  # Only show actual numbers for reasonable sizes
            classical_ops = 10 ** log_classical
            speedup = 10 ** log_speedup
            print(f"{bits:8d}\t{classical_ops:.2e}\t\t{quantum_ops:.2e}\t\t{speedup:.2e}")
        else:
            print(f"{bits:8d}\t10^{log_classical:.1f}\t\t\t{quantum_ops:.2e}\t\t10^{log_speedup:.1f}")
    
    print("\nKey Insights:")
    print("• Classical trial division: O(√N) operations")
    print("• Shor's quantum algorithm: O(log³N) operations")  
    print("• For RSA-2048: Classical ~10^308 vs Quantum ~10^10 operations")
    print("• This represents a speedup of ~10^298 - truly astronomical!")
    print("\nThis is why RSA will be broken by large-scale quantum computers!")

if __name__ == "__main__":
    print("=== Shor's Algorithm Demo ===")
    print("Educational implementation showing the key concepts")
    print()
    
    # Test numbers
    test_numbers = [15, 21, 35, 77, 91]
    
    for N in test_numbers:
        print(f"\n{'='*50}")
        print(f"Factoring N = {N}")
        print('='*50)
        
        start_time = time.time()
        result = factor_N(N)
        elapsed = time.time() - start_time
        
        if result.factors:
            print(f"\n✅ SUCCESS!")
            print(f"Factors: {result.factors}")
            print(f"Verification: {result.factors[0]} × {result.factors[1]} = {result.factors[0] * result.factors[1]}")
        else:
            print(f"\n❌ Could not factor {N}")
        
        print(f"Time: {elapsed:.4f} seconds")
    
    # Show theoretical quantum advantage
    demo_quantum_advantage()
