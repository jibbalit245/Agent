# Replit Background Worker Deployments

> Source: https://docs.replit.com/deployments/background-worker-deployments
> Updated URL: https://docs.replit.com/cloud-services/deployments/background-worker-deployments
> Last updated: 2026-06

## What are Background Worker Deployments?

Background Worker Deployments run **long-lived processes** that don't serve HTTP traffic. Unlike web apps (Autoscale/Reserved VM) that respond to HTTP requests, background workers continuously process tasks, consume message queues, run bots, or perform ongoing computations.

## Key Characteristics

- **No HTTP endpoint**: Workers don't serve web traffic
- **Continuous execution**: Runs until stopped or crashes
- **Auto-restart**: Replit can restart crashed workers
- **Full app environment**: Access to all packages, files, and secrets
- **Compute Units billing**: Pay for actual compute consumed

## Use Cases

Background Workers are best for:
- ✅ Message queue consumers (Redis, RabbitMQ, SQS)
- ✅ Discord/Telegram/Slack bots
- ✅ Data stream processors
- ✅ WebSocket servers (persistent connections)
- ✅ Background task workers (Celery, etc.)
- ✅ Polling services
- ✅ File processing pipelines
- ✅ Machine learning model inference servers

NOT for:
- ❌ Web apps with HTTP endpoints (use Autoscale or Reserved VM)
- ❌ Periodic/scheduled tasks (use Scheduled deployments)

## Comparison with Other Deployment Types

| Feature | Background Worker | Autoscale | Reserved VM | Scheduled |
|---------|-----------------|-----------|-------------|-----------|
| HTTP serving | No | Yes | Yes | No |
| Always running | Yes | Scale to zero | Yes | Periodic |
| Cold starts | Possible | Yes | No | N/A |
| Billing | Compute Units | Compute Units | Fixed monthly | Compute Units per run |
| Use case | Long processes | Web apps | Production apps | Cron jobs |

## How to Deploy

1. Open your Replit App
2. Click **Deploy**
3. Select **Background Worker** deployment type
4. Configure:
   - **Run command**: Command to start your worker
   - **Machine size**: CPU and RAM allocation
   - **Deployment secrets**: Production environment variables
5. Click **Deploy**

## Configuration

### Run Command Examples

```bash
# Python worker
python worker.py

# Node.js worker
node worker.js

# Celery worker
celery -A myapp worker --loglevel=info

# Discord bot
python bot.py
```

### Machine Sizes

Choose based on workload:
- Lightweight workers (bots, queue consumers): Nano or Micro
- Data processing: Small or Medium
- Heavy computation: Large

## Example: Discord Bot

```python
# bot.py
import discord
import os

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content == '!hello':
        await message.channel.send('Hello!')

# Runs indefinitely
client.run(os.environ['DISCORD_TOKEN'])
```

Deployment secret: `DISCORD_TOKEN` = your bot token
Run command: `python bot.py`

## Example: Queue Consumer

```python
# worker.py
import redis
import time
import os

r = redis.from_url(os.environ['REDIS_URL'])

def process_job(job_data):
    # Process the job
    print(f"Processing: {job_data}")

while True:
    # Block waiting for jobs
    job = r.brpop('job_queue', timeout=30)
    if job:
        process_job(job[1])
    else:
        print("Waiting for jobs...")
```

## Example: Celery Worker

```python
# tasks.py
from celery import Celery
import os

app = Celery('tasks', broker=os.environ['REDIS_URL'])

@app.task
def process_data(data):
    # Long-running task
    result = heavy_computation(data)
    return result
```

Run command: `celery -A tasks worker --loglevel=info`

## Deployment Secrets

Background workers often need credentials:
- Database URLs
- API keys
- Message broker URLs
- Authentication tokens

Add them in Deployments → Secrets panel.

## Monitoring and Logs

- View real-time worker logs in Deployments panel
- Monitor CPU and memory usage
- Set up restart policies for crashed workers

## Error Handling and Restarts

Implement robust error handling in your worker:

```python
import time
import logging

logging.basicConfig(level=logging.INFO)

def main():
    while True:
        try:
            # Main worker logic
            process_messages()
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(5)  # Brief pause before retry

if __name__ == '__main__':
    main()
```

## Pricing

Billed by **Compute Units** consumed:
- 1 CPU second = 18 Compute Units
- 1 GB-second RAM = 2 Compute Units
- $1 per million Compute Units

Workers run continuously, so costs accumulate over time. Use the smallest machine size that meets your needs.

**Estimate**: A worker using 10% CPU and 256 MB RAM continuously:
- 0.1 CPU × 86,400 seconds/day = 8,640 CPU-seconds/day = ~155,520 CU/day
- 0.256 GB × 86,400 seconds/day = 22,118 GB-seconds/day = ~44,236 CU/day
- Total: ~200,000 CU/day = ~6 million CU/month ≈ **$6/month**
