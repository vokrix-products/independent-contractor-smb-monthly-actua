import os, time, requests, json
import processor

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_SERVICE_KEY = os.environ['SUPABASE_SERVICE_KEY']
PRODUCT_ID = os.environ['PRODUCT_ID']

HEADERS = {
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "apikey": SUPABASE_SERVICE_KEY,
    "Content-Type": "application/json"
}

def download_file(bucket, file_path):
    if file_path.startswith(bucket + "/"):
        file_path = file_path[len(bucket) + 1:]
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "apikey": SUPABASE_SERVICE_KEY})
    resp.raise_for_status()
    return resp.content

def insert_notification(customer_id, title, body, ntype):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/notifications", headers=HEADERS, json={
            "product_id": PRODUCT_ID, "customer_id": customer_id,
            "title": title, "body": body, "type": ntype, "read": False
        })
    except Exception as e:
        print(f"Notification error: {e}")

def update_job(job_id, status, output_file_path=None, result_summary=None):
    payload = {"status": status, "completed_at": "now()"}
    if output_file_path:
        payload["output_file_path"] = output_file_path
    if result_summary:
        payload["result_summary"] = result_summary
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}", headers=HEADERS, json=payload)
    if r.status_code not in (200, 204):
        print(f"Failed to update job {job_id}: {r.text}")

def main():
    while True:
        try:
            url = f"{SUPABASE_URL}/rest/v1/jobs?status=eq.pending&job_type=eq.process_upload&product_id=eq.{PRODUCT_ID}&order=created_at.asc&limit=1"
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code == 200:
                jobs = resp.json()
                if jobs:
                    job = jobs[0]
                    job_id = job["id"]
                    customer_id = job["customer_id"]
                    input_file_path = job["input_file_path"]
                    # Mark processing immediately to prevent re-processing
                    update_job(job_id, "processing")
                    try:
                        file_bytes = download_file("uploads", input_file_path)
                    except Exception as e:
                        update_job(job_id, "failed", result_summary=f"Download error: {str(e)}")
                        insert_notification(customer_id, "Processing failed", "Error downloading input file.", "error")
                        continue
                    try:
                        records = processor.process_file(file_bytes)
                    except Exception as e:
                        update_job(job_id, "failed", result_summary=f"Processing error: {str(e)}")
                        insert_notification(customer_id, "Processing failed", "Error processing file.", "error")
                        continue
                    for rec in records:
                        rec_data = {
                            "product_id": PRODUCT_ID,
                            "customer_id": customer_id,
                            "title": rec.get("title", "Job Report"),
                            "status": rec.get("status", "within_budget:good"),
                            "details": rec.get("details", {}),
                            "source_file_path": input_file_path,
                            "due_date": rec.get("due_date")
                        }
                        r = requests.post(f"{SUPABASE_URL}/rest/v1/records", headers=HEADERS, json=rec_data)
                        if r.status_code != 201:
                            print(f"Record insert failed: {r.text}")
                    result_summary = f"Processed {len(records)} records."
                    update_job(job_id, "completed", result_summary=result_summary)
                    insert_notification(customer_id, "Processing complete", "Your upload has been processed successfully.", "success")
                else:
                    time.sleep(10)
            else:
                time.sleep(10)
        except Exception as e:
            print(f"Poller error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
