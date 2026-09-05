import re
import sys
import logging
from mcp.server.mcpserver import MCPServer
from pydantic import BaseModel, field_validator, ValidationError

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("mcp-server")

mcp = MCPServer("customer-service")

# --------------- Data samples ---------------
CUSTOMERS = {
    "CUST-00001": {"name": "customer1", "email": "customer1@gmail.com"},
    "CUST-00002": {"name": "customer2", "email": "customer2@gmail.com"},
    "CUST-00003": {"name": "customer3", "email": "customer3@gmail.com"},
}

REFUND_LOG: list[dict] = []

# --------------- Data validation -------------
class CustomerIdInput(BaseModel):
    customer_id: str

    @field_validator("customer_id")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if not re.match(r"^CUST-\d{5}$", v):
            raise ValueError("customer_id must match format CUST-XXXXX (5 digits)")
        return v

class RefundInput(BaseModel):
    customer_id: str
    amount: float
    reason: str

    @field_validator("customer_id")
    @classmethod
    def validate_format(cls, v: str) -> str:
        if not re.match(r"^CUST-\d{5}$", v):
            raise ValueError("customer_id must match format CUST-XXXXX (5 digits)")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be a positive number")
        return v

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("reason must be at least 10 characters long")
        return v


# --------------- Tools ---------------
@mcp.tool()
def get_customer_record(customer_id: str) -> dict:
    """Look up a customer record by ID. The customer_id must be in the format CUST-XXXXX."""
    try:
        validated = CustomerIdInput(customer_id=customer_id)
    except ValidationError as e:
        return {"error": e.errors()[0]["msg"]}
    record = CUSTOMERS.get(validated.customer_id)
    if record is None:
        return {"error": f"No customer found with ID {validated.customer_id}"}
    logger.info("Looked up customer %s", validated.customer_id)
    return {"customer_id": validated.customer_id, **record}

@mcp.tool()
def trigger_refund(customer_id: str, amount: float, reason: str) -> dict:
    """Trigger a refund for a customer. Requires a valid customer_id (CUST-XXXXX), a positive amount, and a reason (min 10 chars)."""
    try:
        validated = RefundInput(customer_id=customer_id, amount=amount, reason=reason)
    except ValidationError as e:
        return {"error": [err["msg"] for err in e.errors()]}
    if validated.customer_id not in CUSTOMERS:
        return {"error": f"No customer found with ID {validated.customer_id}"}
    refund = {
        "customer_id": validated.customer_id,
        "amount": validated.amount,
        "reason": validated.reason,
        "status": "processed",
    }
    REFUND_LOG.append(refund)
    logger.info("Refund of %.2f processed for %s", validated.amount, validated.customer_id)
    return refund

if __name__ == "__main__":
    logger.info("Server initialized")
    mcp.run(transport="stdio")