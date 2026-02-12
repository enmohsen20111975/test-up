"""
Paymob Payment Gateway Integration
Handles payment processing for Egyptian market

Paymob API Documentation: https://docs.paymob.com/
"""

import os
import hmac
import hashlib
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PaymobClient:
    """
    Paymob payment gateway client for Egypt
    
    Features:
    - Order registration
    - Payment key generation
    - Webhook signature verification
    - Payment callback handling
    """
    
    def __init__(self):
        """Initialize Paymob client"""
        self.api_key = os.getenv("PAYMOB_API_KEY")
        self.integration_id = os.getenv("PAYMOB_INTEGRATION_ID")
        self.hmac_secret = os.getenv("PAYMOB_HMAC_SECRET")
        self.iframe_id = os.getenv("PAYMOB_IFRAME_ID")
        
        # Paymob API endpoints
        self.base_url = "https://accept.paymob.com/api"
        self.auth_url = f"{self.base_url}/auth/tokens"
        self.order_url = f"{self.base_url}/ecommerce/orders"
        self.payment_key_url = f"{self.base_url}/acceptance/payment_keys"
        
        # Check if credentials are valid (not placeholders)
        if not self.api_key or not self.integration_id or not self.hmac_secret or \
           "placeholder" in str(self.api_key).lower() or \
           "placeholder" in str(self.integration_id).lower() or \
           "placeholder" in str(self.hmac_secret).lower():
            print("[WARN] Paymob credentials not configured - payment features disabled")
            print("  Configure PAYMOB_* variables in .env for payment functionality")
            print("  PAYMOB_INTEGRATION_ID must be a numeric ID (e.g., 123456), not an API key")
            self.configured = False
        else:
            # Validate integration ID is numeric
            try:
                int(self.integration_id)
                self.configured = True
                print("[OK] Paymob client initialized")
            except ValueError:
                print("[WARN] Paymob INTEGRATION_ID must be numeric (e.g., 123456)")
                print("  Current value looks like an API key, not an integration ID")
                print("  Get the numeric Integration ID from: Dashboard > Developers > Payment Integrations")
                print("  Payment features disabled - will use demo mode")
                self.configured = False
    
    # ==================== Authentication ====================
    
    async def authenticate(self) -> str:
        """
        Authenticate with Paymob and get auth token
        
        Returns:
            Authentication token
        """
        if not self.configured:
            raise Exception("Paymob not configured")
            
        try:
            response = requests.post(
                self.auth_url,
                json={"api_key": self.api_key}
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("token", "")
        
        except Exception as e:
            print(f"Paymob authentication error: {e}")
            raise
    
    # ==================== Order Management ====================
    
    async def register_order(self, auth_token: str, order_data: Dict) -> Dict:
        """
        Register an order with Paymob
        
        Args:
            auth_token: Authentication token from authenticate()
            order_data: Order information
                - amount_cents: Amount in cents (e.g., 10000 for 100 EGP)
                - currency: Currency code (default: EGP)
                - items: List of order items
        
        Returns:
            Order data with order ID
        """
        try:
            payload = {
                "auth_token": auth_token,
                "delivery_needed": "false",
                "amount_cents": order_data["amount_cents"],
                "currency": order_data.get("currency", "EGP"),
                "items": order_data.get("items", [])
            }
            
            response = requests.post(self.order_url, json=payload)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            print(f"Paymob order registration error: {e}")
            raise
    
    # ==================== Payment Key ====================
    
    async def get_payment_key(
        self,
        auth_token: str,
        order_id: int,
        amount_cents: int,
        billing_data: Dict
    ) -> str:
        """
        Generate payment key for checkout
        
        Args:
            auth_token: Authentication token
            order_id: Order ID from register_order()
            amount_cents: Amount in cents
            billing_data: Customer billing information
                - email: Customer email
                - first_name: First name
                - last_name: Last name
                - phone_number: Phone number
                - country: Country (optional)
                - city: City (optional)
                - street: Street (optional)
        
        Returns:
            Payment key for iframe/checkout
        """
        try:
            payload = {
                "auth_token": auth_token,
                "amount_cents": amount_cents,
                "expiration": 3600,  # 1 hour
                "order_id": order_id,
                "billing_data": {
                    "email": billing_data.get("email", ""),
                    "first_name": billing_data.get("first_name", "NA"),
                    "last_name": billing_data.get("last_name", "NA"),
                    "phone_number": billing_data.get("phone_number", "+20000000000"),
                    "country": billing_data.get("country", "EG"),
                    "city": billing_data.get("city", "Cairo"),
                    "street": billing_data.get("street", "NA"),
                    "building": billing_data.get("building", "NA"),
                    "floor": billing_data.get("floor", "NA"),
                    "apartment": billing_data.get("apartment", "NA"),
                },
                "currency": "EGP",
                "integration_id": int(self.integration_id)
            }
            
            response = requests.post(self.payment_key_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data.get("token", "")
        
        except Exception as e:
            print(f"Paymob payment key error: {e}")
            raise
    
    # ==================== Payment URL ====================
    
    def get_payment_url(self, payment_key: str) -> str:
        """
        Generate payment iframe URL
        
        Args:
            payment_key: Payment key from get_payment_key()
        
        Returns:
            Full payment URL for redirect
        """
        if self.iframe_id:
            return f"https://accept.paymob.com/api/acceptance/iframes/{self.iframe_id}?payment_token={payment_key}"
        else:
            # Fallback to standard checkout
            return f"https://accept.paymob.com/api/acceptance/payment_keys?payment_token={payment_key}"
    
    # ==================== Webhook Handling ====================
    
    def verify_webhook(self, webhook_data: Dict, signature: str) -> bool:
        """
        Verify webhook signature from Paymob
        
        Args:
            webhook_data: Webhook payload
            signature: HMAC signature from header
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Extract relevant fields for HMAC calculation
            obj = webhook_data.get("obj", {})
            
            # Paymob HMAC calculation order
            fields = [
                str(obj.get("amount_cents", "")),
                str(obj.get("created_at", "")),
                str(obj.get("currency", "")),
                str(obj.get("error_occured", "")),
                str(obj.get("has_parent_transaction", "")),
                str(obj.get("id", "")),
                str(obj.get("integration_id", "")),
                str(obj.get("is_3d_secure", "")),
                str(obj.get("is_auth", "")),
                str(obj.get("is_capture", "")),
                str(obj.get("is_refunded", "")),
                str(obj.get("is_standalone_payment", "")),
                str(obj.get("is_voided", "")),
                str(obj.get("order", {}).get("id", "")),
                str(obj.get("owner", "")),
                str(obj.get("pending", "")),
                str(obj.get("source_data", {}).get("pan", "")),
                str(obj.get("source_data", {}).get("sub_type", "")),
                str(obj.get("source_data", {}).get("type", "")),
                str(obj.get("success", ""))
            ]
            
            # Concatenate fields
            concatenated = "".join(fields)
            
            # Calculate HMAC
            calculated_hmac = hmac.new(
                self.hmac_secret.encode(),
                concatenated.encode(),
                hashlib.sha512
            ).hexdigest()
            
            return calculated_hmac == signature
        
        except Exception as e:
            print(f"Webhook verification error: {e}")
            return False
    
    async def process_callback(self, webhook_data: Dict) -> Dict:
        """
        Process payment callback from Paymob
        
        Args:
            webhook_data: Webhook payload
        
        Returns:
            Processed payment information
        """
        try:
            obj = webhook_data.get("obj", {})
            
            # Extract payment information
            result = {
                "id": obj.get("id"),
                "order_id": obj.get("order", {}).get("id"),
                "amount_cents": obj.get("amount_cents"),
                "currency": obj.get("currency", "EGP"),
                "success": obj.get("success", False),
                "status": "success" if obj.get("success") else "failed",
                "payment_method": obj.get("source_data", {}).get("type", ""),
                "billing_data": obj.get("billing_data", {}),
                "created_at": obj.get("created_at"),
                "is_refunded": obj.get("is_refunded", False),
                "is_voided": obj.get("is_voided", False),
                "error_occured": obj.get("error_occured", False),
            }
            
            return result
        
        except Exception as e:
            print(f"Callback processing error: {e}")
            raise
    
    # ==================== Refund ====================
    
    async def refund_transaction(
        self,
        auth_token: str,
        transaction_id: int,
        amount_cents: int
    ) -> Dict:
        """
        Refund a transaction
        
        Args:
            auth_token: Authentication token
            transaction_id: Transaction ID to refund
            amount_cents: Amount to refund in cents
        
        Returns:
            Refund response
        """
        try:
            refund_url = f"{self.base_url}/acceptance/void_refund/refund"
            
            payload = {
                "auth_token": auth_token,
                "transaction_id": transaction_id,
                "amount_cents": amount_cents
            }
            
            response = requests.post(refund_url, json=payload)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            print(f"Refund error: {e}")
            raise
