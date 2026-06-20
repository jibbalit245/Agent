# Replicate Billing & Pricing

> Source: https://replicate.com/docs/topics/billing
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official pricing data.

## Billing Model

Replicate is a **pay-as-you-go** platform. You are billed for the compute time used to run models. There are no subscription fees for basic API access.

## What Gets Billed

### Public Models (Serverless)
- Billed **only for active processing time**
- Setup time, queue time, and idle time are **free**
- Billing starts when the model begins processing your input
- Billing stops when the model produces output or errors

### Private Models & Deployments
- Billed for **all online time**: setup + idle + active processing
- Dedicated instances that stay warm cost more

### Official Models
- Priced by **predictable metrics** rather than raw compute time:
  - Number of output images
  - Seconds of video output
  - Number of input and output tokens
  - Processing time

## Hardware Pricing (Per Second)

These are the per-second rates for serverless compute on different hardware:

| Hardware | SKU | Price per Second | Price per Hour (approx) |
|----------|-----|-----------------|------------------------|
| CPU | `cpu` | $0.000100/sec | $0.36/hr |
| Nvidia T4 GPU | `gpu-t4-nano` | $0.000225/sec | $0.81/hr |
| Nvidia L40S GPU | `gpu-l40s-medium` | $0.000975/sec | $3.51/hr |
| Nvidia A100 (80GB) GPU | `gpu-a100-large` | $0.001400/sec | $5.04/hr |
| Nvidia H100 GPU | `gpu-h100-medium` | $0.001525/sec | $5.49/hr |

> **Note:** A40 GPUs are being migrated to L40S GPUs on Replicate. New models should use L40S.

## Billing Example

```
20-second inference on A100 (80GB):
20 seconds × $0.001400/sec = $0.028
```

```
60-second video generation on T4:
60 seconds × $0.000225/sec = $0.0135
```

## Free Tier

- New accounts receive a small amount of free compute credit
- Check your account at https://replicate.com/account for current free tier details

## Cost Calculation

Replicate bills based on `predict_time` from the prediction metrics (not total wall clock time):

```python
prediction = replicate.predictions.get("prediction_id")
predict_time = prediction.metrics.get("predict_time", 0)  # seconds
# Cost = predict_time × hardware_rate_per_second
```

## Official Model Pricing Examples

Some popular official models use simplified pricing:

| Model | Pricing Metric |
|-------|---------------|
| FLUX.1 schnell | Per output image |
| FLUX.1 dev | Per output image |
| Stable Diffusion | Per output image |
| Whisper (transcription) | Per second of audio |
| LLM models | Per input + output token |

## Deployments Pricing

Deployments maintain always-on instances:

- **Minimum instances**: Set min_instances to keep containers warm (billed continuously)
- **Scale-up**: Additional instances created on demand
- **Scale-down**: Configurable delay before scaling down (billing continues during idle)

```python
# A deployment with min_instances=1 bills continuously 24/7
# for the hardware cost of one instance
deployment_config = {
    "hardware": "gpu-a100-large",
    "min_instances": 1,          # Always-on, costs ~$5.04/hr continuously
    "max_instances": 5,          # Can scale up to 5 instances
    "scale_down_delay": 300      # Wait 5 min before scaling down
}
```

## Viewing Billing

- Dashboard: https://replicate.com/account/billing
- API usage history: https://replicate.com/account/usage
- Set up billing alerts in account settings

## Payment

- Credit card required for billing
- Bills processed monthly
- Usage visible in real-time on dashboard

## Cost Optimization Tips

1. **Use serverless** for intermittent workloads (only pay when running)
2. **Use sync mode** for latency-sensitive apps (faster due to pre-warmed instances)
3. **Choose appropriate hardware** - don't use A100 if T4 is sufficient
4. **Use `webhook_events_filter=["completed"]`** to minimize webhook overhead
5. **Cache results** - store outputs to avoid re-running identical predictions
6. **Cancel predictions** that are no longer needed:
   ```python
   prediction.cancel()
   ```
7. **Monitor via predictions list** to identify expensive or stuck predictions

## Budget Alerts

Configure spending limits in your account settings to prevent unexpected charges. You can set:
- Monthly spending limits
- Per-prediction cost alerts
- Email notifications when thresholds are reached
