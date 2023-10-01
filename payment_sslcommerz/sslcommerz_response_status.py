# -*- coding: utf-8 -*-

SSLCOMMERZ_STATUS = {
    "VALID": "Transaction is successful",
    "VALIDATED": "Transaction is successful",
    "FAILED": "Transaction is declined by customer's Issuer Bank.",
    "CANCELLED": "Transaction is cancelled by the customer.",
    "UNATTEMPTED": "Customer did not choose to pay any channel.",
    "EXPIRED": "Payment Timeout",
    "INVALID_TRANSACTION": "Invalid validation id"
}

REFUND_INIT_STATUS = {
    "success": "Refund request is initiated successfully",
    "failed": "Refund request is failed to initiate",
    "processing": "The refund has been initiated already"
}

REFUND_STATUS = {
    "refunded": "Refund request has been proceeded successfully",
    "processing": "Refund request is under processing",
    "cancelled": "Refund request has been cancelled"
}
