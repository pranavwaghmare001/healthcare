from PIL import Image, ImageDraw

# Create a blank white image
img = Image.new('RGB', (500, 300), color=(255, 255, 255))
d = ImageDraw.Draw(img)

# Add mock medical text to simulate an OCR scan
d.text((20, 20), "CITY GENERAL HOSPITAL - LAB RESULTS", fill=(0, 0, 0))
d.text((20, 60), "Patient Name: Jane Doe", fill=(0, 0, 0))
d.text((20, 90), "Date: 2026-04-08", fill=(0, 0, 0))
d.text((20, 140), "TEST RESULTS:", fill=(0, 0, 0))
d.text((20, 170), "Blood pressure: 118 / 76 mmHg", fill=(0, 0, 0))
d.text((20, 200), "Fasting Glucose : 92 mg/dl", fill=(0, 0, 0))
d.text((20, 230), "Heart rate : 68 BPM", fill=(0, 0, 0))

# Save
img.save("e:/smart health assistant/dummy_report.png")
print("Image created successfully.")
