# 🛠️ Development Process Guide

This document describes the development workflow, tools used, and how to configure them correctly. Follow this guide to ensure consistency and reproducibility across all environments.

---

## ⚙️ Tools & Setup

### 🔹 DVC - Data Version Control

We use [DVC](https://dvc.org) to manage datasets and machine learning pipelines.

- **Local development** uses a Dockerized [MinIO](https://min.io) instance (S3-compatible).
- **Production pipelines** use **AWS S3** as the shared remote storage.

---

### 🏗️ Setting up DVC

#### 1. Install DVC with S3 support
```bash
pip install dvc[s3]
```

Alternatively, follow the [official DVC installation guide](https://dvc.org/doc/install) for your OS.

#### 2. Configure AWS credentials

DVC needs AWS credentials to interact with S3 remotes. **Never hardcode credentials in `.dvc/config`.**

**Recommended approaches:**

- **Linux / macOS**: Add to your shell config:
  ```bash
  export AWS_ACCESS_KEY_ID=your-access-key
  export AWS_SECRET_ACCESS_KEY=your-secret-key
  ```
- **Windows**: Set environment variables via PowerShell or system settings.
- **Alternative**: Use `aws configure` to store them safely in `~/.aws/credentials`.

➡️ **Do not commit credentials into `.dvc/config` or version control.**

---

### 🗄️ Local MinIO Setup

To simulate S3 locally:

1. Start MinIO with Docker Compose:
   ```bash
   docker-compose up -d minio
   ```

2. DVC remote config for MinIO:
   ```ini
   ['remote "minio-local"']
       url = s3://dvcstore/
       endpointurl = http://localhost:9000
   ```

3. Access MinIO UI: [http://localhost:9001](http://localhost:9001)

Each developer runs their own MinIO instance locally to avoid AWS costs during development.

---

## 🚀 Development Workflow

### ✅ Step 1: Prepare Data

Place dataset files in:
```plaintext
data/training/
```

### ✅ Step 2: Track Data with DVC

To track the folder:
```bash
dvc add data/training/
git add data/training.dvc .gitignore
git commit -m "Track training data with DVC"
```

> If new files are added to `data/training/`, re-run `dvc add data/training/` to update tracking.

### ✅ Step 3: Push Data to Remotes

- Push to **local MinIO**:
  ```bash
  dvc push --remote minio-local
  ```

- Push to **production S3** when ready:
  ```bash
  dvc push --remote s3-prod
  ```

- Set minio-local as teh default remote
  ```bash
    dvc remote default minio-local --local
  ```

### ✅ Step 4: Run Pipelines

Reproduce pipeline stages:
```bash
dvc repro
```

Always `dvc pull` before switching branches or starting work:
```bash
dvc pull --remote s3-prod
```

---

## 🌍 Team Collaboration & Remote Pipelines

- DVC metadata (`.dvc`, `dvc.yaml`, `dvc.lock`) is tracked in Git.
- Data itself lives in S3 or MinIO.
- Git pushes trigger CI/CD pipelines which:
  - Pull data from S3
  - Reproduce results with `dvc repro`

Example flow:
```bash
dvc pull --remote s3-prod
# Work locally, push to MinIO if needed
dvc push --remote minio-local
# Finalize work
dvc push --remote s3-prod
git push origin feature/my-branch
```

---

## 🛡️ Best Practices

- ✅ Run `dvc status` before pushing to verify tracked data state.
- ✅ Re-run `dvc add data/training/` after adding new files.
- ✅ Do not commit secrets/credentials.
- ✅ Use `.dvc/config.local` for machine-specific configs (ignored by Git).
- ✅ Validate dataset changes using:
  ```bash
  dvc diff
  ```

---

## ✅ Useful Commands Cheat Sheet

| Action                               | Command                                       |
|--------------------------------------|-----------------------------------------------|
| Track folder                         | `dvc add data/training/`                      |
| Push to local MinIO                  | `dvc push --remote minio-local`               |
| Push to production S3                | `dvc push --remote s3-prod`                   |
| Pull from S3                         | `dvc pull --remote s3-prod`                   |
| Reproduce pipeline                   | `dvc repro`                                   |
| Check DVC status                     | `dvc status`                                  |
| Compare data versions                | `dvc diff`                                    |
| Switch default remote (local only)   | `dvc remote default minio-local --local`      |

---

## ✅ Quick Troubleshooting

| Problem                                  | Solution                                   |
|------------------------------------------|--------------------------------------------|
| File changes not detected                | Re-run `dvc add data/training/`            |
| New data not pushed                      | Check `dvc status` and re-run `dvc push`   |
| Missing files in S3                      | Ensure you pushed with `--remote s3-prod`  |
| MinIO has no data after reset            | Re-push to MinIO: `dvc push --remote minio-local` |
| Incorrect file shows as folder in S3     | Ensure it's a file, re-add, commit, push   |

---

Happy coding! 🚀
