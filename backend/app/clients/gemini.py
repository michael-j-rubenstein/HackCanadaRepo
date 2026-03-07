from google.genai import types

from app.models.receipt import ReceiptData
from app.services.gemini import generate_structured_async


RECEIPT_EXTRACTION_PROMPT = (
    "Analyze this receipt image and extract all relevant data. "
    "If a field cannot be determined, use null. "
    "For items, always try to extract at least the name and total_price. "
    "IMPORTANT: Receipt item names are often abbreviated (e.g., 'BNLS/SL BRST' means 'Chicken Breast', "
    "'GRN PEPPERS' means 'Green Peppers', 'BBy SPINACH' means 'Baby Spinach'). "
    "Expand all abbreviations into full, common grocery product names. "
    "For each item, also classify it into exactly one of these categories: "
    "Dairy, Produce, Meat, Bakery, Beverages, Pantry. "
    "Set the 'category' field to the matching category name. "
    "IMPORTANT: Many receipts show the weight or volume purchased (e.g., '2.12 kg', '1.5 lb', '500 g', '1.75 L'). "
    "If a weight or volume is shown for an item, extract it into 'weight_value' (number) and "
    "'weight_unit' (one of: g, kg, lb, oz, ml, L). If no weight/volume is shown, leave them null."
)


async def extract_receipt(image_data: bytes, mime_type: str = "image/jpeg") -> ReceiptData:
    """Extract structured receipt data from an image using Gemini Vision."""
    contents = [
        types.Content(
            parts=[
                types.Part.from_text(text=RECEIPT_EXTRACTION_PROMPT),
                types.Part.from_bytes(data=image_data, mime_type=mime_type),
            ]
        )
    ]

    text = await generate_structured_async(
        contents=contents,
        response_schema=ReceiptData.model_json_schema(),
    )

    print(f"Gemini response: {text}")

    return ReceiptData.model_validate_json(text)
