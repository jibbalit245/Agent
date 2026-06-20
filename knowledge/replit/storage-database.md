# Replit Database (Key-Value Store)

> Source: https://docs.replit.com/storage/replit-database
> Updated URL: https://docs.replit.com/cloud-services/storage-and-databases/replit-database
> Blog: https://blog.replit.com/database
> Last updated: 2026-06

## What is Replit Database?

The **Replit Database** (also called Replit DB or Key-Value Store) is a fast, free, built-in database included with every Repl. It's a simple key-value store that persists data between runs without any setup.

Think of it as a persistent Python dictionary or JavaScript object that survives app restarts.

## Key Features

- **Zero configuration**: No setup required, just import and use
- **Persistent**: Data survives Repl restarts and re-runs
- **Free**: Included with every Replit account
- **Simple API**: Dictionary-like interface
- **JSON support**: Store any JSON-serializable type

## Storage Limits

| Limit | Value |
|-------|-------|
| **Total storage** | 50 MiB per store (sum of all keys + values) |
| **Max keys** | 5,000 keys per store |
| **Max key length** | 1,000 bytes |
| **Max value size** | 5 MiB per value |

## How It Works

### Environment Variable

The database URL is available via:
```
REPLIT_DB_URL
```

In the workspace: injected automatically.
In deployed apps: reads from `/tmp/replitdb` instead.

## Python Usage

### Installation

The `replit` package is pre-installed in Python Repls:

```bash
# If needed:
poetry add replit
# or
pip install replit
```

### Basic Operations

```python
from replit import db

# Set a value
db["username"] = "alice"
db["count"] = 42
db["user"] = {"name": "Alice", "age": 30}  # JSON types supported

# Get a value
name = db["username"]         # Raises KeyError if not found
name = db.get("username")     # Returns None if not found

# Check if key exists
if "username" in db:
    print("User exists")

# Delete a key
del db["username"]

# List all keys
all_keys = db.keys()
print(list(all_keys))

# Get all items
for key, value in db.items():
    print(f"{key}: {value}")
```

### Prefix Queries

```python
from replit import db

# Store user data with prefix
db["user:alice"] = {"age": 30, "email": "alice@example.com"}
db["user:bob"] = {"age": 25, "email": "bob@example.com"}
db["post:1"] = {"title": "Hello", "author": "alice"}

# Get all keys with prefix "user:"
user_keys = db.prefix("user:")
print(list(user_keys))
# Output: ["user:alice", "user:bob"]
```

### Storing Complex Data

```python
from replit import db
import json

# Store a list
db["favorites"] = ["apple", "banana", "cherry"]

# Retrieve and use
fruits = db["favorites"]
print(fruits[0])  # "apple"

# Store nested objects
db["config"] = {
    "theme": "dark",
    "notifications": True,
    "maxItems": 100
}

config = db["config"]
print(config["theme"])  # "dark"
```

### ObservedDict and ObservedList

The Replit DB returns special objects that track mutations:

```python
from replit import db

# These auto-sync to the database on mutation
db["mylist"] = [1, 2, 3]
mylist = db["mylist"]  # Returns ObservedList
mylist.append(4)  # Automatically persisted!

db["mydict"] = {"a": 1}
mydict = db["mydict"]  # Returns ObservedDict
mydict["b"] = 2  # Automatically persisted!
```

## Node.js Usage

### Installation

```bash
npm install @replit/database
```

### Basic Operations

```javascript
const Database = require("@replit/database");
const db = new Database();

async function main() {
  // Set a value
  await db.set("username", "alice");
  await db.set("count", 42);
  await db.set("user", { name: "Alice", age: 30 });

  // Get a value
  const name = await db.get("username");
  console.log(name); // "alice"

  // List all keys
  const keys = await db.list();
  console.log(keys); // ["username", "count", "user"]

  // List keys with prefix
  const userKeys = await db.list("user");

  // Delete a key
  await db.delete("username");

  // Get all entries
  const all = await db.getAll();
  console.log(all);
}

main();
```

### TypeScript

```typescript
import Database from "@replit/database";

const db = new Database();

interface User {
  name: string;
  age: number;
  email: string;
}

async function saveUser(id: string, user: User): Promise<void> {
  await db.set(`user:${id}`, user);
}

async function getUser(id: string): Promise<User | null> {
  return await db.get(`user:${id}`) as User | null;
}
```

## Direct HTTP API

The database exposes a REST HTTP API (available via `REPLIT_DB_URL`):

```bash
# Set a value
curl -X POST "$REPLIT_DB_URL" \
  --data-urlencode "key=hello" \
  --data-urlencode "value=world"

# Get a value
curl "$REPLIT_DB_URL/hello"

# List keys
curl "$REPLIT_DB_URL?prefix="

# List keys with prefix
curl "$REPLIT_DB_URL?prefix=user:"

# Delete a key
curl -X DELETE "$REPLIT_DB_URL/hello"
```

This allows use from **any language** that can make HTTP requests.

### Go Example (using HTTP API)

```go
package main

import (
    "fmt"
    "io"
    "net/http"
    "net/url"
    "os"
    "strings"
)

var dbURL = os.Getenv("REPLIT_DB_URL")

func set(key, value string) error {
    data := url.Values{}
    data.Set(key, value)
    resp, err := http.Post(dbURL, "application/x-www-form-urlencoded",
        strings.NewReader(data.Encode()))
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    return nil
}

func get(key string) (string, error) {
    resp, err := http.Get(dbURL + "/" + url.PathEscape(key))
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()
    body, _ := io.ReadAll(resp.Body)
    return string(body), nil
}

func main() {
    set("message", "Hello from Go!")
    value, _ := get("message")
    fmt.Println(value)
}
```

## Common Patterns

### Simple Counter

```python
from replit import db

def increment(key: str) -> int:
    current = db.get(key, 0)
    new_value = int(current) + 1
    db[key] = new_value
    return new_value

visits = increment("page_views")
print(f"Total visits: {visits}")
```

### User Session Storage

```python
from replit import db
import uuid
import time

def create_session(user_id: str) -> str:
    session_id = str(uuid.uuid4())
    db[f"session:{session_id}"] = {
        "user_id": user_id,
        "created_at": time.time(),
        "expires_at": time.time() + 3600  # 1 hour
    }
    return session_id

def get_session(session_id: str) -> dict | None:
    session = db.get(f"session:{session_id}")
    if session and session["expires_at"] > time.time():
        return session
    return None
```

### Caching

```python
from replit import db
import time

CACHE_TTL = 300  # 5 minutes

def get_cached(key: str, fetch_fn):
    cache_key = f"cache:{key}"
    cached = db.get(cache_key)
    
    if cached and cached.get("expires_at", 0) > time.time():
        return cached["data"]
    
    # Fetch fresh data
    data = fetch_fn()
    db[cache_key] = {
        "data": data,
        "expires_at": time.time() + CACHE_TTL
    }
    return data
```

## Deployment Considerations

In deployed apps:
- The database URL is read from `/tmp/replitdb` instead of `REPLIT_DB_URL`
- The same database is shared between workspace and deployment
- Use separate key namespaces if needed (e.g., `dev:key` vs `prod:key`)

## Replit DB vs. PostgreSQL

| Feature | Replit DB (KV) | PostgreSQL |
|---------|---------------|------------|
| Type | Key-value store | Relational database |
| Setup | Zero config | Requires setup |
| Queries | By key or prefix | SQL (full power) |
| Storage limit | 50 MiB | Much larger |
| Transactions | No | Yes |
| Best for | Simple data, caching | Complex data, relations |
| Cost | Free | Additional cost |

For complex data relationships, use Replit's built-in PostgreSQL database instead.
