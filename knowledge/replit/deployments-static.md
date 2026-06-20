# Replit Static Deployments

> Source: https://docs.replit.com/deployments/static-deployments
> Updated URL: https://docs.replit.com/cloud-services/deployments/static-deployments
> Last updated: 2026-06

## What are Static Deployments?

Static Deployments serve **HTML, CSS, and JavaScript files** from a CDN (Content Delivery Network) with automatic caching and TLS certificates. They are the most cost-effective option for websites that don't require a backend server.

Static deployments are ideal for:
- Marketing/landing pages
- Documentation sites
- Single-page applications (React, Vue, Angular builds)
- Portfolio sites
- Any pre-built static content

## Key Features

- **CDN delivery**: Files served from distributed locations for faster load times globally
- **Automatic caching**: Content cached at the edge for performance
- **TLS certificates**: Automatic HTTPS provisioning
- **Custom domains**: Bring your own domain
- **HTTP routing**: Configure response headers, URL rewrites, and redirects
- **Custom error pages**: Configure 404 and other error pages
- **No server costs**: Pay only for data transfer

## How to Deploy

1. Build your static site (run build command: `npm run build`, etc.)
2. Open your Replit App
3. Click **Deploy**
4. Select **Static** deployment type
5. Configure:
   - **Output directory**: Where your built files live (e.g., `dist/`, `build/`, `public/`)
   - **Build command** (optional): Command to build your site
   - Custom domain (optional)
6. Click **Deploy**

Your site will be live at `appname.replit.app`.

## Configuration Options

### Output Directory
Point to where your built HTML/CSS/JS files are located:
- React (CRA): `build/`
- Vite: `dist/`
- Next.js static export: `out/`
- Plain HTML: root `/` or `public/`

### Build Command
Run a build step before deploying:
```bash
npm run build
# or
vite build
# or
hugo
```

### URL Rewrites and Redirects

Configure routing behavior in your `.replit` file or through the deployment settings:
- **Rewrites**: Serve a different file for a URL (e.g., SPA routing)
- **Redirects**: HTTP redirect to a different URL
- **Custom headers**: Set response headers (Cache-Control, security headers, etc.)

### SPA Routing (Single Page Applications)

For React/Vue/Angular apps with client-side routing, configure a catch-all rewrite to serve `index.html` for all routes:

```toml
# In .replit or deployment settings
[[static.routes]]
path = "/*"
serve = "/index.html"
```

## Pricing

Static deployments are the cheapest option:
- Pay **only for data transfer** (bandwidth)
- No compute costs
- Very low cost for most sites
- Core plan credits can cover most static site hosting

## Custom Domains

1. Go to Deployments → Settings → **Link a domain**
2. Enter your domain name (e.g., `www.example.com`)
3. Copy DNS records from Replit:
   - **A record**: Points to Replit's IP address
   - **TXT record**: For domain verification
4. Add records at your DNS registrar (Namecheap, GoDaddy, Cloudflare, etc.)
5. Wait for DNS propagation (minutes to 48 hours)
6. TLS/SSL certificate automatically provisioned

## CDN and Caching

- Files are distributed to CDN edge nodes globally
- Automatic cache invalidation on redeploy
- Configure `Cache-Control` headers for fine-grained control

## Limitations

- No server-side code execution
- No server-side rendering (use Autoscale for SSR)
- Cannot run Node.js/Python/etc. server processes
- Dynamic data requires external APIs or serverless functions

## Comparison with Other Deployment Types

| Feature | Static | Autoscale | Reserved VM |
|---------|--------|-----------|-------------|
| Server code | No | Yes | Yes |
| Cost | Data transfer only | Compute Units | Fixed monthly |
| CDN | Yes | No | No |
| Cold starts | N/A | Possible | No |
| Best for | Static sites | Web apps/APIs | Always-on apps |

## Example: Deploying a React App

```bash
# 1. Build the app
npm run build
# Creates build/ directory

# 2. In Replit Deploy panel:
# - Output directory: build
# - Build command: npm run build
# - Click Deploy
```

## Example: Deploying a Vite App

```bash
# Build creates dist/
npm run build

# In Replit Deploy panel:
# - Output directory: dist
# - Build command: npm run build
```
