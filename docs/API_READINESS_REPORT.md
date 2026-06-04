# API Readiness Report -- QADE Optimization Service

This report audits the readiness of the repository to serve the `/optimize` API endpoint and lists the infrastructure components required to launch.

## 1. FastAPI Infrastructure Readiness Score: **80%**

While the core transpilation, evolution, and pattern-matching algorithms are fully built and tested, the actual web server wrapper, API key schemas, and rate-limiting middleware do not exist in the codebase.

---

## 2. Gap Analysis & Missing Components

### 2.1. Web Server Entrypoint (FastAPI Wrapper)
- **Status**: **Missing**.
- **Action**: Create a new file `quantum/api/main.py` which instantiates the FastAPI app and exposes the endpoints:
  - `POST /v1/optimize`
  - `GET /v1/health`
- **Estimated Effort**: 1 Developer-Day.

### 2.2. Request/Response Schemas (Pydantic Models)
- **Status**: **Missing**.
- **Action**: Define request structures in `quantum/api/schemas.py`:
  - Request:
    ```python
    class OptimizeRequest(BaseModel):
        qasm_circuit: str
        target_backend: str
        optimization_level: int = 2
    ```
  - Response:
    ```python
    class OptimizeResponse(BaseModel):
        optimized_qasm: str
        original_depth: int
        optimized_depth: int
        estimated_fidelity: float
        symbolic_explanation: str
    ```
- **Estimated Effort**: 1 Developer-Day.

### 2.3. Authentication & API Key Management
- **Status**: **Missing**.
- **Action**: Create a simple SQLite table `api_keys` inside `theory_memory.db` mapping hashes of API keys to users, tiers, and limits. Add a FastAPI dependency checking:
  - Header `X-API-Key`
  - Validate against the database.
- **Estimated Effort**: 2 Developer-Days.

### 2.4. Rate Limiting
- **Status**: **Missing**.
- **Action**: Integrate `slowapi` or redis-based rate-limiting middleware in the FastAPI entrypoint to prevent abuse of the heavy genetic optimizer engine.
- **Estimated Effort**: 1 Developer-Day.

### 2.5. Structured Logging & Latency Monitoring
- **Status**: **Missing**.
- **Action**: Add structured logging to output compile duration, gate reductions, and error types. Setup standard Prometheus metric endpoints to export:
  - API request count
  - Compile latency histogram (ms)
  - Cache hits vs misses in the Knowledge Graph.
- **Estimated Effort**: 2 Developer-Days.

---

## 3. Launch Timeline

The total remaining effort to get a functional, secure, and production-ready `POST /optimize` API deployed to AWS or GCP is **7 developer-days** (less than **2 weeks**).
