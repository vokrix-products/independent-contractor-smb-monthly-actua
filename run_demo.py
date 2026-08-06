from processor import process_file

# Hardcoded test CSV – realistic job scenario
test_bytes = b"Job Name,Budget,Actual\nKitchen Remodel,50000,55000\nBathroom Update,15000,14000\n"

results = process_file(test_bytes)
assert isinstance(results, list), "process_file did not return a list"
print("Extraction result:")
for i, rec in enumerate(results):
    print(f"Record {i+1}: {rec}")

if len(results) == 0:
    print("No records extracted. Check DEEPSEEK_API_KEY and model availability.")
else:
    print("Demo completed successfully.")
