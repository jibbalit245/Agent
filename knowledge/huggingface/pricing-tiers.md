# HuggingFace Pricing Tiers
> Sources: https://huggingface.co/pricing, https://huggingface.co/pro, https://huggingface.co/docs/hub/pro, https://huggingface.co/docs/hub/en/billing, https://github.com/huggingface/hub-docs/blob/main/docs/hub/storage-limits.md, https://huggingface.co/docs/inference-providers/pricing, WebSearch results 2026-06-20
> Fetched: 2026-06-20

---

## Account Tiers

### Free Tier — $0

**Who it's for:** Students, hobbyists, open-source contributors, experimentation

**Included:**
- Access to all public models, datasets, and Spaces
- Unlimited public repositories (best-effort storage, first few GB encouraged)
- 100 GB private repository storage
- Community features (discussions, likes, collections)
- Inference API (serverless) with rate limits
- ~$0.10/month inference credits for Inference Providers
- 5 minutes/day ZeroGPU quota (using others' ZeroGPU Spaces)
- CPU Basic Spaces (2 vCPU, 16 GB RAM) — free

**Limitations:**
- Rate limits on inference (low — a few hundred requests/hr on popular models)
- No ZeroGPU Space hosting (can use others' ZeroGPU Spaces)
- Spaces sleep after ~48hr inactivity
- Cannot create private Spaces (beyond 1)

---

### PRO Account — $9/month

**Who it's for:** Individual developers, researchers, power users

**Included (all Free features plus):**
- $2/month of inference provider credits included
- 8x more daily ZeroGPU quota (40 minutes/day vs 5 min/day)
- Can create and host your own ZeroGPU Spaces (up to 10)
- Higher rate limits on Inference API (~8x more)
- 1 TB private repository storage (vs 100 GB free)
- Up to 10 TB public storage
- Pay-as-you-go inference after credits exhausted
- ZeroGPU Dev Mode (live code editing in running Space)
- Ability to publish Social Posts and Community Blogs
- Data Studio on private datasets
- Custom domains for Spaces (PRO feature)
- Private model/dataset repositories (unlimited)

**ZeroGPU on PRO:**
- 40 min/day on RTX Pro 6000 Blackwell GPU
- Additional quota purchasable at $1 per 10 minutes
- Highest queue priority

---

### Team Plan — $20/user/month

**Who it's for:** Small to medium teams, companies with shared AI workflows

**Included (all PRO features plus):**
- Shared organization workspace
- SSO (Single Sign-On) support
- Audit logs for compliance
- 1 TB private storage per seat
- 12 TB base public storage + 1 TB per seat
- Shared compute budget across team
- Up to 50 ZeroGPU Spaces
- 40–45 min/day ZeroGPU quota per seat
- Centralized billing (one invoice)
- Custom organization domains
- Team collaboration tools

---

### Enterprise Hub — Starting $50/user/month

**Who it's for:** Large organizations, enterprises with compliance/security needs

**Included (all Team features plus):**
- 45–60 min/day ZeroGPU quota
- Up to 200 ZeroGPU Spaces (or more with custom contract)
- 200 TB base public storage + 1 TB per seat
- Up to 1,000 TB for large contracts
- 1 TB private storage per seat
- Highest rate limits on Inference API
- SAML SSO
- Dedicated support from HuggingFace experts
- Legal and compliance processes
- Managed billing with annual commitments
- Hardware Partner Program access
- Regional storage options (data sovereignty)
- Advanced security controls
- Custom SLAs

---

## Pricing Comparison Table

| Feature | Free | PRO ($9/mo) | Team ($20/user/mo) | Enterprise ($50+/user/mo) |
|---------|------|-------------|-------------------|--------------------------|
| Inference credits/mo | $0.10 | $2.00 | $2.00/seat | $2.00/seat |
| Rate limits | Low | 8x higher | Highest | Highest |
| Private storage | 100 GB | 1 TB | 1 TB/seat | 1 TB/seat |
| Public storage | Best-effort | Up to 10 TB | 12 TB + 1TB/seat | 200 TB + 1TB/seat |
| ZeroGPU quota | 5 min/day | 40 min/day | 40-45 min/day | 45-60 min/day |
| ZeroGPU hosting | No | Up to 10 Spaces | Up to 50 Spaces | 200+ Spaces |
| SSO/SAML | No | No | SSO | SAML + SSO |
| Audit logs | No | No | Yes | Yes |
| Dedicated support | No | No | No | Yes |
| Annual contracts | No | No | No | Yes |

---

## Inference Provider Pricing

When you exhaust monthly credits, you pay per use at provider rates.

**HuggingFace charges the same as the provider — no markup.**

### Monthly Included Credits
| Account | Monthly Credits |
|---------|----------------|
| Free | $0.10 |
| PRO | $2.00 |
| Team org | $2.00/seat |
| Enterprise org | $2.00/seat |

### How Billing Works
1. Each request uses credits based on: compute time × hardware cost
2. Credits are spent from the monthly allotment first
3. After credits exhausted: charges go to your payment method
4. PRO and Enterprise can enable pay-as-you-go
5. Track usage at: https://huggingface.co/settings/billing

### Billing to Organization
```python
from huggingface_hub import InferenceClient

# Bill this request to an org (useful for team accounts)
client = InferenceClient(
    provider="featherless-ai",
    api_key="hf_xxxxxxxxxxxxxxxx",
    bill_to="my-org-name",
)
```

Or via HTTP header:
```
X-HF-Bill-To: my-org-name
```

---

## Spaces Hardware Pricing

| Hardware | Price/hr | Notes |
|----------|----------|-------|
| CPU Basic | Free | 2 vCPU, 16 GB RAM; sleeps after 48hr |
| CPU Upgrade | ~$0.03/hr | 8 vCPU, 32 GB RAM; always on |
| T4-small | ~$0.40/hr | 1x T4, 16 GB VRAM |
| T4-medium | ~$0.60/hr | 1x T4, 16 GB VRAM |
| A10G-small | ~$1.00/hr | 1x A10G, 24 GB VRAM |
| A10G-large | ~$1.50/hr | 1x A10G, 24 GB VRAM |
| A100-large | ~$2.50–4.00/hr | 1x A100, 80 GB VRAM |
| ZeroGPU | Included (quota) | Shared; 5–60 min/day by tier |

**Monthly Spaces cost examples:**
- T4-small running 24/7: ~$288/month
- A10G-small running 24/7: ~$720/month
- ZeroGPU (PRO, 40 min/day): $9/mo subscription only

---

## Persistent Storage Pricing

Attached to Spaces or used as a volume for data persistence:

| Tier | Size | Price/month |
|------|------|-------------|
| Small | 20 GB | $5 |
| Medium | 150 GB | $25 |
| Large | 1 TB | $100 |

---

## Repository Storage Pricing

Extra storage beyond what's included in your plan:

| Tier | Rate |
|------|------|
| Private storage extra | $18/TB/month |
| Private storage (500TB+) | $12/TB/month (volume discount) |
| Public storage extra (small) | $12/TB/month |
| Public storage extra (50TB+) | $10/TB/month |

---

## Inference Endpoints Pricing (Dedicated)

Pay per minute of running time:

| Instance | Price/hr | Notes |
|----------|----------|-------|
| CPU small | ~$0.06 | 1 vCPU, 2 GB |
| CPU medium | ~$0.12 | 2 vCPU, 4 GB |
| NVIDIA T4 x1 | ~$0.50 | 14 GB VRAM |
| NVIDIA A10G x1 | ~$1.80 | 24 GB VRAM |
| NVIDIA A100 x1 | ~$4.00 | 80 GB VRAM |
| AWS Inferentia2 x1 | ~$0.75 | 32 GB accelerator memory |

Scale-to-zero endpoints don't bill when idle.

---

## Billing Page

Monitor all spending: **https://huggingface.co/settings/billing**

Shows:
- Monthly credit usage
- Pay-as-you-go charges
- Breakdown by model and provider
- Storage costs
- Space runtime costs

---

## References

- [HuggingFace Pricing Page](https://huggingface.co/pricing)
- [PRO Account Page](https://huggingface.co/pro)
- [Billing Documentation](https://huggingface.co/docs/hub/en/billing)
- [Inference Providers Pricing](https://huggingface.co/docs/inference-providers/pricing)
- [Inference Endpoints Pricing](https://huggingface.co/docs/inference-endpoints/pricing)
- [Storage Limits](https://huggingface.co/docs/hub/main/storage-limits)
