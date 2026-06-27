# ThinClaw Rust adapter sketch

Suggested Rust shape:

```rust
pub trait RoutineFlowLoader {
    fn load_flow(&self, path: &std::path::Path) -> Result<FlowDefinition, FlowError>;
    fn create_routine(&self, flow: FlowDefinition) -> Result<RoutineId, FlowError>;
    fn record_decision(&self, run_id: RunId, decision: OperatorDecision) -> Result<(), FlowError>;
}
```

ThinClaw should remain the durable home for routine state, human decisions, and cross-session memory.

