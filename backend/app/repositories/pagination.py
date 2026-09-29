from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.schemas.common import PageQuery


def paginate(db: Session, stmt: Select[Any], query: PageQuery) -> dict[str, Any]:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    offset = (query.page - 1) * query.page_size
    items = db.scalars(stmt.limit(query.page_size).offset(offset)).all()
    return {"items": items, "total": total, "page": query.page, "page_size": query.page_size}
