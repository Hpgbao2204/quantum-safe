#!/usr/bin/env python3
"""
Interactive Shor's Algorithm Educational Demo
============================================

This is an enhanced educational implementation of Shor's algorithm that includes:
- Step-by-step explanation of the algorithm
- Interactive prompts for better learning
- Quantum circuit visualization
- Multiple factoring examples
- Performance comparisons

Author: Educational Demo
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.primitives import Sampler
from qiskit.visualization import plot_histogram
import numpy as np
import math
import random
import time
import matplotlib.pyplot as plt

def gcd(a, b):
    """Calculate the greatest common divisor using Euclidean algorithm."""
    original_a, original_b = a, b
    steps = []
    while b:
        quotient = a // b
        remainder = a % b
        steps.append(f"{a} = {b} × {quotient} + {remainder}")
        a, b = b, remainder
    
    print(f"GCD calculation steps:")
    for step in steps:
        print(f"  {step}")
    print(f"  GCD({original_a}, {original_b}) = {a}")
    return a

def mod_exp(base, exp, mod):
    """Compute (base^exp) mod mod using fast modular exponentiation."""
    result = 1
    base = base % mod
    print(f"Computing {base}^{exp} mod {mod}:")
    
    binary_exp = bin(exp)[2:]  # Remove '0b' prefix
    print(f"  {exp} in binary: {binary_exp}")
    
    for i, bit in enumerate(reversed(binary_exp)):
        if bit == '1':
            result = (result * base) % mod
            print(f"  Step {i}: result = {result}")
        base = (base * base) % mod
    
    return result

def find_period_classical(a, N, verbose=True):
    """Classical method to find the period of a^x mod N with detailed output."""
    if verbose:
        print(f"\nFinding period of {a}^x mod {N}:")
        print("x\t{}^x mod {}\tPattern".format(a, N))
        print("-" * 30)
    
    sequence = []
    for r in range(1, N):
        value = mod_exp(a, r, N) if not verbose else pow(a, r, N)
        sequence.append(value)
        
        if verbose:
            print(f"{r}\t{value}\t\t{sequence}")
        
        if value == 1:
            if verbose:
                print(f"\nPeriod found: r = {r}")
                print(f"Verification: {a}^{r} mod {N} = {value}")
            return r
    
    return None

def create_quantum_period_finding_circuit(n_qubits, a, N):
    """Create a quantum circuit for period finding (educational version)."""
    # This is a simplified educational circuit
    # Real Shor's algorithm requires more complex modular exponentiation
    
    qr_control = QuantumRegister(n_qubits, 'control')
    qr_work = QuantumRegister(n_qubits, 'work') 
    cr = ClassicalRegister(n_qubits, 'result')
    
    circuit = QuantumCircuit(qr_control, qr_work, cr)
    
    # Step 1: Initialize control register in superposition
    for i in range(n_qubits):
        circuit.h(qr_control[i])
    
    # Step 2: Initialize work register to |1⟩
    circuit.x(qr_work[0])
    
    # Step 3: Controlled modular exponentiation (simplified)
    # In a real implementation, this would be much more complex
    for i in range(n_qubits):
        # Simplified controlled operations
        circuit.cx(qr_control[i], qr_work[i % len(qr_work)])
        circuit.p(np.pi / (2 ** i), qr_control[i])
    
    # Step 4: Inverse Quantum Fourier Transform on control register
    def qft_dagger(circuit, qubits):
        n = len(qubits)
        # Reverse the order first
        for i in range(n // 2):
            circuit.swap(qubits[i], qubits[n - 1 - i])
        
        for i in range(n):
            # Controlled rotations
            for j in range(i):
                circuit.cp(-np.pi / (2 ** (i - j)), qubits[j], qubits[i])
            # Hadamard gate
            circuit.h(qubits[i])
    
    qft_dagger(circuit, qr_control)
    
    # Step 5: Measure control register
    circuit.measure(qr_control, cr)
    
    return circuit

def interactive_shor_demo():
    """Interactive demonstration of Shor's algorithm."""
    print("🎯 Interactive Shor's Algorithm Demo")
    print("=" * 50)
    
    # Get user input
    try:
        N = int(input("Enter a composite number to factor (e.g., 15, 21, 35): "))
        if N < 4:
            print("Please enter a number ≥ 4")
            return
    except ValueError:
        print("Invalid input. Using default N = 15")
        N = 15
    
    print(f"\n📊 Analyzing N = {N}")
    print("-" * 30)
    
    # Check basic cases
    print("Step 1: Checking basic cases...")
    
    if N % 2 == 0:
        print(f"✅ N is even! Trivial factor: 2")
        print(f"Factors: 2 × {N//2} = {N}")
        return
    
    # Check for perfect powers
    print("Step 2: Checking if N is a perfect power...")
    is_power = False
    for k in range(2, int(math.log2(N)) + 1):
        root = round(N ** (1/k))
        if root ** k == N:
            print(f"✅ N = {root}^{k}")
            print(f"Factors: {root} (repeated {k} times)")
            is_power = True
            break
    
    if not is_power:
        print("✅ N is not a perfect power")
    
    # Main Shor's algorithm
    print(f"\nStep 3: Running Shor's algorithm on N = {N}")
    print("-" * 40)
    
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔄 Attempt {attempt}/{max_attempts}")
        
        # Choose random a
        while True:
            a = random.randint(2, N - 1)
            g = gcd(a, N)
            if g == 1:
                break
            else:
                print(f"Lucky! gcd({a}, {N}) = {g} is a non-trivial factor!")
                print(f"Factors: {g} × {N//g} = {N}")
                return
        
        print(f"\n📍 Chosen a = {a}")
        input("Press Enter to continue with period finding...")
        
        # Find period
        print(f"\n🔍 Finding period of {a}^x mod {N}")
        period = find_period_classical(a, N, verbose=True)
        
        if period is None:
            print("❌ Could not find period")
            continue
        
        print(f"\n✅ Period r = {period}")
        
        # Check if period is suitable
        if period % 2 == 1:
            print("❌ Period is odd, need to try different 'a'")
            continue
        
        # Calculate a^(r/2) mod N
        half_period_power = pow(a, period // 2, N)
        print(f"\n🧮 Computing {a}^({period}/2) mod {N} = {half_period_power}")
        
        if half_period_power == N - 1:
            print(f"❌ {a}^(r/2) ≡ -1 (mod {N}), need to try different 'a'")
            continue
        
        # Extract factors
        print(f"\n🎯 Extracting factors using GCD:")
        factor1 = gcd(half_period_power - 1, N)
        factor2 = gcd(half_period_power + 1, N)
        
        print(f"gcd({half_period_power} - 1, {N}) = gcd({half_period_power - 1}, {N}) = {factor1}")
        print(f"gcd({half_period_power} + 1, {N}) = gcd({half_period_power + 1}, {N}) = {factor2}")
        
        if factor1 > 1 and factor1 < N:
            other_factor = N // factor1
            print(f"\n🎉 SUCCESS! Found factors:")
            print(f"   {factor1} × {other_factor} = {N}")
            
            # Show quantum circuit that would be used
            show_quantum_circuit = input("\nWould you like to see the quantum circuit? (y/n): ").lower().startswith('y')
            if show_quantum_circuit:
                display_quantum_circuit(N, a)
            
            return
        
        elif factor2 > 1 and factor2 < N:
            other_factor = N // factor2
            print(f"\n🎉 SUCCESS! Found factors:")
            print(f"   {factor2} × {other_factor} = {N}")
            return
        
        print("❌ No non-trivial factors found, trying again...")
    
    print(f"\n❌ Could not factor {N} after {max_attempts} attempts")

def display_quantum_circuit(N, a):
    """Display the quantum circuit used in Shor's algorithm."""
    print(f"\n🔮 Quantum Circuit for Factoring {N} (using a = {a})")
    print("=" * 60)
    
    n_qubits = max(4, math.ceil(math.log2(N)))
    circuit = create_quantum_period_finding_circuit(n_qubits, a, N)
    
    print(circuit.draw(output='text'))
    
    print(f"\nCircuit Details:")
    print(f"• Control qubits: {n_qubits} (for superposition and QFT)")
    print(f"• Work qubits: {n_qubits} (for modular exponentiation)")
    print(f"• Classical bits: {n_qubits} (for measurement results)")
    print(f"• Total operations: {len(circuit.data)}")
    
    # Simulate the circuit (for educational purposes)
    simulate = input("\nSimulate this quantum circuit? (y/n): ").lower().startswith('y')
    if simulate:
        print("🚀 Running quantum simulation...")
        
        simulator = AerSimulator()
        sampler = Sampler(simulator)
        
        try:
            job = sampler.run(circuit, shots=1024)
            result = job.result()
            counts = result.quasi_dists[0].binary_probabilities()
            
            print(f"Measurement results (top 5):")
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for bitstring, probability in sorted_counts:
                decimal_value = int(bitstring, 2)
                print(f"  |{bitstring}⟩ → {decimal_value:2d} (probability: {probability:.3f})")
                
        except Exception as e:
            print(f"Simulation error: {e}")

def comparison_demo():
    """Compare classical vs quantum approaches for different numbers."""
    print("\n📈 Classical vs Quantum Comparison")
    print("=" * 50)
    
    test_numbers = [15, 21, 35, 77, 91, 143]
    
    print("Number\tClassical Time\tQuantum Advantage")
    print("-" * 45)
    
    for N in test_numbers:
        # Time classical factoring
        start = time.time()
        
        # Simple trial division for comparison
        factors = []
        for i in range(2, int(N**0.5) + 1):
            if N % i == 0:
                factors = [i, N // i]
                break
        
        classical_time = time.time() - start
        
        # Estimate quantum advantage (theoretical)
        classical_complexity = N**0.5  # Trial division complexity
        quantum_complexity = (math.log(N))**3  # Shor's complexity
        advantage = classical_complexity / quantum_complexity
        
        print(f"{N}\t{classical_time:.6f}s\t\t{advantage:.1f}x speedup")
    
    print(f"\nNote: Quantum advantage grows exponentially with number size!")
    print(f"For RSA-2048 (617 digits), quantum speedup would be astronomical!")

if __name__ == "__main__":
    while True:
        print("\n" + "="*60)
        print("🎓 Shor's Algorithm Educational Suite")
        print("="*60)
        print("1. Interactive Factoring Demo")
        print("2. Classical vs Quantum Comparison")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            interactive_shor_demo()
        elif choice == '2':
            comparison_demo()
        elif choice == '3':
            print("👋 Thanks for learning about Shor's algorithm!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")
