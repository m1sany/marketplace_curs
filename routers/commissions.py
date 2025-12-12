from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, Commission
from schemas import CommissionResponse
from auth import get_current_seller

router = APIRouter(prefix="/api/commissions", tags=["commissions"])


@router.get("", response_model=List[CommissionResponse])
async def get_commissions(
    current_user: User = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """Получить список комиссий текущего продавца"""
    result = await db.execute(
        select(Commission).where(Commission.seller_id == current_user.id)
    )
    commissions = result.scalars().all()
    return commissions


@router.get("/{commission_id}", response_model=CommissionResponse)
async def get_commission(
    commission_id: int,
    current_user: User = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """Получить комиссию по ID"""
    result = await db.execute(select(Commission).where(Commission.id == commission_id))
    commission = result.scalar_one_or_none()
    
    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commission not found"
        )
    
    if commission.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return commission

