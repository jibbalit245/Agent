# Vertex AI - Introduction to the Unified Platform

> Source: https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content sourced from Vertex AI Python SDK (github.com/googleapis/python-aiplatform) and PyPI documentation.
> Fetched: 2026-06-20

## Overview

Vertex AI is Google Cloud's **fully managed, end-to-end platform for data science and machine learning**. It provides integrated tools for building, deploying, and managing ML models using both AutoML and custom code approaches.

The platform unifies disparate ML tools and workflows under a single interface, enabling data scientists and ML engineers to:

- Build and train ML models at scale
- Deploy models to production with managed endpoints
- Run batch prediction jobs
- Access state-of-the-art generative AI models (Gemini family)
- Manage datasets, experiments, and pipelines
- Monitor model performance in production

## Key Components

### 1. Generative AI
- **Gemini Models**: Access Google's most capable multimodal models (text, image, video, audio)
- **Model Garden**: Explore and deploy models from Google and third parties
- **Agent Engine**: Build and deploy AI agents with tools
- **Prompt Management**: Create, version, and optimize prompts

### 2. ML Platform
- **Datasets**: Managed datasets for tabular, image, text, and video data
- **Training**: Custom training jobs and AutoML
- **Models**: Model registry and versioning
- **Endpoints**: Online prediction serving
- **Batch Prediction**: Large-scale offline prediction

### 3. MLOps
- **Pipelines**: Orchestrate ML workflows with Kubeflow or TFX
- **Experiments**: Track and compare model runs
- **Model Monitoring**: Detect data drift and model degradation
- **Feature Store**: Centralized feature storage and serving

## Supported Regions

Vertex AI is available in multiple regions globally. Key regions include:
- `us-central1` (Iowa) - default/recommended
- `us-east1`, `us-east4`, `us-west1`, `us-west4`
- `europe-west1`, `europe-west2`, `europe-west4`
- `asia-east1`, `asia-northeast1`, `asia-southeast1`
- `australia-southeast1`

## Quick Start

### Prerequisites
1. Create or select a Google Cloud project
2. Enable billing
3. Enable the Vertex AI API: `gcloud services enable aiplatform.googleapis.com`
4. Set up authentication (ADC or service account)

### Python SDK Installation

```bash
pip install google-cloud-aiplatform
```

### SDK Initialization

```python
from google.cloud import aiplatform

aiplatform.init(
    project='my-project',
    location='us-central1',
    staging_bucket='gs://my_staging_bucket',
    credentials=my_credentials,           # Optional: explicit credentials
    encryption_spec_key_name=my_key,      # Optional: CMEK key
    experiment='my-experiment',           # Optional: experiment tracking
    experiment_description='description'  # Optional
)
```

### GenAI Client

```python
import vertexai

client = vertexai.Client(
    project='my-project',
    location='us-central1'
)
```

## Core Workflows

### Dataset Management

```python
# Create tabular dataset from GCS
my_dataset = aiplatform.TabularDataset.create(
    display_name="my-dataset",
    gcs_source=['gs://path/to/my/dataset.csv']
)

# Create text dataset and import data separately
my_dataset = aiplatform.TextDataset.create(display_name="my-dataset")
my_dataset.import_data(
    gcs_source=['gs://path/to/my/dataset.csv'],
    import_schema_uri=aiplatform.schema.dataset.ioformat.text.multi_label_classification
)

# Retrieve existing dataset by resource name
dataset = aiplatform.ImageDataset(
    'projects/my-project/location/us-central1/datasets/{DATASET_ID}'
)
```

### Custom Training

Training scripts must read from environment variables set by Vertex AI:

```python
import os

data_format = os.environ['AIP_DATA_FORMAT']
training_uri = os.environ['AIP_TRAINING_DATA_URI']
validation_uri = os.environ['AIP_VALIDATION_DATA_URI']
test_uri = os.environ['AIP_TEST_DATA_URI']
model_dir = os.environ['AIP_MODEL_DIR']  # Write model artifacts here
```

Run a custom training job:

```python
job = aiplatform.CustomTrainingJob(
    display_name="my-training-job",
    script_path="training_script.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-2:latest",
    requirements=["gcsfs==0.7.1"],
    model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-2:latest",
)

model = job.run(
    my_dataset,
    replica_count=1,
    machine_type="n1-standard-4",
    accelerator_type='NVIDIA_TESLA_K80',
    accelerator_count=1
)
```

### AutoML Training

```python
dataset = aiplatform.TabularDataset(
    'projects/my-project/location/us-central1/datasets/{DATASET_ID}'
)

job = aiplatform.AutoMLTabularTrainingJob(
    display_name="train-automl",
    optimization_prediction_type="regression",
    optimization_objective="minimize-rmse",
)

model = job.run(
    dataset=dataset,
    target_column="target_column_name",
    training_fraction_split=0.6,
    validation_fraction_split=0.2,
    test_fraction_split=0.2,
    budget_milli_node_hours=1000,
    model_display_name="my-automl-model",
    disable_early_stopping=False,
)
```

### Model Deployment

```python
# Upload model
model = aiplatform.Model.upload(
    display_name='my-model',
    artifact_uri="gs://python/to/my/model/dir",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-2:latest",
)

# Deploy model to auto-created endpoint
endpoint = model.deploy(
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=5,
    accelerator_type='NVIDIA_TESLA_K80',
    accelerator_count=1
)

# Get online predictions
endpoint.predict(
    instances=[[6.7, 3.1, 4.7, 1.5], [4.6, 3.1, 1.5, 0.2]]
)
```

### Batch Prediction

```python
model = aiplatform.Model(
    '/projects/my-project/locations/us-central1/models/{MODEL_ID}'
)

batch_prediction_job = model.batch_predict(
    job_display_name='my-batch-prediction-job',
    instances_format='csv',
    machine_type='n1-standard-4',
    gcs_source=['gs://path/to/my/file.csv'],
    gcs_destination_prefix='gs://path/to/my/batch_prediction/results/',
    service_account='my-sa@my-project.iam.gserviceaccount.com'
)

# Or asynchronously
batch_prediction_job = model.batch_predict(..., sync=False)
batch_prediction_job.wait_for_resource_creation()
print(batch_prediction_job.state)
batch_prediction_job.wait()
```

### Pipelines

```python
pl = aiplatform.PipelineJob(
    display_name="My first pipeline",
    enable_caching=False,  # True=always cache, False=never, None=defer to component
    template_path="pipeline.json",
    parameter_values=parameter_values,
    pipeline_root=pipeline_root,  # GCS path for pipeline artifacts
)

# Blocking run
pl.run(service_account=service_account, sync=True)

# Non-blocking submit
pl.submit(service_account=service_account)
```

### Model Evaluation

```python
model = aiplatform.Model(
    'projects/my-project/locations/us-central1/models/{MODEL_ID}'
)

# List all evaluations
evaluations = model.list_model_evaluations()

# Get primary evaluation and its metrics
evaluation = model.get_model_evaluation()
eval_metrics = evaluation.metrics

# Reference evaluation by resource name
evaluation = aiplatform.ModelEvaluation(
    evaluation_name='projects/my-project/locations/us-central1/models/{MODEL_ID}/evaluations/{EVALUATION_ID}'
)
```

## SDK Package Structure

| Directory | Purpose |
|-----------|---------|
| `google/cloud` | Main SDK resource APIs |
| `google/cloud/aiplatform_v1` | GAPIC auto-generated code (production) |
| `google/cloud/aiplatform_v1beta1` | GAPIC auto-generated code (beta features) |
| `samples` | Example code and tutorials |
| `tests` | Unit and integration tests |
| `docs` | Documentation |
| `vertexai` | Generative AI SDK namespace |

## Optional SDK Features

Install with optional features:

```bash
pip install google-cloud-aiplatform[feature_name]
```

Available optional feature groups:
- `endpoint` - Endpoint management
- `full` - Complete feature set
- `metadata` - Metadata handling
- `tensorboard` - TensorBoard integration
- `testing` - Testing utilities
- `xai` - Explainable AI
- `pipelines` - ML pipelines
- `vizier` - Hyperparameter optimization
- `prediction` - Model prediction
- `datasets` - Dataset management
- `ray` - Ray integration
- `adk` - Agent Development Kit
- `agent-engines` - Agent engine support
- `evaluation` - Model evaluation
- `langchain` - LangChain integration
- `llama-index` - LlamaIndex integration

## Deprecation Notice (as of June 24, 2025)

The following modules are deprecated and will be removed June 24, 2026:
- `vertexai.generative_models`
- `vertexai.language_models`
- `vertexai.vision_models`
- `vertexai.tuning`
- `vertexai.caching`

**Migration:** Use the Google Gen AI SDK (`google-genai`) instead.

## Documentation Links

- API Reference: https://cloud.google.com/python/docs/reference/aiplatform/latest
- Product Documentation: https://cloud.google.com/vertex-ai/docs
- Sample Notebooks: https://github.com/GoogleCloudPlatform/vertex-ai-samples/tree/main/notebooks
- GitHub Repository: https://github.com/googleapis/python-aiplatform
