"""POS收银业务逻辑"""

from sqlalchemy.orm import Session
from datetime import date, datetime
from fastapi import HTTPException
import json

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.member import Member
from app.models.promotion import Promotion

MEMBER_LEVEL_RULES = {
    "normal": {"min_spent": 0, "discount": 1.0, "points_rate": 1},
    "silver": {"min_spent": 1000, "discount": 0.98, "points_rate": 1.2},
    "gold": {"min_spent": 5000, "discount": 0.95, "points_rate": 2},
    "diamond": {"min_spent": 15000, "discount": 0.90, "points_rate": 3},
}
LEVEL_ORDER = ["normal", "silver", "gold", "diamond"]


def create_order_logic(db: Session, order_data: dict, current_user):
    """创建订单核心逻辑"""
    items = order_data.get("items", [])
    member_id = order_data.get("member_id")
    payment_method = order_data.get("payment_method", "wechat")

    if not items:
        raise HTTPException(400, "购物车为空")

    store_id = current_user.store_id

    # 1. 验证库存并获取商品信息
    order_items_data = []
    total_amount = 0
    category_totals = {}  # 用于品类折扣计算

    for item in items:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product:
            raise HTTPException(400, f"商品ID {item['product_id']} 不存在")

        inv = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == product.id, Inventory.store_id == store_id
            )
            .first()
        )
        if not inv or inv.quantity < item["quantity"]:
            raise HTTPException(400, f"商品 {product.name} 库存不足")

        subtotal = product.price * item["quantity"]
        total_amount += subtotal
        order_items_data.append(
            {
                "product_id": product.id,
                "quantity": item["quantity"],
                "unit_price": product.price,
                "subtotal": subtotal,
            }
        )

        # 统计品类金额
        category_totals[product.category] = (
            category_totals.get(product.category, 0) + subtotal
        )

    # 2. 计算促销优惠
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

    promo_discount = 0
    for p in promos:
        rules = json.loads(p.rules_json)
        if p.type == "full_reduction":
            if total_amount >= rules["threshold"]:
                promo_discount = max(promo_discount, rules["reduction"])
        elif p.type == "percentage":
            cat = rules.get("category", "")
            disc = rules.get("discount", 1.0)
            if cat in category_totals:
                saving = category_totals[cat] * (1 - disc)
                promo_discount = max(promo_discount, saving)

    # 3. 计算会员折扣
    member_discount = 0
    member = None
    if member_id:
        member = db.query(Member).filter(Member.id == member_id).first()
        if member:
            level_info = MEMBER_LEVEL_RULES.get(
                member.level, MEMBER_LEVEL_RULES["normal"]
            )
            member_discount = total_amount * (1 - level_info["discount"])

    # 4. 取最大优惠（不叠加）
    discount_amount = round(max(promo_discount, member_discount), 2)
    payment_amount = round(total_amount - discount_amount, 2)

    # 5. 生成订单号
    today_str = date.today().strftime("%Y%m%d")
    count = db.query(Order).filter(Order.order_no.like(f"ORD{today_str}%")).count()
    order_no = f"ORD{today_str}{count + 1:04d}"

    # 6. 创建订单
    order = Order(
        order_no=order_no,
        store_id=store_id,
        member_id=member_id,
        total_amount=total_amount,
        discount_amount=discount_amount,
        payment_amount=payment_amount,
        payment_method=payment_method,
        status="completed",
        cashier_id=current_user.id,
        created_at=datetime.now(),
    )
    db.add(order)
    db.flush()

    # 7. 创建订单明细
    for item_data in order_items_data:
        db.add(OrderItem(order_id=order.id, **item_data))

    # 8. 扣减库存
    for item in items:
        inv = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == item["product_id"],
                Inventory.store_id == store_id,
            )
            .first()
        )
        inv.quantity -= item["quantity"]

    # 9. 更新会员
    member_level_up = False
    if member:
        level_info = MEMBER_LEVEL_RULES.get(
            member.level, MEMBER_LEVEL_RULES["normal"]
        )
        earned_points = int(payment_amount * level_info["points_rate"])
        member.points += earned_points
        member.total_spent += payment_amount
        member.total_orders += 1

        # 检查升级
        current_idx = LEVEL_ORDER.index(member.level)
        if current_idx < len(LEVEL_ORDER) - 1:
            next_level = LEVEL_ORDER[current_idx + 1]
            if member.total_spent >= MEMBER_LEVEL_RULES[next_level]["min_spent"]:
                member.level = next_level
                member.level_updated_at = datetime.now()
                member_level_up = True

    db.commit()

    return {
        "order_no": order_no,
        "total_amount": total_amount,
        "discount_amount": discount_amount,
        "payment_amount": payment_amount,
        "member_level_up": member_level_up,
    }
