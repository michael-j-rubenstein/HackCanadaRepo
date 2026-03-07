from pydantic import BaseModel


class ReceiptExtractionRequest(BaseModel):
    image_data: bytes
    mime_type: str = "image/jpeg"
