from decimal import Decimal


class AuctionEndedError(Exception):
    """İhale sona ermiş, teklif kabul edilemez."""

    def __init__(self, auction_id: int) -> None:
        self.auction_id = auction_id
        super().__init__(f"İhale #{auction_id} sona ermiştir.")


class BidTooLowError(Exception):
    """Teklif mevcut en yüksek tekliften düşük."""

    def __init__(self, current: Decimal, minimum: Decimal) -> None:
        self.current = current
        self.minimum = minimum
        super().__init__(f"Teklifiniz çok düşük. Mevcut: {current}, minimum: {minimum}")


class ForbiddenBidError(Exception):
    """Satıcı kendi ilanına teklif veremez."""

    def __init__(self, message: str = "Kendi ilanınıza teklif veremezsiniz.") -> None:
        self.message = message
        super().__init__(message)


class InvalidTokenError(Exception):
    """Geçersiz veya süresi dolmuş JWT."""

    def __init__(self, detail: str = "Geçersiz veya süresi dolmuş token.") -> None:
        self.detail = detail
        super().__init__(detail)
