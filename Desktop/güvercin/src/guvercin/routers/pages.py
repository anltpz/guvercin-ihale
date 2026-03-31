import pathlib

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html")


@router.get("/giris")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.get("/kayit")
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.get("/ilanlar")
async def pigeons_page(request: Request):
    return templates.TemplateResponse(request, "pigeons.html")


@router.get("/ilan/{pigeon_id}")
async def pigeon_detail_page(request: Request, pigeon_id: int):
    return templates.TemplateResponse(
        request, "pigeon_detail.html", {"pigeon_id": pigeon_id}
    )


@router.get("/ilan-ekle")
async def pigeon_create_page(request: Request):
    return templates.TemplateResponse(request, "pigeon_create.html")


@router.get("/ihaleler")
async def auctions_page(request: Request):
    return templates.TemplateResponse(request, "auctions.html")


@router.get("/ihale/{auction_id}")
async def auction_detail_page(request: Request, auction_id: int):
    return templates.TemplateResponse(
        request, "auction_detail.html", {"auction_id": auction_id}
    )


@router.get("/odeme")
async def payment_page(request: Request):
    return templates.TemplateResponse(request, "payment.html")
