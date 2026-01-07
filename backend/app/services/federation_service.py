import httpx
from app.core.config import settings
from app.federation.crypto import sign_data, verify_signature


async def send_federated_invoice(invoice):
    """Send invoice to another instance"""
    from app.federation.crypto import sign_data
    import json
    
    # Extract target instance domain
    to_user_parts = invoice.to_user.split("@")
    if len(to_user_parts) != 2:
        raise ValueError("Invalid user identifier format. Expected: user@instance.domain")
    
    username, target_domain = to_user_parts
    
    # Get target instance info
    async with httpx.AsyncClient() as client:
        instance_info = await client.get(f"https://{target_domain}/.well-known/money-instance")
        instance_info.raise_for_status()
        instance_data = instance_info.json()
    
    # Sign the invoice
    invoice_json = invoice.model_dump_json()
    signature = sign_data(invoice_json)
    
    # Send to target instance
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{instance_data['api_endpoint']}/federation/invoice/receive",
            json=invoice.model_dump(),
            headers={
                "X-Signature": signature,
                "X-Instance": settings.INSTANCE_DOMAIN
            }
        )
        response.raise_for_status()
        return response.json()


async def verify_and_store_invoice(invoice, signature: str) -> bool:
    """Verify invoice signature from another instance"""
    from app.federation.crypto import verify_signature
    import json
    
    # Extract sender instance
    from_parts = invoice.from_user.split("@")
    if len(from_parts) != 2:
        return False
    
    _, sender_domain = from_parts
    
    # Get sender's public key
    async with httpx.AsyncClient() as client:
        try:
            instance_info = await client.get(f"https://{sender_domain}/.well-known/money-instance")
            instance_info.raise_for_status()
            sender_data = instance_info.json()
        except:
            return False
    
    # Verify signature
    invoice_json = invoice.model_dump_json()
    return verify_signature(invoice_json, signature, sender_data["public_key"])


async def fetch_instance_public_key(domain: str) -> str:
    """Fetch public key from another instance"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://{domain}/.well-known/money-instance")
        response.raise_for_status()
        data = response.json()
        return data["public_key"]
