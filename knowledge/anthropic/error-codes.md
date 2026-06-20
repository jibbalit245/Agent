# HTTP Error Codes Reference
> Source: https://platform.claude.com/docs/en/api/errors.md
> Fetched: 2026-06-20
---

## Error Code Summary

| Code | Error Type              | Retryable | Common Cause                         |
| ---- | ----------------------- | --------- | ------------------------------------ |
| 400  | `invalid_request_error` | No        | Invalid request format or parameters |
| 401  | `authentication_error`  | No        | Invalid or missing API key           |
| 403  | `permission_error`      | No        | API key lacks permission             |
| 404  | `not_found_error`       | No        | Invalid endpoint or model ID         |
| 413  | `request_too_large`     | No        | Request exceeds size limits          |
| 429  | `rate_limit_error`      | Yes       | Too many requests                    |
| 500  | `api_error`             | Yes       | Anthropic service issue              |
| 529  | `overloaded_error`      | Yes       | API is temporarily overloaded        |

## Detailed Error Information

### 400 Bad Request

**Causes:**
- Malformed JSON in request body
- Missing required parameters (`model`, `max_tokens`, `messages`)
- Invalid parameter types (e.g., string where integer expected)
- Empty messages array
- Messages not alternating user/assistant

**Example error:**

```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "messages: roles must alternate between \"user\" and \"assistant\""
  },
  "request_id": "req_011CSHoEeqs5C35K2UUqR7Fy"
}
```

**Fix:** Validate request structure before sending. Check that:
- `model` is a valid model ID
- `max_tokens` is a positive integer
- `messages` array is non-empty and alternates correctly

**Model-specific 400s on Fable 5 / Opus 4.8 / 4.7:**
- `temperature`, `top_p`, `top_k` are removed — sending any of them returns 400. Delete the parameter.
- `thinking: {type: "enabled", budget_tokens: N}` is removed — sending it returns 400. Use `thinking: {type: "adaptive"}` instead.
- **Fable 5 only:** an explicit `thinking: {type: "disabled"}` returns 400. Omit the `thinking` param entirely instead.
- **Fable 5 only:** if org is set to zero data retention (ZDR) — all Fable 5 requests return `400 invalid_request_error`.

### 401 Unauthorized

**Causes:**
- Missing `x-api-key` header or `Authorization` header
- Invalid API key format
- Revoked or deleted API key
- OAuth bearer token sent via `x-api-key` instead of `Authorization: Bearer`
- Both `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` set

**Fix:** Set `ANTHROPIC_API_KEY`, or run `ant auth login` and leave the client constructor empty. For raw HTTP with an OAuth token, use `Authorization: Bearer <token>` (not `x-api-key:`).

### 403 Forbidden

**Causes:**
- API key doesn't have access to the requested model
- Organization-level restrictions
- Attempting to access beta features without beta access

**Fix:** Check your API key permissions in the Console.

### 404 Not Found

**Causes:**
- Typo in model ID (e.g., `claude-sonnet-4.6` instead of `claude-sonnet-4-6`)
- Using deprecated model ID
- Invalid API endpoint

**Fix:** Use exact model IDs from the models documentation.

### 413 Request Too Large

**Causes:**
- Request body exceeds maximum size
- Too many tokens in input
- Image data too large

**Fix:** Reduce input size — truncate conversation history, compress/resize images, or split large documents into chunks.

### 429 Rate Limited

**Causes:**
- Exceeded requests per minute (RPM)
- Exceeded tokens per minute (TPM)
- Exceeded tokens per day (TPD)

**Headers to check:**
- `retry-after`: Seconds to wait before retrying
- `x-ratelimit-limit-*`: Your limits
- `x-ratelimit-remaining-*`: Remaining quota

**Fix:** The Anthropic SDKs automatically retry 429 and 5xx errors with exponential backoff (default: `max_retries=2`).

### 500 Internal Server Error

**Fix:** Retry with exponential backoff. If persistent, check [status.anthropic.com](https://status.anthropic.com).

### 529 Overloaded

**Fix:** Retry with exponential backoff. Consider using a different model (Haiku is often less loaded).

## Common Mistakes and Fixes

| Mistake                         | Error            | Fix                                                     |
| ------------------------------- | ---------------- | ------------------------------------------------------- |
| `temperature`/`top_p`/`top_k` on Fable 5 / Opus 4.8 / 4.7 | 400 | Remove the parameter |
| `budget_tokens` on Fable 5 / Opus 4.8 / 4.7 | 400  | Use `thinking: {type: "adaptive"}`                      |
| `thinking: {type: "disabled"}` on Fable 5 | 400    | Omit the `thinking` param entirely |
| Org set to ZDR / retention below 30 days (Fable 5) | 400 on every request | Fix the org's data-retention configuration |
| `budget_tokens` >= `max_tokens` (older models) | 400 | Ensure `budget_tokens` < `max_tokens`                  |
| Typo in model ID                | 404              | Use valid model ID like `claude-opus-4-8`               |
| First message is `assistant`    | 400              | First message must be `user`                            |
| Consecutive same-role messages  | 400              | Alternate `user` and `assistant`                        |
| API key in code                 | 401 (leaked key) | Use environment variable                                |

## Typed Exceptions in SDKs

**Always use the SDK's typed exception classes** instead of checking error messages with string matching.

### Exception class names by language

| HTTP | Python (`anthropic.*`) | TypeScript (`Anthropic.*`) |
|---|---|---|
| 400 | `BadRequestError` | `BadRequestError` |
| 401 | `AuthenticationError` | `AuthenticationError` |
| 403 | `PermissionDeniedError` | `PermissionDeniedError` |
| 404 | `NotFoundError` | `NotFoundError` |
| 429 | `RateLimitError` | `RateLimitError` |
| ≥500 | `InternalServerError` | `InternalServerError` |
| net | `APIConnectionError` | `APIConnectionError` |
| base | `APIError` / `APIStatusError` | `APIError` |

### Python Error Handling Example

```python
try:
    msg = client.messages.create(...)
except anthropic.NotFoundError as e:          # 404 — e.g. bad model ID
    ...
except anthropic.RateLimitError as e:         # 429 — back off and retry
    ...
except anthropic.APIStatusError as e:         # any other non-2xx HTTP response
    print(e.status_code, e.message)
except anthropic.APIConnectionError as e:     # network failure before a response
    ...
```

### Error `.type` Field

All `APIStatusError` subclasses expose a `.type` property (e.g., `"invalid_request_error"`, `"authentication_error"`, `"rate_limit_error"`, `"overloaded_error"`). Use this for programmatic error classification:

```python
except anthropic.APIStatusError as e:
    if e.type == "rate_limit_error":
        # handle rate limiting
    elif e.type == "overloaded_error":
        # handle overload
```
