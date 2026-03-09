# Zero Network MCP Server

An MCP server that gives AI agents instant access to Zero Network documentation, integration guides, and utility tools.

## Tools (14)

### Documentation
| Tool | Description |
|------|-------------|
| `zero_overview` | Network overview — what Zero is, core facts, architecture, links |
| `zero_transaction_format` | 136-byte wire format, 48-byte account state, crypto primitives |
| `zero_python_sdk` | Python SDK — install, wallet, send, bridge, env vars |
| `zero_javascript_sdk` | JavaScript SDK — install, wallet, send, env vars |
| `zero_x402_integration` | x402 HTTP payment protocol — server middleware, client auto-pay |
| `zero_mcp_payments` | MCP payment integration — charge per tool call, spending limits |
| `zero_api_reference` | All 8 gRPC endpoints |
| `zero_network_parameters` | Full parameter table — fees, limits, staking, slashing |
| `zero_validator_info` | Validator setup, hardware, staking, economics |
| `zero_security_model` | Security architecture, Trinity Validators, attack mitigations |
| `zero_implementation_guide` | Step-by-step: API paywall, MCP pricing, website paywall |

### Utilities
| Tool | Description |
|------|-------------|
| `zero_convert` | Convert between USD, Z, and units |
| `zero_estimate_cost` | Estimate transaction costs with competitor comparison |
| `zero_pricing_calculator` | Calculate revenue for a Zero-gated service |

## Usage

### Claude Code / Claude Desktop
Add to your MCP config:
```json
{
  "mcpServers": {
    "zero": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-server", "python", "-m", "zero_mcp.server"]
    }
  }
}
```

### Direct
```bash
cd mcp-server
uv venv && uv pip install "mcp[cli]>=1.0.0"
source .venv/bin/activate
python -m zero_mcp.server
```

## What Agents Can Do

An AI agent connected to this MCP server can:
1. Learn what Zero is and how it works
2. Get SDK code examples for Python or JavaScript
3. Implement x402 paywalls on their APIs
4. Add per-tool pricing to their MCP servers
5. Convert between USD/Z/units
6. Estimate costs for any transaction volume
7. Calculate revenue projections for paid services
