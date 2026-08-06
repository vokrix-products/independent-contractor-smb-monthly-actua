# JobProfitIQ Extraction Backend

## Product

JobProfitIQ is a QuickBooks-native monthly automated reporting product for independent contractors and small businesses. Each month it pulls job data (budgets, actuals, costs) from QuickBooks via a poller, runs it through this extraction backend, and emails a profitability report so the owner can see which jobs are over budget / losing profit before it is too late.

## Archetype

The target user is an independent contractor, solo SMB owner, or small trade business (roofing, remodeling, electrical, plumbing, HVAC). They invoice through QuickBooks and want a zero-effort monthly snapshot of actual-vs-estimate job profitability without building spreadsheets or doing manual accounting analysis.

## Poller Input

The poller invokes `processor.process_file(file_bytes)` with the raw bytes of a document payload. Accepted formats:

- PDF (job cost reports, estimates, invoices)
- Excel (QuickBooks exports, budget/actual sheets)
- CSV
- Plain text

Expected content per job: job/project name, estimated/budget cost, actual cost, and optionally variance, completion status, and a date. The backend extracts each job into a record with:

- `title` — job/project name
- `status` — `over_budget:critical` when actual cost significantly exceeds budget, otherwise `within_budget:good`
- `details` — object of extracted numeric/text fields (budget, actual, variance, etc.)
- `due_date` — ISO-8601 date if present, otherwise `null`

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Set environment variable:
   ```
   export DEEPSEEK_API_KEY=your_key
   ```

## Usage

Run the demo:
```
python run_demo.py
```

Run tests:
```
python run_tests.py
```

Dashboard: https://independent-contractor-smb-monthly-actua.vokrix.co
Vercel project: independent-contractor-smb-monthly-actua
Railway service: 13fb43a7-0ed7-4446-8fb6-688f40118140
Railway: independent-contractor-smb-monthly-actua
Cloudflare: independent-contractor-smb-monthly-actua.vokrix.co
