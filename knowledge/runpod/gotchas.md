# RunPod Common Gotchas and Pitfalls
> Source: https://docs.runpod.io/pods/manage-pods, https://www.runpod.io/articles/guides/docker-setup-pytorch-cuda-12-8-python-3-11, https://deepwiki.com/runpod/docs/3.1-pod-creation-and-configuration, https://www.runpod.io/articles/guides/deploy-vllm-runpod-docker
> Fetched: 2026-06-20

## 1. Spot Pod Termination

**What happens**: Spot (interruptible) pods can be reclaimed by RunPod with only a ~5-second SIGTERM warning when the host machine needs resources. Your process receives SIGTERM and then SIGKILL.

**Symptoms**: Pod disappears from console mid-job; any unsaved work in the container is lost.

**Mitigations**:
- Save checkpoints frequently to a **Network Volume** (Secure Cloud) or external storage (S3, HuggingFace Hub)
- Implement a SIGTERM handler in training code:
  ```python
  import signal
  import sys

  def sigterm_handler(signum, frame):
      print("Received SIGTERM — saving checkpoint before exit")
      save_checkpoint(model, optimizer, step)
      sys.exit(0)

  signal.signal(signal.SIGTERM, sigterm_handler)
  ```
- Use **On-Demand pods** for critical workloads that cannot tolerate interruption
- Design training loops to resume from checkpoint automatically

## 2. Network Volume Mounting Issues

**Issue 1: Volume not appearing in pod**

Cause: Volume and pod are in different datacenters.

Fix: When creating the pod, specify `data_center_id` matching where the volume was created.

```python
# Volume creation
volume = runpod.create_network_volume(
    name="models",
    size=100,
    data_center_id="US-TX-3"  # Remember this
)

# Pod creation — must match
pod = runpod.create_pod(
    data_center_id="US-TX-3",  # Same datacenter
    network_volume_id=volume["id"],
    volume_mount_path="/workspace",
    ...
)
```

**Issue 2: Cannot attach volume after pod creation**

Network volumes cannot be attached or detached from a running pod. You must terminate the pod and create a new one with the volume attached.

**Issue 3: Volume not at expected path**

Verify with: `df -h` and `ls /workspace`. If empty, the volume may not have been attached correctly (see Issue 1).

**Issue 4: Volume full**

```bash
df -h /workspace   # Check usage
du -sh /workspace/* | sort -rh | head -20  # Find large files
```

## 3. Port Configuration

**Issue: 502/503 errors when accessing HTTP services**

Common causes and fixes:

```
# Wrong: Your app listens on 127.0.0.1 (loopback only)
app.run(host="127.0.0.1", port=7860)

# Right: Listen on all interfaces
app.run(host="0.0.0.0", port=7860)
```

- The port must be listed in the pod's exposed HTTP ports at creation time (e.g., `7860/http`)
- After exposing a port, the RunPod URL is: `https://{pod_id}-7860.proxy.runpod.net`
- Services can take 30–60 seconds to start; 502 errors early are normal — wait and refresh

**Issue: SSH not available**

Ensure `22/tcp` is in your exposed port list at creation time. You cannot add ports after pod creation without terminating and recreating.

## 4. Docker Image Requirements

**Issue: "OCI runtime create failed" or container won't start**

Common causes:
- **Wrong architecture**: RunPod runs on x86_64 (amd64). ARM images will fail. Build with:
  ```bash
  docker buildx build --platform linux/amd64 -t myimage:latest .
  ```
- **CUDA mismatch**: Image requires CUDA 12.x but GPU host has CUDA 11.x drivers (or vice versa). Use RunPod's GPU filter: **Additional Filters > CUDA Versions**.
- **No entrypoint/CMD**: Container exits immediately. Ensure your Dockerfile has a long-running process.

**Issue: Container builds but model won't load**

- Insufficient GPU memory: Check model VRAM requirements vs GPU VRAM. A 7B FP16 model needs ~14 GB VRAM.
- Wrong CUDA device: Try setting `CUDA_VISIBLE_DEVICES=0` explicitly.

**Recommended base images** (well-tested on RunPod):

```dockerfile
# PyTorch + CUDA 12.4
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# PyTorch + CUDA 12.8 + Python 3.11
FROM runpod/pytorch:2.6.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04

# Minimal RunPod base
FROM runpod/base:0.6.2-cuda12.4.1
```

## 5. CUDA Version Compatibility

**Issue: `CUDA error: no kernel image is available for execution on the device`**

Your PyTorch (or other library) was compiled for a different CUDA compute capability than the GPU you're running on.

**Fix**: Match the CUDA version in your Docker image to the GPU's driver CUDA version. Use the RunPod console filter "CUDA Versions" when selecting pods.

**Issue: `libcuda.so.1: cannot open shared object file`**

The container is missing CUDA runtime. Use NVIDIA CUDA base images or RunPod's pre-built images.

**CUDA version matrix** (approximate):
| NVIDIA Driver | Max CUDA Version |
|---------------|-----------------|
| 525.x | CUDA 12.0 |
| 535.x | CUDA 12.2 |
| 545.x | CUDA 12.3 |
| 550.x | CUDA 12.4 |
| 560.x | CUDA 12.6 |
| 570.x+ | CUDA 12.8+ |

## 6. Multi-GPU Issues with vLLM / Tensor Parallelism

**Issue: vLLM tensor parallelism fails at worker initialization**

Fix: Set this environment variable:
```bash
VLLM_WORKER_MULTIPROC_METHOD=spawn
```

Without it, tensor parallelism across multiple GPUs fails on some CUDA configurations.

```dockerfile
ENV VLLM_WORKER_MULTIPROC_METHOD=spawn
```

Or at runtime:
```python
import os
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "spawn"
```

## 7. Billing Surprises

**Issue: Unexpected charges for stopped (not terminated) pods**

Stopped pods still charge for:
- Container disk storage (at storage rate, not GPU rate)
- GPU is released when stopped, so GPU charges stop
- Restart them to continue, or **terminate** to stop all charges

**Issue: Network Volume charges accumulating**

Network volumes charge per GB per month even when no pod is attached. Delete volumes you no longer need:

```python
runpod.delete_network_volume(volume_id="vol_abc123")
```

**Issue: Serverless workers billing when no jobs**

If Min Workers > 0, you pay for those workers 24/7. Set Min Workers = 0 for true pay-per-request.

## 8. Serverless Cold Starts Longer Than Expected

**Issue: First request after idle takes 60+ seconds**

Causes:
- Large Docker image being pulled (mitigate with smaller images or FlashBoot)
- Model being downloaded from HuggingFace Hub at startup (bake model into image instead)
- Image not in FlashBoot cache

**Bake model into image to eliminate download time**:

```dockerfile
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN pip install transformers huggingface_hub

# Download model at build time
RUN python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; \
    AutoTokenizer.from_pretrained('mistralai/Mistral-7B-Instruct-v0.3'); \
    AutoModelForCausalLM.from_pretrained('mistralai/Mistral-7B-Instruct-v0.3')"

COPY handler.py /
CMD ["python", "-u", "/handler.py"]
```

Note: This creates a large image. Build times are long but cold starts are fast.

## 9. Serverless Job Timeouts

**Issue: Jobs timing out before completing**

Every serverless endpoint has an **Execution Timeout** (max seconds per job). Default is often 60–120 seconds.

Fix in endpoint settings: Set **Execution Timeout** to match your P99 inference latency + buffer.

Also set `timeout` when calling from client:
```python
output = endpoint.run_sync(input_data, timeout=300)
```

## 10. Authentication Issues with Private Docker Images

**Issue: Pod fails to pull image from private registry**

RunPod supports Docker Hub, GitHub Container Registry (GHCR), and others. Provide credentials:

In pod template or creation, specify:
- **Container Registry Auth**: base64-encoded Docker credentials
- Or push to Docker Hub public repo to avoid auth entirely for testing

```bash
# Generate auth string for RunPod
echo -n '{"username":"myuser","password":"mypassword"}' | base64
```
