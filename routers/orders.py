from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, Product, Order, OrderItem, Commission
from schemas import OrderCreate, OrderResponse, OrderItemResponse
from auth import get_current_active_user

router = APIRouter(prefix="/api/orders", tags=["orders"])

# Ставка комиссии (10%)
COMMISSION_RATE = 0.1


@router.get("", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список заказов текущего пользователя"""
    result = await db.execute(select(Order).where(Order.buyer_id == current_user.id))
    orders = result.scalars().all()
    
    # Загружаем items для каждого заказа
    orders_with_items = []
    for order in orders:
        result = await db.execute(
            select(OrderItem, Product.name)
            .join(Product, OrderItem.product_id == Product.id)
            .where(OrderItem.order_id == order.id)
        )
        items_data = result.all()
        order_dict = {
            "id": order.id,
            "buyer_id": order.buyer_id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
            "items": [
                OrderItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=product_name,
                    quantity=item.quantity,
                    price=item.price
                )
                for item, product_name in items_data
            ]
        }
        orders_with_items.append(OrderResponse(**order_dict))
    
    return orders_with_items


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить заказ по ID"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.buyer_id != current_user.id and not current_user.is_seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    result = await db.execute(
        select(OrderItem, Product.name)
        .join(Product, OrderItem.product_id == Product.id)
        .where(OrderItem.order_id == order.id)
    )
    items_data = result.all()
    
    order_dict = {
        "id": order.id,
        "buyer_id": order.buyer_id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "items": [
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=product_name,
                quantity=item.quantity,
                price=item.price
            )
            for item, product_name in items_data
        ]
    }
    
    return OrderResponse(**order_dict)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый заказ"""
    total_amount = 0.0
    order_items_data = []
    
    # Проверяем товары и рассчитываем сумму
    for item_data in order_data.items:
        result = await db.execute(select(Product).where(Product.id == item_data.product_id))
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item_data.product_id} not found"
            )
        
        if product.quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Not enough quantity for product {product.name}. Available: {product.quantity}"
            )
        
        item_total = product.price * item_data.quantity
        total_amount += item_total
        order_items_data.append((product, item_data.quantity, product.price))
    
    # Создаем заказ
    new_order = Order(
        buyer_id=current_user.id,
        total_amount=total_amount,
        status="pending"
    )
    db.add(new_order)
    await db.flush()  # Получаем ID заказа
    
    # Создаем элементы заказа и обновляем количество товаров
    for product, quantity, price in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=quantity,
            price=price
        )
        db.add(order_item)
        product.quantity -= quantity
    
    # Создаем комиссию для каждого продавца
    seller_totals = {}  # seller_id -> total_amount
    for product, quantity, price in order_items_data:
        if product.seller_id not in seller_totals:
            seller_totals[product.seller_id] = 0.0
        seller_totals[product.seller_id] += price * quantity
    
    for seller_id, amount in seller_totals.items():
        commission_amount = amount * COMMISSION_RATE
        seller_amount = amount - commission_amount
        
        commission = Commission(
            order_id=new_order.id,
            seller_id=seller_id,
            amount=amount,
            commission_rate=COMMISSION_RATE,
            commission_amount=commission_amount,
            seller_amount=seller_amount
        )
        db.add(commission)
    
    await db.commit()
    await db.refresh(new_order)
    
    # Формируем ответ с items
    result = await db.execute(
        select(OrderItem, Product.name)
        .join(Product, OrderItem.product_id == Product.id)
        .where(OrderItem.order_id == new_order.id)
    )
    items_data = result.all()
    
    order_dict = {
        "id": new_order.id,
        "buyer_id": new_order.buyer_id,
        "total_amount": new_order.total_amount,
        "status": new_order.status,
        "created_at": new_order.created_at,
        "items": [
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=product_name,
                quantity=item.quantity,
                price=item.price
            )
            for item, product_name in items_data
        ]
    }
    
    return OrderResponse(**order_dict)


@router.put("/{order_id}/complete", response_model=OrderResponse)
async def complete_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Завершить заказ"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    order.status = "completed"
    await db.commit()
    await db.refresh(order)
    
    # Загружаем items
    result = await db.execute(
        select(OrderItem, Product.name)
        .join(Product, OrderItem.product_id == Product.id)
        .where(OrderItem.order_id == order.id)
    )
    items_data = result.all()
    
    order_dict = {
        "id": order.id,
        "buyer_id": order.buyer_id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "items": [
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=product_name,
                quantity=item.quantity,
                price=item.price
            )
            for item, product_name in items_data
        ]
    }
    
    return OrderResponse(**order_dict)

