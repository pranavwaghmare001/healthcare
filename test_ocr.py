import io
from report_parser import parse_report

class MockFileObj:
    def __init__(self, filepath):
        self.name = filepath
        self.filepath = filepath
        
    def getvalue(self):
        with open(self.filepath, "rb") as f:
            return f.read()

print("--- STARTING OCR TEST ---")
test_file = MockFileObj("dummy_report.png")
result, error = parse_report(test_file)

if error:
    print(f"FAILED: {error}")
else:
    print("SUCCESSFULLY PARSED DATA:")
    for key, value in result.get("metrics", {}).items():
        print(f" >> {key}: {value}")
print("--- TEST COMPLETE ---")
