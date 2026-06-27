# CrustCore Rust adapter sketch

Suggested Rust shape:

```rust
pub struct FlowDefinition {
    pub id: String,
    pub version: String,
    pub nodes: Vec<FlowNode>,
    pub quality_gates: Vec<QualityGate>,
}

pub trait FlowVerifier {
    fn validate_definition(&self, flow: &FlowDefinition) -> Result<(), FlowError>;
    fn verify_gate(&self, gate_id: &str, evidence: EvidenceRef) -> Result<GateResult, FlowError>;
    fn complete_patch(&self, flow_id: &str, evidence: PatchEvidence) -> Result<VerifiedPatch, FlowError>;
}
```

If implemented, the adapter should keep CrustCore responsible for proof and completion, not generic workflow scheduling.
