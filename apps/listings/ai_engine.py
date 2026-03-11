import base64
import io
import json
from decimal import Decimal, InvalidOperation

from django.conf import settings
from openai import OpenAI
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

from .models import ListingRequest, ListingResult
from .ebay_service import (
    search_ebay_comps,
    estimate_prices_from_comps,
    format_comps_summary,
)

register_heif_opener()


def _to_decimal(value):
    if value in (None, "", "null"):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _extract_json(text: str) -> dict:
    """
    Safely extract JSON from model output.
    """
    if not text:
        return {}

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass

    return {}


def _normalize_image_for_openai(image_file):
    """
    Open uploaded image with Pillow, validate it, and convert it to safe JPEG bytes.
    Returns (mime_type, base64_string).
    """
    try:
        image_file.seek(0)
    except Exception:
        pass

    try:
        with Image.open(image_file) as img:
            img.load()

            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert("RGB")

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)

            encoded = base64.b64encode(buffer.read()).decode("utf-8")
            return "image/jpeg", encoded

    except UnidentifiedImageError:
        raise ValueError(
            f"{getattr(image_file, 'name', 'Uploaded file')} is not a valid image."
        )
    except Exception as exc:
        raise ValueError(
            f"Could not process image {getattr(image_file, 'name', 'uploaded file')}: {exc}"
        )
    finally:
        try:
            image_file.seek(0)
        except Exception:
            pass


def build_prompt_data(listing_request: ListingRequest) -> dict:
    return {
        "item_name": listing_request.item_name,
        "category": listing_request.category,
        "platform": listing_request.platform,
        "condition": listing_request.condition,
        "tone": listing_request.tone,
        "brand": listing_request.brand or "",
        "size_details": listing_request.size_details or "",
        "color": listing_request.color or "",
        "material": listing_request.material or "",
        "flaws": listing_request.flaws or "",
        "raw_notes": listing_request.raw_notes or "",
    }


def detect_product_from_images(images) -> dict:
    """
    Analyze multiple uploaded images and return structured product data.
    """
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    if not images:
        return {
            "item_name": "",
            "category": "",
            "platform": "ebay",
            "condition": "good",
            "tone": "simple",
            "brand": "",
            "size_details": "",
            "color": "",
            "material": "",
            "flaws": "",
            "raw_notes": "",
        }

    content = [
        {
            "type": "input_text",
            "text": """
You are analyzing multiple photos of the SAME item.

Your task:
Identify the product as accurately and cautiously as possible based on all images together.

Return VALID JSON ONLY using this exact schema:
{
  "item_name": "",
  "category": "",
  "platform": "ebay",
  "condition": "good",
  "tone": "simple",
  "brand": "",
  "size_details": "",
  "color": "",
  "material": "",
  "flaws": "",
  "raw_notes": ""
}

Rules:
- All images show the same item from different angles or details.
- Be cautious and honest.
- Do NOT invent brand names, sizes, materials, or specifications.
- If uncertain, use broad but useful descriptions.
- "item_name" should be practical and marketplace-friendly.
- "category" should be broad but relevant.
- "condition" should be one short word or phrase like: new, very good, good, fair, used.
- "tone" should always be "simple".
- "platform" should always be "ebay".
- "brand" should be empty if not visible.
- "size_details" should only include visible or user-inferable size clues.
- "color" should reflect the main visible color(s).
- "material" should only be included if reasonably visible or strongly inferable.
- "flaws" should mention only visible wear, marks, chips, scratches, stains, dents etc.
- "raw_notes" should be short, practical, and based only on visible evidence.
- Return JSON only. No markdown. No explanation.
"""
        }
    ]

    for image_file in images:
        mime_type, encoded = _normalize_image_for_openai(image_file)
        content.append(
            {
                "type": "input_image",
                "image_url": f"data:{mime_type};base64,{encoded}",
            }
        )

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )

    data = _extract_json(response.output_text)

    return {
        "item_name": data.get("item_name", ""),
        "category": data.get("category", ""),
        "platform": data.get("platform", "ebay"),
        "condition": data.get("condition", "good"),
        "tone": data.get("tone", "simple"),
        "brand": data.get("brand", ""),
        "size_details": data.get("size_details", ""),
        "color": data.get("color", ""),
        "material": data.get("material", ""),
        "flaws": data.get("flaws", ""),
        "raw_notes": data.get("raw_notes", ""),
    }


def generate_listing_result(listing_request: ListingRequest) -> ListingResult:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    payload = build_prompt_data(listing_request)

    system_prompt = """
You are a professional e-commerce copywriter.

Your job is to write listings that sell.

Focus on:
- clarity
- trust
- buyer intent
- search keywords

Rules:
- Do not invent specifications.
- Use natural human language.
- Avoid AI-like wording.
- Be commercially useful and realistic.
- Return JSON only.
"""

    user_prompt = f"""
Generate a marketplace listing from this data:

{json.dumps(payload, ensure_ascii=False, indent=2)}

Return VALID JSON ONLY with this exact schema:
{{
  "title": "",
  "description": "",
  "bullet_points": [],
  "tags": [],
  "quick_sale_price": "",
  "fair_price": "",
  "premium_price": ""
}}

Rules:
- Platform matters. Adapt style for the selected platform.
- Keep the title concise, searchable, and clickable.
- Description should be natural, persuasive, and honest.
- Bullet points should highlight buyer-facing details only.
- Tags should be short and useful for search.
- Price suggestions should be realistic estimates in GBP.
- Never mention AI.
- Do not use markdown.
- Do not add any extra keys.
- Return JSON only.
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    data = _extract_json(response.output_text)

    bullet_points_list = data.get("bullet_points", [])
    tags_list = data.get("tags", [])

    if not isinstance(bullet_points_list, list):
        bullet_points_list = []

    if not isinstance(tags_list, list):
        tags_list = []

    bullet_points = "\n".join(str(item) for item in bullet_points_list)
    tags = ", ".join(str(item) for item in tags_list)

    # Build eBay search query from strongest available fields
    query_parts = [
        listing_request.brand,
        listing_request.item_name,
        listing_request.material,
        listing_request.color,
    ]
    query = " ".join(part.strip() for part in query_parts if part and str(part).strip()).strip()

    comps = []
    price_data = {
        "quick_sale_price": None,
        "fair_price": None,
        "premium_price": None,
        "comps_count": 0,
    }
    comps_summary = ""

    if query:
        try:
            comps = search_ebay_comps(query=query, limit=10)
            price_data = estimate_prices_from_comps(comps)
            comps_summary = format_comps_summary(comps)
        except Exception:
            # Fallback to model-provided prices if eBay lookup fails
            price_data = {
                "quick_sale_price": _to_decimal(data.get("quick_sale_price")),
                "fair_price": _to_decimal(data.get("fair_price")),
                "premium_price": _to_decimal(data.get("premium_price")),
                "comps_count": 0,
            }
            comps_summary = ""

    # If no comps found, fall back to model prices
    if not price_data.get("quick_sale_price") and not price_data.get("fair_price") and not price_data.get("premium_price"):
        price_data["quick_sale_price"] = _to_decimal(data.get("quick_sale_price"))
        price_data["fair_price"] = _to_decimal(data.get("fair_price"))
        price_data["premium_price"] = _to_decimal(data.get("premium_price"))

    result = ListingResult.objects.create(
        request=listing_request,
        title=str(data.get("title", ""))[:255],
        description=str(data.get("description", "")),
        bullet_points=bullet_points,
        tags=tags[:255],
        quick_sale_price=_to_decimal(price_data.get("quick_sale_price")),
        fair_price=_to_decimal(price_data.get("fair_price")),
        premium_price=_to_decimal(price_data.get("premium_price")),
        comps_count=price_data.get("comps_count") or 0,
        ebay_comps_summary=comps_summary,
    )

    return result