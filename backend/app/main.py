from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import accounts, transactions, categories, federation, shared_accounts, settings_api, bank_import, auth, replication, reconciliation, two_factor, recurring, integrations
from app.core.database import engine, SessionLocal
from app.models import base
import os

# Read version from VERSION file
def get_version():
    version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "VERSION")
    try:
        with open(version_file, "r") as f:
            return f.read().strip()
    except:
        return "1.1.0"  # Fallback

VERSION = get_version()

# Create database tables
base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Money Manager API",
    description="Self-hosted personal finance management with federation support",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(two_factor.router, prefix="/api/v1/2fa", tags=["two-factor-auth"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["accounts"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(shared_accounts.router, prefix="/api/v1/shared-accounts", tags=["shared-accounts"])
app.include_router(federation.router, prefix="/api/v1/federation", tags=["federation"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(bank_import.router, prefix="/api/v1/import", tags=["bank-import"])
app.include_router(replication.router, prefix="/api/v1/replication", tags=["replication"])
app.include_router(reconciliation.router, prefix="/api/v1", tags=["reconciliation"])
app.include_router(recurring.router, prefix="/api/v1/recurring", tags=["recurring"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])


@app.get("/")
async def root():
    return {
        "message": "Money Manager API",
        "version": VERSION,
        "docs": "/docs",
        "instance": settings.INSTANCE_DOMAIN,
        "federation_enabled": settings.FEDERATION_ENABLED,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Well-known endpoint for federation discovery
@app.get("/.well-known/money-instance")
async def instance_info():
    from app.federation.crypto import get_public_key_pem

    return {
        "instance_id": settings.INSTANCE_DOMAIN,
        "version": VERSION,
        "public_key": get_public_key_pem(),
        "api_endpoint": f"{settings.FEDERATION_SCHEME}://{settings.INSTANCE_DOMAIN}/api/v1",
        "federation_enabled": settings.FEDERATION_ENABLED,
    }


# Background Scheduler for recurring transactions (runs once a day)
@app.on_event("startup")
async def start_recurring_scheduler():
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except Exception as e:  # pragma: no cover - scheduler is optional
        print(f"[Recurring] Scheduler unavailable ({e}); use POST /api/v1/recurring/process manually")
        return

    from app.services.recurring_service import process_due_recurring

    def run_recurring_job():
        db = SessionLocal()
        try:
            created = process_due_recurring(db)
            if created:
                print(f"[Recurring] Created {created} due transaction(s)")
        except Exception as e:
            print(f"[Recurring Error] {e}")
        finally:
            db.close()

    recurring_scheduler = AsyncIOScheduler()
    recurring_scheduler.add_job(run_recurring_job, 'interval', hours=24, id='recurring_process', replace_existing=True)
    # Also run shortly after startup so a restart doesn't skip a day
    run_recurring_job()
    recurring_scheduler.start()
    app.state.recurring_scheduler = recurring_scheduler
    print("[Recurring] Daily scheduler started")


# Background Scheduler for Replication
if settings.REPLICATION_ENABLED:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from app.services.replication_service import ReplicationService
    import asyncio

    scheduler = AsyncIOScheduler()

    async def sync_mirrors_job():
        """Background job to sync with all mirror instances"""
        db = SessionLocal()
        try:
            service = ReplicationService(db)
            result = await service.sync_all_mirrors()
            print(f"[Replication Sync] Synced: {result.get('synced_count', 0)}, Failed: {result.get('failed_count', 0)}")
        except Exception as e:
            print(f"[Replication Sync Error] {str(e)}")
        finally:
            db.close()

    def run_sync_job():
        """Wrapper to run async job in sync context"""
        asyncio.create_task(sync_mirrors_job())

    @app.on_event("startup")
    async def start_scheduler():
        """Start background scheduler on app startup"""
        scheduler.add_job(
            run_sync_job,
            'interval',
            minutes=settings.REPLICATION_SYNC_INTERVAL_MINUTES,
            id='mirror_sync',
            replace_existing=True
        )
        scheduler.start()
        print(f"[Replication] Background sync scheduler started (interval: {settings.REPLICATION_SYNC_INTERVAL_MINUTES} minutes)")

    @app.on_event("shutdown")
    async def shutdown_scheduler():
        """Shutdown scheduler on app shutdown"""
        scheduler.shutdown()
        print("[Replication] Background sync scheduler stopped")
