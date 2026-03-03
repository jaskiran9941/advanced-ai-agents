# shared/data.py
# Mock data for Acme Shop (fictional electronics retailer)
# Shared across all 10 levels — never call a real API, just look things up here.

# ---------------------------------------------------------------------------
# ORDERS
# ---------------------------------------------------------------------------
# order_id → dict with status, items, customer_id, timestamps, etc.

ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_id": "CUST-001",
        "status": "delivered",
        "items": [
            {"product_id": "PROD-A", "name": "Wireless Headphones", "qty": 1, "price": 89.99}
        ],
        "total": 89.99,
        "order_date": "2026-02-10",
        "estimated_delivery": "2026-02-14",
        "actual_delivery": "2026-02-14",
        "tracking_number": "TRK-88821",
        "carrier": "FedEx",
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_id": "CUST-001",
        "status": "in_transit",
        "items": [
            {"product_id": "PROD-B", "name": "USB-C Charging Hub", "qty": 2, "price": 34.99}
        ],
        "total": 69.98,
        "order_date": "2026-02-25",
        "estimated_delivery": "2026-03-03",
        "actual_delivery": None,
        "tracking_number": "TRK-99203",
        "carrier": "UPS",
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_id": "CUST-002",
        "status": "delayed",
        "items": [
            {"product_id": "PROD-C", "name": "4K Webcam", "qty": 1, "price": 129.00}
        ],
        "total": 129.00,
        "order_date": "2026-02-18",
        "estimated_delivery": "2026-02-24",
        "actual_delivery": None,
        "tracking_number": "TRK-77654",
        "carrier": "USPS",
        "delay_reason": "Weather disruption in distribution center",
    },
    "ORD-1004": {
        "order_id": "ORD-1004",
        "customer_id": "CUST-002",
        "status": "damaged",
        "items": [
            {"product_id": "PROD-D", "name": "Mechanical Keyboard", "qty": 1, "price": 149.00},
            {"product_id": "PROD-E", "name": "Mouse Pad XL", "qty": 1, "price": 19.99},
        ],
        "total": 168.99,
        "order_date": "2026-02-20",
        "estimated_delivery": "2026-02-26",
        "actual_delivery": "2026-02-27",
        "tracking_number": "TRK-55432",
        "carrier": "FedEx",
        "damage_description": "Box arrived crushed, keyboard has cracked keycap",
    },
    "ORD-1005": {
        "order_id": "ORD-1005",
        "customer_id": "CUST-003",
        "status": "cancelled",
        "items": [
            {"product_id": "PROD-F", "name": "Smart Speaker", "qty": 1, "price": 79.00}
        ],
        "total": 79.00,
        "order_date": "2026-02-22",
        "estimated_delivery": None,
        "actual_delivery": None,
        "tracking_number": None,
        "carrier": None,
        "cancel_reason": "Customer requested cancellation before shipment",
        "refund_status": "refund_issued",
        "refund_amount": 79.00,
    },
}

# ---------------------------------------------------------------------------
# CUSTOMERS
# ---------------------------------------------------------------------------

CUSTOMERS = {
    "CUST-001": {
        "customer_id": "CUST-001",
        "name": "Sarah Chen",
        "email": "sarah.chen@example.com",
        "phone": "555-0101",
        "member_since": "2023-06-15",
        "tier": "gold",          # gold = 2+ years, high spend
        "total_orders": 12,
        "preferred_contact": "email",
        # hooks for L4+ memory:
        "past_issues": ["late delivery (Oct 2025)", "wrong item sent (Dec 2025)"],
    },
    "CUST-002": {
        "customer_id": "CUST-002",
        "name": "Marcus Williams",
        "email": "marcus.w@example.com",
        "phone": "555-0202",
        "member_since": "2024-11-01",
        "tier": "standard",
        "total_orders": 3,
        "preferred_contact": "phone",
        "past_issues": [],
    },
    "CUST-003": {
        "customer_id": "CUST-003",
        "name": "Priya Patel",
        "email": "priya.patel@example.com",
        "phone": "555-0303",
        "member_since": "2022-03-20",
        "tier": "platinum",      # platinum = VIP, highest priority
        "total_orders": 31,
        "preferred_contact": "email",
        "past_issues": ["damaged item (Jan 2026)", "billing discrepancy (Feb 2026)"],
    },
}

# ---------------------------------------------------------------------------
# INVENTORY
# ---------------------------------------------------------------------------

INVENTORY = {
    "PROD-A": {"name": "Wireless Headphones",      "stock": 45,  "price": 89.99,  "sku": "WH-2024"},
    "PROD-B": {"name": "USB-C Charging Hub",        "stock": 12,  "price": 34.99,  "sku": "UCH-6P"},
    "PROD-C": {"name": "4K Webcam",                 "stock": 0,   "price": 129.00, "sku": "WC-4K"},
    "PROD-D": {"name": "Mechanical Keyboard",       "stock": 7,   "price": 149.00, "sku": "KB-MECH"},
    "PROD-E": {"name": "Mouse Pad XL",              "stock": 88,  "price": 19.99,  "sku": "MP-XL"},
    "PROD-F": {"name": "Smart Speaker",             "stock": 3,   "price": 79.00,  "sku": "SS-GEN2"},
    "PROD-G": {"name": "Laptop Stand Adjustable",   "stock": 0,   "price": 49.99,  "sku": "LS-ADJ"},
    "PROD-H": {"name": "Noise-Cancelling Earbuds",  "stock": 21,  "price": 119.00, "sku": "NCE-X"},
    "PROD-I": {"name": "External SSD 1TB",          "stock": 5,   "price": 99.00,  "sku": "SSD-1T"},
    "PROD-J": {"name": "Portable Charger 20000mAh", "stock": 0,   "price": 44.99,  "sku": "PC-20K"},
}

# ---------------------------------------------------------------------------
# FAQ / POLICY DOCS  (used by L3+ RAG)
# ---------------------------------------------------------------------------
# Each entry: id, title, content (plain text, kept short for embedding)

POLICIES = [
    {
        "id": "POL-001",
        "title": "Return Policy",
        "content": (
            "Acme Shop accepts returns within 30 days of delivery for most items. "
            "Items must be in original packaging and unused condition. "
            "Laptops and monitors have a 15-day return window. "
            "Damaged or defective items can be returned at any time within 90 days. "
            "To initiate a return, contact support with your order ID. "
            "Refunds are processed within 5-7 business days to the original payment method."
        ),
    },
    {
        "id": "POL-002",
        "title": "Shipping & Delivery",
        "content": (
            "Standard shipping takes 3-5 business days. "
            "Express shipping (2 business days) is available for an additional $9.99. "
            "Overnight shipping is available for $24.99. "
            "Orders over $100 qualify for free standard shipping. "
            "Once shipped, tracking information is emailed within 24 hours. "
            "Acme Shop is not responsible for carrier delays due to weather or customs."
        ),
    },
    {
        "id": "POL-003",
        "title": "Refund Policy",
        "content": (
            "Refunds are issued to the original payment method within 5-7 business days after "
            "the returned item is received and inspected. "
            "Partial refunds may be issued for items returned in less-than-original condition. "
            "Shipping costs are non-refundable unless the return is due to our error. "
            "Refunds over $200 require manager approval. "
            "Exchanges are processed as a new order; the original order is refunded separately."
        ),
    },
    {
        "id": "POL-004",
        "title": "Warranty Policy",
        "content": (
            "All Acme Shop products carry a 1-year limited warranty against manufacturing defects. "
            "The warranty does not cover accidental damage, water damage, or normal wear and tear. "
            "To file a warranty claim, provide proof of purchase and a description of the defect. "
            "Approved warranty claims result in a replacement unit or store credit. "
            "Extended warranty plans (2 or 3 years) can be purchased within 30 days of buying the product."
        ),
    },
    {
        "id": "POL-005",
        "title": "Account & Billing",
        "content": (
            "Customers can update email, phone, and shipping address from their account settings. "
            "Billing disputes must be reported within 60 days of the charge. "
            "Acme Shop accepts Visa, Mastercard, AmEx, PayPal, and Acme gift cards. "
            "For security, payment method changes require email verification. "
            "Duplicate charges are resolved within 3 business days. "
            "Acme Rewards points (1 point per $1 spent) can be redeemed at checkout for gold and platinum members."
        ),
    },
]
