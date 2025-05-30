import json
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")

MODEL_NAME = "credit-fraud-logistic-regression"
STAGE = "Production"

# Load run metadata
with open("outputs/models/logistic_model_run_metadata.json") as f:
    meta = json.load(f)

run_id = meta["run_id"]
artifact_path = meta["artifact_path"]
model_uri = f"runs:/{run_id}/{artifact_path}"

# Register the model
result = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME)

# Promote it
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name=MODEL_NAME, version=result.version, stage=STAGE, archive_existing_versions=True
)

client.set_registered_model_alias(
    name=MODEL_NAME, alias="latest", version=result.version
)

print(f"✅ Registered and promoted model version {result.version} to {STAGE}")
