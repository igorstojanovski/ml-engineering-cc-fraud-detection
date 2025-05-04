# High-Level Description of an ML CI/CD Flow Using MLFlow

## Experiments

Experiments are performed in feature branches.  
Every change to a feature branch triggers a pipeline that trains and evaluates a model, logging all relevant metrics and parameters to MLFlow **experiments**. These **experiment pipelines do not register models** in the MLFlow Model Registry.

## Main Branch

Only the preferred configuration (e.g., best-performing model + its code) is merged into `main`.

This triggers a CI pipeline that:
- Trains the model using the production config
- Registers it in the MLFlow Model Registry
- Promotes it to the `Production` stage
- Deploys the model

## Local Development

Local development **must not** track to the shared MLFlow tracking server.  
Developers run containerized local MLFlow servers for isolated testing, logging locally to disk or SQLite.  
This avoids cluttering shared experiments and preserves traceability in CI pipelines.


```mermaid
flowchart TB
  subgraph Dev Workflows
    direction TB
    LR(“feature/experiment-logreg”)
    XGB(“feature/experiment-xgboost”)
    MLP(“feature/experiment-mlp”)
  end

  subgraph MLflow Tracking
    direction LR
    ExpLR[“Experiment: logistic-regression-v1”]
    ExpXGB[“Experiment: xgb-depth-sweep-v2”]
    ExpMLP[“Experiment: neural-nets-v1”]

    LR -->|runs →| ExpLR
    XGB -->|runs →| ExpXGB
    MLP -->|runs →| ExpMLP
  end

  main["branch: main"]

  subgraph Release Pipeline on main
    direction TB
    CI[“CI Build & Train”]
    Register[“Register & Promote Run → Model Registry”]
    Deploy[“Deploy Production Model”]
  end

  %% Branch merging into main
  LR ---|merge winning config| main
  XGB ---|merge winning config| main
  MLP ---|merge winning config| main
  
  %% Pipeline flow
  CI --> Register
  Register --> Deploy
  main --> CI
