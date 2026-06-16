"""库存管理与补货审批路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.restock import RestockRequest
from app.models.user import User
from app.models.order import Order, OrderItem

router = APIRouter(tags=["inventory"])


@router.get("/inventory")
def get_inventory(
    status: str = Query("all"),  # all/warning/shortage
    category: str = Query(""),
    keyword: str = Query(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")

    query = db.query(Inventory, Product).join(
        Product, Inventory.product_id == Product.id
    )

    # 门店过滤
    if current_user.store_id != 0:
        query = query.filter(Inventory.store_id == current_user.store_id)

    # 状态过滤
    if status == "warning":
        query = query.filter(
            Inventory.quantity > 0, Inventory.quantity < Inventory.safety_stock
        )
    elif status == "shortage":
        query = query.filter(Inventory.quantity == 0)
    elif status == "fast_moving":
        # 快消商品是库存>安全线的，不在SQL层面过滤，后面Python过滤
        query = query.filter(Inventory.quantity > Inventory.safety_stock)

    # 品类过滤
    if category:
        query = query.filter(Product.category == category)

    # 关键词搜索
    if keyword:
        query = query.filter(
            (Product.name.contains(keyword)) | (Product.sku.contains(keyword))
        )

    results = query.all()

    # 查询近7天各商品的销量
    today_date = date.today()
    seven_days_ago = today_date - timedelta(days=7)

    store_id_for_query = current_user.store_id if current_user.store_id != 0 else None

    recent_sales_q = db.query(
        OrderItem.product_id,
        func.sum(OrderItem.quantity).label("total_sold")
    ).join(Order, Order.id == OrderItem.order_id).filter(
        Order.status == "completed",
        func.date(Order.created_at) >= seven_days_ago,
    )
    if store_id_for_query:
        recent_sales_q = recent_sales_q.filter(Order.store_id == store_id_for_query)
    recent_sales_q = recent_sales_q.group_by(OrderItem.product_id)
    recent_sales = {row.product_id: row.total_sold for row in recent_sales_q.all()}

    items = []
    for inv, prod in results:
        if inv.quantity == 0:
            status_label = "缺货"
        elif inv.quantity < inv.safety_stock:
            status_label = "预警"
        else:
            status_label = "正常"

        # 快消判定：库存>安全线但不够支撑5天
        is_fast_moving = False
        if inv.quantity > inv.safety_stock:
            sold = recent_sales.get(prod.id, 0)
            daily_avg = sold / 7.0
            if daily_avg > 0 and inv.quantity / daily_avg <= 5:
                is_fast_moving = True
                status_label = "快消"

        items.append(
            {
                "id": inv.id,
                "product_id": prod.id,
                "product_name": prod.name,
                "sku": prod.sku,
                "category": prod.category,
                "quantity": inv.quantity,
                "safety_stock": inv.safety_stock,
                "status_label": status_label,
                "is_fast_moving": is_fast_moving,
            }
        )

    # 快消筛选在Python层面过滤
    if status == "fast_moving":
        items = [item for item in items if item["is_fast_moving"]]

    return items


@router.post("/restock-requests", status_code=201)
def create_restock_request(
    data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "manager":
        raise HTTPException(403, "只有店长可以发起补货")

    product_id = data.get("product_id")
    request_qty = data.get("request_qty")
    reason = data.get("reason", "")
    ai_suggest_qty = data.get("ai_suggest_qty")

    # 获取当前库存
    inv = (
        db.query(Inventory)
        .filter(
            Inventory.product_id == product_id,
            Inventory.store_id == current_user.store_id,
        )
        .first()
    )

    if not inv:
        raise HTTPException(404, "库存记录不存在")

    req = RestockRequest(
        store_id=current_user.store_id,
        product_id=product_id,
        current_qty=inv.quantity,
        request_qty=request_qty,
        ai_suggest_qty=ai_suggest_qty,
        reason=reason,
        status="pending",
        applicant_id=current_user.id,
        created_at=datetime.now(),
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return {"id": req.id, "status": "pending"}


@router.get("/restock-requests")
def get_restock_requests(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")

    query = (
        db.query(RestockRequest, Product, User)
        .join(Product, RestockRequest.product_id == Product.id)
        .join(User, RestockRequest.applicant_id == User.id)
    )

    if current_user.store_id != 0:
        query = query.filter(RestockRequest.store_id == current_user.store_id)

    results = query.order_by(RestockRequest.created_at.desc()).all()

    return [
        {
            "id": req.id,
            "product_name": prod.name,
            "sku": prod.sku,
            "current_qty": req.current_qty,
            "request_qty": req.request_qty,
            "ai_suggest_qty": req.ai_suggest_qty,
            "reason": req.reason,
            "status": req.status,
            "applicant_name": user.real_name,
            "created_at": req.created_at.isoformat() if req.created_at else "",
        }
        for req, prod, user in results
    ]


@router.post("/restock")
def restock_product(
    data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """执行补货：直接增加库存并记录"""
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")

    product_id = data.get("product_id")
    quantity = data.get("quantity")
    reason = data.get("reason", "")
    ai_suggest_qty = data.get("ai_suggest_qty")

    if not product_id or not quantity or quantity <= 0:
        raise HTTPException(400, "参数无效")

    store_id = current_user.store_id if current_user.store_id != 0 else data.get("store_id", 1)

    inv = (
        db.query(Inventory)
        .filter(
            Inventory.product_id == product_id,
            Inventory.store_id == store_id,
        )
        .first()
    )
    if not inv:
        raise HTTPException(404, "库存记录不存在")

    inv.quantity += quantity
    inv.updated_at = datetime.now()

    # 同时记录补货请求（状态直接设为completed）
    req = RestockRequest(
        store_id=store_id,
        product_id=product_id,
        current_qty=inv.quantity - quantity,  # 补货前的数量
        request_qty=quantity,
        ai_suggest_qty=ai_suggest_qty,
        reason=reason,
        status="completed",
        applicant_id=current_user.id,
        created_at=datetime.now(),
    )
    db.add(req)
    db.commit()

    return {
        "message": f"补货成功，当前库存: {inv.quantity}",
        "new_quantity": inv.quantity,
        "restock_qty": quantity,
    }


@router.get("/restock-history")
def get_restock_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取最近补货记录（最近5条已完成的）"""
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")

    query = (
        db.query(RestockRequest, Product)
        .join(Product, RestockRequest.product_id == Product.id)
        .filter(RestockRequest.status == "completed")
    )

    if current_user.store_id != 0:
        query = query.filter(RestockRequest.store_id == current_user.store_id)

    results = query.order_by(RestockRequest.created_at.desc()).limit(5).all()

    return [
        {
            "id": req.id,
            "product_name": prod.name,
            "quantity": req.request_qty,
            "created_at": req.created_at.strftime("%m-%d %H:%M") if req.created_at else "",
        }
        for req, prod in results
    ]


@router.put("/restock-requests/{request_id}")
def approve_restock(
    request_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "regional":
        raise HTTPException(403, "只有区域经理可以审批")

    req = db.query(RestockRequest).filter(RestockRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "申请不存在")
    if req.status != "pending":
        raise HTTPException(400, "该申请已处理")

    new_status = data.get("status")  # "approved" or "rejected"
    if new_status not in ["approved", "rejected"]:
        raise HTTPException(400, "状态无效")

    req.status = new_status

    # 批准后自动增加库存
    if new_status == "approved":
        inv = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == req.product_id,
                Inventory.store_id == req.store_id,
            )
            .first()
        )
        if inv:
            inv.quantity += req.request_qty
            inv.updated_at = datetime.now()

    db.commit()
    return {"message": f"已{'批准' if new_status == 'approved' else '驳回'}"}

