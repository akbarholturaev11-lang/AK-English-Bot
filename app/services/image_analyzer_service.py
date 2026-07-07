from app.services.ai_service import AIService


ANALYZER_PROMPT = """
You are an image text extraction assistant.

Task:
Identify only the text visible inside the image.

Strict rules:

1. Analyze the image carefully.
2. If the image contains English text, words, sentences, letters, numbers, or symbols, write them exactly.
3. Do not add anything from yourself.
4. Do not correct spelling or grammar.
5. If the text is unclear, write only the clear part.
6. If there is no text in the image, write exactly:

TEXT:
No text found

ELEMENTS:
None

Response format:

TEXT:
(the exact text from the image)

ELEMENTS:
- each visible word, phrase, line, or useful text fragment on a separate line

Important:
- Do not translate
- Do not explain
- Do not teach
- Only extract the text visible in the image
"""


class ImageAnalyzerService:
    def __init__(self):
        self.ai_service = AIService()
        self.last_ai_result = None

    async def analyze_image(
        self,
        image_bytes: bytes,
        mime_type: str,
    ) -> str:
        self.last_ai_result = await self.ai_service.generate_vision_reply_with_usage(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=ANALYZER_PROMPT,
        )
        return self.last_ai_result.content
