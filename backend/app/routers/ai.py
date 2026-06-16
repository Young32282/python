"""AI辅助决策路由 - 经营洞察 + 补货建议（管理者决策辅助工具）"""

import math
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.order import Order, OrderItem
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.member import Member
from app.config import AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_TIMEOUT

router = APIRouter(prefix="/ai", tags=["AI辅助"])

# ═══════════════════════════════════════════════════════════════
# AI搭配推荐
# 策略：优先调用DeepSeek大模型，超时或失败时降级为规则推荐
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """你是优尚服饰门店的智能导购助手。根据顾客购物车中的商品，给出搭配推荐。
要求：
1. 推荐要具体到商品类型（如"浅色修身牛仔裤"而非泛泛的"裤子"）
2. 简短说明搭配理由或适用场景
3. 控制在50字以内
4. 语气亲切自然，像真实店员在推荐"""

# 品类搭配规则矩阵（AI降级时使用）
PAIRING_RULES = {
    "T恤": {"pair": "裤装", "text": "搭配一条修身牛仔裤，休闲时尚两不误"},
    "衬衫": {"pair": "裤装", "text": "搭配西裤或休闲长裤，商务通勤皆宜"},
    "裤装": {"pair": "T恤", "text": "搭配纯色圆领T恤，简约舒适"},
    "外套": {"pair": "衬衫", "text": "内搭轻薄衬衫，层次感拉满"},
    "配饰": {"pair": "外套", "text": "搭配外套点缀，整体造型更出彩"},
}


def get_smart_fallback(categories: list) -> str:
    """基于购物车品类生成智能规则推荐（AI不可用时的降级方案）"""
    existing = set(categories)
    # 优先推荐购物车中缺少的搭配品类
    for cat in categories:
        if cat in PAIRING_RULES:
            rule = PAIRING_RULES[cat]
            if rule["pair"] not in existing:
                return f"推荐搭配{rule['pair']}：{rule['text']}"
    # 购物车品类已齐全
    if len(categories) >= 3:
        return "搭配齐全！这套适合周末休闲出行，舒适有型"
    return "今日新品已上架，欢迎选购搭配"


@router.post("/recommend")
async def ai_recommend(data: dict, current_user=Depends(get_current_user)):
    """
    AI搭配推荐
    - 正常模式：调用DeepSeek大模型生成个性化推荐
    - 降级模式：基于品类搭配规则矩阵生成推荐（AI不可用时自动切换）
    """
    cart_items = data.get("cart_items", [])
    if not cart_items:
        return {"recommendation": "添加商品后即可获得搭配推荐", "source": "fallback"}

    categories = list(set(item.get("category", "") for item in cart_items))
    items_desc = "、".join(f"{item.get('name', '')}" for item in cart_items[:5])

    # 尝试调用AI大模型
    if AI_API_KEY and AI_API_KEY != "sk-placeholder":
        try:
            async with httpx.AsyncClient(timeout=AI_TIMEOUT) as client:
                resp = await client.post(
                    f"{AI_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {AI_API_KEY}"},
                    json={
                        "model": AI_MODEL,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"顾客购物车有：{items_desc}。请给出一个搭配推荐。"}
                        ],
                        "max_tokens": 100,
                        "temperature": 0.7,
                    }
                )
                if resp.status_code == 200:
                    result = resp.json()
                    text = result["choices"][0]["message"]["content"].strip()
                    return {"recommendation": text, "source": "ai"}
        except Exception:
            pass  # 超时或异常，自动降级到规则推荐

    # 降级：智能规则推荐
    fallback_text = get_smart_fallback(categories)
    return {"recommendation": fallback_text, "source": "fallback"}


# ═══════════════════════════════════════════════════════════════
# 补货建议（规则计算 + AI文案增强）
# 策略：基于近7天销售数据规则计算补货量，调用DeepSeek生成自然语言建议文案
# 降级：AI超时/失败时使用模板文案
# ═══════════════════════════════════════════════════════════════

RESTOCK_CONFIG = {
    "hot_threshold": 8,        # 日均>=8件视为热销
    "cold_threshold": 1,       # 日均<=1件视为滞销
    "hot_safety_days": 21,     # 热销品备货21天（防缺货）
    "normal_safety_days": 14,  # 正常品备货14天
    "cold_safety_days": 7,     # 滞销品仅备货7天（防积压）
}


RESTOCK_AI_PROMPT = """你是零售门店补货顾问。根据以下数据给出简短的补货建议（30字内）：
- 商品日均销量：{daily_avg}件
- 当前库存：{current_qty}件
- 建议安全周期：{safety_days}天
- 建议补货量：{suggest_qty}件
要求：纯文本，不要markdown格式，语言简练有指导性。"""


@router.post("/restock-suggest")
async def ai_restock_suggest(data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    补货建议（规则计算 + AI文案生成）
    算法：根据近7天日均销量 × 安全周期天数 - 当前库存 = 建议补货量
    差异化策略：热销品用更长周期避免缺货，滞销品用更短周期防止积压
    AI增强：调用DeepSeek生成更自然的补货理由文案，失败时降级为模板文案
    """
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")

    product_id = data.get("product_id")
    if not product_id:
        raise HTTPException(400, "缺少product_id")

    store_id = current_user.store_id if current_user.store_id != 0 else 1

    # 查询近7天该商品在该门店的总销量
    seven_days_ago = datetime.now() - timedelta(days=7)
    total_sold = db.query(func.coalesce(func.sum(OrderItem.quantity), 0)).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        OrderItem.product_id == product_id,
        Order.store_id == store_id,
        Order.status == "completed",
        Order.created_at >= seven_days_ago
    ).scalar()

    daily_avg = total_sold / 7.0

    # 当前库存与安全线
    inv = db.query(Inventory).filter(
        Inventory.product_id == product_id,
        Inventory.store_id == store_id
    ).first()
    current_qty = inv.quantity if inv else 0
    safety_stock = inv.safety_stock if inv else 10

    # 根据周转率选择差异化安全周期
    if daily_avg >= RESTOCK_CONFIG["hot_threshold"]:
        safety_days = RESTOCK_CONFIG["hot_safety_days"]
    elif daily_avg <= RESTOCK_CONFIG["cold_threshold"]:
        safety_days = RESTOCK_CONFIG["cold_safety_days"]
    else:
        safety_days = RESTOCK_CONFIG["normal_safety_days"]

    # 计算建议补货量：目标库存 = max(日均×安全天数, 安全线)
    target_qty = max(math.ceil(daily_avg * safety_days), safety_stock)
    suggest_qty = max(1, target_qty - current_qty)

    # 生成差异化理由文案（降级模板）
    if daily_avg >= RESTOCK_CONFIG["hot_threshold"]:
        fallback_reason = f"🔥热销品！近7天日均{daily_avg:.1f}件，当前仅剩{current_qty}件，建议加急补货{suggest_qty}件避免缺货"
    elif daily_avg <= RESTOCK_CONFIG["cold_threshold"]:
        fallback_reason = f"⚠️低周转商品。近7天日均{daily_avg:.1f}件，谨慎补货{suggest_qty}件即可，注意库存积压风险"
    else:
        fallback_reason = f"📊正常周转。近7天日均{daily_avg:.1f}件，按{safety_days}天安全周期建议补货{suggest_qty}件"

    # 尝试调用DeepSeek生成更自然的补货建议文案
    reason = fallback_reason
    if AI_API_KEY and AI_API_KEY != "sk-placeholder":
        try:
            prompt = RESTOCK_AI_PROMPT.format(
                daily_avg=round(daily_avg, 1),
                current_qty=current_qty,
                safety_days=safety_days,
                suggest_qty=suggest_qty
            )
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.post(
                    f"{AI_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {AI_API_KEY}"},
                    json={
                        "model": AI_MODEL,
                        "messages": [
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": "请给出补货建议。"}
                        ],
                        "max_tokens": 60,
                        "temperature": 0.7,
                    }
                )
                if resp.status_code == 200:
                    result = resp.json()
                    ai_text = result["choices"][0]["message"]["content"].strip()
                    if ai_text:
                        reason = ai_text
        except Exception:
            pass  # 超时或异常，使用降级模板文案

    return {
        "suggest_qty": suggest_qty,
        "daily_avg": round(daily_avg, 1),
        "current_qty": current_qty,
        "safety_days": safety_days,
        "reason": reason,
    }


# ═══════════════════════════════════════════════════════════════
# AI经营洞察（Dashboard使用）
# 策略：根据角色（店长/区域经理）差异化数据收集和prompt
# 降级：AI不可用时返回基于规则的简单分析（同样分角色）
# ═══════════════════════════════════════════════════════════════

# 店长版本 - 关注本门店具体运营细节
INSIGHT_PROMPT_MANAGER = """你是一个门店运营顾问。根据以下本门店数据，给出具体可执行的运营建议。
关注：具体商品表现、库存状况、补货时机、促销效果、客流与客单价变化。
要求：
1. 分析要基于数据，指出具体商品和品类的异常
2. 给出可执行的建议（如"某商品需紧急补货"、"建议对某品类启动促销"等）
3. 控制在3-5条，每条一行
4. 用数字说话，具体到商品名称
5. 纯文本输出，不要使用markdown格式（不要**加粗**、不要#标题、不要列表符号如1.或-）
6. 每条建议以emoji开头，一行一条"""

# 区域经理版本 - 关注跨门店对比和战略方向
INSIGHT_PROMPT_REGIONAL = """你是一个零售区域战略分析师。根据以下多门店汇总数据，给出区域运营策略建议。
关注：门店间对比、品类战略、资源调配、整体增长方向、会员发展情况。
要求：
1. 分析门店间差异，指出表现优/差的门店
2. 给出品类策略建议（哪个品类加大投入、哪个收缩）
3. 给出区域资源调配建议
4. 控制在4-6条，每条一行
5. 纯文本输出，不要使用markdown格式（不要**加粗**、不要#标题、不要列表符号如1.或-）
6. 每条建议以emoji开头，一行一条"""


@router.get("/insight")
async def get_ai_insight(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    AI经营洞察（角色差异化）
    - 店长：本门店具体运营细节、商品表现、库存预警、补货/促销建议
    - 区域经理：跨门店对比、品类战略、资源调配、会员发展
    """
    if current_user.role not in ["manager", "regional"]:
        raise HTTPException(403, "无权限")

    is_regional = current_user.role == "regional"
    store_id = None if is_regional else current_user.store_id

    # ─── 通用数据收集 ───────────────────────────────────────────
    seven_days_ago = datetime.now() - timedelta(days=7)
    fourteen_days_ago = datetime.now() - timedelta(days=14)

    # 近7天销售总额
    sales_query = db.query(func.coalesce(func.sum(Order.payment_amount), 0)).filter(
        Order.status == "completed",
        Order.created_at >= seven_days_ago
    )
    if store_id:
        sales_query = sales_query.filter(Order.store_id == store_id)
    recent_sales = sales_query.scalar()

    # 前7天销售总额（用于环比）
    prev_sales_query = db.query(func.coalesce(func.sum(Order.payment_amount), 0)).filter(
        Order.status == "completed",
        Order.created_at >= fourteen_days_ago,
        Order.created_at < seven_days_ago
    )
    if store_id:
        prev_sales_query = prev_sales_query.filter(Order.store_id == store_id)
    prev_sales = prev_sales_query.scalar()

    # 近7天订单数
    order_count_query = db.query(func.count(Order.id)).filter(
        Order.status == "completed",
        Order.created_at >= seven_days_ago
    )
    if store_id:
        order_count_query = order_count_query.filter(Order.store_id == store_id)
    order_count = order_count_query.scalar()

    # 库存预警数
    warning_query = db.query(Inventory).filter(Inventory.quantity <= 10, Inventory.quantity > 0)
    if store_id:
        warning_query = warning_query.filter(Inventory.store_id == store_id)
    warning_count = warning_query.count()

    # 缺货数
    shortage_query = db.query(Inventory).filter(Inventory.quantity <= 0)
    if store_id:
        shortage_query = shortage_query.filter(Inventory.store_id == store_id)
    shortage_count = shortage_query.count()

    # 品类销售统计（近7天）
    category_sales = db.query(
        Product.category,
        func.sum(OrderItem.subtotal).label("total")
    ).join(
        OrderItem, OrderItem.product_id == Product.id
    ).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        Order.status == "completed",
        Order.created_at >= seven_days_ago
    )
    if store_id:
        category_sales = category_sales.filter(Order.store_id == store_id)
    category_sales = category_sales.group_by(Product.category).all()

    sales_change = ((recent_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
    avg_order = recent_sales / order_count if order_count > 0 else 0
    category_text = "、".join(f"{cat}(¥{total:.0f})" for cat, total in category_sales[:5])

    # ─── 角色差异化数据 & Prompt ─────────────────────────────────
    if is_regional:
        # 区域经理：额外收集跨门店数据
        # 各门店销售额对比
        store_sales = db.query(
            Order.store_id,
            func.sum(Order.payment_amount).label("total_sales"),
            func.count(Order.id).label("order_cnt")
        ).filter(
            Order.status == "completed",
            Order.created_at >= seven_days_ago
        ).group_by(Order.store_id).all()
        store_sales_text = "、".join(
            f"门店{s.store_id}(销售¥{s.total_sales:.0f}/{s.order_cnt}单)" for s in store_sales
        )

        # 品类趋势对比（本周 vs 上周）
        prev_category_sales = db.query(
            Product.category,
            func.sum(OrderItem.subtotal).label("total")
        ).join(
            OrderItem, OrderItem.product_id == Product.id
        ).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.status == "completed",
            Order.created_at >= fourteen_days_ago,
            Order.created_at < seven_days_ago
        ).group_by(Product.category).all()
        prev_cat_dict = {cat: total for cat, total in prev_category_sales}
        category_trend_parts = []
        for cat, total in category_sales:
            prev_total = prev_cat_dict.get(cat, 0)
            if prev_total > 0:
                change = (total - prev_total) / prev_total * 100
                direction = "↑" if change >= 0 else "↓"
                category_trend_parts.append(f"{cat}{direction}{abs(change):.0f}%")
            else:
                category_trend_parts.append(f"{cat}(新增)")
        category_trend_text = "、".join(category_trend_parts)

        # 整体会员发展情况
        new_members_count = db.query(func.count(Member.id)).filter(
            Member.created_at >= seven_days_ago
        ).scalar()
        total_members = db.query(func.count(Member.id)).scalar()

        data_summary = f"""区域近7天经营数据汇总：
- 区域总销售额：¥{recent_sales:.0f}（环比{'增长' if sales_change >= 0 else '下降'}{abs(sales_change):.1f}%）
- 区域总订单数：{order_count}单，平均客单价：¥{avg_order:.0f}
- 各门店表现：{store_sales_text}
- 品类销售：{category_text}
- 品类趋势（环比）：{category_trend_text}
- 库存预警：{warning_count}件低于安全线，{shortage_count}件缺货
- 会员发展：本周新增{new_members_count}人，总会员{total_members}人"""

        system_prompt = INSIGHT_PROMPT_REGIONAL
    else:
        # 店长：额外收集本门店具体商品数据
        # 热销TOP5商品
        top_products = db.query(
            Product.name,
            func.sum(OrderItem.quantity).label("sold_qty")
        ).join(
            OrderItem, OrderItem.product_id == Product.id
        ).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.status == "completed",
            Order.created_at >= seven_days_ago,
            Order.store_id == store_id
        ).group_by(Product.name).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(5).all()
        top_text = "、".join(f"{name}({qty}件)" for name, qty in top_products)

        # 滞销商品（有库存但近7天0销量）
        sold_product_ids = db.query(OrderItem.product_id).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.status == "completed",
            Order.created_at >= seven_days_ago,
            Order.store_id == store_id
        ).distinct().subquery()

        slow_items = db.query(Product.name, Inventory.quantity).join(
            Inventory, Inventory.product_id == Product.id
        ).filter(
            Inventory.store_id == store_id,
            Inventory.quantity > 0,
            ~Product.id.in_(sold_product_ids)
        ).limit(5).all()
        slow_text = "、".join(f"{name}(库存{qty})" for name, qty in slow_items) if slow_items else "无"

        # 库存预警具体商品
        warning_items = db.query(Product.name, Inventory.quantity).join(
            Inventory, Inventory.product_id == Product.id
        ).filter(
            Inventory.store_id == store_id,
            Inventory.quantity <= 10,
            Inventory.quantity > 0
        ).order_by(Inventory.quantity.asc()).limit(5).all()
        warning_text = "、".join(f"{name}(剩{qty})" for name, qty in warning_items) if warning_items else "无"

        data_summary = f"""本门店近7天经营数据：
- 销售总额：¥{recent_sales:.0f}（环比{'增长' if sales_change >= 0 else '下降'}{abs(sales_change):.1f}%）
- 订单数：{order_count}单，客单价：¥{avg_order:.0f}
- 热销商品TOP5：{top_text}
- 滞销商品（7天零销量）：{slow_text}
- 库存预警商品：{warning_text}
- 缺货商品数：{shortage_count}件
- 品类销售：{category_text}"""

        system_prompt = INSIGHT_PROMPT_MANAGER

    # ─── 调用AI ─────────────────────────────────────────────────
    if AI_API_KEY and AI_API_KEY != "sk-placeholder":
        try:
            async with httpx.AsyncClient(timeout=AI_TIMEOUT) as client:
                resp = await client.post(
                    f"{AI_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {AI_API_KEY}"},
                    json={
                        "model": AI_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": data_summary + "\n\n请基于以上数据给出经营建议。"}
                        ],
                        "max_tokens": 400,
                        "temperature": 0.7,
                    }
                )
                if resp.status_code == 200:
                    result = resp.json()
                    text = result["choices"][0]["message"]["content"].strip()
                    return {"content": text, "source": "ai"}
        except Exception:
            pass

    # ─── 收集近7天各商品销量（用于快消预警） ─────────────────────────
    recent_sales_query = db.query(
        OrderItem.product_id,
        func.sum(OrderItem.quantity).label("total_sold")
    ).join(Order, Order.id == OrderItem.order_id).filter(
        Order.status == "completed",
        Order.created_at >= seven_days_ago,
    )
    if store_id:
        recent_sales_query = recent_sales_query.filter(Order.store_id == store_id)
    recent_sales_query = recent_sales_query.group_by(OrderItem.product_id)
    recent_sales = {row.product_id: row.total_sold for row in recent_sales_query.all()}

    # 查询库存（用于快消预警）
    store_inventory_query = db.query(Inventory)
    if store_id:
        store_inventory_query = store_inventory_query.filter(Inventory.store_id == store_id)
    store_inventory = store_inventory_query.all()

    # ─── 降级：规则分析（分角色） ─────────────────────────────────
    if is_regional:
        # 区域经理降级：门店对比和品类趋势
        lines = []
        if sales_change >= 10:
            lines.append(f"📈 区域销售增长{sales_change:.1f}%，整体势头向好")
        elif sales_change <= -10:
            lines.append(f"📉 区域销售下降{abs(sales_change):.1f}%，建议排查各门店问题并制定促销策略")
        else:
            lines.append(f"📊 区域销售平稳（环比{sales_change:.1f}%），可关注结构优化")

        # 门店对比
        if store_sales:
            best = max(store_sales, key=lambda s: s.total_sales)
            worst = min(store_sales, key=lambda s: s.total_sales)
            if best.store_id != worst.store_id:
                lines.append(f"🏆 门店{best.store_id}表现最佳(¥{best.total_sales:.0f})，门店{worst.store_id}需重点关注(¥{worst.total_sales:.0f})")

        # 品类趋势
        if category_trend_parts:
            lines.append(f"📦 品类趋势：{category_trend_text}，建议加大增长品类投入")

        if new_members_count > 0:
            lines.append(f"👥 本周新增会员{new_members_count}人，总计{total_members}人，持续推进会员拉新")

        if shortage_count > 0:
            lines.append(f"🚨 区域内{shortage_count}件商品缺货，建议协调调拨或加急补货")

        # 动态预警：库存充足但消耗过快
        fast_moving_items = []
        for inv_item in store_inventory:
            if inv_item.quantity > inv_item.safety_stock:
                sold = recent_sales.get(inv_item.product_id, 0)
                daily_avg = sold / 7.0
                if daily_avg > 0 and inv_item.quantity / daily_avg <= 5:
                    product = db.query(Product).filter(Product.id == inv_item.product_id).first()
                    if product:
                        days_left = round(inv_item.quantity / daily_avg, 1)
                        fast_moving_items.append(f"{product.name}(剩{inv_item.quantity}件,约{days_left}天)")

        if fast_moving_items:
            lines.append(f"⚡ 快消预警：{','.join(fast_moving_items[:3])}库存消耗过快，虽高于安全线但即将不足，建议提前补货")

        if not lines:
            lines.append("✅ 区域经营状况良好，暂无异常需要关注")

        return {"content": "\n".join(lines), "source": "fallback"}
    else:
        # 店长降级：具体到商品和库存的建议
        lines = []
        if sales_change >= 10:
            lines.append(f"📈 本店销售增长{sales_change:.1f}%，注意热销品库存是否充足")
        elif sales_change <= -10:
            lines.append(f"📉 本店销售下降{abs(sales_change):.1f}%，建议对滞销商品启动促销")
        else:
            lines.append(f"📊 销售平稳（环比{sales_change:.1f}%），经营状况正常")

        if shortage_count > 0:
            lines.append(f"🚨 {shortage_count}件商品已缺货，建议立即发起补货申请")

        if warning_items:
            warning_names = "、".join(f"{name}(剩{qty})" for name, qty in warning_items[:3])
            lines.append(f"⚠️ 库存预警：{warning_names}，尽快安排补货")
        elif warning_count > 0:
            lines.append(f"⚠️ {warning_count}件商品库存低于安全线，关注补货节奏")

        if top_products:
            top_names = "、".join(f"{name}" for name, _ in top_products[:3])
            lines.append(f"🔥 热销商品：{top_names}，确保库存充足并考虑关联陈列")

        if slow_items:
            slow_names = "、".join(f"{name}" for name, _ in slow_items[:3])
            lines.append(f"💤 滞销提醒：{slow_names}近7天零销量，建议促销清仓或调整陈列")

        # 动态预警：库存充足但消耗过快
        fast_moving_items = []
        for inv_item in store_inventory:
            if inv_item.quantity > inv_item.safety_stock:
                sold = recent_sales.get(inv_item.product_id, 0)
                daily_avg = sold / 7.0
                if daily_avg > 0 and inv_item.quantity / daily_avg <= 5:
                    product = db.query(Product).filter(Product.id == inv_item.product_id).first()
                    if product:
                        days_left = round(inv_item.quantity / daily_avg, 1)
                        fast_moving_items.append(f"{product.name}(剩{inv_item.quantity}件,约{days_left}天)")

        if fast_moving_items:
            lines.append(f"⚡ 快消预警：{','.join(fast_moving_items[:3])}库存消耗过快，虽高于安全线但即将不足，建议提前补货")

        if avg_order > 0:
            lines.append(f"💰 客单价¥{avg_order:.0f}，{'表现优秀' if avg_order > 200 else '可通过搭配推荐提升'}")

        if not lines:
            lines.append("✅ 当前经营状况良好，暂无异常需要关注")

        return {"content": "\n".join(lines), "source": "fallback"}
