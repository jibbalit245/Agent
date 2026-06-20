# Replit Custom Domains

> Source: https://docs.replit.com/deployments/custom-domains
> Updated URL: https://docs.replit.com/build/add-custom-domain
> Last updated: 2026-06

## Overview

All Replit deployment types support custom domains. Instead of the default `appname.replit.app` URL, you can use your own domain (e.g., `www.myapp.com`).

Replit automatically provisions **TLS/SSL certificates** for custom domains.

## Supported Deployment Types

Custom domains work with:
- Autoscale deployments
- Reserved VM deployments
- Static deployments

## Setup Process

### Step 1: Add Domain in Replit

1. Go to your Replit App
2. Click the **Deployments** tab
3. Go to **Settings**
4. Click **Link a domain** (or "Add custom domain")
5. Enter your domain name (e.g., `www.example.com` or `example.com`)
6. Click **Add** / **Continue**

### Step 2: Get DNS Records

Replit will display DNS records you need to add:

**A Record** (for root domains):
```
Type: A
Name: @  (or your subdomain)
Value: [Replit's IP address]
TTL: 3600 (or Auto)
```

**CNAME Record** (for subdomains, preferred):
```
Type: CNAME
Name: www  (or your subdomain)
Value: [your-app].replit.app
TTL: 3600 (or Auto)
```

**TXT Record** (for domain verification):
```
Type: TXT
Name: @  (or as specified)
Value: replit-verify=[verification-code]
TTL: 3600
```

### Step 3: Add DNS Records at Your Registrar

Go to your domain registrar's DNS management:

**Namecheap:**
1. Domain List → Manage → Advanced DNS
2. Add records

**GoDaddy:**
1. My Products → DNS
2. Add records

**Cloudflare:**
1. Select domain → DNS → Add record
2. Note: Set proxy status to **DNS only** (grey cloud), not proxied

**Google Domains / Squarespace:**
1. DNS → Manage custom records

### Step 4: Wait for Propagation

DNS changes can take:
- **Minutes**: Often propagates quickly
- **Up to 48 hours**: Full global propagation in worst case
- **Typical**: 15 minutes to a few hours

### Step 5: TLS Certificate Auto-Provisioned

Once DNS propagates, Replit automatically:
- Verifies domain ownership via TXT record
- Provisions a TLS/SSL certificate (via Let's Encrypt or similar)
- Enables HTTPS on your custom domain

No manual certificate management needed.

## Domain Types

### Root Domain (Apex Domain)

```
example.com
```

Use an A record pointing to Replit's IP:
```
Type: A
Name: @
Value: [Replit IP]
```

Some DNS providers support ALIAS or ANAME records as an alternative to A records for apex domains.

### Subdomain

```
www.example.com
app.example.com
api.example.com
```

Use a CNAME record:
```
Type: CNAME
Name: www (or app, api, etc.)
Value: your-app-name.replit.app
```

### Recommended: Use www Subdomain

Best practice is to use `www.example.com` with CNAME and redirect `example.com` to `www`:
1. Set CNAME for `www` → `your-app.replit.app`
2. Set up redirect at registrar: `example.com` → `www.example.com`

## Cloudflare Configuration

If using Cloudflare for DNS:

1. **Disable proxy** (orange cloud → grey cloud) for the Replit records
   - Replit needs direct DNS resolution
   - Proxy mode can interfere with Replit's TLS provisioning

2. Or use Full (Strict) SSL mode if keeping proxy enabled

**Cloudflare DNS records:**
```
Type: CNAME
Name: www
Target: your-app.replit.app
Proxy status: DNS only (grey cloud)
```

## Multiple Domains

You can link multiple custom domains to the same deployment:
1. Repeat the Add Domain process for each domain
2. All domains point to the same app
3. Each gets its own TLS certificate

## Removing a Custom Domain

1. Deployments → Settings → Custom Domains
2. Click the domain you want to remove
3. Click **Remove** or **Unlink**
4. Remove the DNS records from your registrar

## Troubleshooting

### Domain Not Resolving

- Wait for DNS propagation (up to 48 hours)
- Verify DNS records are correct using: `dig www.example.com`
- Check that A/CNAME records point to the correct values

### Certificate Not Provisioning

- Ensure TXT verification record is set correctly
- Make sure domain resolves to Replit's server (not Cloudflare proxy)
- Contact Replit support if it persists after 24 hours

### SSL/TLS Errors

- Wait for certificate provisioning to complete
- Disable Cloudflare proxy if enabled
- Verify the domain is correctly linked in Replit dashboard

### Testing DNS

```bash
# Check A record
dig example.com A

# Check CNAME
dig www.example.com CNAME

# Check TXT
dig example.com TXT

# Or use online tools:
# https://www.whatsmydns.net/
# https://dnschecker.org/
```

## Pricing

Custom domains are included with all deployment types. No additional cost beyond the deployment itself.

You need to purchase your domain from a registrar separately:
- Namecheap (~$10-15/year)
- GoDaddy
- Google Domains / Squarespace
- Cloudflare Registrar (cost price)
