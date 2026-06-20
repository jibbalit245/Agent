# Replit Pricing

> Source: https://replit.com/pricing (403 Forbidden — content compiled from search results)
> Sources: search results from multiple pricing review sites, Replit blog posts
> Last updated: 2026-06

## Current Plans (as of 2026)

Replit underwent a major pricing overhaul in **February 2026** with the introduction of the Pro plan and retirement of the old Teams plan.

## Plan Overview

| Plan | Price | Target User |
|------|-------|-------------|
| **Starter** | Free | Learners, hobbyists |
| **Core** | $25/month ($20/month billed annually) | Individual developers |
| **Pro** | $100/month (up to 15 builders) | Small teams |
| **Enterprise** | Custom pricing | Organizations |

## Starter Plan (Free)

The Starter plan was launched in **December 2025**.

### Included:
- Access to Replit workspace
- Basic AI features
- Limited compute hours
- Public Repls
- Community access
- Limited Agent usage

### Limitations:
- Limited AI agent calls
- No private Repls (or very limited)
- No deployment credits included
- No collaborators

## Core Plan — $25/month

($20/month when billed annually = $240/year, saving ~20%)

### Included:
- **$25/month in usage credits** (covers AI, compute, and deployments)
- Access to latest AI models
- Smarter Agent capabilities
- Up to **5 collaborators**
- Unlimited workspaces
- Private Repls
- Full Agent access
- Autonomous long builds
- Ability to publish unlimited apps

### Usage Credits Details:
- Credits cover: AI Agent calls, Autoscale deployments, Reserved VMs, Object Storage, PostgreSQL, Data Transfer
- Credits expire at end of billing cycle (do NOT roll over on Core)
- Additional usage billed at standard rates

### Deployment Credits Estimate:
- Core's $25 credits can cover a small web app with light traffic
- A small app with light traffic: ~$5-10/month in deployment costs
- Always-on deployments (Reserved VM): $20+/month (may exceed credits)

## Pro Plan — $100/month

Launched **February 2026**, replaces the old Teams plan.

### Included:
- Up to **15 builders** (team members)
- More usage credits than Core (tiered credit discounts)
- **Credit rollover**: Unused credits roll over for one month
- Priority support
- Enhanced collaboration features
- Unified settings
- Per-workspace usage tracking
- Simplified sharing

### Notes:
- Old Teams plan customers automatically upgraded to Pro at no additional cost for remainder of subscription term (starting March 3, 2026)
- Previous Teams plan cost $40/user/month

## Enterprise Plan — Custom Pricing

Contact Replit directly for pricing.

### Features:
- **SSO (SAML)**: Integration with Okta, Azure AD, Google Workspace, OneLogin
- **SCIM Provisioning**: Automatic user provisioning/deprovisioning via identity provider
- **Role-based access control**: IDP groups for granular permissions
- **Audit logs**: Full visibility into workspace activity for compliance
- **Workspace Security Center**: CVE detection across dependencies
- **SBOM export**: Software Bill of Materials for compliance
- **Private deployments**: Mandate static security scans before publishing
- **SOC-2 compliant** platform
- **Dedicated Account Manager**: Assigned from day one
- **Self-serve setup**: Available without sales call
- Advanced security controls

### Available via:
- Microsoft Azure Marketplace
- Direct from Replit

## Deployment Pricing (Usage-Based)

Deployment costs are separate from (or covered by) plan credits.

### Compute Units

| Resource | Rate |
|----------|------|
| 1 CPU second | 18 Compute Units |
| 1 GB-second RAM | 2 Compute Units |
| 1 million Compute Units | $1.00 |

### Autoscale Deployments

| Item | Cost |
|------|------|
| Base fee | $1/month per deployment |
| Compute | $1 per million Compute Units |
| Data transfer | Additional per GB |

### Reserved VM Deployments

| Size | Approximate Monthly Cost |
|------|--------------------------|
| Shared / Nano (~0.25 vCPU, 256MB) | ~$5-7/month |
| Standard (~1 vCPU, 1GB) | ~$10/month |
| Standard 2x (~2 vCPU, 2GB) | ~$20/month |
| Performance (~4 vCPU, 4GB) | ~$40/month |

*Prices approximate — check Replit dashboard for current exact pricing*

### Static Deployments
- Cost: Data transfer only (very low)
- Best value deployment option

### Scheduled Deployments
- Billed: Compute Units per run
- Only charged while job is running

## Outbound Data Transfer

- Charged per GB transferred out of Replit's infrastructure
- Covered by plan credits up to credit limit
- Rate: Check current Replit pricing page

## AI Feature Pricing

AI Agent and Assistant usage consumes credits:
- Agent task complexity affects credit usage
- Heavy Agent use can exhaust monthly credits quickly
- Additional credits can be purchased beyond plan allotment

## Historical Pricing Changes

| Date | Change |
|------|--------|
| Feb 2025 | $1/month base fee added to Autoscale deployments |
| Dec 2025 | Free Starter plan launched |
| Feb 2026 | Pro plan launched; Teams plan retired; Core repriced |
| Feb 2026 | Core dropped from $25 to $20/month (when billed annually) |

## Cost Optimization Tips

1. **Use Static deployments** for frontend-only apps (cheapest option)
2. **Scale to zero** with Autoscale to avoid idle costs
3. **Right-size your VM**: Don't over-provision for Reserved VM
4. **Monitor credit usage**: Track AI and compute spending
5. **Annual billing**: Save ~20% on Core plan
6. **Use Replit DB** (free) instead of PostgreSQL for simple data storage

## Billing Management

- Add credit card in Account Settings → Billing
- View usage and bills in Account Settings → Usage
- Set spending limits (where available)
- Credits auto-renew monthly

## Free Alternatives Within Plans

Before incurring extra costs, use these free/included features:
- **Replit DB** (Key-Value Store): Free, 50 MiB per store
- **Static deployments**: Very low cost (data transfer only)
- **Workspace secrets**: Free, unlimited
- **Nix packages**: Free to use
