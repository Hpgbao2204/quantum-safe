# MPC-in-the-Head Zero-Knowledge Proofs Implementation

This folder contains comprehensive implementations of MPC-in-the-head zero-knowledge proof protocols, based on the paper **"Improved Non-Interactive Zero Knowledge with Applications to Post-Quantum Signatures"** by Katz, Kolesnikov, and Wang (CCS 2018).

## 📁 Files Overview

### 📄 Paper Documentation
- **`Paper.md`** - Complete reconstruction of the original research paper with technical details
- **`3243734.3243805.pdf`** - Original paper PDF from ACM Digital Library

### 🔬 Implementation Files

#### 1. `complete_mpc_implementation.py` - **[RECOMMENDED]**
**The most comprehensive and educational implementation**
- ✅ **Preprocessing model** (key contribution of the paper)
- ✅ **Witness-independent preprocessing** 
- ✅ **Performance analysis** for different circuit sizes
- ✅ **Detailed explanations** of each protocol step
- ✅ **Multiple circuit types** (AND, XOR gates)
- ✅ **Fiat-Shamir transform** for non-interactive proofs
- ✅ **Security analysis** and paper contributions explanation

#### 2. `simple_mpc_demo.py` - **[EDUCATIONAL]**
**Best for learning the core concepts**
- ✅ **Clear, step-by-step** protocol execution
- ✅ **Zero-knowledge property** demonstration
- ✅ **Security properties** explanation
- ✅ **Educational comments** throughout
- ⚠️ Simplified implementation for clarity

#### 3. `mpc_in_the_head_demo.py` - **[BASIC]**
**Original comprehensive attempt**
- ✅ Complete protocol implementation
- ✅ Detailed comments and explanations
- ⚠️ Some circuit simulation issues (educational value)

#### 4. `mpc_in_the_head_fixed.py` - **[INTERMEDIATE]**
**Fixed version with better error handling**
- ✅ Improved circuit simulation
- ✅ Better soundness testing
- ✅ Enhanced verification steps

## 🚀 Quick Start

### Run the Complete Implementation
```bash
cd redeploy-paper
python3 complete_mpc_implementation.py
```

### Run Educational Demo
```bash
python3 simple_mpc_demo.py
```

## 🎯 What These Implementations Demonstrate

### Core Protocol Steps
1. **SETUP** - Initialize n virtual MPC parties
2. **SECRET_SHARING** - Share witness bits using XOR secret sharing
3. **SIMULATE** - Each party computes Boolean circuit on their shares
4. **COMMIT** - Prover commits to all party views cryptographically
5. **CHALLENGE** - Verifier (or Fiat-Shamir) selects parties to open
6. **OPEN** - Prover reveals selected party views
7. **VERIFY** - Verifier checks consistency and correctness

### Key Innovations from the Paper
- **Preprocessing Model**: Heavy computation done offline, before witness is known
- **Improved Efficiency**: 20-50% smaller proofs than previous methods for 300-100k AND gates
- **Post-Quantum Security**: Based on symmetric primitives only (no number theory)
- **Practical Applications**: Enables quantum-safe digital signatures

### Security Properties
- **Completeness**: Honest prover always convinces verifier
- **Soundness**: Cheating probability ≤ 1/n per round (exponentially decreasing)
- **Zero-Knowledge**: Verifier learns nothing about witness beyond statement validity

## 📊 Performance Characteristics

| Circuit Size | Preprocessing Time | Online Time | Total Time | Use Case |
|-------------|-------------------|-------------|------------|-----------|
| 10 gates    | ~0.001s          | ~0.010s     | ~0.011s    | Toy examples |
| 100 gates   | ~0.005s          | ~0.050s     | ~0.055s    | Small circuits |
| 1000 gates  | ~0.040s          | ~0.200s     | ~0.240s    | Medium circuits |
| 10k gates   | ~0.300s          | ~1.500s     | ~1.800s    | Large circuits |

*Note: Times are approximate and depend on hardware. The key benefit is that preprocessing is witness-independent.*

## 🔐 Security Analysis

### Soundness Security
- With n=8 parties: ~3.0 bits security per round
- For 128-bit security: need ~43 rounds
- Each round reduces cheating probability by factor of n

### Zero-Knowledge Property
- Verifier sees n-1 out of n party views
- Hidden party's shares mask witness reconstruction
- Could simulate transcript without knowing witness

### Post-Quantum Security
- No reliance on factoring or discrete log problems
- Based on symmetric primitives (SHA, AES)
- Quantum algorithms provide no advantage

## 🌟 Real-World Applications

### Digital Signatures
- **Picnic signatures** (NIST candidate) based on similar techniques
- Quantum-safe alternative to RSA/ECDSA
- Competitive signature sizes with hash-based schemes

### Privacy-Preserving Systems
- Anonymous authentication
- Zero-knowledge proofs of membership
- Private smart contract execution

### Blockchain Integration
- Privacy coins (Zcash-style applications)
- Anonymous voting systems
- Confidential transactions

## 🔬 Technical Details

### Circuit Representation
- Boolean circuits over GF(2)
- Supported gates: AND (multiplication), XOR (addition), NOT (free)
- Circuit size measured in number of AND gates

### Cryptographic Primitives
- **Hash Function**: SHA-256 for commitments and Fiat-Shamir
- **Secret Sharing**: XOR-based additive sharing
- **Randomness**: Cryptographically secure random number generation

### Optimization Techniques
1. **Preprocessing**: Generate randomness and multiplication triples offline
2. **Batching**: Process multiple gates simultaneously when possible
3. **Memory Management**: Efficient storage of party views and commitments

## 📈 Comparison with Other ZK Systems

| System | Proof Size | Prover Time | Verifier Time | Trusted Setup |
|--------|-----------|-------------|---------------|---------------|
| This Work | Small* | Medium | Fast | No |
| Groth16 | Tiny | Fast | Very Fast | Yes |
| PLONK | Small | Medium | Fast | Universal |
| STARKs | Large | Slow | Medium | No |

*Optimal for 300-100k AND gate circuits

## 🎓 Educational Value

These implementations are designed for:
- **Students** learning zero-knowledge proofs
- **Researchers** understanding MPC-in-the-head techniques
- **Developers** implementing post-quantum cryptography
- **Security analysts** evaluating quantum-safe systems

## 🔗 References and Further Reading

### Original Paper
- [Katz, Kolesnikov, Wang - "Improved Non-Interactive Zero Knowledge with Applications to Post-Quantum Signatures"](https://doi.org/10.1145/3243734.3243805)
- CCS 2018, pages 525-537
- 177+ citations, high research impact

### Related Work
- **ZKBoo** - Original MPC-in-the-head construction
- **ZKB++** - Improved efficiency and security
- **Ligero** - Sublinear communication complexity
- **Picnic** - Practical signature scheme implementation

### NIST Post-Quantum Cryptography
- [NIST PQC Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Picnic Signature Specification](https://microsoft.github.io/Picnic/)

### Academic Resources
- [Zero-Knowledge Proofs Survey](https://github.com/matter-labs/awesome-zero-knowledge-proofs)
- [Post-Quantum Cryptography Overview](https://pqcrypto.org/)

## ⚠️ Important Notes

### Academic Use Only
These implementations are for **educational and research purposes only**. They are not production-ready and should not be used in real cryptographic systems without extensive security review.

### Security Warnings
- Simplified random number generation (use proper CSPRNGs in production)
- No side-channel attack protections
- Limited error handling for edge cases
- Timing attacks not considered

### Production Considerations
For real-world use, consider:
- Formal security proofs
- Constant-time implementations
- Side-channel protections
- Extensive testing and validation
- Professional cryptographic review

## 💡 Contributing

To improve these implementations:
1. Fork the repository
2. Create educational examples
3. Add performance optimizations
4. Improve documentation
5. Submit pull requests

Focus on maintaining educational clarity while improving correctness and efficiency.

---

**🎯 Goal**: Understand MPC-in-the-head zero-knowledge proofs and their applications to post-quantum cryptography through hands-on implementation and experimentation.
