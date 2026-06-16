"""POS收银路由"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
import json

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.promotion import Promotion
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.member import Member
from app.models.user import User
from app.services.pos_service import create_order_logic

router = APIRouter(tags=["pos"])


@router.get("/promotions/active")
def get_active_promotions(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """获取当前生效的促销活动"""
    today = date.today().isoformat()
    promos = (
        db.query(Promotion)
        .filter(
            Promotion.status == "active",
            Promotion.start_date <= today,
            Promotion.end_date >= today,
        )
        .all()
    )
    return [
        {
            "id": p.id,
            "name": p.name,
            "type": p.type,
            "rules": json.loads(p.rules_json),
        }
        for p in promos
    ]


@router.post("/orders")
def create_order(
    order_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """创建订单"""
    # order_data: {"items": [{"product_id": 1, "quantity": 2}], "member_id": null, "payment_method": "wechat"}
    result = create_order_logic(db, order_data, current_user)
    return result


@router.get("/orders")
def get_orders(
    today: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取订单列表（支持today参数筛选今日订单）"""
    query = db.query(Order)

    # 如果传了today参数，仅查今日订单（POS页面用）
    if today == "true":
        if current_user.role not in ["manager", "regional"]:
            raise HTTPException(403, "无权限")
        today_start = datetime.combine(date.today(), datetime.min.time())
        query = query.filter(Order.created_at >= today_start)

    # 门店过滤
    if current_user.store_id and current_user.store_id != 0:
        query = query.filter(Order.store_id == current_user.store_id)

    orders = query.order_by(Order.id.desc()).limit(100).all()

    # 获取收银员姓名
    result = []
    for o in orders:
        cashier = db.query(User).filter(User.id == o.cashier_id).first()
        # 获取订单明细
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        items_data = []
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            items_data.append(
                {
                    "product_id": item.product_id,
                    "product_name": product.name if product else "未知商品",
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal,
                }
            )
        result.append(
            {
                "id": o.id,
                "order_no": o.order_no,
                "total_amount": o.total_amount,
                "discount_amount": o.discount_amount,
                "payment_amount": o.payment_amount,
                "payment_method": o.payment_method,
                "status": o.status,
                "member_id": o.member_id,
                "cashier_name": cashier.real_name if cashier else "",
                "created_at": o.created_at.isoformat() if o.created_at else "",
                "items": items_data,
            }
        )
    return result


@router.put("/orders/{order_id}/void")
def void_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """作废订单（manager权限）"""
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "订单不存在")
    if order.status != "completed":
        raise HTTPException(400, "只能作废已完成订单")
    if current_user.store_id != 0 and order.store_id != current_user.store_id:
        raise HTTPException(403, "无权操作其他门店订单")

    # 回滚库存
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    for item in items:
        inv = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == item.product_id,
                Inventory.store_id == order.store_id,
            )
            .first()
        )
        if inv:
            inv.quantity += item.quantity

    # 回滚会员积分和消费额（但不触发降级）
    if order.member_id:
        member = db.query(Member).filter(Member.id == order.member_id).first()
        if member:
            member.points = max(0, member.points - int(order.payment_amount))
            member.total_spent = max(0, member.total_spent - order.payment_amount)
            member.total_orders = max(0, member.total_orders - 1)
            # 不触发降级！会员等级只升不降

    order.status = "voided"
    db.commit()
    return {"message": "订单已作废"}
