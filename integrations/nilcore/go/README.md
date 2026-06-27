# NilCore Go adapter sketch

Suggested Go shape:

```go
type FlowDefinition struct {
    ID      string
    Version string
    Nodes   []FlowNode
    Edges   []FlowEdge
}

type WorkflowExecutor interface {
    Load(path string) (*FlowDefinition, error)
    CheckCapabilities(flow *FlowDefinition) error
    Run(ctx context.Context, flow *FlowDefinition, input map[string]any) (*RunResult, error)
}
```

NilCore should own worker dispatch, sandbox boundaries, retries, and supervisor reconciliation.

