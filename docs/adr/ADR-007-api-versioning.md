# ADR-007: API Versioning Strategy

**Status**: Proposed
**Date**: 2026-02-11
**Epic**: EP-011 (Versioned REST API)
**Story**: ST-033
**Refines**: ADR-001-P section on endpoint versioning

## Context

The AI Platform exposes a single `POST /decide` endpoint at root level with no version prefix.
The endpoint uses raw `Dict[str, Any]` for request and response, mounted via a plain
`APIRouter()` in `app/main.py`.

As part of PI02 and EP-011, we are introducing a consumer-facing REST API with versioned paths.
ADR-001-P stated that major version should be reflected in URL or header, but deferred the
concrete strategy. This ADR concretizes that decision.

**Important distinction:** The API version (`v1`, `v2`) is independent of the contract schema
version in `contracts/VERSION` (currently `2.0.0`). API version covers the HTTP transport
contract (paths, headers, response envelope). Schema version covers the shape of
CommandDTO/DecisionDTO payloads per ADR-001-P.

### Options Considered

| # | Option | Pros | Cons |
|---|--------|------|------|
| A | **URL path prefix** (`/v1/decide`) | Explicit in logs/monitoring/docs; trivial with FastAPI `prefix=`; easy to route at LB/gateway level | URL changes on major bump; parallel paths during migration |
| B | Header-based (`Accept-Version: v1`) | URLs stable; content-negotiation friendly | Invisible in access logs; harder to route; requires custom middleware |
| C | Query parameter (`/decide?v=1`) | Simple to add | Not cacheable by version; pollutes query space; unconventional |

## Decision

We will use **URL path prefix versioning** as the primary API versioning mechanism.

1. **Versioned path prefix.** All platform endpoints are mounted under `/v1/` (e.g., `POST /v1/decide`).
   FastAPI router uses `app.include_router(router, prefix="/v1")`.

2. **Backward-compatible unversioned path.** The unversioned `POST /decide` is retained and
   delegates internally to the v1 implementation. This preserves existing consumer code and
   test scripts during migration.

3. **`API-Version` response header.** All responses from versioned endpoints include the header
   `API-Version: v1`. This provides version visibility for clients that do not inspect the URL path.

4. **Version lifecycle.**
   - A new major API version (`/v2/`) is introduced only on breaking changes to the HTTP transport
     contract that cannot be handled by additive changes.
   - Payload field changes follow ADR-001-P (schema versioning) and do not by themselves require
     a new API version.
   - When `/v2/` is introduced, `/v1/` remains supported for at least 2 PI cycles (~6 months),
     with a `Sunset` response header indicating the deprecation timeline.

5. **API version vs schema version.** These are independent axes:
   - `API-Version: v1` -- HTTP transport version (this ADR).
   - `schema_version` in DecisionDTO payload -- contract schema version (ADR-001-P).

## Consequences

### Positive

- Explicit version in every URL makes debugging, log analysis, and monitoring straightforward.
- FastAPI native `prefix=` support means near-zero implementation cost.
- Backward-compatible `/decide` path avoids breaking 270+ existing tests and `api_sanity.py`.
- Clear separation of API version (transport) and schema version (payload).

### Negative

- Two paths (`/decide` and `/v1/decide`) exist in parallel, increasing test surface slightly.
  Mitigation: Unversioned path is a thin delegate; tested once.
- URL changes on future major bumps require consumer updates.
  Mitigation: 2-PI deprecation window; `Sunset` header warns consumers.

## Links

- ADR-001-P: `docs/adr/ADR-001-contract-versioning-compatibility-policy.md`
- EP-011: `docs/planning/epics/EP-011/epic.md`
- ST-033: `docs/planning/epics/EP-011/stories/ST-033-versioned-api-path.md`
