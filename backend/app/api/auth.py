from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import secrets

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    AttestationConveyancePreference,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.models.user import User, WebAuthnCredential

router = APIRouter()

# In-memory challenge storage (in production, use Redis or similar)
# Format: {user_id: challenge}
registration_challenges = {}
authentication_challenges = {}


# Pydantic Models
class RegistrationStartRequest(BaseModel):
    email: EmailStr
    username: str


class RegistrationCompleteRequest(BaseModel):
    user_id: int
    credential: dict
    device_name: Optional[str] = None


class AuthenticationStartRequest(BaseModel):
    username: str


class AuthenticationCompleteRequest(BaseModel):
    username: str
    credential: dict


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# Registration Endpoints
@router.post("/auth/register/begin")
async def begin_registration(
    request: RegistrationStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start Passkey registration process

    Creates a new user and generates WebAuthn registration options
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == request.email) | (User.username == request.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Create new user
    user = User(
        email=request.email,
        username=request.username,
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate registration options
    options = generate_registration_options(
        rp_id=settings.INSTANCE_DOMAIN,
        rp_name="Money Manager",
        user_id=str(user.id).encode(),
        user_name=request.username,
        user_display_name=request.email,
        attestation=AttestationConveyancePreference.NONE,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
        supported_pub_key_algs=[
            COSEAlgorithmIdentifier.ECDSA_SHA_256,
            COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
        ],
    )

    # Store challenge temporarily
    registration_challenges[user.id] = options.challenge

    return {
        "user_id": user.id,
        "options": options_to_json(options)
    }


@router.post("/auth/register/complete")
async def complete_registration(
    request: RegistrationCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Complete Passkey registration

    Verifies the credential and stores it in the database
    """
    # Get user
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get stored challenge
    challenge = registration_challenges.get(request.user_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration challenge not found or expired"
        )

    try:
        # Verify registration response
        verification = verify_registration_response(
            credential=request.credential,
            expected_challenge=challenge,
            expected_rp_id=settings.INSTANCE_DOMAIN,
            expected_origin=f"https://{settings.INSTANCE_DOMAIN}",
        )

        # Store credential
        credential = WebAuthnCredential(
            user_id=user.id,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
            device_name=request.device_name
        )
        db.add(credential)
        db.commit()

        # Clean up challenge
        del registration_challenges[request.user_id]

        # Generate access token
        access_token = create_access_token({"sub": str(user.id)})

        return {
            "message": "Registration successful",
            "access_token": access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration verification failed: {str(e)}"
        )


# Authentication Endpoints
@router.post("/auth/login/begin")
async def begin_authentication(
    request: AuthenticationStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start Passkey authentication process

    Generates WebAuthn authentication options
    """
    # Get user
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    # Get user's credentials
    credentials = db.query(WebAuthnCredential).filter(
        WebAuthnCredential.user_id == user.id
    ).all()

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No passkeys registered for this user"
        )

    # Generate authentication options
    options = generate_authentication_options(
        rp_id=settings.INSTANCE_DOMAIN,
        allow_credentials=[
            PublicKeyCredentialDescriptor(id=cred.credential_id)
            for cred in credentials
        ],
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    # Store challenge
    authentication_challenges[user.id] = options.challenge

    return {
        "user_id": user.id,
        "options": options_to_json(options)
    }


@router.post("/auth/login/complete", response_model=TokenResponse)
async def complete_authentication(
    request: AuthenticationCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Complete Passkey authentication

    Verifies the credential and returns JWT token
    """
    # Get user
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get stored challenge
    challenge = authentication_challenges.get(user.id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authentication challenge not found or expired"
        )

    # Get credential from database
    credential_id = request.credential.get("id")
    if not credential_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credential format"
        )

    # Convert credential ID to bytes for lookup
    from base64 import urlsafe_b64decode
    try:
        # Add padding if necessary for base64url
        padding = 4 - (len(credential_id) % 4)
        if padding and padding != 4:
            credential_id += '=' * padding
        credential_id_bytes = urlsafe_b64decode(credential_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid credential ID format: {str(e)}"
        )

    cred = db.query(WebAuthnCredential).filter(
        WebAuthnCredential.credential_id == credential_id_bytes,
        WebAuthnCredential.user_id == user.id
    ).first()

    if not cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )

    try:
        # Verify authentication response
        verification = verify_authentication_response(
            credential=request.credential,
            expected_challenge=challenge,
            expected_rp_id=settings.INSTANCE_DOMAIN,
            expected_origin=f"https://{settings.INSTANCE_DOMAIN}",
            credential_public_key=cred.public_key,
            credential_current_sign_count=cred.sign_count,
        )

        # Update sign count and last used
        cred.sign_count = verification.new_sign_count
        cred.last_used = datetime.utcnow()
        db.commit()

        # Clean up challenge
        del authentication_challenges[user.id]

        # Generate access token
        access_token = create_access_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication verification failed: {str(e)}"
        )


# User info endpoint
@router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at,
    }


# ============================================================================
# OAuth2/OIDC Endpoints (Authentik, Keycloak, etc.)
# ============================================================================

from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse

# OAuth state storage (in production, use Redis)
oauth_states = {}

# Initialize OAuth client
oauth = OAuth()
if settings.OAUTH_ENABLED:
    oauth.register(
        name='oidc',
        client_id=settings.OAUTH_CLIENT_ID,
        client_secret=settings.OAUTH_CLIENT_SECRET,
        server_metadata_url=None,  # We configure manually
        authorize_url=settings.OAUTH_AUTHORIZATION_URL,
        access_token_url=settings.OAUTH_TOKEN_URL,
        client_kwargs={
            'scope': settings.OAUTH_SCOPES,
        }
    )


class OAuthLoginRequest(BaseModel):
    """Request to get OAuth login URL"""
    pass


@router.get("/auth/oauth/config")
async def get_oauth_config():
    """Get OAuth configuration for frontend"""
    return {
        "enabled": settings.OAUTH_ENABLED,
        "authorization_url": settings.OAUTH_AUTHORIZATION_URL if settings.OAUTH_ENABLED else None,
        "client_id": settings.OAUTH_CLIENT_ID if settings.OAUTH_ENABLED else None,
        "redirect_uri": settings.OAUTH_REDIRECT_URI if settings.OAUTH_ENABLED else None,
        "scopes": settings.OAUTH_SCOPES if settings.OAUTH_ENABLED else None,
    }


@router.get("/auth/oauth/login")
async def oauth_login(request: Request):
    """
    Redirect to OAuth provider (Authentik, Keycloak, etc.)

    This endpoint redirects the user to the OAuth provider's authorization page.
    """
    if not settings.OAUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth authentication is not enabled"
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True

    # Build authorization URL
    redirect_uri = settings.OAUTH_REDIRECT_URI
    scope = settings.OAUTH_SCOPES

    auth_url = (
        f"{settings.OAUTH_AUTHORIZATION_URL}"
        f"?client_id={settings.OAUTH_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&state={state}"
    )

    return {"authorization_url": auth_url, "state": state}


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str


@router.post("/auth/oauth/callback", response_model=TokenResponse)
async def oauth_callback(
    request: OAuthCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from provider

    Exchanges authorization code for access token and creates/updates user
    """
    if not settings.OAUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth authentication is not enabled"
        )

    # Verify state
    if request.state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )

    # Clean up state
    del oauth_states[request.state]

    try:
        # Exchange code for token
        import httpx
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                settings.OAUTH_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": request.code,
                    "redirect_uri": settings.OAUTH_REDIRECT_URI,
                    "client_id": settings.OAUTH_CLIENT_ID,
                    "client_secret": settings.OAUTH_CLIENT_SECRET,
                }
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )

            token_data = token_response.json()
            access_token = token_data.get("access_token")

            # Get user info from provider
            userinfo_response = await client.get(
                settings.OAUTH_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )

            userinfo = userinfo_response.json()

            # Extract user data
            email = userinfo.get("email")
            username = userinfo.get("preferred_username") or userinfo.get("sub")

            if not email or not username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user info from provider"
                )

            # Find or create user
            user = db.query(User).filter(User.email == email).first()

            if not user:
                # Create new user from OAuth
                user = User(
                    email=email,
                    username=username,
                    is_active=True,
                    is_superuser=False
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # Generate our JWT token
            jwt_token = create_access_token({"sub": str(user.id)})

            return {
                "access_token": jwt_token,
                "token_type": "bearer"
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}"
        )
