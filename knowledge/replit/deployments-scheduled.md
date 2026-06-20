# Replit Scheduled Deployments

> Source: https://docs.replit.com/deployments/scheduled-deployments
> Updated URL: https://docs.replit.com/cloud-services/deployments/scheduled-deployments
> Last updated: 2026-06

## What are Scheduled Deployments?

Scheduled Deployments (also called **scheduled jobs**) allow you to run a command automatically on a defined schedule. The job runs in your Replit App's environment, completes its task, then terminates until the next scheduled run.

Think of them as **managed cron jobs** running in your Replit App's environment.

## Key Features

- **Natural language scheduling**: Enter a human-readable schedule description; AI converts it to a cron expression
- **Cron expression support**: Optionally enter the cron expression directly
- **Timezone support**: Select from a timezone dropdown
- **Managed infrastructure**: No server management required
- **Environment access**: Full access to your app's dependencies, files, and secrets

## Use Cases

Scheduled deployments work best for:
- ✅ Sending periodic notifications or emails
- ✅ Database backups and maintenance
- ✅ Status checks and health monitoring
- ✅ Data sync and ETL jobs
- ✅ Report generation
- ✅ Cache warming

NOT designed for:
- ❌ Continuous web applications
- ❌ Long-running services (use Reserved VM or Background Worker)
- ❌ Real-time event processing

## Limitations

| Constraint | Value |
|-----------|-------|
| **Maximum timeout** | 11 hours per job run |
| **Minimum interval** | 1 minute (cannot run more than once per minute) |

## How to Set Up

1. Open your Replit App
2. Click **Deploy**
3. Select **Scheduled** deployment type
4. Configure:
   - **Command**: The command to run (e.g., `python backup.py`)
   - **Schedule description**: Natural language (e.g., "Every Monday at 9 AM")
   - **Cron expression** (optional): Override with exact cron syntax
   - **Timezone**: Select from dropdown
   - **Deployment secrets**: Add production environment variables
5. Click **Deploy**

## Scheduling Options

### Natural Language

Enter plain English descriptions:
- "Every day at midnight"
- "Every Monday and Wednesday at 10 AM"
- "March 24th at 3 PM"
- "Every Tuesday and Thursday at 3:00 PM"
- "Every 5 minutes"
- "First day of every month at 9 AM"

The AI converts your description into a cron expression automatically.

### Cron Expression Format

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

**Common cron expressions:**
```
0 * * * *     # Every hour
0 0 * * *     # Every day at midnight
0 9 * * 1     # Every Monday at 9 AM
*/5 * * * *   # Every 5 minutes
0 0 1 * *     # First of every month at midnight
0 9 * * 1-5   # Weekdays at 9 AM
```

## Environment and Secrets

Scheduled jobs run in your app's full environment:
- Access to all installed packages
- Access to all files in your Repl
- Deployment secrets (added separately from workspace secrets)

Add deployment secrets:
1. Deployments → Secrets
2. Add production key-value pairs

## Example: Daily Database Backup

```python
# backup.py
import os
import datetime
import boto3  # or your storage client

def backup():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # ... backup logic ...
    print(f"Backup completed: {timestamp}")

if __name__ == '__main__':
    backup()
```

Schedule: "Every day at 2 AM"
Command: `python backup.py`

## Example: Weekly Report

```python
# weekly_report.py
import smtplib
from email.mime.text import MIMEText

def send_report():
    # Generate report data
    # Send email
    pass

if __name__ == '__main__':
    send_report()
```

Schedule: "Every Monday at 9 AM"
Command: `python weekly_report.py`

## Monitoring

- View job run history and logs in Deployments panel
- See last run time and next scheduled run
- Check exit codes and output

## Pricing

Scheduled deployments are billed by **Compute Units** consumed during each run:
- 1 CPU second = 18 Compute Units
- 1 GB-second RAM = 2 Compute Units
- $1 per million Compute Units

Cost is only incurred while the job is actively running. Idle time between runs costs nothing.
