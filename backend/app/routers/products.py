"""商品路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.member import Member

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/search")
def search_products(
    keyword: str = Query(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    store_id = current_user.store_id if current_user.store_id != 0 else 1

    query = db.query(Product, Inventory.quantity).outerjoin(
        Inventory,
        and_(Inventory.product_id == Product.id, Inventory.store_id == store_id)
    ).filter(Product.status == "active")
    if keyword:
        query = query.filter(
            (Product.name.contains(keyword)) | (Product.sku.contains(keyword))
        )
    results = query.limit(20).all()
    return [
        {
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "price": p.price,
            "stock": qty if qty is not None else 0,
        }
        for p, qty in results
    ]


@router.get("/members/identify")
def identify_member(
    phone: str = Query(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """通过手机号识别会员"""
    if not phone:
        return None
    member = db.query(Member).filter(Member.phone == phone).first()
    if not member:
        return None
    return {
        "id": member.id,
        "name": member.name,
        "phone": member.phone,
        "level": member.level,
        "points": member.points,
        "total_spent": member.total_spent,
        "total_orders": member.total_orders,
    }
