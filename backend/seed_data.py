"""种子数据脚本 - 生成模拟真实运营约1个月的服饰门店数据"""

import sys
import os
import random
import json
from datetime import datetime, timedelta
from collections import defaultdict

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import (
    User, Product, Inventory, Member,
    Order, OrderItem, Promotion, RestockRequest,
)
from app.services.auth_service import hash_password

# 固定随机种子，保证可重复
random.seed(42)

# ═══════════════════════════════════════════════════════════════════
# 商品数据定义
# ═══════════════════════════════════════════════════════════════════

PRODUCTS_DATA = {
    "T恤": {
        "prefix": "TS",
        "price_range": (79, 199),
        "items": [
            "纯棉圆领基础款", "条纹短袖休闲款", "印花潮流T恤", "V领修身商务款",
            "宽松oversize款", "运动速干T恤", "polo领经典款", "撞色拼接款",
            "简约纯色百搭款", "字母印花街头款", "冰丝凉感夏季款", "重磅厚棉质感款",
        ],
    },
    "衬衫": {
        "prefix": "CS",
        "price_range": (159, 399),
        "items": [
            "牛津纺商务衬衫", "纯棉格纹休闲衬衫", "免烫修身正装衬衫", "亚麻透气衬衫",
            "法兰绒保暖衬衫", "竖条纹职场衬衫", "纯色百搭基础衬衫", "牛仔水洗衬衫",
            "弹力修身韩版衬衫", "宽松oversize衬衫", "微光泽丝滑衬衫", "立领中国风衬衫",
        ],
    },
    "裤装": {
        "prefix": "KZ",
        "price_range": (199, 499),
        "items": [
            "直筒牛仔裤经典蓝", "修身小脚休闲裤", "宽松工装裤军绿", "西裤商务正装款",
            "束脚运动裤", "阔腿裤潮流款", "九分裤休闲百搭", "弹力紧身牛仔裤",
            "灯芯绒复古裤", "棉麻透气夏裤", "加绒保暖冬裤", "短裤五分裤运动款",
        ],
    },
    "外套": {
        "prefix": "WT",
        "price_range": (299, 899),
        "items": [
            "连帽卫衣休闲款", "飞行员夹克", "风衣中长款英伦风", "牛仔外套水洗蓝",
            "针织开衫薄款", "棒球服撞色款", "冲锋衣防风防水", "羊毛大衣商务款",
            "摇粒绒保暖外套", "工装夹克复古款", "轻薄羽绒服", "西装外套休闲版",
        ],
    },
    "配饰": {
        "prefix": "PS",
        "price_range": (49, 199),
        "items": [
            "棒球帽纯色百搭", "针织围巾保暖款", "真皮腰带商务款", "帆布双肩包",
            "运动袜三双装", "墨镜偏光太阳镜", "手表简约石英表", "钱包短款牛皮",
            "领带商务正装", "渔夫帽潮流款", "手套触屏冬季款", "背包通勤电脑包",
        ],
    },
}


def seed_users(db):
    """创建用户"""
    users_data = [
        {"username": "cashier1", "password": "123456", "role": "cashier", "store_id": 1, "real_name": "张小明"},
        {"username": "cashier2", "password": "123456", "role": "cashier", "store_id": 2, "real_name": "李小红"},
        {"username": "manager1", "password": "123456", "role": "manager", "store_id": 1, "real_name": "王店长"},
        {"username": "manager2", "password": "123456", "role": "manager", "store_id": 2, "real_name": "刘店长"},
        {"username": "regional1", "password": "123456", "role": "regional", "store_id": 0, "real_name": "陈经理"},
    ]
    for u in users_data:
        user = User(
            username=u["username"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
            store_id=u["store_id"],
            real_name=u["real_name"],
        )
        db.add(user)
    db.commit()
    print(f"  ✓ 创建 {len(users_data)} 个用户")


def seed_products(db):
    """创建商品（60个）"""
    product_id = 0
    products_info = []  # 存储商品信息用于后续订单生成

    for category, data in PRODUCTS_DATA.items():
        for idx, item_name in enumerate(data["items"], 1):
            product_id += 1
            price_low, price_high = data["price_range"]
            price = round(random.uniform(price_low, price_high), 0)
            sku = f"{data['prefix']}{product_id:04d}"

            product = Product(
                sku=sku,
                name=item_name,
                category=category,
                price=price,
                status="active",
            )
            db.add(product)
            products_info.append({
                "id": product_id,
                "name": item_name,
                "category": category,
                "price": price,
            })

    db.commit()
    print(f"  ✓ 创建 {product_id} 个商品（5品类 × 12款）")
    return products_info


def seed_members(db):
    """创建会员（50个随机 + 3个固定测试）"""
    now = datetime.now()

    surnames = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴",
                "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
                "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧"]
    given_names = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "洋", "艳",
                   "勇", "军", "杰", "娟", "涛", "明", "超", "秀英", "华", "平",
                   "刚", "桂英", "文", "玲", "慧", "鑫", "浩", "彬", "博", "婷"]

    # 等级分布：普通60%、银卡25%、金卡10%、钻石5%
    levels = (["normal"] * 30 + ["silver"] * 13 + ["gold"] * 5 + ["diamond"] * 2)
    random.shuffle(levels)

    used_phones = set()
    member_records = []

    for i in range(50):
        # 生成唯一手机号
        prefix = random.choice(["130", "131", "132", "135", "136", "137", "138",
                                 "150", "151", "152", "155", "156",
                                 "180", "181", "182", "185", "186", "187", "188", "189"])
        while True:
            phone = prefix + "".join([str(random.randint(0, 9)) for _ in range(8)])
            if phone not in used_phones:
                used_phones.add(phone)
                break

        level = levels[i]
        name = f"{random.choice(surnames)}{random.choice(given_names)}"
        # 注册时间：1-60天前
        created_at = now - timedelta(days=random.randint(1, 60))

        preferences_list = ["T恤", "衬衫", "裤装", "外套", "配饰"]
        preferences = ",".join(random.sample(preferences_list, random.randint(1, 3)))

        member = Member(
            phone=phone,
            name=name,
            level=level,
            total_spent=0.0,  # 后面根据订单数据修正
            total_orders=0,
            points=0,
            preferences=preferences,
            created_at=created_at,
        )
        db.add(member)
        member_records.append(member)

    # ═══════════════════════════════════════════════════════════
    # 固定测试会员（用于验收演示，手机号固定不变）
    # ═══════════════════════════════════════════════════════════
    test_members = [
        Member(
            phone="13800001001",
            name="测试银卡",
            level="silver",
            total_spent=2500.0,
            total_orders=12,
            points=1250,
            preferences="T恤,外套",
            created_at=now - timedelta(days=90),
        ),
        Member(
            phone="13800001002",
            name="测试升级",
            level="silver",
            total_spent=4800.0,
            total_orders=18,
            points=2400,
            preferences="衬衫,裤装",
            created_at=now - timedelta(days=180),
        ),
        Member(
            phone="13800001003",
            name="测试回滚",
            level="gold",
            total_spent=5200.0,
            total_orders=25,
            points=5000,
            preferences="外套,配饰",
            created_at=now - timedelta(days=200),
        ),
    ]
    for tm in test_members:
        db.add(tm)

    db.commit()
    print(f"  ✓ 创建 50 个随机会员 + 3 个固定测试会员")
    return member_records


def seed_promotions(db):
    """创建促销活动（3条当前有效）"""
    now = datetime.now()
    today = now.date()
    start = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    end = (today + timedelta(days=25)).strftime("%Y-%m-%d")

    promotions = [
        Promotion(
            name="满300减30",
            type="full_reduction",
            rules_json=json.dumps({"threshold": 300, "reduction": 30}),
            start_date=start,
            end_date=end,
            status="active",
        ),
        Promotion(
            name="T恤品类9折",
            type="percentage",
            rules_json=json.dumps({"category": "T恤", "discount": 0.9}),
            start_date=start,
            end_date=end,
            status="active",
        ),
        Promotion(
            name="新会员首单满200减20",
            type="full_reduction",
            rules_json=json.dumps({"threshold": 200, "reduction": 20, "new_member_only": True}),
            start_date=(today - timedelta(days=10)).strftime("%Y-%m-%d"),
            end_date=(today + timedelta(days=20)).strftime("%Y-%m-%d"),
            status="active",
        ),
    ]
    for p in promotions:
        db.add(p)
    db.commit()
    print(f"  ✓ 创建 {len(promotions)} 条促销活动")


# ═══════════════════════════════════════════════════════════════════
# 特殊AI场景：高于安全线但消耗快的商品
# 这些商品日均销量高，当前库存虽>safety_stock但只够支撑2-3天
# ═══════════════════════════════════════════════════════════════════
SPECIAL_AI_CASES = [
    {"product_id": 1, "current_qty": 18, "daily_sales": 6, "desc": "纯棉圆领基础款-只够3天"},
    {"product_id": 6, "current_qty": 15, "daily_sales": 5, "desc": "运动速干T恤-只够3天"},
    {"product_id": 11, "current_qty": 20, "daily_sales": 8, "desc": "冰丝凉感夏季款-只够2.5天"},
]


def seed_orders(db, products_info, member_records):
    """
    创建近30天的历史订单（300-400笔）
    同时追踪每个商品在每个门店的累计销量，用于后续设置库存
    """
    now = datetime.now()
    today = now.date()
    payment_methods = ["cash", "wechat", "alipay", "card"]
    # 支付方式权重：微信>支付宝>现金>刷卡
    payment_weights = [15, 40, 30, 15]

    # cashier user_id: cashier1=1(store1), cashier2=2(store2)
    store_cashiers = {1: 1, 2: 2}

    # 可关联的会员ID（1-50，不含固定测试会员）
    member_ids = list(range(1, 51))

    # 追踪销量：{(product_id, store_id): total_qty_sold}
    sales_tracker = defaultdict(int)
    # 追踪近7天销量（用于特殊AI场景校正）
    recent_7d_sales = defaultdict(int)  # {(product_id, store_id): qty_in_last_7_days}
    # 追踪会员消费：{member_id: {"spent": float, "orders": int}}
    member_tracker = defaultdict(lambda: {"spent": 0.0, "orders": 0})

    total_orders = 0
    total_items = 0
    voided_count = 0

    # 预先决定哪些天的哪些订单会被作废（2-3笔）
    void_assignments = set()
    void_day_offsets = random.sample(range(3, 25), 3)  # 3个不同日期
    for d in void_day_offsets:
        void_assignments.add((d, random.randint(1, 8)))  # (day_offset, seq_in_day)

    # 按天生成订单（含今天，确保Dashboard有数据）
    for day_offset in range(29, -1, -1):
        order_date = today - timedelta(days=day_offset)

        # 近期订单密度略高（模拟生意增长）
        if day_offset <= 7:
            daily_count = random.randint(12, 16)
        elif day_offset <= 15:
            daily_count = random.randint(10, 14)
        else:
            daily_count = random.randint(8, 12)

        for seq in range(1, daily_count + 1):
            total_orders += 1

            # 门店分配（门店1约55%）
            store_id = 1 if random.random() < 0.55 else 2
            cashier_id = store_cashiers[store_id]

            # 是否关联会员（约40%）
            member_id = random.choice(member_ids) if random.random() < 0.4 else None

            # 订单号：ORD + 日期 + 4位序号
            order_no = f"ORD{order_date.strftime('%Y%m%d')}{seq:04d}"

            # 随机时间 9:00-21:00（午间和傍晚高峰）
            hour_weights = [3, 5, 8, 10, 7, 5, 6, 9, 12, 10, 8, 5, 2]  # 9-21点权重
            hours = list(range(9, 22))
            hour = random.choices(hours, weights=hour_weights, k=1)[0]
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            created_at = datetime(order_date.year, order_date.month, order_date.day,
                                  hour, minute, second)

            # 选取商品（1-4个不重复商品）
            item_count = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10], k=1)[0]
            selected_products = random.sample(products_info, item_count)

            order_total = 0.0
            order_items = []

            for prod in selected_products:
                qty = random.choices([1, 2, 3], weights=[60, 30, 10], k=1)[0]
                unit_price = prod["price"]
                subtotal = unit_price * qty
                order_total += subtotal

                order_items.append({
                    "product_id": prod["id"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "subtotal": subtotal,
                })
                total_items += 1

            # 判断是否作废
            is_voided = (day_offset, seq) in void_assignments
            if is_voided:
                voided_count += 1

            # 折扣计算
            discount = 0.0
            if order_total >= 300 and not is_voided:
                discount = 30.0

            payment_amount = round(order_total - discount, 2)

            # 确定状态
            status = "voided" if is_voided else "completed"

            order = Order(
                order_no=order_no,
                store_id=store_id,
                member_id=member_id,
                total_amount=round(order_total, 2),
                discount_amount=discount,
                payment_amount=payment_amount,
                payment_method=random.choices(payment_methods, weights=payment_weights, k=1)[0],
                status=status,
                cashier_id=cashier_id,
                created_at=created_at,
            )
            db.add(order)
            db.flush()  # 获取 order.id

            for item_data in order_items:
                oi = OrderItem(
                    order_id=order.id,
                    product_id=item_data["product_id"],
                    quantity=item_data["quantity"],
                    unit_price=item_data["unit_price"],
                    subtotal=item_data["subtotal"],
                )
                db.add(oi)

                # 只有completed订单计入销量
                if status == "completed":
                    sales_tracker[(item_data["product_id"], store_id)] += item_data["quantity"]
                    if day_offset <= 6:
                        recent_7d_sales[(item_data["product_id"], store_id)] += item_data["quantity"]

            # 更新会员消费追踪（只有completed且有会员的）
            if member_id and status == "completed":
                member_tracker[member_id]["spent"] += payment_amount
                member_tracker[member_id]["orders"] += 1

    db.commit()

    # ═══════════════════════════════════════════════════════════════
    # 为特殊AI场景商品补充近7天订单，确保日均销量达标
    # ═══════════════════════════════════════════════════════════════
    extra_orders = 0
    store_id_for_special = 1  # 特殊场景在门店1
    for case in SPECIAL_AI_CASES:
        pid = case["product_id"]
        target_7d_total = case["daily_sales"] * 7  # 如日均6 → 7天42件
        current_7d = recent_7d_sales.get((pid, store_id_for_special), 0)
        needed = target_7d_total - current_7d

        if needed <= 0:
            continue

        # 将需要补充的销量分散到近7天中
        prod = products_info[pid - 1]  # product_id从1开始
        remaining = needed
        for day_offset in range(6, -1, -1):
            if remaining <= 0:
                break
            order_date = today - timedelta(days=day_offset)
            # 每天补充 1-3 笔订单
            daily_add = min(remaining, random.randint(case["daily_sales"] - 1, case["daily_sales"] + 1))
            if daily_add <= 0:
                continue

            total_orders += 1
            extra_orders += 1
            seq = 90 + extra_orders  # 避免与正常订单号冲突
            order_no = f"ORD{order_date.strftime('%Y%m%d')}{seq:04d}"
            hour = random.randint(10, 20)
            created_at = datetime(order_date.year, order_date.month, order_date.day,
                                  hour, random.randint(0, 59), random.randint(0, 59))

            subtotal = prod["price"] * daily_add
            member_id = random.choice(member_ids) if random.random() < 0.4 else None

            order = Order(
                order_no=order_no,
                store_id=store_id_for_special,
                member_id=member_id,
                total_amount=round(subtotal, 2),
                discount_amount=0.0,
                payment_amount=round(subtotal, 2),
                payment_method=random.choice(payment_methods),
                status="completed",
                cashier_id=store_cashiers[store_id_for_special],
                created_at=created_at,
            )
            db.add(order)
            db.flush()

            oi = OrderItem(
                order_id=order.id,
                product_id=pid,
                quantity=daily_add,
                unit_price=prod["price"],
                subtotal=subtotal,
            )
            db.add(oi)

            sales_tracker[(pid, store_id_for_special)] += daily_add
            remaining -= daily_add

            if member_id:
                member_tracker[member_id]["spent"] += subtotal
                member_tracker[member_id]["orders"] += 1

    db.commit()
    print(f"  ✓ 创建 {total_orders} 笔历史订单（含 {total_items} 条明细，{voided_count} 笔已作废）")
    if extra_orders > 0:
        print(f"    （含 {extra_orders} 笔AI场景补充订单，覆盖 {len(SPECIAL_AI_CASES)} 个高消耗商品）")

    return sales_tracker, member_tracker


def seed_inventory(db, products_info, sales_tracker):
    """
    创建库存记录，保证逻辑一致：
    当前库存 = 初始进货量 - 累计销量
    """
    num_products = len(products_info)

    # 特殊AI场景商品ID集合（在门店1设置特定库存）
    special_product_ids = {case["product_id"]: case["current_qty"] for case in SPECIAL_AI_CASES}

    # 选择需要低库存和缺货的商品（在门店1，排除特殊场景商品）
    candidate_products = [pid for pid in range(1, num_products + 1) if pid not in special_product_ids]
    low_stock_products_s1 = set(random.sample(candidate_products, 6))  # 6个低库存
    out_of_stock_products_s1 = set(random.sample(list(low_stock_products_s1), 2))  # 其中2个缺货
    # 门店2也有几个低库存
    low_stock_products_s2 = set(random.sample(range(1, num_products + 1), 3))
    out_of_stock_products_s2 = set(random.sample(list(low_stock_products_s2), 1))

    low_count = 0
    zero_count = 0
    special_count = 0

    for product_id in range(1, num_products + 1):
        for store_id in [1, 2]:
            sold = sales_tracker.get((product_id, store_id), 0)

            # 特殊AI场景商品（仅门店1）
            if store_id == 1 and product_id in special_product_ids:
                quantity = special_product_ids[product_id]
                special_count += 1
            elif store_id == 1 and product_id in out_of_stock_products_s1:
                # 缺货：当前库存为0
                quantity = 0
                zero_count += 1
            elif store_id == 1 and product_id in low_stock_products_s1:
                # 低库存：3-9件
                quantity = random.randint(3, 9)
                low_count += 1
            elif store_id == 2 and product_id in out_of_stock_products_s2:
                quantity = 0
                zero_count += 1
            elif store_id == 2 and product_id in low_stock_products_s2:
                quantity = random.randint(4, 8)
                low_count += 1
            else:
                # 正常库存：30-80件
                quantity = random.randint(30, 80)

            inv = Inventory(
                product_id=product_id,
                store_id=store_id,
                quantity=quantity,
                safety_stock=10,
            )
            db.add(inv)

    db.commit()
    print(f"  ✓ 创建 {num_products * 2} 条库存记录（{low_count} 个低库存预警，{zero_count} 个缺货）")
    print(f"    （{special_count} 个特殊AI场景商品：库存>安全线但消耗快，只够2-3天）")


def update_member_stats(db, member_tracker):
    """根据订单数据更新会员的消费统计"""
    updated = 0
    for member_id, stats in member_tracker.items():
        member = db.query(Member).filter(Member.id == member_id).first()
        if member:
            member.total_spent = round(stats["spent"], 2)
            member.total_orders = stats["orders"]
            member.points = int(stats["spent"] * 0.5)  # 每消费1元 = 0.5积分

            # 根据消费额更新等级
            if stats["spent"] >= 20000:
                member.level = "diamond"
            elif stats["spent"] >= 5000:
                member.level = "gold"
            elif stats["spent"] >= 2000:
                member.level = "silver"
            else:
                member.level = "normal"

            updated += 1
    db.commit()
    print(f"  ✓ 更新 {updated} 个会员的消费统计和等级")


def main():
    print("=" * 55)
    print("  Smart Store 种子数据初始化")
    print("  模拟真实运营约1个月的服饰门店数据")
    print("=" * 55)

    # 创建所有表
    print("\n[1/8] 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("  ✓ 数据库表创建完成")

    # 清空数据
    print("\n[2/8] 清空现有数据...")
    db = SessionLocal()
    try:
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(RestockRequest).delete()
        db.query(Inventory).delete()
        db.query(Promotion).delete()
        db.query(Member).delete()
        db.query(Product).delete()
        db.query(User).delete()
        db.commit()
        print("  ✓ 现有数据已清空")

        # 插入种子数据
        print("\n[3/8] 创建用户...")
        seed_users(db)

        print("\n[4/8] 创建商品...")
        products_info = seed_products(db)

        print("\n[5/8] 创建会员...")
        member_records = seed_members(db)

        print("\n[6/8] 创建促销活动...")
        seed_promotions(db)

        print("\n[7/8] 创建历史订单...")
        sales_tracker, member_tracker = seed_orders(db, products_info, member_records)

        print("\n[8/8] 同步库存与会员统计...")
        seed_inventory(db, products_info, sales_tracker)
        update_member_stats(db, member_tracker)

        # 打印数据概览
        print("\n" + "=" * 55)
        print("  ✓ 种子数据初始化完成！")
        print("=" * 55)
        print("\n  数据概览:")
        print(f"    用户:     5 个（cashier×2, manager×2, regional×1）")
        print(f"    商品:     {len(products_info)} 个（5品类×12款）")
        print(f"    库存:     {len(products_info) * 2} 条记录（2门店）")
        print(f"    会员:     53 个（50随机 + 3固定测试）")
        print(f"    促销:     3 条（当前有效）")
        total_o = db.query(Order).count()
        total_i = db.query(OrderItem).count()
        print(f"    订单:     {total_o} 笔（含 {total_i} 条明细）")
        print(f"\n  启动服务器: uvicorn app.main:app --reload --port 8000")
        print(f"  测试登录:   POST http://localhost:8000/auth/login")
        print(f'    Body:     {{"username": "cashier1", "password": "123456"}}')

    except Exception as e:
        db.rollback()
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
