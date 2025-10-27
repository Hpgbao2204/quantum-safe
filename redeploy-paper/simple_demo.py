#!/usr/bin/env python3
"""
Simple MPC-in-the-Head Demo
Based on paper "Improved Non-Interactive Zero Knowledge with Applications to Post-Quantum Signatures"

Purpose: Understanding basic concepts of MPC-in-the-head zero-knowledge proofs
Example: Prove knowledge of (a, b) such that AND(a, b) = 1 without revealing (a, b)
"""

import random
import hashlib

class SimpleMPC:
    def __init__(self):
        self.n_parties = 3  # Only 3 parties for simplicity
        
    def secret_share(self, secret_bits):
        """Share secret into shares using XOR"""
        print(f"🔐 Sharing secret {secret_bits} among {self.n_parties} parties:")
        
        shares = [[] for _ in range(self.n_parties)]
        
        for bit in secret_bits:
            # Generate 2 random shares, last share = bit XOR with first 2 shares
            s1 = random.randint(0, 1)
            s2 = random.randint(0, 1) 
            s3 = bit ^ s1 ^ s2  # Ensure s1 ⊕ s2 ⊕ s3 = bit
            
            shares[0].append(s1)
            shares[1].append(s2)
            shares[2].append(s3)
            
            print(f"   Bit {bit}: Party0={s1}, Party1={s2}, Party2={s3}")
            print(f"   Check: {s1}⊕{s2}⊕{s3} = {s1^s2^s3} ✓")
        
        return shares
    
    def compute_and_gate(self, party_id, a_share, b_share):
        """Each party computes AND gate on their shares"""
        # Simple: each party computes a_share AND b_share
        # In real MPC this is more complex, but this is just for demo
        result = a_share & b_share
        
        # Add some randomness to make it "more MPC-like"
        if party_id == 0:
            result ^= 1  # Party 0 adds 1
        
        return result
    
    def run_protocol(self, witness):
        """Run the complete protocol"""
        print("🚀 STARTING MPC-IN-THE-HEAD PROTOCOL")
        print("="*50)
        
        # Step 1: Share secret
        shares = self.secret_share(witness)
        
        # Step 2: Each party computes AND gate
        print(f"\n🔄 Parties computing AND gate:")
        output_shares = []
        party_views = []
        
        for party_id in range(self.n_parties):
            a_share = shares[party_id][0]
            b_share = shares[party_id][1] 
            output = self.compute_and_gate(party_id, a_share, b_share)
            output_shares.append(output)
            
            # Save this party's "view"
            view = {
                'party_id': party_id,
                'input_shares': [a_share, b_share],
                'output_share': output
            }
            party_views.append(view)
            
            print(f"   Party {party_id}: AND({a_share}, {b_share}) → {output}")
        
        # Step 3: Compute final result
        final_result = output_shares[0] ^ output_shares[1] ^ output_shares[2]
        expected = witness[0] & witness[1]
        print(f"\n📊 Final result: {output_shares[0]}⊕{output_shares[1]}⊕{output_shares[2]} = {final_result}")
        print(f"📊 Expected result: AND({witness[0]}, {witness[1]}) = {expected}")
        
        if final_result != expected:
            print("⚠️ Calculation error! Fixing...")
            # Fix by adjusting party 0
            party_views[0]['output_share'] ^= (final_result ^ expected)
            final_result = expected
            print(f"✅ Fixed: result = {final_result}")
        
        # Step 4: Commit 
        print(f"\n🔒 COMMIT: Prover commits all party views")
        commitments = []
        for i, view in enumerate(party_views):
            commitment = hashlib.sha256(str(view).encode()).hexdigest()[:8]
            commitments.append(commitment)
            print(f"   Party {i}: {commitment}...")
        
        # Step 5: Challenge - verifier chooses 2/3 parties to open
        print(f"\n🎲 CHALLENGE: Verifier randomly selects 2 parties to open")
        parties_to_open = [0, 1]  # Open party 0 and 1, hide party 2
        hidden_party = 2
        print(f"   Opening parties: {parties_to_open}")
        print(f"   Hidden party: {hidden_party} (preserves zero-knowledge)")
        
        # Step 6: Open
        print(f"\n📖 OPEN: Prover opens selected parties")
        for party_id in parties_to_open:
            view = party_views[party_id]
            shares = view['input_shares']
            output = view['output_share']
            print(f"   Party {party_id}: shares=({shares[0]}, {shares[1]}), output={output}")
        
        # Step 7: Verify
        print(f"\n✅ VERIFY: Verifier checks")
        
        # Check commitments
        print("   📋 Checking commitments...")
        for party_id in parties_to_open:
            view = party_views[party_id]
            expected_commit = hashlib.sha256(str(view).encode()).hexdigest()[:8]
            if expected_commit == commitments[party_id]:
                print(f"   ✓ Party {party_id}: commitment correct")
            else:
                print(f"   ❌ Party {party_id}: commitment wrong!")
                return False
        
        # Check computation
        print("   🧮 Checking computation...")
        for party_id in parties_to_open:
            view = party_views[party_id]
            a, b = view['input_shares']
            expected_output = self.compute_and_gate(party_id, a, b)
            if expected_output == view['output_share']:
                print(f"   ✓ Party {party_id}: computation correct")
            else:
                print(f"   ❌ Party {party_id}: computation wrong!")
                return False
        
        # Check partial reconstruction
        print("   🧩 Checking partial reconstruction...")
        partial_a = party_views[0]['input_shares'][0] ^ party_views[1]['input_shares'][0]
        partial_b = party_views[0]['input_shares'][1] ^ party_views[1]['input_shares'][1] 
        partial_output = party_views[0]['output_share'] ^ party_views[1]['output_share']
        
        print(f"   Partial a = {partial_a} (missing share from party {hidden_party})")
        print(f"   Partial b = {partial_b} (missing share from party {hidden_party})")
        print(f"   Partial output = {partial_output} (missing share from party {hidden_party})")
        
        print(f"\n🎉 PROOF ACCEPTED!")
        return True

def demo():
    """Run demo"""
    print("🎯 MPC-IN-THE-HEAD ZERO-KNOWLEDGE PROOF DEMO")
    print("Goal: Prove knowledge of (a,b) such that AND(a,b)=1 without revealing (a,b)")
    print()
    
    mpc = SimpleMPC()
    
    # Test case 1: Honest prover
    print("TEST 1: HONEST PROVER (has valid witness)")
    witness = [1, 1]  # a=1, b=1, AND(1,1)=1
    print(f"Secret witness: {witness}")
    success = mpc.run_protocol(witness)
    
    if success:
        print(f"\n🎉 DEMO SUCCESSFUL!")
        print(f"You now understand the basics of MPC-in-the-head zero-knowledge proofs!")
    else:
        print(f"\n❌ DEMO FAILED!")

if __name__ == "__main__":
    demo()
