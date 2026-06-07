from fastapi import APIRouter, HTTPException, Query
import httpx
import os
import html
import re

places_router = APIRouter()


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(text))


@places_router.get("/search")
async def search_places(q: str = Query(..., min_length=1)):
    client_id = os.getenv("NAVER_CLIENT_ID", "")
    client_secret = os.getenv("NAVER_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        raise HTTPException(status_code=503, detail="장소 검색 서비스 자격증명이 설정되지 않았습니다.")

    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {"query": q, "display": 10, "sort": "comment"}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, params=params, timeout=5.0)
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="검색 서버 응답 시간 초과")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="검색 API 오류가 발생했습니다.")

    data = resp.json()
    items = []

    for item in data.get("items", []):
        mapx = item.get("mapx", "")
        mapy = item.get("mapy", "")
        if not mapx or not mapy:
            continue
        try:
            # Naver Local Search API returns coordinates as integer strings (WGS84 * 1e7)
            lng = int(mapx) / 1e7
            lat = int(mapy) / 1e7
        except (ValueError, TypeError):
            continue

        items.append({
            "title": _clean_html(item.get("title", "")),
            "category": item.get("category", ""),
            "address": item.get("address", ""),
            "roadAddress": item.get("roadAddress", ""),
            "lat": lat,
            "lng": lng,
        })

    return {"items": items}
