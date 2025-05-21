# MLOps Workflow: DVC + MLflow
## Developer Flow with Master Branch Rebuilds

This document outlines a typical machine learning development workflow using Git, DVC (Data Version Control), and MLflow. A key aspect of this workflow is that while developers build and test models locally and in Pull Requests, the **official model artifact for the main branch is always built within a controlled CI/CD environment** when changes are merged into `master`/`main`.

---

## 1. Developer Local Workflow

Developers work on new features, model improvements, or bug fixes in isolated Git branches.

1.  **Branch Creation:**
    * Create a new feature branch from the latest `master`/`main`:
        ```bash
        git checkout master
        git pull
        git checkout -b feature/my-new-model
        ```

2.  **Data & Dependencies:**
    * Ensure you have the necessary DVC-tracked data:
        ```bash
        dvc pull
        ```
    * If adding new large data files:
        ```bash
        dvc add path/to/new_data.csv
        ```

3.  **Code Development & Experimentation:**
    * Modify or write Python scripts for data processing, feature engineering, model training, and evaluation.
    * **MLflow Integration:** Instrument your training scripts to log experiments:
        * `mlflow.start_run()`: Begin an MLflow run.
        * `mlflow.log_param()`: Log hyperparameters.
        * `mlflow.log_metric()`: Log performance metrics (e.g., accuracy, F1-score).
        * `mlflow.log_artifact()`: Log auxiliary files (e.g., plots, sample outputs).
        * `mlflow.<framework>.log_model()`: Log the trained model in MLflow's format.

4.  **Define & Run DVC Pipelines:**
    * Define or update stages in `dvc.yaml` to codify your ML pipeline (e.g., preprocessing, training, evaluation).
        ```yaml
        # dvc.yaml example
        stages:
          preprocess:
            cmd: python src/preprocess.py --input data/raw --output data/processed
            deps:
              - data/raw
              - src/preprocess.py
            outs:
              - data/processed
          train:
            cmd: python src/train.py --input data/processed --output models/
            deps:
              - data/processed
              - src/train.py
            outs:
              - models/model.pkl
            # DVC can also track metrics files
            metrics:
              - metrics/train_metrics.json:
                  cache: false # MLflow is primary for metrics, DVC can version the file
        ```
    * Execute the DVC pipeline. This command will run stages if dependencies or code have changed and update `dvc.lock`:
        ```bash
        dvc repro
        ```
    * If new outputs like models or processed data are generated and not yet tracked, or if they were defined as `outs` in a new stage:
        ```bash
        # This is usually handled by `dvc repro` if `outs` are defined in dvc.yaml
        # If adding manually:
        # dvc add models/model.pkl
        ```

5.  **Local Testing:**
    * Run unit tests and any relevant integration tests locally.

---

## 2. Committing & Pushing Changes

Once the developer is satisfied with their changes and the locally built model:

1.  **Stage Changes for Git:**
    * Add all modified code, DVC metadata files (`.dvc` files for new/changed data/outputs), `dvc.yaml`, and the updated `dvc.lock`:
        ```bash
        git add .
        ```

2.  **Commit to Git:**
    * ```bash
        git commit -m "FEAT: Implement new model architecture and training pipeline for X"
        ```

3.  **Push Git Branch:**
    * ```bash
        git push origin feature/my-new-model
        ```

4.  **Push DVC Artifacts:**
    * Push the DVC-tracked large files (datasets, locally built model artifacts) to DVC remote storage:
        ```bash
        dvc push
        ```

---

## 3. Pull Request (PR) Process & Pipeline

The developer creates a Pull Request from their feature branch to the `master`/`main` branch.

1.  **PR Creation:** Initiate a PR in the Git hosting platform (e.g., GitHub, GitLab).

2.  **PR Pipeline Triggered (CI):** This pipeline focuses on validation and testing the proposed changes.
    * **Checkout Code:**
        ```bash
        git checkout feature/my-new-model # Or the PR's merge commit
        ```
    * **Fetch DVC Artifacts:**
        ```bash
        dvc pull
        ```
        *This pulls data and the model built by the developer on their machine, as referenced by `dvc.lock` in the PR.*
    * **Run Code Quality Checks:** Linting, formatting, static analysis.
    * **Run Unit Tests:** Verify individual code components.
    * **Run Integration Tests:** Test interactions between components. These might use the DVC-pulled (developer-built) model.
    * **Model Evaluation (on developer's model):**
        * Load the model pulled by `dvc pull`.
        * Evaluate it against a standard validation/test dataset (also pulled via DVC).
        * Log metrics to MLflow (e.g., under a PR-specific experiment or tag).
        * Compare metrics against defined thresholds or baselines.
    * **DVC Sanity Checks:**
        ```bash
        dvc status -c # Check for inconsistencies
        ```
    * **`dvc repro` Behavior:** Since `dvc pull` fetched artifacts matching `dvc.lock`, `dvc repro` in the PR pipeline will likely **not re-run** most stages (like training), as their inputs/outputs will appear up-to-date. The focus is on validating the *existing* artifacts and code.
    * **Report Status:** CI pipeline reports success/failure to the PR.

---

## 4. Master/Main Branch Pipeline (Post-Merge)

After the PR is reviewed and merged into `master`/`main`:

1.  **Pipeline Triggered (CI/CD):** This pipeline handles the official build, versioning, and registration of the model.

2.  **Checkout Code:**
    * ```bash
        git checkout master
        git pull # Ensure latest code from master
        ```

3.  **Fetch DVC Input Data:**
    * ```bash
        dvc pull # Pulls necessary input data.
        ```
    * *Critically, this pipeline will NOT rely on the developer-pushed model binary for the official build.*

4.  **Build Official Model Artifact in CI:**
    * The core principle: **The model is rebuilt from scratch in the controlled CI environment.**
    * Execute the DVC pipeline, forcing the training stage (and any other desired stages) to re-run, or ensure it runs due to changes in code/dependencies that were merged:
        ```bash
        # Option 1: Force re-run of specific stages like training
        dvc repro -f train 
        # Option 2: Run the full pipeline; changes from the merge should trigger necessary stages
        # dvc repro
        ```
    * The training script (executed by `dvc repro`) logs parameters, metrics, and the **newly CI-built model** to MLflow.

5.  **Version CI-Built Artifacts:**
    * `dvc repro` (if it ran) automatically updates `dvc.lock` with the hashes of the **CI-built model** and any other outputs.
    * Push the CI-built model and other DVC artifacts to DVC remote storage:
        ```bash
        dvc push
        ```
    * Commit the updated `dvc.lock` (if changed by the CI build) back to `master`:
        ```bash
        git add dvc.lock
        # Configure git user for CI if not already done
        git config --global user.name "CI Pipeline"
        git config --global user.email "ci@example.com"
        git commit -m "CI: Build and version official model artifacts [skip ci]"
        git push origin master
        ```
        *(Note: Automatically committing back to master from CI requires careful setup and consideration of alternatives like using Git tags for specific build versions.)*

6.  **Register Model in MLflow Model Registry:**
    * The **CI-built and MLflow-logged model** is registered in the MLflow Model Registry.
    * Its stage can be transitioned (e.g., to "Staging" for further testing or "Production" if automated).

7.  **Optional: Trigger Deployment:**
    * Based on the model's registration and stage in MLflow, a deployment pipeline can be triggered to deploy the model to serving environments.

---

## 5. Key Artifacts & Versioning Summary

* **Git:** Versions source code (`.py`), DVC metadata (`.dvc` files, `dvc.yaml`, `dvc.lock`), MLflow project files (`MLproject`), environment configurations (`requirements.txt`).
* **DVC Remote Storage (S3, GCS, etc.):** Stores large data files, intermediate artifacts, and **model binaries** (both developer-pushed for PRs and CI-built for official versions).
* **MLflow Tracking Server:**
    * Tracks experiments: parameters, metrics, code versions (Git commit).
    * Stores artifacts: plots, evaluation results, and **logged models** (which include the model files, `MLmodel` descriptor, and environment).
    * **MLflow Model Registry:** Manages the lifecycle (versions, stages) of the **CI-built models** intended for deployment.

This workflow ensures that while developers have flexibility and can validate their work effectively, the official models are built reproducibly in a consistent, controlled CI environment, which is crucial for robust MLOps.