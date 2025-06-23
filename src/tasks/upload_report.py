from prefect import task
from prefect.context import get_run_context

from datetime import datetime
from prefect.client.orchestration import get_client
import json
from io import BytesIO
from config.minio import get_minio, setup_minio_buckets, BUCKET  

@task
async def save_task_metadata_to_minio():
    context = get_run_context()
    flow_run_id = context.flow_run.id

    async with get_client() as client:
        task_runs = await client.read_task_runs(
            flow_run_filter={"flow_run_id": {"any_": [flow_run_id]}}
        )

    task_data = []

    for tr in task_runs:
        duration = (
            (tr.end_time - tr.start_time).total_seconds()
            if tr.start_time and tr.end_time else None
        )

        task_data.append({
            "task_run_id": str(tr.id),
            "task_name": tr.name,
            "state": tr.state.name if tr.state else "Unknown",
            "start_time": tr.start_time.isoformat() if tr.start_time else None,
            "end_time": tr.end_time.isoformat() if tr.end_time else None,
            "duration_seconds": duration,
            "total_run_time": tr.total_run_time,
            "estimated_run_time": tr.estimated_run_time,
            "created": tr.created.isoformat() if tr.created else None,
            "updated": tr.updated.isoformat() if tr.updated else None,
            "tags": tr.tags,
            "flow_run_id": str(tr.flow_run_id),
            "infrastructure_pid": tr.infrastructure_pid,
            "retries": tr.retries,
        })

    # Convertir a JSON
    json_bytes = json.dumps(task_data, indent=2).encode("utf-8")
    byte_stream = BytesIO(json_bytes)

    # Subir a MinIO
    minio_client = get_minio()
    setup_minio_buckets(minio_client)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    object_name = f"{timestamp}/task_metadata.json"

    minio_client.put_object(
        bucket_name=BUCKET,
        object_name=object_name,
        data=byte_stream,
        length=len(json_bytes),
        content_type="application/json",
    )
