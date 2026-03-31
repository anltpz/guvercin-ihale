from datetime import datetime, timedelta, timezone
from typing import Callable

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from guvercin.config import settings
from guvercin.database import get_db
from guvercin.exceptions import InvalidTokenError
from guvercin.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(plain: str) -> str:
    """Düz metin şifreyi bcrypt ile hash'ler.

    Args:
        plain: Hash'lenecek düz metin şifre.

    Returns:
        Bcrypt hash string'i.
    """
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Düz metin şifreyi hash ile karşılaştırır.

    Args:
        plain: Doğrulanacak düz metin şifre.
        hashed: Veritabanındaki bcrypt hash.

    Returns:
        Eşleşme durumu.
    """
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT erişim token'ı oluşturur.

    Args:
        data: Token payload'ı (en az "sub" anahtarı içermeli).
        expires_delta: Opsiyonel özel süre. Yoksa config'den alınır.

    Returns:
        Kodlanmış JWT string'i.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """JWT token'ını çözümler.

    Args:
        token: Çözümlenecek JWT string'i.

    Returns:
        Token payload dict'i.

    Raises:
        InvalidTokenError: Token geçersiz veya süresi dolmuşsa.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("sub") is None:
            raise InvalidTokenError()
        return payload
    except JWTError:
        raise InvalidTokenError()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT'den mevcut kullanıcıyı çözümler.

    Args:
        token: Authorization header'dan gelen JWT.
        db: Veritabanı oturumu.

    Returns:
        Doğrulanmış User nesnesi.

    Raises:
        InvalidTokenError: Token geçersiz veya kullanıcı bulunamazsa.
    """
    payload = decode_access_token(token)
    username: str = payload["sub"]
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise InvalidTokenError("Kullanıcı bulunamadı.")
    return user


def require_role(role: str) -> Callable:
    """Rol kontrolü dependency factory'si.

    Args:
        role: Gerekli rol adı ("seller" veya "buyer").

    Returns:
        FastAPI dependency fonksiyonu.
    """

    async def _check(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if role not in current_user.roles:
            raise HTTPException(
                status_code=403,
                detail=f"Bu işlem için '{role}' rolü gerekli.",
            )
        return current_user

    return _check
