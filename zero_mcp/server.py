"""Zero Network MCP Server.

Provides AI agents with tools to understand, integrate, and interact with the Zero Network.
Run with: uvx zero-mcp or python -m zero_mcp.server
"""

import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Zero Network")

# ============================================================
# NETWORK KNOWLEDGE BASE
# ============================================================

NETWORK_OVERVIEW = """# Zero Network

A permissionless, decentralized stablecoin microtransaction network for users and AI agents.

## Core Facts
- 1 Z = $0.01 USD (one penny), backed 1:1 by USDC/USDT locked in vault contracts
- Transaction fee: 0.01 Z ($0.0001) flat, always
- Finality: <500ms
- Transaction size: 136 bytes on wire
- No smart contracts, no VM, no gas market — transfer-only ledger
- Permissionless: anyone can create an account (just an Ed25519 keypair)

## Token Model
- Smallest unit: 0.01 Z (1 unit = $0.0001)
- Min transaction: 0.01 Z amount + 0.01 Z fee = 0.02 Z total ($0.0002)
- Max transaction: 25 Z ($0.25)
- Account creation: 5.00 Z ($0.05) one-time fee on first receive
- Per-account rate limit: 100 tx/s

## Bridge
- Bridge in: Lock USDC on Base or USDT on Arbitrum → mint Z on Zero (1 USDC = 100 Z)
- Bridge out: Burn Z on Zero → release USDC on Base or USDT on Arbitrum
- Trinity Validators (3 trusted parties, 2-of-3 multisig) control all mint/burn operations
- Circuit breaker: <=20% TVL/24h normal, 20-50% requires 3-of-3, >50% auto-pauses

## Architecture
- Block-lattice account model (each account has its own chain, inherently parallel)
- Leaderless DAG-based aBFT consensus (Mysticeti/Lachesis inspired)
- Ring buffer transfer log (validators never bloat, ~50-110 GB forever)
- Flat storage, no Merkle tries — O(1) account lookups
- Custom Rust implementation

## Fee Split
- 70% to validators (proportional to stake)
- 15% to bridge reserve (vault contract gas)
- 15% to protocol reserve

## Links
- Docs: https://docs.zzero.net
- Explorer: https://explorer.zzero.net
- MCP: https://mcp.zzero.net
- GitHub: https://github.com/Zzero-net
"""

TRANSACTION_FORMAT = """# Zero Transaction Format (136 bytes)

```
ZeroTransfer {
    from:      [32 bytes]  // Ed25519 public key (sender)
    to:        [32 bytes]  // Ed25519 public key (recipient)
    amount:    [4 bytes]   // u32, in units (1 unit = 0.01 Z = $0.0001)
    nonce:     [4 bytes]   // u32, per-account monotonic counter
    signature: [64 bytes]  // Ed25519 full signature
}
// Total: 136 bytes
```

## Amount Encoding
- Amount is in units, not Z. 1 Z = 100 units.
- To send 0.50 Z, set amount = 50
- To send 1.00 Z, set amount = 100
- Max amount: 2500 units (25 Z = $0.25)

## Account State (48 bytes per account)
```
Account {
    balance:  [4 bytes]   // u32, current balance in units
    nonce:    [4 bytes]   // u32, last transaction nonce
    head:     [32 bytes]  // BLAKE3 hash of latest block
    flags:    [8 bytes]   // reserved (frozen, validator, etc.)
}
```

## Cryptographic Primitives
- Signatures: Ed25519 (ed25519-dalek with verify_strict)
- Hashing: BLAKE3 (256-bit, hardware-accelerated)
- Wire signature: Full 64-byte Ed25519 signature
"""

PYTHON_SDK = """# Zero Python SDK

## Installation
```bash
pip install zero-network
```

## Quick Start (4 lines)
```python
from zero_network import Wallet

w = Wallet.from_env()             # reads ZERO_KEY env var
w.send("zr_recipient", 10)       # send 0.10 Z, fee: 0.01 Z auto-deducted
print(w.balance())                # check balance
```

## Create a New Wallet
```python
from zero_network import Wallet

w = Wallet.create()               # generate Ed25519 keypair
print(w.address)                  # zr_7f3a...2b1c
print(w.phrase)                   # 12-word recovery phrase
```

## Environment Variables
```bash
export ZERO_KEY="base64_ed25519_private_key"
export ZERO_RPC="https://rpc.zzero.net"
```

## Bridge Operations
```python
# Bridge in USDC from Arbitrum
w.bridge_in("arbitrum", "USDC", usdc_tx_hash)

# Bridge out Z to USDC on Base
w.bridge_out("base", "USDC", 10000)  # burn 100 Z → release 1 USDC
```

## Transaction History
```python
w.balance()         # current balance in Z
w.history(10)       # last 10 transactions
```
"""

JAVASCRIPT_SDK = """# Zero JavaScript SDK

## Installation
```bash
npm install @zero-network/sdk
```

## Quick Start (4 lines)
```javascript
import { Wallet } from '@zero-network/sdk';

const w = Wallet.fromEnv();              // reads ZERO_KEY env var
await w.send('zr_recipient', 10);       // send 0.10 Z
console.log(await w.balance());          // check balance
```

## Create a New Wallet
```javascript
const w = Wallet.create();
console.log(w.address);    // zr_7f3a...2b1c
```

## Environment Variables
```bash
export ZERO_KEY="hex_ed25519_seed"
export ZERO_RPC="https://rpc.zzero.net"
```

## Dependencies
- tweetnacl: Ed25519 (byte-compatible with Rust ed25519-dalek and Python PyNaCl)
- @grpc/grpc-js: gRPC transport
"""

X402_INTEGRATION = """# x402 Protocol Integration

Zero is the native settlement layer for the x402 HTTP payment protocol.

## How x402 Works
1. Agent sends HTTP request to an endpoint
2. Server returns HTTP 402 with payment details (amount, address, network: "zero")
3. Agent's SDK auto-pays the requested amount in Z
4. Agent retries the request with X-Zero-Receipt header containing the tx hash
5. Server verifies receipt on-chain (<500ms) and serves the response

## Server (Python FastAPI)
```python
from zero_network.x402 import x402_gate

@app.get("/api/search")
@x402_gate(amount=10)  # 0.10 Z per call
async def search(query: str):
    return do_search(query)
```

## Server (Express.js)
```javascript
const { ZeroPaywall } = require('@zero-network/sdk');
const paywall = new ZeroPaywall({ address: process.env.ZERO_ADDRESS });

app.get('/api/data', paywall.gate(5), async (req, res) => {
    // Only reached after 0.05 Z payment verified
    res.json(await getData());
});
```

## Client (Auto-Pay)
```python
from zero_network import Wallet
from zero_network.x402 import x402_fetch

w = Wallet.from_env()
result = await x402_fetch(
    "https://api.example.com/data",
    wallet=w,
    max_price=25    # spending limit: 0.25 Z per call
)
print(result.json())
```

## 402 Response Format
```json
{
    "x-402-version": 1,
    "x-402-network": "zero",
    "x-402-amount": 10,
    "x-402-address": "zr_pub...",
    "x-402-description": "Pay 0.10 Z to access this resource"
}
```
"""

MCP_PAYMENT_INTEGRATION = """# MCP Server Payment Integration

Charge AI agents per tool call using Zero micropayments.

## Server Implementation (Python)
```python
from mcp.server import Server
from zero_network import Wallet

server = Server("my-paid-tools")
wallet = Wallet.from_env()

@server.tool("web_search", zero_price=2)   # 0.02 Z per call
async def search(query: str):
    return await search_web(query)

@server.tool("run_code", zero_price=10)    # 0.10 Z per call
async def run_code(code: str, language: str):
    return await sandbox_exec(code, language)

@server.tool("image_gen", zero_price=25)   # 0.25 Z per call
async def gen_image(prompt: str):
    return await generate_image(prompt)
```

## Payment Flow
1. Agent calls `tools/list` → sees `zero_price` in tool metadata
2. Agent invokes tool without payment
3. Server returns `payment_required` with address and amount
4. Agent's wallet sends Z to server's address
5. Agent retries tool call with payment tx hash
6. Server verifies payment on-chain, executes tool, returns result

## Client Implementation
```python
from mcp.client import Client
from zero_network import Wallet
from zero_network.mcp import ZeroPaymentHandler

wallet = Wallet.from_env()
handler = ZeroPaymentHandler(wallet=wallet)

client = Client(
    server_url="https://mcp.example.com",
    payment_handler=handler
)

# Automatic: discovers price, pays, gets result
result = await client.call_tool("web_search", {"query": "AI research"})
```

## Tool Schema with Pricing
```json
{
    "tools": [
        {
            "name": "web_search",
            "description": "Search the web",
            "zero_price": 2,
            "zero_address": "zr_pub..."
        }
    ]
}
```

## Spending Limits
```python
from zero_network.spending import SpendingPolicy

policy = SpendingPolicy(
    max_per_call=25,       # 0.25 Z max per single payment
    max_per_minute=100,    # 1.00 Z max per minute
    max_per_hour=1000,     # 10.00 Z max per hour
    max_per_day=10000,     # 100.00 Z ($1.00) max per day
)
wallet.set_policy(policy)
```
"""

API_REFERENCE = """# Zero Network API (8 Endpoints)

All endpoints use gRPC. HTTP/JSON proxy available for browser access.

## Transfer Endpoints

### Send
```
Send(from, to, amount, nonce, signature) → tx_hash
```
Submit a signed transfer. Fee (0.01 Z) is auto-deducted from sender.

### GetTransfer
```
GetTransfer(tx_hash) → { status, from, to, amount, timestamp }
```
Look up a transfer by hash. Status: pending | confirmed | not_found.

### GetHistory
```
GetHistory(account, limit) → [transfers]
```
Get recent transfers for an account (from the rolling window).

## Account Endpoints

### GetBalance
```
GetBalance(account) → balance (in units)
```
Returns current balance. Divide by 100 for Z value.

### GetAccount
```
GetAccount(account) → { balance, nonce, head }
```
Full account state: balance, last nonce, head block hash.

## Bridge Endpoints

### BridgeIn
```
BridgeIn(source_chain, token, tx_hash) → pending_mint
```
Initiate a bridge-in. Provide the USDC/USDT lock transaction hash from the source chain. Trinity Validators will attest and mint Z.

### BridgeOut
```
BridgeOut(dest_chain, token, dest_address, amount) → pending_release
```
Request a bridge-out. Burns Z and queues a release on the destination chain.

### GetBridgeStatus
```
GetBridgeStatus(bridge_id) → { status, confirmations, amount }
```
Check bridge operation status: pending | attesting | complete | failed.

## Status Endpoint

### GetStatus
```
GetStatus() → { 17 metrics }
```
Returns: consensus round, finalized events/txs, epoch, accounts, supply, fee pool, reserves, stake, peers, pending.
"""

NETWORK_PARAMETERS = """# Zero Network Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Z peg | 1 Z = $0.01 | Fixed, backed 1:1 by USDC/USDT |
| Units per Z | 100 | 1 unit = $0.0001 |
| Transaction fee | 0.01 Z (1 unit) | $0.0001 flat per tx |
| Account creation fee | 5.00 Z | $0.05 one-time on first receive |
| Max transfer | 25 Z (2,500 units) | $0.25 per transaction |
| Min send balance | 1 Z | Accounts below this can only receive |
| Per-account rate limit | 100 tx/s | Sliding window |
| Finality target | <500ms | Deterministic |
| Transaction size | 136 bytes | Wire format |
| Account state | 48 bytes | Balance + nonce + head + flags |
| Max validators | 1,024 | Ranked by stake |
| Min validator stake | 10,000 Z ($100) | Permissionless entry |
| Unbonding period | 7 days | Prevents stake-and-slash |
| Fee split | 70/15/15 | Validators / Bridge reserve / Protocol |
| Slashing (equivocation) | 100% stake burned | Double-signing |
| Slashing (downtime) | 10% stake burned | Extended inactivity |
| Slashing (bad attestation) | 100% stake burned | Invalid bridge attestation |
| Bridge circuit breaker | Tiered | <=20%: 2-of-3, 20-50%: 3-of-3, >50%: blocked |
| Guardian rotation delay | 48 hours | Observable on-chain |
| Dust pruning | <0.10 Z for 30 days | Inactive small accounts pruned |
| Validator storage | ~50-110 GB | Ring buffer, constant forever |
"""

VALIDATOR_INFO = """# Running a Zero Validator

## Requirements

### Hardware (Minimum)
- CPU: 4 cores (x86_64 or ARM64)
- RAM: 16 GB
- Storage: 256 GB NVMe SSD
- Network: 100 Mbps symmetric
- Cost: ~$30/month VPS

### Hardware (Recommended)
- CPU: 8+ cores
- RAM: 32 GB
- Storage: 512 GB NVMe SSD
- Network: 1 Gbps symmetric

## Quick Start
```bash
curl -sSf https://install.zzero.net | sh
zero-node init --stake-key /path/to/key
zero-node run
```

## Staking
- Minimum stake: 10,000 Z ($100)
- Validators ranked by stake, max 1,024 active
- 7-day unbonding period for withdrawals
- Trust score: 0-1000 (start at 500)
  - +1 for timely events
  - -5 for missed events
  - -2 for late events
  - -1000 for equivocation (immediate ejection)
  - Below 100 = ejection

## Slashing
- Equivocation (double-signing): 100% stake burned
- Extended downtime: 10% stake burned
- Invalid bridge attestation: 100% stake burned
- Slashed funds go to protocol reserve

## Economics
- Validators earn 70% of all transaction fees, proportional to stake
- At 100M daily tx with 100 validators: ~$50/day each
- At 1B daily tx with 100 validators: ~$500/day each
"""

SECURITY_MODEL = """# Zero Security Model

## Architecture
- Transfer-only ledger: no smart contracts, no VM, no opcodes
- Single operation: move Z from A to B
- Ed25519 signatures + BLAKE3 hashing
- No Merkle tries, no complex state transitions

## Bridge Security (Trinity Validators)
- 3 trusted parties control mint/burn operations (2-of-3 multisig)
- Each Trinity Validator = different organization, different legal jurisdiction
- Hardware-only signing (HSM/hardware wallets, never on servers)
- No delegation without on-chain expiry
- Asymmetric pause: any 1 Trinity Validator can pause, only admin can unpause
- Timelocked guardian rotation: 48h delay, observable on-chain

## Vault Contract (Solidity, on Base + Arbitrum)
- OpenZeppelin AccessControl with role-based permissions
- EIP-712 typed signatures for human-readable signing
- Tiered circuit breaker: <=20% TVL/24h (2-of-3), 20-50% (3-of-3), >50% (blocked)
- ReentrancyGuard on all fund-moving functions
- Replay prevention via unique bridgeId

## Attack Mitigations
| Attack | Mitigation |
|--------|-----------|
| Transaction spam | Per-account rate limit (100 tx/s) + flat fee |
| Dust account spam | Account creation fee (5 Z) |
| State bloat | Ring buffer + dust pruning |
| Validator equivocation | 100% stake slash + immediate ejection |
| Validator downtime | 10% stake slash + trust score degradation |
| Invalid bridge attestation | 100% stake slash |
| Bridge key compromise | Tiered circuit breaker + asymmetric pause |
| Sybil validators | Min stake 10,000 Z, max 1,024 ranked by stake |
| Stake-and-slash | 7-day unbonding period |
| Bridge drain | Circuit breaker: max 20% reserves/24h |
"""

IMPLEMENTATION_GUIDE = """# Implementing Zero Payments

## For API Providers (x402)

### Step 1: Create a Zero Wallet
```bash
pip install zero-network
python -c "from zero_network import Wallet; w = Wallet.create(); print(f'Address: {w.address}\\nKey: {w.secret_b64}')"
```
Save the key securely. Set as environment variable:
```bash
export ZERO_KEY="your_base64_key"
export ZERO_ADDRESS="zr_your_address"
```

### Step 2: Add x402 Middleware
```python
from zero_network.x402 import x402_gate

@app.get("/api/your-endpoint")
@x402_gate(amount=5)  # 0.05 Z per call
async def your_endpoint(param: str):
    return your_logic(param)
```

### Step 3: That's It
- Agents with Zero wallets will auto-pay and get access
- No API keys to issue or manage
- No subscription tiers
- Revenue appears in your wallet instantly

## For MCP Server Providers

### Step 1: Add Pricing to Your Tools
```python
@server.tool("your_tool", zero_price=5)  # 0.05 Z
async def your_tool(input: str):
    return your_logic(input)
```

### Step 2: Handle Payment Verification
The Zero MCP SDK handles payment verification automatically.
When an agent calls your tool:
1. First call returns `payment_required` with your address and price
2. Agent pays
3. Agent retries with tx hash
4. SDK verifies payment, your tool executes

## For Website Publishers

### Paywall Any Page
```javascript
const { ZeroPaywall } = require('@zero-network/sdk');
const paywall = new ZeroPaywall({ address: process.env.ZERO_ADDRESS });

// 0.05 Z to read an article
app.get('/article/:id', paywall.gate(5), (req, res) => {
    res.render('article', { id: req.params.id });
});
```

## Pricing Guidelines
| Service Type | Suggested Price | USD Equivalent |
|-------------|----------------|----------------|
| Simple API call | 0.01-0.05 Z | $0.0001-0.0005 |
| Search query | 0.02-0.10 Z | $0.0002-0.001 |
| Content access | 0.05-0.25 Z | $0.0005-0.0025 |
| Code execution | 0.10-0.25 Z | $0.001-0.0025 |
| Image generation | 0.25 Z | $0.0025 |
| Data export | 0.10-0.25 Z | $0.001-0.0025 |
"""

# ============================================================
# TOOLS
# ============================================================

@mcp.tool()
def zero_overview() -> str:
    """Get a comprehensive overview of the Zero Network — what it is, how it works, key facts, and links."""
    return NETWORK_OVERVIEW


@mcp.tool()
def zero_transaction_format() -> str:
    """Get the Zero transaction wire format (136 bytes), account state format (48 bytes), and cryptographic primitives."""
    return TRANSACTION_FORMAT


@mcp.tool()
def zero_python_sdk() -> str:
    """Get Python SDK documentation — installation, wallet creation, sending Z, bridge operations, environment variables."""
    return PYTHON_SDK


@mcp.tool()
def zero_javascript_sdk() -> str:
    """Get JavaScript SDK documentation — installation, wallet creation, sending Z, environment variables."""
    return JAVASCRIPT_SDK


@mcp.tool()
def zero_x402_integration() -> str:
    """Get x402 HTTP payment protocol integration guide — server middleware (Python/JS), client auto-pay, 402 response format."""
    return X402_INTEGRATION


@mcp.tool()
def zero_mcp_payments() -> str:
    """Get MCP server payment integration guide — how to charge AI agents per tool call, payment flow, spending limits."""
    return MCP_PAYMENT_INTEGRATION


@mcp.tool()
def zero_api_reference() -> str:
    """Get the Zero Network API reference — all 8 gRPC endpoints: Send, GetTransfer, GetHistory, GetBalance, GetAccount, BridgeIn, BridgeOut, GetBridgeStatus."""
    return API_REFERENCE


@mcp.tool()
def zero_network_parameters() -> str:
    """Get all Zero Network parameters — fees, limits, staking, slashing, circuit breaker thresholds, pruning rules."""
    return NETWORK_PARAMETERS


@mcp.tool()
def zero_validator_info() -> str:
    """Get validator documentation — hardware requirements, staking, trust scoring, slashing rules, economics."""
    return VALIDATOR_INFO


@mcp.tool()
def zero_security_model() -> str:
    """Get the Zero security model — attack mitigations, Trinity Validators, vault contract security, bridge protections."""
    return SECURITY_MODEL


@mcp.tool()
def zero_implementation_guide() -> str:
    """Get step-by-step implementation guide for accepting Zero payments — API providers (x402), MCP servers, website paywalls, pricing guidelines."""
    return IMPLEMENTATION_GUIDE


@mcp.tool()
def zero_convert(amount: float, direction: str = "usd_to_z") -> str:
    """Convert between USD, Z tokens, and units.

    Args:
        amount: The amount to convert
        direction: One of "usd_to_z", "z_to_usd", "z_to_units", "units_to_z"
    """
    if direction == "usd_to_z":
        z = amount / 0.01
        units = int(z * 100)
        return f"${amount:.4f} USD = {z:.2f} Z = {units} units"
    elif direction == "z_to_usd":
        usd = amount * 0.01
        units = int(amount * 100)
        return f"{amount:.2f} Z = ${usd:.4f} USD = {units} units"
    elif direction == "z_to_units":
        units = int(amount * 100)
        usd = amount * 0.01
        return f"{amount:.2f} Z = {units} units = ${usd:.4f} USD"
    elif direction == "units_to_z":
        z = amount / 100
        usd = z * 0.01
        return f"{int(amount)} units = {z:.2f} Z = ${usd:.4f} USD"
    else:
        return f"Unknown direction '{direction}'. Use: usd_to_z, z_to_usd, z_to_units, units_to_z"


@mcp.tool()
def zero_estimate_cost(num_transactions: int, avg_amount_z: float = 0.10) -> str:
    """Estimate the cost of operating on Zero Network.

    Args:
        num_transactions: Number of transactions to estimate for
        avg_amount_z: Average transaction amount in Z (default 0.10 Z)
    """
    fee_per_tx = 0.01  # Z
    total_fees_z = num_transactions * fee_per_tx
    total_fees_usd = total_fees_z * 0.01
    total_amount_z = num_transactions * avg_amount_z
    total_amount_usd = total_amount_z * 0.01
    total_z = total_fees_z + total_amount_z
    total_usd = total_z * 0.01

    return f"""# Cost Estimate for {num_transactions:,} transactions

## Fees
- Fee per transaction: 0.01 Z ($0.0001)
- Total fees: {total_fees_z:,.2f} Z (${total_fees_usd:,.4f})

## Payments (at {avg_amount_z:.2f} Z average)
- Total payment volume: {total_amount_z:,.2f} Z (${total_amount_usd:,.4f})

## Total Cost
- Total Z needed: {total_z:,.2f} Z (${total_usd:,.4f})
- USDC to bridge in: ${total_usd:,.4f} (= {total_z / 100:,.4f} USDC)

## Comparison
- Same on Ethereum L1: ${num_transactions * 0.50:,.2f} - ${num_transactions * 5.00:,.2f}
- Same on Solana: ${num_transactions * 0.0005:,.4f} - ${num_transactions * 0.005:,.4f}
- Same on Base: ${num_transactions * 0.001:,.4f} - ${num_transactions * 0.01:,.4f}
- **Zero: ${total_fees_usd:,.4f}** (fees only)
"""


@mcp.tool()
def zero_pricing_calculator(
    price_per_call_z: float,
    daily_calls: int,
) -> str:
    """Calculate expected revenue for a Zero-gated service.

    Args:
        price_per_call_z: Price per API/tool call in Z
        daily_calls: Expected number of calls per day
    """
    daily_revenue_z = price_per_call_z * daily_calls
    daily_revenue_usd = daily_revenue_z * 0.01
    monthly_revenue_usd = daily_revenue_usd * 30
    annual_revenue_usd = daily_revenue_usd * 365

    return f"""# Revenue Estimate

## Pricing
- Price per call: {price_per_call_z:.2f} Z (${price_per_call_z * 0.01:.4f})
- Daily calls: {daily_calls:,}

## Revenue
- Daily: {daily_revenue_z:,.2f} Z (${daily_revenue_usd:,.2f})
- Monthly: {daily_revenue_z * 30:,.2f} Z (${monthly_revenue_usd:,.2f})
- Annual: {daily_revenue_z * 365:,.2f} Z (${annual_revenue_usd:,.2f})

## For Context
- No API key management needed
- No subscription billing infrastructure
- No chargebacks
- Instant settlement (<500ms)
- Revenue appears in your Zero wallet immediately
"""


def main():
    """Run the Zero MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
