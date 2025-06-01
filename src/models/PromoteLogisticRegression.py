import mlflow
from mlflow.tracking import MlflowClient
import json
import sys
import os
import time

# Add the project root to the path to ensure correct imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.constants import MLFLOW_URI, MODEL_NAME

mlflow.set_tracking_uri(MLFLOW_URI)
client = MlflowClient()

model_name = MODEL_NAME

with open("outputs/models/model_run_metadata.json") as f:
    meta = json.load(f)

run_id = meta["run_id"]
artifact_path = meta["artifact_path"]
model_uri = f"runs:/{run_id}/{artifact_path}"

# Register the model
registered_model = mlflow.register_model(model_uri=model_uri, name=model_name)

# Wait until the registration is complete
model_version = None
for _ in range(10):
    details = client.get_model_version(
        name=model_name, version=registered_model.version
    )
    if details.status == "READY":
        model_version = registered_model.version
        break
    time.sleep(1)

if model_version is None:
    raise RuntimeError("Model registration did not complete in time.")

# Set aliases for the newly registered version
client.set_registered_model_alias(
    name=model_name, alias="production", version=model_version
)
client.set_registered_model_alias(
    name=model_name, alias="champion", version=model_version
)

print(f"Successfully set aliases for model '{model_name}' version {model_version}")
