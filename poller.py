import os, time, requests, json, datetime
import processor

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_SERVICE_KEY = os.environ['SUPABASE_SERVICE_KEY']
PRODUCT_ID = os.environ['PRODUCT_ID']
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
BREVO_FROM_EMAIL = "jan@vokrix.net"
BREVO_FROM_NAME = "Vokrix"

HEADERS = {
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "apikey": SUPABASE_SERVICE_KEY,
    "Content-Type": "application/json"
}

def get_customer_email(customer_id):
    try:
        r = requests.get(
            f"{SUPABASE_URL}/auth/v1/admin/users/{customer_id}",
            headers={"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "apikey": SUPABASE_SERVICE_KEY}
        )
        if r.status_code == 200:
            return r.json().get("email")
    except Exception as e:
        print(f"Email lookup error: {e}")
    return None

def send_email(to_email, subject, html):
    if not BREVO_API_KEY or not to_email:
        print("Skipping email — no API key or email")
        return
    try:
        r = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": BREVO_API_KEY, "Content-Type": "application/json"},
            json={
                "sender": {"name": BREVO_FROM_NAME, "email": BREVO_FROM_EMAIL},
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html
            }
        )
        if r.status_code not in (200, 201):
            print(f"Brevo error: {r.status_code} {r.text}")
        else:
            print(f"Email sent to {to_email}: {subject}")
    except Exception as e:
        print(f"Email error: {e}")

def build_report_html(records, is_alert=False):
    over_budget = [r for r in records if 'critical' in r.get('status', '')]
    at_risk = [r for r in records if 'warning' in r.get('status', '')]
    on_track = [r for r in records if 'good' in r.get('status', '')]
    completed = [r for r in records if 'completed' in r.get('status', '')]

    rows = ""
    for r in records:
        status = r.get('status', '')
        if 'critical' in status:
            color = '#ef4444'
            label = 'Over Budget'
        elif 'warning' in status:
            color = '#f59e0b'
            label = 'At Risk'
        elif 'completed' in status:
            color = '#6b7280'
            label = 'Completed'
        else:
            color = '#22c55e'
            label = 'On Track'

        details = r.get('details', {})
        summary = r.get('summary', '')
        forecast = r.get('forecast', '')
        estimate = details.get('estimate', '')
        actual = details.get('actual_cost', '')
        margin = details.get('margin_percent', '')

        rows += f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid #1e2028;font-weight:600;color:#e2e8f0">{r.get('title','')}</td>
            <td style="padding:12px;border-bottom:1px solid #1e2028">
                <span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-size:12px">{label}</span>
            </td>
            <td style="padding:12px;border-bottom:1px solid #1e2028;color:#94a3b8;font-size:13px">
                {f'Est: ${estimate}' if estimate else ''} {f'/ Act: ${actual}' if actual else ''} {f'/ Margin: {margin}%' if margin else ''}
            </td>
            <td style="padding:12px;border-bottom:1px solid #1e2028;color:#94a3b8;font-size:13px">{summary}</td>
        </tr>
        {'<tr><td colspan="4" style="padding:4px 12px 12px;border-bottom:1px solid #1e2028;color:#5e6ad2;font-size:12px;font-style:italic">Forecast: ' + forecast + '</td></tr>' if forecast else ''}
        """

    title = "🚨 Over-Budget Alert" if is_alert else f"📊 Monthly Job Profitability Report — {datetime.date.today().strftime('%B %Y')}"
    subtitle = f"{len(over_budget)} over budget · {len(at_risk)} at risk · {len(on_track)} on track · {len(completed)} completed"

    return f"""
    <div style="font-family:system-ui,sans-serif;background:#010102;color:#e2e8f0;max-width:700px;margin:0 auto;padding:32px">
        <h1 style="color:#e2e8f0;margin-bottom:4px">{title}</h1>
        <p style="color:#64748b;margin-bottom:24px">{subtitle}</p>
        <table style="width:100%;border-collapse:collapse;background:#0f1117;border-radius:8px;overflow:hidden">
            <thead>
                <tr style="background:#1a1d27">
                    <th style="padding:12px;text-align:left;color:#64748b;font-weight:500">Job</th>
                    <th style="padding:12px;text-align:left;color:#64748b;font-weight:500">Status</th>
                    <th style="padding:12px;text-align:left;color:#64748b;font-weight:500">Financials</th>
                    <th style="padding:12px;text-align:left;color:#64748b;font-weight:500">Summary</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <p style="margin-top:24px;color:#374151;font-size:12px">
            Vokrix · <a href="https://vokrix.co" style="color:#5e6ad2">vokrix.co</a>
        </p>
    </div>
    """

def send_monthly_report(customer_id, records):
    email = get_customer_email(customer_id)
    if not email:
        return
    html = build_report_html(records, is_alert=False)
    send_email(email, f"Your Monthly Job Profitability Report — {datetime.date.today().strftime('%B %Y')}", html)

def send_over_budget_alert(customer_id, over_budget_records):
    email = get_customer_email(customer_id)
    if not email:
        return
    html = build_report_html(over_budget_records, is_alert=True)
    jobs_list = ', '.join([r.get('title', 'Job') for r in over_budget_records])
    send_email(email, f"🚨 Over-Budget Alert: {jobs_list}", html)

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

def send_monthly_reports_if_needed():
    today = datetime.date.today()
    if today.day != 1:
        return
    # get all unique customers for this product
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/records?product_id=eq.{PRODUCT_ID}&select=customer_id",
            headers=HEADERS
        )
        if r.status_code != 200:
            return
        rows = r.json()
        seen = set()
        customer_ids = [row['customer_id'] for row in rows if row['customer_id'] not in seen and not seen.add(row['customer_id'])]
        for customer_id in customer_ids:
            # get all their records
            r2 = requests.get(
                f"{SUPABASE_URL}/rest/v1/records?product_id=eq.{PRODUCT_ID}&customer_id=eq.{customer_id}&order=created_at.desc&limit=50",
                headers=HEADERS
            )
            if r2.status_code != 200:
                continue
            records = r2.json()
            if records:
                send_monthly_report(customer_id, records)
    except Exception as e:
        print(f"Monthly report error: {e}")

def main():
    print(f"Poller started — PRODUCT_ID={PRODUCT_ID}")
    send_monthly_reports_if_needed()
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
                            "status": rec.get("status", "on_track:good"),
                            "details": {**rec.get("details", {}), "summary": rec.get("summary", ""), "forecast": rec.get("forecast", "")},
                            "source_file_path": input_file_path,
                            "due_date": rec.get("due_date")
                        }
                        r = requests.post(f"{SUPABASE_URL}/rest/v1/records", headers=HEADERS, json=rec_data)
                        if r.status_code != 201:
                            print(f"Record insert failed: {r.text}")

                    result_summary = f"Processed {len(records)} jobs."
                    update_job(job_id, "completed", result_summary=result_summary)
                    insert_notification(customer_id, "Report ready", f"{len(records)} jobs processed.", "success")

                    # send over-budget alert immediately
                    over_budget = [r for r in records if 'critical' in r.get('status', '')]
                    if over_budget:
                        send_over_budget_alert(customer_id, over_budget)
                        insert_notification(customer_id, "🚨 Over-budget jobs found", f"{len(over_budget)} job(s) are over budget.", "warning")
                else:
                    time.sleep(10)
            else:
                time.sleep(10)
        except Exception as e:
            print(f"Poller error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
