from aiohttp import web
import datetime

ads_db = {}
next_id = 1


async def create_ad(request):
    global next_id
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    if not data or 'title' not in data or 'description' not in data or 'owner' not in data:
        return web.json_response(
            {"error": "Missing required fields: title, description, owner"},
            status=400
        )

    new_ad = {
        "id": next_id,
        "title": data["title"],
        "description": data["description"],
        "owner": data["owner"],
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

    ads_db[next_id] = new_ad
    next_id += 1
    return web.json_response(new_ad, status=201)


async def get_ad(request):
    ad_id = int(request.match_info['ad_id'])
    ad = ads_db.get(ad_id)
    if not ad:
        return web.json_response({"error": "Ad not found"}, status=404)
    return web.json_response(ad)


async def delete_ad(request):
    ad_id = int(request.match_info['ad_id'])
    if ad_id not in ads_db:
        return web.json_response({"error": "Ad not found"}, status=404)
    del ads_db[ad_id]
    return web.json_response({"message": "Ad deleted"})


app = web.Application()
app.router.add_post('/ads', create_ad)
app.router.add_get('/ads/{ad_id}', get_ad)
app.router.add_delete('/ads/{ad_id}', delete_ad)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)