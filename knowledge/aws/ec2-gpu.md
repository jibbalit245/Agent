# AWS EC2 GPU Instances for ML/AI
> Source: AWS EC2 documentation, nops.io, wring.co, thundercompute.com
> Fetched: 2026-06-20

## GPU Instance Families Overview

| Family | GPU Type | Primary Use | Notes |
|--------|---------|-------------|-------|
| P5 | NVIDIA H100 | Frontier model training | Most powerful; expensive |
| P4d / P4de | NVIDIA A100 | LLM training, fine-tuning | Sweet spot for large models |
| P3 | NVIDIA V100 | Legacy training | Older gen, still available |
| G6 | NVIDIA L4 | Inference, cost-optimized | New in 2024; best inference perf/$ |
| G5 | NVIDIA A10G | Inference, small training | Most versatile mid-tier |
| G4dn | NVIDIA T4 | Inference, transcoding | Cheapest GPU, good for batch |
| Inf2 | AWS Inferentia2 | Compiled model inference | Best cost for high-throughput |
| Trn1 | AWS Trainium | Training (AWS-native) | Cost-optimized training |

---

## P-Series (Training Workloads)

### P5 Family — NVIDIA H100 SXM

| Instance | GPUs | GPU Memory | vCPUs | RAM | ~On-Demand/hr | Spot ~$/hr |
|----------|------|-----------|-------|-----|----------------|------------|
| p5.48xlarge | 8x H100 80GB | 640 GB | 192 | 2 TB | ~$98.32 | ~$30–50 |
| p5e.48xlarge | 8x H100 80GB | 640 GB | 192 | 2 TB | ~$103.00 | ~$35–50 |
| p5en.48xlarge | 8x H100 94GB | 752 GB | 192 | 2 TB | ~$120+ | Limited |

**Note**: P5 pricing reduced up to 45% in June 2025.

### P4 Family — NVIDIA A100

| Instance | GPUs | GPU Memory | vCPUs | RAM | ~On-Demand/hr |
|----------|------|-----------|-------|-----|----------------|
| p4d.24xlarge | 8x A100 40GB | 320 GB | 96 | 1152 GB | ~$32.77 |
| p4de.24xlarge | 8x A100 80GB | 640 GB | 96 | 1152 GB | ~$40.97 |

**Note**: P4d/P4de pricing reduced up to 33% in June 2025.

### P3 Family — NVIDIA V100 (Legacy)

| Instance | GPUs | GPU Memory | vCPUs | RAM | ~On-Demand/hr |
|----------|------|-----------|-------|-----|----------------|
| p3.2xlarge | 1x V100 16GB | 16 GB | 8 | 61 GB | ~$3.06 |
| p3.8xlarge | 4x V100 64GB | 64 GB | 32 | 244 GB | ~$12.24 |
| p3.16xlarge | 8x V100 128GB | 128 GB | 64 | 488 GB | ~$24.48 |
| p3dn.24xlarge | 8x V100 256GB | 256 GB | 96 | 768 GB | ~$31.22 |

P3 uses older Volta architecture GPUs. Still good for training models that don't need H100/A100 features.

---

## G-Series (Inference Optimized)

### G6 Family — NVIDIA L4 (Inference Best Value)

| Instance | GPUs | GPU Memory | vCPUs | RAM | ~On-Demand/hr |
|----------|------|-----------|-------|-----|----------------|
| g6.xlarge | 1x L4 24GB | 24 GB | 4 | 16 GB | ~$0.85 |
| g6.2xlarge | 1x L4 24GB | 24 GB | 8 | 32 GB | ~$1.00 |
| g6.4xlarge | 1x L4 24GB | 24 GB | 16 | 64 GB | ~$1.68 |
| g6.8xlarge | 1x L4 24GB | 24 GB | 32 | 128 GB | ~$2.42 |
| g6.12xlarge | 4x L4 96GB | 96 GB | 48 | 192 GB | ~$5.67 |
| g6.16xlarge | 1x L4 24GB | 24 GB | 64 | 256 GB | ~$4.28 |
| g6.48xlarge | 8x L4 192GB | 192 GB | 192 | 768 GB | ~$13.35 |

G6 instances provide 2x inference performance vs G4dn at similar price points.

### G5 Family — NVIDIA A10G (Versatile)

| Instance | GPUs | GPU Memory | vCPUs | RAM | ~On-Demand/hr |
|----------|------|-----------|-------|-----|----------------|
| g5.xlarge | 1x A10G 24GB | 24 GB | 4 | 16 GB | ~$1.006 |
| g5.2xlarge | 1x A10G 24GB | 24 GB | 8 | 32 GB | ~$1.212 |
| g5.4xlarge | 1x A10G 24GB | 24 GB | 16 | 64 GB | ~$1.624 |
| g5.8xlarge | 1x A10G 24GB | 24 GB | 32 | 128 GB | ~$2.448 |
| g5.12xlarge | 4x A10G 96GB | 96 GB | 48 | 192 GB | ~$5.672 |
| g5.16xlarge | 1x A10G 24GB | 24 GB | 64 | 256 GB | ~$4.096 |
| g5.48xlarge | 8x A10G 192GB | 192 GB | 192 | 768 GB | ~$16.288 |

### G4dn Family — NVIDIA T4 (Budget Inference)

| Instance | GPUs | GPU Memory | vCPUs | RAM | ~On-Demand/hr |
|----------|------|-----------|-------|-----|----------------|
| g4dn.xlarge | 1x T4 16GB | 16 GB | 4 | 16 GB | ~$0.526 |
| g4dn.2xlarge | 1x T4 16GB | 16 GB | 8 | 32 GB | ~$0.752 |
| g4dn.4xlarge | 1x T4 16GB | 16 GB | 16 | 64 GB | ~$1.204 |
| g4dn.8xlarge | 1x T4 16GB | 16 GB | 32 | 128 GB | ~$2.264 |
| g4dn.12xlarge | 4x T4 64GB | 64 GB | 48 | 192 GB | ~$3.912 |
| g4dn.16xlarge | 1x T4 16GB | 16 GB | 64 | 256 GB | ~$4.528 |
| g4dn.metal | 8x T4 128GB | 128 GB | 96 | 384 GB | ~$7.824 |

---

## AWS-Native Accelerators

### Inf2 — AWS Inferentia2 (Best Cost for High-Throughput Inference)

| Instance | Accelerators | Accelerator Memory | vCPUs | RAM | ~$/hr |
|----------|-------------|-------------------|-------|-----|-------|
| inf2.xlarge | 1x Inferentia2 | 32 GB | 4 | 16 GB | ~$0.758 |
| inf2.8xlarge | 1x Inferentia2 | 32 GB | 32 | 128 GB | ~$1.968 |
| inf2.24xlarge | 6x Inferentia2 | 192 GB | 96 | 384 GB | ~$6.494 |
| inf2.48xlarge | 12x Inferentia2 | 384 GB | 192 | 768 GB | ~$12.987 |

**Requires**: Model compilation with AWS Neuron SDK. SageMaker JumpStart provides pre-compiled versions for popular models.

### Trn1 — AWS Trainium (Training)

| Instance | Accelerators | ~$/hr |
|----------|-------------|-------|
| trn1.2xlarge | 1x Trainium | ~$1.34 |
| trn1.32xlarge | 16x Trainium | ~$21.50 |
| trn1n.32xlarge | 16x Trainium | ~$24.78 |

---

## Deep Learning AMIs (DLAMI)

AWS provides pre-configured AMIs with CUDA, PyTorch, TensorFlow, and other ML libraries installed.

### DLAMI Types

1. **AWS Deep Learning AMI GPU PyTorch** — Latest PyTorch + CUDA (Ubuntu/Amazon Linux)
2. **AWS Deep Learning AMI GPU TensorFlow** — TensorFlow + CUDA
3. **AWS Deep Learning AMI (Conda)** — Multiple frameworks via conda environments
4. **AWS Deep Learning Containers (DLC)** — Docker images, used with ECS/EKS

### Finding DLAMIs

```bash
# Find latest PyTorch DLAMI
aws ec2 describe-images \
  --region us-east-1 \
  --owners amazon \
  --filters \
    "Name=name,Values=Deep Learning AMI GPU PyTorch*" \
    "Name=state,Values=available" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text
```

### Latest DLAMI Images (2025)

- **Deep Learning AMI GPU PyTorch 2.4** (Ubuntu 22.04): `ami-xxxxxxxxxxxxxxxxx`
- **Deep Learning AMI GPU PyTorch 2.6** (Amazon Linux 2023): Latest available

These include:
- CUDA 12.x (varies by AMI version)
- cuDNN
- PyTorch + TorchVision
- NCCL for multi-GPU communication
- Elastic Fabric Adapter (EFA) for multi-node
- AWS OFI NCCL plugin

### Supported Instance Types per DLAMI

```
G4dn, G5, G6, Gr6, P3, P4, P4de, P5, P5e, P5en
```

---

## Spot Instances for Training

Save 60-90% on GPU costs with spot instances.

### Requesting Spot

```python
import boto3

ec2 = boto3.client("ec2", region_name="us-east-1")

# Launch spot instance
response = ec2.run_instances(
    ImageId="ami-xxxx",  # DLAMI AMI ID
    InstanceType="p3.2xlarge",
    MinCount=1,
    MaxCount=1,
    KeyName="my-keypair",
    SecurityGroupIds=["sg-xxxx"],
    SubnetId="subnet-xxxx",
    
    # Spot options
    InstanceMarketOptions={
        "MarketType": "spot",
        "SpotOptions": {
            "MaxPrice": "2.00",  # Max spot price you'll pay
            "SpotInstanceType": "persistent",  # Or "one-time"
            "InstanceInterruptionBehavior": "terminate"  # Or "stop", "hibernate"
        }
    },
    
    # User data to run training script
    UserData="""#!/bin/bash
    source activate pytorch
    cd /home/ubuntu/training
    python train.py --checkpoint-dir /mnt/efs/checkpoints
    """,
    
    # EBS volume
    BlockDeviceMappings=[
        {
            "DeviceName": "/dev/xvda",
            "Ebs": {"VolumeSize": 100, "VolumeType": "gp3"}
        }
    ]
)
```

### Checkpoint Strategy for Spot

Spot instances can be interrupted with 2 minutes warning. Always checkpoint:

```python
import boto3
import signal
import sys

ec2 = boto3.client("ec2", region_name="us-east-1")

def check_spot_interruption():
    """Check if spot instance is being interrupted."""
    try:
        import urllib.request
        response = urllib.request.urlopen(
            "http://169.254.169.254/latest/meta-data/spot/termination-time",
            timeout=1
        )
        return True  # Termination notice found
    except:
        return False  # No interruption

# In your training loop
for epoch in range(num_epochs):
    for batch in dataloader:
        train_step(batch)
        
        if check_spot_interruption():
            print("Spot interruption detected! Saving checkpoint...")
            save_checkpoint(model, optimizer, epoch, batch_idx)
            sys.exit(0)
        
        if batch_idx % 100 == 0:
            save_checkpoint(model, optimizer, epoch, batch_idx)
```

---

## Model Sizing Guide (VRAM Requirements)

| Model Size | FP16 VRAM | INT8 VRAM | INT4 VRAM | Recommended Instance |
|-----------|-----------|-----------|-----------|---------------------|
| 7B params | ~14 GB | ~7 GB | ~4 GB | g4dn.xlarge (T4 16GB) |
| 13B params | ~26 GB | ~13 GB | ~7 GB | g5.2xlarge (A10G 24GB) |
| 30B params | ~60 GB | ~30 GB | ~15 GB | g5.12xlarge (4x A10G) |
| 70B params | ~140 GB | ~70 GB | ~35 GB | p4d.24xlarge (8x A100) |
| 180B params | ~360 GB | ~180 GB | ~90 GB | p5.48xlarge (8x H100) |

Rule of thumb: **~2 GB VRAM per 1B parameters at FP16**.

---

## Cost Optimization

1. **Use Spot for training** — 60-90% savings; implement checkpointing
2. **Choose instance by task**:
   - Inference → G4dn (cheapest), G6 (best perf/$)
   - Fine-tuning 7B-13B → G5
   - Training 70B+ → P4d or P5 Spot
3. **Use DLAMI** — Avoid spending hours configuring CUDA
4. **Stop instances when not training** — Stopped EBS-backed instances don't charge compute
5. **Use EFS for datasets** — Share large datasets across instances instead of duplicating on EBS
6. **Savings Plans** — 1-year compute savings plans give ~30-40% off

---

## Quotas

By default, new AWS accounts have very low GPU quotas (often 0 for P3/P4/P5).

```bash
# Check your current GPU quotas
aws service-quotas list-service-quotas \
  --service-code ec2 \
  --query 'Quotas[?contains(QuotaName, `Running On-Demand`) && contains(QuotaName, `instances`)].[QuotaName, Value]' \
  --output table \
  --region us-east-1
```

Request increases via the AWS Service Quotas console. Plan 1-5 business days for approval.
