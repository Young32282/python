"""会员管理路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.member import Member
from app.models.order import Order, OrderItem

router = APIRouter(prefix="/members", tags=["members"])

MEMBER_LEVEL_RULES = {
    "normal":  {"min_spent": 0,     "discount": 1.0,  "points_rate": 1},
    "silver":  {"min_spent": 1000,  "discount": 0.98, "points_rate": 1.2},
    "gold":    {"min_spent": 5000,  "discount": 0.95, "points_rate": 2},
    "diamond": {"min_spent": 15000, "discount": 0.90, "points_rate": 3},
}
LEVEL_ORDER = ["normal", "silver", "gold", "diamond"]


@router.get("/identify")
def identify_member(phone: str = Query(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """POS收银时通过手机号识别会员"""
    member = db.query(Member).filter(Member.phone == phone).first()
    if not member:
        raise HTTPException(404, "会员不存在")
    level_info = MEMBER_LEVEL_RULES.get(member.level, MEMBER_LEVEL_RULES["normal"])
    return {
        "id": member.id,
        "name": member.name,
        "phone": member.phone,
        "level": member.level,
        "points": member.points,
        "discount": level_info["discount"]
    }


@router.get("")
def search_members(keyword: str = Query(""), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """会员列表搜索"""
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")

    query = db.query(Member)
    if keyword:
        query = query.filter((Member.phone.contains(keyword)) | (Member.name.contains(keyword)))

    members = query.limit(50).all()
    return [{
        "id": m.id,
        "phone": m.phone,
        "name": m.name,
        "level": m.level,
        "points": m.points,
        "total_spent": m.total_spent,
        "total_orders": m.total_orders,
        "created_at": m.created_at.isoformat() if m.created_at else ""
    } for m in members]


@router.get("/{member_id}")
def get_member_detail(member_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """会员详情"""
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")

    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(404, "会员不存在")

    # 计算下一等级信息
    current_idx = LEVEL_ORDER.index(member.level)
    if current_idx >= len(LEVEL_ORDER) - 1:
        next_level = None
        next_level_threshold = 0
        spent_to_next = 0
    else:
        next_level = LEVEL_ORDER[current_idx + 1]
        next_level_threshold = MEMBER_LEVEL_RULES[next_level]["min_spent"]
        spent_to_next = max(0, next_level_threshold - member.total_spent)

    level_info = MEMBER_LEVEL_RULES.get(member.level, MEMBER_LEVEL_RULES["normal"])

    return {
        "id": member.id,
        "phone": member.phone,
        "name": member.name,
        "level": member.level,
        "total_spent": member.total_spent,
        "total_orders": member.total_orders,
        "points": member.points,
        "preferences": member.preferences,
        "created_at": member.created_at.isoformat() if member.created_at else "",
        "level_updated_at": member.level_updated_at.isoformat() if member.level_updated_at else "",
        "next_level": next_level,
        "next_level_threshold": next_level_threshold,
        "spent_to_next": spent_to_next,
        "current_discount": level_info["discount"]
    }


@router.get("/{member_id}/orders")
def get_member_orders(member_id: int, page: int = Query(1), page_size: int = Query(10), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """会员历史订单"""
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")

    total = db.query(func.count(Order.id)).filter(Order.member_id == member_id).scalar()

    orders = db.query(Order).filter(Order.member_id == member_id).order_by(
        Order.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for o in orders:
        items_count = db.query(func.count(OrderItem.id)).filter(OrderItem.order_id == o.id).scalar()
        items.append({
            "order_no": o.order_no,
            "total_amount": o.total_amount,
            "discount_amount": o.discount_amount,
            "payment_amount": o.payment_amount,
            "payment_method": o.payment_method,
            "status": o.status,
            "created_at": o.created_at.isoformat() if o.created_at else "",
            "items_count": items_count
        })

    return {"total": total, "items": items}
