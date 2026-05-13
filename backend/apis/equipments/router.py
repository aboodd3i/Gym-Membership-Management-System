from fastapi import APIRouter
from database import get_db_connection
from models import *

router = APIRouter()


@router.get("/api/equipment", response_model=List[EquipmentResponse], tags=["Equipment"])
def get_all_equipment():
    """Fetches all equipment inventory."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment ORDER BY category, name;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.get("/api/equipment/maintenance-alerts", response_model=List[MaintenanceAlert], tags=["Equipment"])
def get_maintenance_alerts():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT e.equipment_id, name, category, condition_status,
               next_maintenance_date,
               next_maintenance_date - CURRENT_DATE AS days_until_maintenance
        FROM equipment e
        WHERE next_maintenance_date <= CURRENT_DATE + 30
           OR condition_status ILIKE 'broken'      /* <-- Changed to ILIKE */
           OR condition_status ILIKE 'needs repair' /* <-- Changed to ILIKE */
        ORDER BY next_maintenance_date;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


@router.patch("/api/equipment/{equipment_id}/condition", tags=["Equipment"])
def update_equipment_condition(equipment_id: int, cond_data: UpdateEquipmentStatus):
    """Updates equipment condition (e.g., marking it as broken)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE equipment SET condition_status = %s, next_maintenance_date = CURRENT_DATE 
        WHERE equipment_id = %s;
    """, (cond_data.condition_status, equipment_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Equipment condition updated."}


@router.patch("/api/equipment/{equipment_id}/repair-complete", tags=["Equipment"])
def complete_equipment_repair(equipment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE equipment SET condition_status = 'good', next_maintenance_date = CURRENT_DATE + INTERVAL '6 months' 
        WHERE equipment_id = %s;
    """, (equipment_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Equipment repaired and next maintenance scheduled."}
