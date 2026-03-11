import base64
import requests
from statistics import median
from django.conf import settings


EBAY_OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_BROWSE_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"


def get_ebay_access_token():
    client_id = settings.EBAY_CLIENT_ID
    client_secret = settings.EBAY_CLIENT_SECRET

    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }

    response = requests.post(EBAY_OAUTH_URL, headers=headers, data=data, timeout=30)
    response.raise_for_status()

    return response.json()["access_token"]


def search_ebay_comps(query, limit=10):
    token = get_ebay_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": settings.EBAY_MARKETPLACE_ID,
    }

    params = {
        "q": query,
        "limit": limit,
        "filter": "buyingOptions:{FIXED_PRICE}",
    }

    response = requests.get(
        EBAY_BROWSE_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    items = data.get("itemSummaries", [])

    comps = []

    for item in items:
        price_obj = item.get("price", {})
        value = price_obj.get("value")

        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        comps.append({
            "title": item.get("title", ""),
            "price": value,
            "currency": price_obj.get("currency", "GBP"),
            "condition": item.get("condition", ""),
            "itemWebUrl": item.get("itemWebUrl", ""),
        })

    return comps


def estimate_prices_from_comps(comps):
    prices = sorted([item["price"] for item in comps if item["price"] > 0])

    if not prices:
        return {
            "quick_sale_price": None,
            "fair_price": None,
            "premium_price": None,
            "comps_count": 0,
        }

    med = median(prices)

    quick_sale = round(med * 0.85, 2)
    fair_price = round(med, 2)
    premium_price = round(med * 1.15, 2)

    return {
        "quick_sale_price": quick_sale,
        "fair_price": fair_price,
        "premium_price": premium_price,
        "comps_count": len(prices),
    }


def format_comps_summary(comps):
    lines = []

    for comp in comps[:5]:
        lines.append(
            f"- {comp['title']} | £{comp['price']} | {comp['condition']}"
        )

    return "\n".join(lines)