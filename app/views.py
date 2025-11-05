from aiohttp import web
from pydantic import BaseModel, ValidationError, field_validator
from sqlalchemy import select, update, delete
from .models import Ad

class CreateAdSchema(BaseModel):
    title: str
    description: str
    owner: str

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v) > 100:
            raise ValueError('Title cannot exceed 100 characters')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()

    @field_validator('owner')
    @classmethod
    def validate_owner(cls, v):
        if not v or not v.strip():
            raise ValueError('Owner cannot be empty')
        if len(v) > 100:
            raise ValueError('Owner cannot exceed 100 characters')
        return v.strip()

class UpdateAdSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    owner: str | None = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Title cannot be empty')
            if len(v) > 100:
                raise ValueError('Title cannot exceed 100 characters')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Description cannot be empty')
            return v.strip()
        return v

    @field_validator('owner')
    @classmethod
    def validate_owner(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Owner cannot be empty')
            if len(v) > 100:
                raise ValueError('Owner cannot exceed 100 characters')
            return v.strip()
        return v

async def create_ad(request):
    try:
        data = await request.json()
    except Exception as e:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    
    try:
        ad_data = CreateAdSchema(**data)
    except ValidationError as e:
        errors = []
        for error in e.errors():
            errors.append({
                "field": ".".join(str(x) for x in error.get("loc", [])),
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "value_error")
            })
        return web.json_response({"error": errors}, status=400)

    session_maker = request.app["session_maker"]
    async with session_maker() as session:
        new_ad = Ad(**ad_data.model_dump())
        session.add(new_ad)
        await session.commit()
        await session.refresh(new_ad)
        return web.json_response({
            "id": new_ad.id,
            "title": new_ad.title,
            "description": new_ad.description,
            "owner": new_ad.owner,
            "created_at": new_ad.created_at.isoformat() + "Z"
        }, status=201)

async def get_ad(request):
    try:
        ad_id = int(request.match_info["ad_id"])
    except ValueError:
        return web.json_response({"error": "Invalid ad ID"}, status=400)
    session_maker = request.app["session_maker"]
    async with session_maker() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()
        if not ad:
            return web.json_response({"error": "Ad not found"}, status=404)
        return web.json_response({
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "owner": ad.owner,
            "created_at": ad.created_at.isoformat() + "Z"
        })

async def update_ad(request):
    try:
        ad_id = int(request.match_info["ad_id"])
    except ValueError:
        return web.json_response({"error": "Invalid ad ID"}, status=400)
    
    try:
        data = await request.json()
    except Exception as e:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    
    try:
        update_data = UpdateAdSchema(**data).model_dump(exclude_unset=True)
    except ValidationError as e:
        errors = []
        for error in e.errors():
            errors.append({
                "field": ".".join(str(x) for x in error.get("loc", [])),
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "value_error")
            })
        return web.json_response({"error": errors}, status=400)

    if not update_data:
        return web.json_response({"error": "No fields to update"}, status=400)

    session_maker = request.app["session_maker"]
    async with session_maker() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()
        if not ad:
            return web.json_response({"error": "Ad not found"}, status=404)
        await session.execute(update(Ad).where(Ad.id == ad_id).values(**update_data))
        await session.commit()
       
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        updated_ad = result.scalar_one()
        return web.json_response({
            "id": updated_ad.id,
            "title": updated_ad.title,
            "description": updated_ad.description,
            "owner": updated_ad.owner,
            "created_at": updated_ad.created_at.isoformat() + "Z"
        })

async def delete_ad(request):
    try:
        ad_id = int(request.match_info["ad_id"])
    except ValueError:
        return web.json_response({"error": "Invalid ad ID"}, status=400)
    session_maker = request.app["session_maker"]
    async with session_maker() as session:
        result = await session.execute(select(Ad).where(Ad.id == ad_id))
        ad = result.scalar_one_or_none()
        if not ad:
            return web.json_response({"error": "Ad not found"}, status=404)
        await session.execute(delete(Ad).where(Ad.id == ad_id))
        await session.commit()
        return web.json_response({"message": "Ad deleted"})