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
    
    # Sign the EXACT bytes we will send so the receiver can verify them as-is
    invoice_json = invoice.model_dump_json()
    signature = sign_data(invoice_json)

    # Send the raw signed body (do not let httpx re-serialize the dict)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{instance_data['api_endpoint']}/federation/invoice/receive",
            content=invoice_json,
            headers={
                "Content-Type": "application/json",
                "X-Signature": signature,
                "X-Instance": settings.INSTANCE_DOMAIN,
            },
        )
        response.raise_for_status()
        return response.json()


async def verify_invoice_signature(raw_body: str, from_user: str, signature: str) -> bool:
    """Verify a federated invoice signature over the exact received bytes.

    ``raw_body`` must be the verbatim request body the sender signed; verifying
    a re-serialized model would be fragile across instances.
    """
    from app.federation.crypto import verify_signature

    from_parts = from_user.split("@")
    if len(from_parts) != 2:
        return False
    _, sender_domain = from_parts

    # Fetch the sender instance's published public key
    async with httpx.AsyncClient() as client:
        try:
            instance_info = await client.get(f"https://{sender_domain}/.well-known/money-instance")
            instance_info.raise_for_status()
            sender_data = instance_info.json()
        except Exception:
            return False

    return verify_signature(raw_body, signature, sender_data["public_key"])


async def fetch_instance_public_key(domain: str) -> str:
    """Fetch public key from another instance"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://{domain}/.well-known/money-instance")
        response.raise_for_status()
        data = response.json()
        return data["public_key"]


async def fetch_instance_info(domain: str) -> dict:
    """Fetch a peer instance's discovery document over its HTTPS endpoint.

    Trust at pairing time is bootstrapped by the peer's TLS (Let's Encrypt)
    certificate: a successful HTTPS fetch authenticates the domain, and the
    returned public key is then pinned by the caller.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"https://{domain}/.well-known/money-instance")
        response.raise_for_status()
        data = response.json()
    if "public_key" not in data:
        raise ValueError("Peer did not expose a public key")
    return {
        "instance_id": data.get("instance_id", domain),
        "public_key": data["public_key"],
        "api_endpoint": data.get("api_endpoint", f"https://{domain}/api/v1"),
        "federation_enabled": data.get("federation_enabled", False),
    }
