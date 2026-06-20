# Modal Scheduled Functions (Cron)

> Source: https://modal.com/docs/guide/cron
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## Overview

Modal supports scheduled (cron) functions that run automatically on a time-based schedule. Use `modal.Period` for simple intervals or `modal.Cron` for Unix cron syntax.

## Basic Scheduling

### `modal.Period` - Simple Intervals

```python
import modal

app = modal.App("scheduled-app")

@app.function(schedule=modal.Period(hours=1))
def run_every_hour():
    print("Running hourly task!")

@app.function(schedule=modal.Period(minutes=30))
def run_every_30_min():
    print("Running every 30 minutes")

@app.function(schedule=modal.Period(days=1))
def run_daily():
    print("Running daily task!")

@app.function(schedule=modal.Period(seconds=60))
def run_every_minute():
    print("Running every minute")
```

### `modal.Cron` - Unix Cron Syntax

```python
# Run at midnight UTC every day
@app.function(schedule=modal.Cron("0 0 * * *"))
def midnight_task():
    print("It's midnight UTC!")

# Run every day at 6 AM New York time
@app.function(schedule=modal.Cron("0 6 * * *", timezone="America/New_York"))
def morning_report():
    print("Good morning! Sending daily report...")

# Run every Monday at 9 AM UTC
@app.function(schedule=modal.Cron("0 9 * * 1"))
def weekly_report():
    print("Running weekly Monday report")

# Run at 9 AM on the first day of every month
@app.function(schedule=modal.Cron("0 9 1 * *"))
def monthly_billing():
    print("Processing monthly billing")

# Run every 5 minutes
@app.function(schedule=modal.Cron("*/5 * * * *"))
def frequent_check():
    print("Checking every 5 minutes")
```

## Cron Syntax Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

### Common Cron Expressions

| Expression | Description |
|-----------|-------------|
| `* * * * *` | Every minute |
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour |
| `0 */6 * * *` | Every 6 hours |
| `0 0 * * *` | Daily at midnight UTC |
| `0 9 * * *` | Daily at 9 AM UTC |
| `0 9 * * 1` | Every Monday at 9 AM |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 0 1 * *` | First day of month |
| `0 0 1 1 *` | January 1st (yearly) |

## Period vs Cron: When to Use Each

| Feature | `modal.Period` | `modal.Cron` |
|---------|---------------|-------------|
| Syntax | Simple (hours, minutes, etc.) | Unix cron expression |
| Timezone support | No | Yes |
| Reset on redeploy | Yes (resets timer) | No (runs at scheduled time) |
| Best for | Simple intervals | Specific times, timezones |

> **Important:** `modal.Period` resets its timer on each deploy. If you redeploy mid-interval, the next run will be from the redeploy time. Use `modal.Cron` for time-sensitive schedules.

## Real-World Examples

### Daily Data Collection

```python
import modal

app = modal.App("daily-collector")
image = modal.Image.debian_slim().pip_install("requests", "pandas")

@app.function(
    image=image,
    schedule=modal.Cron("0 6 * * *"),  # 6 AM UTC daily
    secrets=[modal.Secret.from_name("api-credentials")],
    timeout=3600
)
def collect_daily_data():
    """Collect and store daily metrics."""
    import requests
    import os
    from datetime import datetime
    
    api_key = os.environ["API_KEY"]
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    response = requests.get(
        "https://api.example.com/metrics",
        headers={"Authorization": f"Bearer {api_key}"},
        params={"date": today}
    )
    
    data = response.json()
    print(f"Collected {len(data)} records for {today}")
    return data
```

### Weekly Report Email

```python
@app.function(
    image=image,
    schedule=modal.Cron("0 9 * * 1", timezone="America/New_York"),  # Monday 9 AM ET
    secrets=[modal.Secret.from_name("email-credentials")]
)
def send_weekly_report():
    """Send weekly metrics report every Monday."""
    import smtplib
    import os
    from email.message import EmailMessage
    
    # Gather data
    metrics = gather_weekly_metrics()
    
    # Send email
    msg = EmailMessage()
    msg["Subject"] = f"Weekly Report - {get_week_label()}"
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"] = os.environ["EMAIL_TO"]
    msg.set_content(format_report(metrics))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
        server.send_message(msg)
    
    print("Weekly report sent!")
```

### Hacker News Alerts (From Modal Examples)

```python
import modal
from datetime import datetime

app = modal.App("hackernews-alerts")
image = modal.Image.debian_slim().pip_install("requests")

@app.function(
    image=image,
    schedule=modal.Period(hours=1),
    secrets=[modal.Secret.from_name("slack-webhook")]
)
def check_hackernews():
    """Check Hacker News for interesting stories hourly."""
    import requests
    import os
    
    KEYWORDS = ["modal", "serverless", "GPU", "machine learning"]
    
    # Get top stories
    top_stories = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json"
    ).json()[:30]
    
    interesting = []
    for story_id in top_stories:
        story = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        ).json()
        
        title = story.get("title", "").lower()
        if any(kw.lower() in title for kw in KEYWORDS):
            interesting.append(story)
    
    if interesting:
        # Send Slack notification
        slack_url = os.environ["SLACK_WEBHOOK_URL"]
        message = "\n".join([
            f"• <{s['url']}|{s['title']}>" for s in interesting
        ])
        
        requests.post(slack_url, json={
            "text": f"*HN Stories matching your keywords:*\n{message}"
        })
        
        print(f"Found {len(interesting)} interesting stories")
```

### Database Backup

```python
@app.function(
    image=modal.Image.debian_slim().pip_install("psycopg2-binary", "boto3"),
    schedule=modal.Cron("0 2 * * *"),  # 2 AM daily
    secrets=[
        modal.Secret.from_name("postgres-credentials"),
        modal.Secret.from_name("aws-credentials")
    ],
    timeout=3600,
    volumes={"/backups": modal.Volume.from_name("db-backups")}
)
def backup_database():
    """Create and store database backup."""
    import os
    import subprocess
    from datetime import datetime
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/backups/backup_{timestamp}.sql"
    
    # Create backup
    subprocess.run([
        "pg_dump",
        "-h", os.environ["PGHOST"],
        "-U", os.environ["PGUSER"],
        "-d", os.environ["PGDATABASE"],
        "-f", backup_file
    ], env={**os.environ}, check=True)
    
    print(f"Backup created: {backup_file}")
    
    # Upload to S3
    import boto3
    s3 = boto3.client("s3")
    s3.upload_file(backup_file, "my-backups-bucket", f"db/{timestamp}.sql")
    
    print(f"Backup uploaded to S3")
```

### Model Retraining

```python
@app.function(
    image=ml_image,
    gpu="A100-80GB",
    schedule=modal.Cron("0 0 * * 0"),  # Every Sunday midnight
    secrets=[modal.Secret.from_name("training-secrets")],
    timeout=86400,  # 24 hours
    volumes={"/data": data_volume, "/models": model_volume}
)
def weekly_retrain():
    """Retrain model on fresh data every week."""
    from datetime import datetime
    
    print(f"Starting weekly retrain at {datetime.utcnow()}")
    
    # Load latest training data
    data = load_training_data("/data/training")
    
    # Train model
    model = train_model(data)
    
    # Save new version
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    model.save(f"/models/v_{timestamp}")
    
    model_volume.commit()
    print(f"Model retrained and saved: v_{timestamp}")
```

## Deploying Scheduled Functions

```bash
# Deploy (required for schedules to run)
modal deploy my_scheduler.py

# View scheduled function logs
modal app logs my-app

# Stop scheduled execution
modal app stop my-app
```

> **Note:** Scheduled functions only run when deployed with `modal deploy`. They do NOT run with `modal run` or `modal serve`.

## Monitoring Scheduled Runs

- View execution history in Modal dashboard
- Check logs: `modal app logs my-app`
- Set up alerting for failures using `retries` parameter:

```python
@app.function(
    schedule=modal.Cron("0 9 * * *"),
    retries=3,  # Retry up to 3 times on failure
    timeout=300
)
def reliable_daily_task():
    pass
```
