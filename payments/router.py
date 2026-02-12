from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from auth.router import get_current_user
from auth.models import User
from payments.paymob_client import PaymobClient

router = APIRouter(prefix="/payments", tags=["payments"])

# Initialize Paymob client
paymob_client = PaymobClient()

# Pydantic models
class PaymentRequest(BaseModel):
    amount: float
    currency: str = "EGP"
    user_email: str
    user_name: str
    user_phone: str
    course_slug: Optional[str] = None
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    payment_url: str
    order_id: str
    payment_key: str

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: float
    currency: str = "USD"
    duration_months: int
    features: List[str]
    recommended: bool = False

class SubscribeRequest(BaseModel):
    plan_id: str
    user_email: str
    user_name: str
    user_phone: str

class UserSubscription(BaseModel):
    user_email: str
    plan_id: str
    plan_name: str
    status: str  # active, expired, cancelled
    start_date: str
    end_date: str
    auto_renew: bool = True

# Subscription plans
SUBSCRIPTION_PLANS = [
    {
        "id": "basic",
        "name": "Basic",
        "price": 9.99,
        "currency": "USD",
        "duration_months": 1,
        "features": [
            "50 analytics reports/month",
            "Basic AI assistant",
            "Standard support",
            "Community forum access"
        ],
        "recommended": False
    },
    {
        "id": "pro",
        "name": "Professional",
        "price": 29.99,
        "currency": "USD",
        "duration_months": 1,
        "features": [
            "Unlimited analytics reports",
            "Advanced AI assistant",
            "Priority support",
            "API access",
            "Custom integrations"
        ],
        "recommended": True
    },
    {
        "id": "enterprise",
        "name": "Enterprise",
        "price": 99.99,
        "currency": "USD",
        "duration_months": 1,
        "features": [
            "Everything in Pro",
            "Dedicated account manager",
            "Custom development",
            "SLA guarantee",
            "On-premise deployment"
        ],
        "recommended": False
    }
]

@router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    """Get available subscription plans"""
    return SUBSCRIPTION_PLANS

@router.post("/initiate", response_model=PaymentResponse)
async def initiate_payment(payment_request: PaymentRequest):
    """Initiate a payment with Paymob"""
    try:
        if not paymob_client.configured:
            raise HTTPException(status_code=503, detail="Payment service not configured")
        
        # Convert amount to cents
        amount_cents = int(payment_request.amount * 100)
        
        # Authenticate with Paymob
        auth_token = await paymob_client.authenticate()
        
        # Register order
        order_data = {
            "amount_cents": amount_cents,
            "currency": payment_request.currency,
            "items": [
                {
                    "name": payment_request.description or "EngiSuite Analytics Subscription",
                    "amount_cents": amount_cents,
                    "quantity": 1
                }
            ]
        }
        
        order_result = await paymob_client.register_order(auth_token, order_data)
        order_id = order_result.get("id")
        
        if not order_id:
            raise HTTPException(status_code=500, detail="Failed to create order")
        
        # Get payment key
        billing_data = {
            "email": payment_request.user_email,
            "first_name": payment_request.user_name.split()[0] if payment_request.user_name else "User",
            "last_name": " ".join(payment_request.user_name.split()[1:]) if payment_request.user_name and len(payment_request.user_name.split()) > 1 else "User",
            "phone_number": payment_request.user_phone,
            "country": "EG",
            "city": "Cairo"
        }
        
        payment_key = await paymob_client.get_payment_key(
            auth_token, order_id, amount_cents, billing_data
        )
        
        # Generate payment URL
        payment_url = paymob_client.get_payment_url(payment_key)
        
        return PaymentResponse(
            payment_url=payment_url,
            order_id=str(order_id),
            payment_key=payment_key
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")

@router.post("/subscribe")
async def subscribe_to_plan(subscribe_request: SubscribeRequest, db: Session = Depends(get_db)):
    """Subscribe to a specific plan"""
    # Find the plan
    plan = next((p for p in SUBSCRIPTION_PLANS if p["id"] == subscribe_request.plan_id), None)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Initiate payment for the plan
    payment_request = PaymentRequest(
        amount=plan["price"],
        currency=plan["currency"],
        user_email=subscribe_request.user_email,
        user_name=subscribe_request.user_name,
        user_phone=subscribe_request.user_phone,
        description=f"{plan['name']} Subscription",
        course_slug=None
    )
    
    return await initiate_payment(payment_request)

@router.post("/webhook")
async def payment_webhook(request: Request):
    """Handle payment webhook from Paymob"""
    try:
        # Get signature from headers
        signature = request.headers.get("x-paymob-hmac")
        if not signature:
            return JSONResponse(status_code=400, content={"detail": "Missing signature"})
        
        # Get request body
        webhook_data = await request.json()
        
        # Verify signature
        if not paymob_client.verify_webhook(webhook_data, signature):
            return JSONResponse(status_code=401, content={"detail": "Invalid signature"})
        
        # Process the payment
        payment_info = await paymob_client.process_callback(webhook_data)
        
        # Update user subscription status if payment was successful
        if payment_info["success"]:
            # TODO: Implement subscription management logic
            print(f"Payment successful: {payment_info['id']} for {payment_info['amount_cents']} cents")
        else:
            print(f"Payment failed: {payment_info['id']}")
        
        return JSONResponse(content={"success": True, "message": "Webhook processed successfully"})
        
    except Exception as e:
        print(f"Webhook processing error: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@router.get("/status/{order_id}")
async def get_payment_status(order_id: str):
    """Get payment status for an order"""
    try:
        # TODO: Implement payment status check
        return JSONResponse(content={"order_id": order_id, "status": "pending"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
