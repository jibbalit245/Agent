# RunPod GPU Pods — Types, Pricing, SSH, Storage
> Source: https://www.runpod.io/pricing, https://docs.runpod.io/pods/manage-pods, https://northflank.com/blog/runpod-gpu-pricing, https://computeprices.com/providers/runpod
> Fetched: 2026-06-20

## GPU Types and Pricing

Prices vary by cloud tier (Community vs Secure) and GPU availability. These are representative rates as of 2026.

### Consumer GPUs (Community Cloud only)

| GPU | VRAM | On-Demand | Spot | Best For |
|-----|------|-----------|------|----------|
| RTX 3090 | 24 GB | ~$0.19–0.34/hr | ~$0.10–0.15/hr | Small model inference, fine-tuning |
| RTX 3090 Ti | 24 GB | ~$0.22–0.39/hr | ~$0.12–0.17/hr | Same as 3090 |
| RTX 4090 | 24 GB | ~$0.34–0.69/hr | ~$0.19–0.35/hr | Fast inference, quantized models up to 24B |

### Professional GPUs

| GPU | VRAM | On-Demand (Community) | On-Demand (Secure) | Best For |
|-----|------|-----------------------|--------------------|----------|
| A100 PCIe 40GB | 40 GB | ~$0.89/hr | ~$1.39/hr | 13B–30B model training |
| A100 SXM 80GB | 80 GB | ~$1.49/hr | ~$1.89/hr | 30B–70B training, multi-GPU |
| H100 PCIe 80GB | 80 GB | ~$1.89/hr | ~$2.89/hr | Frontier model training |
| H100 SXM 80GB | 80 GB | ~$2.99/hr | ~$3.49/hr | Fastest H100, multi-GPU |
| RTX A6000 | 48 GB | ~$0.79/hr | N/A | Large inference, 34B models |
| L40S | 48 GB | ~$0.99/hr | ~$1.49/hr | Inference-optimized |
| L4 | 24 GB | ~$0.44/hr | ~$0.59/hr | Efficient inference |

**Note**: Community Cloud prices fluctuate with supply. Secure Cloud prices are more stable.

## Creating a Pod

### Via Web Console

1. Go to **Pods > Deploy**
2. Select your GPU model and count
3. Choose Community or Secure Cloud
4. Configure:
   - **Container Disk**: Ephemeral storage within the container (disappears on terminate) — typically 20–200 GB
   - **Volume Disk**: Persistent storage for this pod only (also disappears on terminate)
   - **Network Volume**: Persistent, survives pod deletion (Secure Cloud only)
5. Select a **Template** (pre-built Docker image) or enter a custom image
6. Set **Environment Variables**
7. Configure **Exposed Ports** (HTTP ports, TCP ports)
8. Click **Deploy**

### Via API / SDK

```python
import runpod

runpod.api_key = "your_runpod_api_key"

pod = runpod.create_pod(
    name="my-training-pod",
    image_name="runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
    gpu_type_id="NVIDIA GeForce RTX 4090",
    cloud_type="SECURE",           # "COMMUNITY" or "SECURE"
    gpu_count=1,
    volume_in_gb=50,               # Container disk size
    container_disk_in_gb=20,
    min_memory_in_gb=32,
    ports="8888/http,22/tcp",      # Exposed ports
    env={"MY_VAR": "value"},
    data_center_id="US-TX-3"       # Optional: specific datacenter
)

print(pod["id"], pod["desiredStatus"])
```

## SSH Access

Every pod gets a public SSH endpoint once running.

### Finding SSH details

In the console: Click on the pod > "Connect" button > copy the SSH command.

Format: `ssh root@{pod_ip} -p {port} -i ~/.ssh/id_rsa`

Or with password if no key configured.

### Adding SSH keys

Add public keys under **Settings > SSH Public Keys** in the console. Keys are injected into all pods at creation.

Via environment variable in Docker:
```bash
PUBLIC_KEY="ssh-rsa AAAA..."  # Set as env var when creating pod
```

The RunPod base images automatically add `PUBLIC_KEY` to `~/.ssh/authorized_keys`.

### Port forwarding for local development

```bash
# Forward Jupyter notebook to local port 8888
ssh -L 8888:localhost:8888 root@{pod_ip} -p {pod_port}

# Forward vscode-server
ssh -L 8080:localhost:8080 root@{pod_ip} -p {pod_port}
```

## HTTP Service Ports

Expose HTTP services from your pod:

- In console, set ports as `8080/http`, `7860/http` etc.
- RunPod provides a public HTTPS URL: `https://{pod_id}-{port}.proxy.runpod.net`
- TCP ports are also available for raw connections: `{pod_ip}:{external_port}`

Example use cases:
- `7860/http` — Gradio apps
- `8888/http` — Jupyter notebooks
- `11434/http` — Ollama
- `8000/http` — FastAPI inference server

## Persistent Storage: Network Volumes

Network Volumes are the primary mechanism for data that outlives a pod.

### Key properties

- **Persists** independently of pods — not deleted when pod is terminated
- **Secure Cloud only** — not available in Community Cloud
- **Location-bound** — volumes are tied to a specific datacenter; pod must be in same DC
- **NVMe-backed** — 200–400 MB/s typical, up to 10 GB/s peak
- **Pricing**: Standard ~$0.07/GB/month; High-performance ~$0.20/GB/month
- **Cannot be attached/detached** after pod creation — must be set at deployment time

### Creating a Network Volume

Via console: **Storage > Network Volumes > Create Volume**

Via API:
```python
volume = runpod.create_network_volume(
    name="model-weights",
    size=100,  # GB
    data_center_id="US-TX-3"
)
```

### Attaching to a pod

```python
pod = runpod.create_pod(
    name="my-pod",
    image_name="runpod/pytorch:latest",
    gpu_type_id="NVIDIA A100 80GB PCIe",
    cloud_type="SECURE",
    volume_mount_path="/workspace",  # Where volume is mounted
    network_volume_id=volume["id"],
    # ...
)
```

The volume is accessible at `/workspace` inside the pod. Models, datasets, and checkpoints saved there survive pod termination.

### Verifying mount

```bash
df -h          # Should show /workspace with your volume size
ls /workspace  # Your persisted files
```

## Pod Templates

Templates are pre-configured pod setups combining a Docker image, default disk sizes, environment variables, and port configurations.

### Popular official templates

| Template | Image | Use Case |
|----------|-------|----------|
| RunPod PyTorch | runpod/pytorch:2.4.0-py3.11-cuda12.4.1 | General ML dev |
| RunPod TensorFlow | runpod/tensorflow | TF workloads |
| Stable Diffusion WebUI | auto1111/stable-diffusion-webui | Image generation |
| Jupyter Notebook | jupyter/base-notebook | Interactive notebooks |
| Ollama | ollama/ollama | Local LLM serving |

### Custom templates

Create your own template from any Docker image + configuration. Templates can be saved and reused or shared with teams.

## Managing Pods

```python
import runpod

# List all pods
pods = runpod.get_pods()

# Get pod status
pod = runpod.get_pod(pod_id="abc123")
print(pod["desiredStatus"], pod["runtime"]["uptimeInSeconds"])

# Stop a pod (preserves container disk, cheaper than running)
runpod.stop_pod(pod_id="abc123")

# Resume a stopped pod
runpod.resume_pod(pod_id="abc123", gpu_count=1)

# Terminate a pod (deletes container disk; network volume survives)
runpod.terminate_pod(pod_id="abc123")
```
