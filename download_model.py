from huggingface_hub import snapshot_download
import os

model_id = "phanerozoic/Tiny-Viking-1.1b-v0.1"
token = os.getenv("HF_ACCESS_TOKEN")

snapshot_download(
    repo_id=model_id,
    token=token,
    cache_dir="/app/model"
)