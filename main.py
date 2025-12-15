from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(title="FBA Fulfillment Engine", version="1.0.0")

# Data Models
class ProductStock(BaseModel):
    product_sku: str
    quantity: int
    fulfillment_center: str

class OrderRequest(BaseModel):
    customer_id: str
    items: List[ProductStock]
    priority: Optional[bool] = False

class OrderResponse(BaseModel):
    order_id: str
    status: str
    routed_to: str
    eta: str
    total_items: int

# Mock Fulfillment Centers (Amazon Scale)
FULFILLMENT_CENTERS = {
    "FC_BLR": {"location": "Bangalore", "capacity": 10000, "current_load": 7500},
    "FC_HYD": {"location": "Hyderabad", "capacity": 8000, "current_load": 6000},
    "FC_MUM": {"location": "Mumbai", "capacity": 12000, "current_load": 9000}
}

orders = []

@app.post("/api/orders", response_model=OrderResponse)
def create_order(order: OrderRequest):
    # FBA Routing Logic - Amazon Style
    best_fc = route_to_optimal_center(order.items)
    
    if best_fc is None:
        raise HTTPException(status_code=400, detail="No available fulfillment center")
    
    order_id = str(uuid.uuid4())[:8]
    new_order = OrderResponse(
        order_id=order_id,
        status="ROUTED",
        routed_to=best_fc,
        eta="2-3 days",
        total_items=len(order.items)
    )
    
    orders.append(new_order.dict())
    return new_order

def route_to_optimal_center(items: List[ProductStock]) -> Optional[str]:
    """Amazon FBA Multi-Center Routing Algorithm"""
    best_fc = None
    best_score = float('inf')
    
    for fc_id, fc_data in FULFILLMENT_CENTERS.items():
        load_factor = fc_data["current_load"] / fc_data["capacity"]
        
        # Prioritize: Capacity → Location → Load
        score = load_factor * 100
        
        if score < best_score:
            best_score = score
            best_fc = fc_id
    
    return best_fc

@app.get("/api/fulfillment-centers")
def get_centers():
    return FULFILLMENT_CENTERS

@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    for order in orders:
        if order["order_id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.get("/api/health")
def health():
    return {"status": "FBA Fulfillment Engine - Multi-region ready ✅"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
