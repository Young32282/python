"""经营看板路由"""

from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/dashboard", tags=["经营看板"])

ALLOWED_ROLES = ("manager", "regional")


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    """权限检查：manager 及以上"""
    if current_user.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员及以上角色",
        )
    return current_user


def _store_filter(query, current_user: User):
    """根据用户 store_id 添加门店过滤条件"""
    if current_user.store_id == 0:
        return query  # regional 看全部
    return query.filter(Order.store_id == current_user.store_id)


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """获取今日经营概览"""
    today = date.today()
    yesterday = today - timedelta(days=1)

    # 今日已完成订单
    today_query = db.query(Order).filter(
        Order.status == "completed",
        func.date(Order.created_at) == today,
    )
    today_query = _store_filter(today_query, current_user)
    today_orders_list = today_query.all()

    today_sales = sum(o.payment_amount for o in today_orders_list)
    today_orders = len(today_orders_list)
    avg_price = round(today_sales / today_orders, 2) if today_orders > 0 else 0

    # 会员消费占比
    member_sales = sum(o.payment_amount for o in today_orders_list if o.member_id is not None)
    member_ratio = round(member_sales / today_sales, 2) if today_sales > 0 else 0

    # 昨日销售额
    yesterday_query = db.query(Order).filter(
        Order.status == "completed",
        func.date(Order.created_at) == yesterday,
    )
    yesterday_query = _store_filter(yesterday_query, current_user)
    yesterday_orders_list = yesterday_query.all()
    yesterday_sales = sum(o.payment_amount for o in yesterday_orders_list)

    # 环比增长
    if yesterday_sales > 0:
        sales_growth = round((today_sales - yesterday_sales) / yesterday_sales, 2)
    else:
        sales_growth = 0

    # 库存预警统计
    inventory_query = db.query(Inventory)
    if current_user.store_id != 0:
        inventory_query = inventory_query.filter(Inventory.store_id == current_user.store_id)

    warning_count = inventory_query.filter(
        Inventory.quantity <= Inventory.safety_stock,
        Inventory.quantity > 0
    ).count()
    shortage_count = inventory_query.filter(
        Inventory.quantity <= 0
    ).count()

    # 动态预警：库存>安全线但近7天日均消耗速度快的商品
    seven_days_ago = today - timedelta(days=7)
    recent_sales_query = db.query(
        OrderItem.product_id,
        func.sum(OrderItem.quantity).label("total_sold")
    ).join(Order, Order.id == OrderItem.order_id).filter(
        Order.status == "completed",
        func.date(Order.created_at) >= seven_days_ago,
    )
    if current_user.store_id != 0:
        recent_sales_query = recent_sales_query.filter(Order.store_id == current_user.store_id)
    recent_sales_query = recent_sales_query.group_by(OrderItem.product_id)
    recent_sales = {row.product_id: row.total_sold for row in recent_sales_query.all()}

    # 找出库存>安全线但日均消耗量使得库存不足以支撑5天的商品
    fast_moving_query = db.query(Inventory).filter(
        Inventory.quantity > Inventory.safety_stock
    )
    if current_user.store_id != 0:
        fast_moving_query = fast_moving_query.filter(Inventory.store_id == current_user.store_id)
    inv_items = fast_moving_query.all()

    fast_moving_count = 0
    for inv_item in inv_items:
        sold = recent_sales.get(inv_item.product_id, 0)
        daily_avg = sold / 7.0
        if daily_avg > 0 and inv_item.quantity / daily_avg <= 5:
            fast_moving_count += 1

    return {
        "today_sales": round(today_sales, 2),
        "today_orders": today_orders,
        "avg_price": avg_price,
        "member_ratio": member_ratio,
        "yesterday_sales": round(yesterday_sales, 2),
        "sales_growth": sales_growth,
        "warning_count": warning_count,
        "shortage_count": shortage_count,
        "fast_moving_count": fast_moving_count,
    }


@router.get("/trend")
def get_trend(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """获取近N天销售趋势"""
    today = date.today()
    start_date = today - timedelta(days=days - 1)

    # 查询每日汇总
    query = db.query(
        func.date(Order.created_at).label("order_date"),
        func.sum(Order.payment_amount).label("amount"),
        func.count(Order.id).label("order_count"),
    ).filter(
        Order.status == "completed",
        func.date(Order.created_at) >= start_date,
        func.date(Order.created_at) <= today,
    )

    if current_user.store_id != 0:
        query = query.filter(Order.store_id == current_user.store_id)

    query = query.group_by(func.date(Order.created_at))
    raw_data = query.all()

    # 构建日期映射
    data_map = {}
    for row in raw_data:
        d = row.order_date
        if isinstance(d, str):
            d = d  # SQLite 返回字符串
        else:
            d = d.isoformat()
        data_map[d] = {
            "amount": round(float(row.amount), 2),
            "order_count": int(row.order_count),
        }

    # 补齐所有日期
    result = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        d_str = d.isoformat()
        if d_str in data_map:
            result.append({
                "date": d_str,
                "amount": data_map[d_str]["amount"],
                "order_count": data_map[d_str]["order_count"],
            })
        else:
            result.append({"date": d_str, "amount": 0, "order_count": 0})

    return result


@router.get("/category-share")
def get_category_share(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """获取品类销售占比（最近7天）"""
    today = date.today()
    start_date = today - timedelta(days=6)

    # 联表查询：OrderItem -> Product 获取 category
    query = db.query(
        Product.category,
        func.sum(OrderItem.subtotal).label("total_amount"),
    ).join(
        OrderItem, OrderItem.product_id == Product.id
    ).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        Order.status == "completed",
        func.date(Order.created_at) >= start_date,
        func.date(Order.created_at) <= today,
    )

    if current_user.store_id != 0:
        query = query.filter(Order.store_id == current_user.store_id)

    query = query.group_by(Product.category).order_by(func.sum(OrderItem.subtotal).desc())
    raw_data = query.all()

    # 计算总额和百分比
    grand_total = sum(float(row.total_amount) for row in raw_data) if raw_data else 0

    result = []
    for row in raw_data:
        amount = round(float(row.total_amount), 2)
        percentage = round(amount / grand_total, 2) if grand_total > 0 else 0
        result.append({
            "category": row.category,
            "total_amount": amount,
            "percentage": percentage,
        })

    return result


@router.get("/store-compare")
def get_store_compare(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """获取各门店对比数据（仅区域经理可用）"""
    if current_user.store_id != 0:
        raise HTTPException(status_code=403, detail="仅区域经理可查看多门店对比")

    today = date.today()
    seven_days_ago = today - timedelta(days=6)

    # 查询各门店近7天的销售数据
    store_stats = db.query(
        Order.store_id,
        func.sum(Order.payment_amount).label("total_sales"),
        func.count(Order.id).label("order_count"),
    ).filter(
        Order.status == "completed",
        func.date(Order.created_at) >= seven_days_ago,
        func.date(Order.created_at) <= today,
    ).group_by(Order.store_id).all()

    # 门店名称映射
    store_names = {1: "门店1（旗舰店）", 2: "门店2（社区店）"}

    result = []
    for row in store_stats:
        total_sales = round(float(row.total_sales), 2) if row.total_sales else 0
        order_count = int(row.order_count) if row.order_count else 0
        avg_price = round(total_sales / order_count, 2) if order_count > 0 else 0
        result.append({
            "store_id": row.store_id,
            "store_name": store_names.get(row.store_id, f"门店{row.store_id}"),
            "total_sales": total_sales,
            "order_count": order_count,
            "avg_price": avg_price,
        })

    # 按销售额降序
    result.sort(key=lambda x: x["total_sales"], reverse=True)
    return result


@router.get("/store-trends")
def get_store_trends(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """获取各门店独立销售趋势（仅区域经理）"""
    if current_user.store_id != 0:
        raise HTTPException(status_code=403, detail="仅区域经理可查看")

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    # 查询各门店每日汇总
    query = db.query(
        Order.store_id,
        func.date(Order.created_at).label("order_date"),
        func.sum(Order.payment_amount).label("amount"),
        func.count(Order.id).label("order_count"),
    ).filter(
        Order.status == "completed",
        func.date(Order.created_at) >= start_date,
        func.date(Order.created_at) <= today,
    ).group_by(Order.store_id, func.date(Order.created_at))

    raw_data = query.all()

    # 按门店组织数据
    store_names = {1: "门店1（旗舰店）", 2: "门店2（社区店）"}
    store_data = {}
    for row in raw_data:
        sid = row.store_id
        if sid not in store_data:
            store_data[sid] = {"store_name": store_names.get(sid, f"门店{sid}"), "data": {}}
        d = row.order_date if isinstance(row.order_date, str) else row.order_date.isoformat()
        store_data[sid]["data"][d] = {
            "amount": round(float(row.amount), 2),
            "order_count": int(row.order_count),
        }

    # 补齐日期
    result = []
    for sid, info in store_data.items():
        trend = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            d_str = d.isoformat()
            if d_str in info["data"]:
                trend.append({"date": d_str, **info["data"][d_str]})
            else:
                trend.append({"date": d_str, "amount": 0, "order_count": 0})
        result.append({
            "store_id": sid,
            "store_name": info["store_name"],
            "trend": trend,
        })

    return result


@router.get("/store-inventory")
def get_store_inventory_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """获取各门店库存概况（仅区域经理）"""
    if current_user.store_id != 0:
        raise HTTPException(status_code=403, detail="仅区域经理可查看")

    from sqlalchemy import case

    results = db.query(
        Inventory.store_id,
        func.count(Inventory.id).label("total_items"),
        func.sum(case((Inventory.quantity <= 0, 1), else_=0)).label("shortage_count"),
        func.sum(case((and_(Inventory.quantity > 0, Inventory.quantity <= Inventory.safety_stock), 1), else_=0)).label("warning_count"),
        func.sum(case((Inventory.quantity > Inventory.safety_stock, 1), else_=0)).label("normal_count"),
    ).group_by(Inventory.store_id).all()

    store_names = {1: "门店1（旗舰店）", 2: "门店2（社区店）"}

    return [{
        "store_id": row.store_id,
        "store_name": store_names.get(row.store_id, f"门店{row.store_id}"),
        "total_items": int(row.total_items),
        "shortage_count": int(row.shortage_count),
        "warning_count": int(row.warning_count),
        "normal_count": int(row.normal_count),
    } for row in results]
