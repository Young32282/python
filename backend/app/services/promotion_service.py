"""促销计算服务"""

import json
from sqlalchemy.orm import Session
from datetime import date

from app.models.promotion import Promotion


def get_active_promotions(db: Session):
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


def calculate_promotion_discount(promos, total_amount: float, category_totals: dict):
    """计算促销优惠金额（取最大优惠）"""
    promo_discount = 0
    for p in promos:
        rules = json.loads(p.rules_json) if isinstance(p.rules_json, str) else p.get("rules", {})
        promo_type = p.type if hasattr(p, "type") else p.get("type", "")

        if promo_type == "full_reduction":
            threshold = rules.get("threshold", 0)
            reduction = rules.get("reduction", 0)
            if total_amount >= threshold:
                promo_discount = max(promo_discount, reduction)
        elif promo_type == "percentage":
            cat = rules.get("category", "")
            disc = rules.get("discount", 1.0)
            if cat in category_totals:
                saving = category_totals[cat] * (1 - disc)
                promo_discount = max(promo_discount, saving)

    return round(promo_discount, 2)
