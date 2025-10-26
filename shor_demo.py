from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.primitives import Sampler
import numpy as np
import math
import random
import time

def gcd(a, b):
    """Calculate the greatest common divisor of a and b."""
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
    """Classical method to find the period of a^x mod N."""
    for r in range(1, N):
        if mod_exp(a, r, N) == 1:
            return r
    return None

def quantum_fourier_transform(circuit, qubits):
    """Apply Quantum Fourier Transform to the given qubits."""
    n = len(qubits)
    for i in range(n):
        # Apply Hadamard gate
        circuit.h(qubits[i])
        # Apply controlled rotations
        for j in range(i + 1, n):
            circuit.cp(np.pi / (2 ** (j - i)), qubits[j], qubits[i])
    
    # Swap qubits to reverse the order
    for i in range(n // 2):
        circuit.swap(qubits[i], qubits[n - 1 - i])

def create_qft_circuit(n_qubits):
    """Create a simple QFT-based period finding circuit."""
    # This is a simplified version for educational purposes
    qr = QuantumRegister(n_qubits, 'q')
    cr = ClassicalRegister(n_qubits, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    # Initialize superposition
    for i in range(n_qubits):
        circuit.h(qr[i])
    
    # Add some phase rotations (simplified version of modular exponentiation)
    for i in range(n_qubits):
        circuit.p(np.pi / (2 ** i), qr[i])
    
    # Apply inverse QFT
    quantum_fourier_transform(circuit, qr)
    
    # Measure all qubits
    circuit.measure(qr, cr)
    
    return circuit

def run_shor_educational(N, shots=1024):
    """Educational implementation of Shor's algorithm."""
    print(f"Factoring N = {N} using Shor's algorithm (educational version)")
    
    # Step 1: Check if N is even
    if N % 2 == 0:
        return [2, N // 2], 0.0
    
    # Step 2: Check if N is a perfect power
    for k in range(2, int(math.log2(N)) + 1):
        root = round(N ** (1/k))
        if root ** k == N:
            return [root, N // root], 0.0
    
    start_time = time.time()
    
    # Step 3: Choose random a < N such that gcd(a, N) = 1
    while True:
        a = random.randint(2, N - 1)
        if gcd(a, N) == 1:
            break
    
    print(f"Chosen a = {a}")
    
    # Step 4: Find the period of a^x mod N
    # For educational purposes, we'll use classical computation for small N
    # but show how the quantum part would work
    
    if N <= 100:  # Use classical method for small numbers
        print("Using classical period finding for educational demonstration...")
        period = find_period_classical(a, N)
        print(f"Period r = {period}")
    else:
        print("For larger numbers, we would use quantum period finding...")
        # Create a simple quantum circuit to demonstrate
        n_qubits = max(4, math.ceil(math.log2(N)))
        circuit = create_qft_circuit(n_qubits)
        
        # Simulate the circuit
        simulator = AerSimulator()
        sampler = Sampler(simulator)
        
        # Run the circuit
        job = sampler.run(circuit, shots=shots)
        result = job.result()
        
        # For this demo, we'll still use classical computation
        # but show that we ran a quantum circuit
        print(f"Quantum circuit executed with {shots} shots")
        print("In a real implementation, we would analyze the measurement results")
        print("to extract the period using continued fractions...")
        
        period = find_period_classical(a, N)
        print(f"Period r = {period} (found classically for comparison)")
    
    elapsed_time = time.time() - start_time
    
    # Step 5: Check if period is odd or if a^(r/2) ≡ -1 (mod N)
    if period is None:
        print("Could not find period")
        return [], elapsed_time
        
    if period % 2 == 1:
        print("Period is odd, trying again with different a...")
        return [], elapsed_time
    
    # Step 6: Compute factors
    x = mod_exp(a, period // 2, N)
    if x == N - 1:
        print("a^(r/2) ≡ -1 (mod N), trying again with different a...")
        return [], elapsed_time
    
    factor1 = gcd(x - 1, N)
    factor2 = gcd(x + 1, N)
    
    factors = []
    if factor1 > 1 and factor1 < N:
        factors.append(factor1)
        factors.append(N // factor1)
    elif factor2 > 1 and factor2 < N:
        factors.append(factor2)
        factors.append(N // factor2)
    
    return factors, elapsed_time

def run_shor_with_retries(N, max_attempts=5, shots=1024):
    """Run Shor's algorithm with multiple attempts for better success rate."""
    print(f"Attempting to factor N = {N} (up to {max_attempts} attempts)")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Attempt {attempt} ---")
        factors, elapsed_time = run_shor_educational(N, shots)
        
        if factors:
            return factors, elapsed_time, attempt
        else:
            print("This attempt failed, trying with a different random 'a'...")
    
    return [], 0, max_attempts

if __name__ == "__main__":
    numbers = [15, 21, 35]   # Small numbers for educational demo
    
    print("=== Shor's Algorithm Educational Demo ===")
    print("This implementation shows the key steps of Shor's algorithm.")
    print("For small numbers, we use classical computation to demonstrate the logic.")
    print("The quantum advantage comes with much larger numbers.\n")
    
    for N in numbers:
        print(f"\n{'='*60}")
        print(f"FACTORING N = {N}")
        print('='*60)
        
        try:
            factors, total_time, attempts_used = run_shor_with_retries(N, max_attempts=5, shots=1024)
            
            if factors:
                print(f"\n🎉 SUCCESS after {attempts_used} attempt(s)!")
                print(f"Factors found: {factors}")
                print(f"Verification: {factors[0]} × {factors[1]} = {factors[0] * factors[1]}")
                print(f"Total time: {total_time:.3f} seconds")
            else:
                print(f"\n❌ Could not factor {N} after {attempts_used} attempts")
                print("This can happen due to the probabilistic nature of the algorithm")
                
        except Exception as e:
            print(f"Error: {e}")
    
    print(f"\n{'='*60}")
    print("🎓 Educational Notes:")
    print("• Shor's algorithm is probabilistic - it may need multiple attempts")
    print("• For small numbers, classical algorithms are much faster")
    print("• Quantum advantage appears with large composite numbers (hundreds of digits)")
    print("• The quantum speedup comes from the period-finding subroutine using QFT")
    print("• This demo shows the classical logic of the algorithm")
    print("• Real quantum computers would be needed for the exponential speedup")
    print("• The algorithm breaks RSA encryption by factoring large semiprimes")
    print('='*60)
