from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from guvercin.database import get_db
from guvercin.models.pigeon import Pigeon
from guvercin.models.user import User
from guvercin.services.auth import require_role

router = APIRouter()


class PigeonCreate(BaseModel):
    name: str
    breed: str
    age: int | None = None
    gender: str | None = None
    color: str | None = None
    weight_kg: float | None = None
    photo_url: str | None = None
    description: str | None = None

    @field_validator("name", "breed")
    @classmethod
    def min_length(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("En az 2 karakter olmalı.")
        return v.strip()

    @field_validator("gender")
    @classmethod
    def valid_gender(cls, v: str | None) -> str | None:
        if v is not None and v not in ("erkek", "disi", "bilinmiyor"):
            raise ValueError("Cinsiyet: erkek, disi veya bilinmiyor.")
        return v


class PigeonResponse(BaseModel):
    id: int
    seller_id: int
    name: str
    breed: str
    age: int | None
    gender: str | None
    color: str | None
    weight_kg: float | None
    photo_url: str | None
    description: str | None

    model_config = {"from_attributes": True}


@router.post("/", response_model=PigeonResponse, status_code=201)
async def create_pigeon(
    body: PigeonCreate,
    seller: User = Depends(require_role("seller")),
    db: AsyncSession = Depends(get_db),
) -> PigeonResponse:
    """Güvercin ilanı oluştur — sadece satıcı."""
    pigeon = Pigeon(
        seller_id=seller.id,
        name=body.name,
        breed=body.breed,
        age=body.age,
        gender=body.gender,
        color=body.color,
        weight_kg=body.weight_kg,
        photo_url=body.photo_url,
        description=body.description,
    )
    db.add(pigeon)
    await db.commit()
    await db.refresh(pigeon)
    return pigeon


@router.get("/", response_model=list[PigeonResponse])
async def list_pigeons(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[PigeonResponse]:
    """Tüm güvercin ilanlarını listele."""
    result = await db.execute(select(Pigeon).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{pigeon_id}", response_model=PigeonResponse)
async def get_pigeon(
    pigeon_id: int, db: AsyncSession = Depends(get_db)
) -> PigeonResponse:
    """Güvercin detayı."""
    pigeon = await db.get(Pigeon, pigeon_id)
    if not pigeon:
        raise HTTPException(status_code=404, detail="Güvercin bulunamadı.")
    return pigeon


@router.put("/{pigeon_id}", response_model=PigeonResponse)
async def update_pigeon(
    pigeon_id: int,
    body: PigeonCreate,
    seller: User = Depends(require_role("seller")),
    db: AsyncSession = Depends(get_db),
) -> PigeonResponse:
    """Güvercin ilanı güncelle — sadece sahibi."""
    pigeon = await db.get(Pigeon, pigeon_id)
    if not pigeon:
        raise HTTPException(status_code=404, detail="Güvercin bulunamadı.")
    if pigeon.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Bu ilan size ait değil.")

    pigeon.name = body.name
    pigeon.breed = body.breed
    pigeon.age = body.age
    pigeon.gender = body.gender
    pigeon.color = body.color
    pigeon.weight_kg = body.weight_kg
    pigeon.photo_url = body.photo_url
    pigeon.description = body.description
    await db.commit()
    await db.refresh(pigeon)
    return pigeon


@router.delete("/{pigeon_id}", status_code=204)
async def delete_pigeon(
    pigeon_id: int,
    seller: User = Depends(require_role("seller")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Güvercin ilanı sil — sadece sahibi."""
    pigeon = await db.get(Pigeon, pigeon_id)
    if not pigeon:
        raise HTTPException(status_code=404, detail="Güvercin bulunamadı.")
    if pigeon.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Bu ilan size ait değil.")

    await db.delete(pigeon)
    await db.commit()
