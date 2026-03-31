from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
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
    photo_url: str | None = None
    description: str | None = None


class PigeonResponse(BaseModel):
    id: int
    seller_id: int
    name: str
    breed: str
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
