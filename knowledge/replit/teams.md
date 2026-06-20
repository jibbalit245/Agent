# Replit Teams and Collaboration

> Source: https://docs.replit.com/teams/teams-intro
> Updated URL: https://docs.replit.com/category/teams
> Last updated: 2026-06

## Overview

Replit's team and collaboration features allow multiple developers to work together on Replit Apps. As of **February 2026**, the old Teams plan was retired and replaced with the **Pro plan**, which includes team collaboration features.

## Collaboration Tiers

| Plan | Collaborators | Price |
|------|--------------|-------|
| Starter (Free) | None | Free |
| Core | Up to 5 | $25/month |
| Pro | Up to 15 builders | $100/month |
| Enterprise | Unlimited | Custom |

## Core Plan Collaboration (5 Collaborators)

Core plan now includes collaborators — previously a Teams-only feature.

### Features:
- Share Repls with up to 5 collaborators
- Real-time multiplayer editing
- Collaborative debugging
- Shared workspace environment

## Pro Plan (Teams Replacement)

Launched **February 2026**, the Pro plan is designed for small-to-medium development teams.

### Price: $100/month

### Includes:
- Up to **15 builders** (team members)
- More usage credits than Core
- **Credit rollover**: Unused credits carry forward one month
- Priority support
- Enhanced collaboration features:
  - Unified settings across team
  - Per-workspace usage tracking
  - Simplified sharing workflows
- Tiered credit discounts

### Migration from Teams:
- Old Teams plan customers automatically upgraded to Pro
- No additional cost for remainder of subscription term
- Upgrade started rolling out March 3, 2026

## Enterprise Plan Collaboration

For organizations needing advanced controls.

### Authentication & User Management:
- **SSO/SAML** integration: Okta, Azure AD, Google Workspace, OneLogin
- **SCIM Provisioning**: Auto-provision/deprovision users via identity provider
- **Role-based access control**: IDP groups for granular permissions

### Security & Compliance:
- Audit logs for all workspace activity
- SOC-2 compliant platform
- Workspace Security Center (CVE detection)
- SBOM (Software Bill of Materials) export
- Mandate private deployments
- Static security scans before publishing

### Support:
- Dedicated Account Manager from day one
- Self-serve setup (faster than traditional sales process)

## Real-Time Collaboration (Multiplayer)

All paid plans include **multiplayer mode**:
- Multiple users edit the same Repl simultaneously
- See each other's cursors and changes in real-time
- Collaborative debugging
- Shared terminal/shell sessions

### How to Invite Collaborators:

1. Open your Replit App
2. Click the **Share** button (or invite icon)
3. Enter collaborator's email or Replit username
4. Select permission level (view/edit)
5. Send invitation

Collaborators receive an email with a link to join.

## Workspace Sharing

### Types of Access:

| Level | Can View | Can Edit | Can Deploy |
|-------|---------|---------|-----------|
| View | ✅ | ❌ | ❌ |
| Edit | ✅ | ✅ | Depends |
| Owner | ✅ | ✅ | ✅ |

### Public vs. Private Repls:
- **Public Repls**: Anyone can view, only collaborators can edit
- **Private Repls**: Only invited collaborators can view/edit (requires paid plan)

## Team Workflows

### Typical Team Setup:

1. **Create organization workspace** (Pro/Enterprise)
2. **Invite team members**
3. **Create shared Repls** for projects
4. **Set up deployment environments** with appropriate secrets
5. **Use GitHub integration** for source control

### GitHub Integration:

Teams can use GitHub for source control alongside Replit:
1. Import repositories from GitHub
2. Make changes in Replit
3. Push back to GitHub
4. Use GitHub Actions/CI alongside Replit deployments

```bash
# In Replit Shell
git clone https://github.com/your-org/your-repo
git add .
git commit -m "Changes from Replit"
git push origin main
```

## Education Features (Teams for Education)

Replit has separate education-focused features:
- Classroom management for teachers
- Assignment creation and distribution
- Student submission tracking
- Code review tools

Note: Education features are distinct from the Pro team features.

## Usage Tracking

Pro/Enterprise plans include **per-workspace usage tracking**:
- Monitor AI credit consumption per workspace
- Track compute usage by team member
- Identify cost centers
- Set budgets (where available)

## Enterprise Self-Serve

Replit Enterprise is now self-serve:
1. Go to replit.com/enterprise
2. Sign up for Enterprise
3. Configure SSO/SCIM
4. Invite team members
5. Assigned dedicated Account Manager from day one

Self-serve setup is faster than traditional enterprise sales processes.

## Microsoft Azure Marketplace

Replit Enterprise is available through the **Microsoft Azure Marketplace**:
- Simplified billing through Azure
- Enterprise procurement compliance
- Available at: marketplace.microsoft.com

## Replit's Partnership with Visa

Replit has expanded enterprise leadership with a **Visa investment and partnership** (announced 2025/2026), including:
- Payments expansion capabilities
- Solution Partner Program
- Enhanced enterprise features

## Migration Guide (Teams → Pro)

If you were on the old Teams plan:

1. **Automatic upgrade**: All Teams customers automatically moved to Pro
2. **No action required**: Your subscription continues
3. **Same or better features**: Pro includes everything Teams had
4. **Pricing**: No additional cost for the remainder of your term
5. **Billing**: After current term, you'll be billed at Pro rates ($100/month)

## FAQ

**Q: What happened to the Teams plan?**
A: It was retired in February 2026 and replaced by the Pro plan, which offers similar features at a team-focused price point.

**Q: Can I collaborate for free?**
A: Free Starter plan has limited collaboration. Core plan allows up to 5 collaborators for $25/month.

**Q: How does real-time collaboration work?**
A: Multiple users can simultaneously edit files in the same Repl, similar to Google Docs for code.

**Q: Can team members have different permission levels?**
A: Yes — view-only or edit access can be granted per collaborator.
