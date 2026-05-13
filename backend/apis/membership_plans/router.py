from fastapi import APIRouter, status
from database import get_db_connection
from models import *

router = APIRouter()


@router.get("/api/plans", response_model=List[PlanResponse], tags=["Plans"])
def get_all_plans():
    """Fetches all available membership plans ordered by price."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT plan_id, plan_name, duration_months, price, description FROM membership_plans ORDER BY price ASC;")
    plans = cursor.fetchall()
    cursor.close()
    conn.close()
    return plans


@router.post("/api/plans", status_code=status.HTTP_201_CREATED, tags=["Plans"])
def create_plan(plan_data: PlanCreateRequest):
    """Inserts a new custom membership plan into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO membership_plans (plan_name, duration_months, price, description) VALUES (%s, %s, %s, %s);",
        (plan_data.plan_name, plan_data.duration_months, plan_data.price, plan_data.description)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Plan created successfully!"}
