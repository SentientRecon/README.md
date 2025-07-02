"""
Sentient Recon Agent (SRA) - Main FastAPI Application
Advanced Cybersecurity Operations Platform with AI-driven Intelligence
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

# Core imports
from .core.database import get_db, init_db
from .core.security import SecurityManager, verify_token, hash_password
from .core.asimov_rules import AsimovSafetyEngine
from .core.cognitive_engine import CognitiveEngine
from .core.config import settings
from .models import models
from .schemas import schemas
from .services import (
    auth_service,
    mission_service,
    threat_service,
    incident_service,
    compliance_service,
    monitoring_service,
    analytics_service
)

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global instances
security_manager = SecurityManager()
asimov_engine = AsimovSafetyEngine()
cognitive_engine = CognitiveEngine()
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🤖 Starting Sentient Recon Agent (SRA)")
    
    # Initialize database
    await init_db()
    logger.info("📊 Database initialized")
    
    # Initialize Asimov Safety Engine
    await asimov_engine.initialize()
    logger.info("🛡️ Asimov Safety Engine initialized")
    
    # Initialize Cognitive Engine
    await cognitive_engine.initialize()
    logger.info("🧠 Cognitive Engine initialized")
    
    # Start background tasks
    asyncio.create_task(background_health_monitor())
    asyncio.create_task(background_threat_intelligence_sync())
    
    logger.info("✅ SRA Platform fully operational")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down SRA Platform")
    await cognitive_engine.shutdown()
    await asimov_engine.shutdown()
    logger.info("👋 SRA Platform shutdown complete")

# FastAPI app initialization
app = FastAPI(
    title="Sentient Recon Agent (SRA)",
    description="Advanced Cybersecurity Operations Platform with AI-driven Intelligence",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", 
                exc_info=exc, 
                request_url=str(request.url),
                request_method=request.method)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting and request tracking"""
    client_ip = request.client.host
    request_id = security_manager.generate_request_id()
    request.state.request_id = request_id
    
    # Check rate limits
    if not await security_manager.check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": "Rate limit exceeded",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Process request
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Log request
    logger.info("Request processed",
               request_id=request_id,
               method=request.method,
               url=str(request.url),
               status_code=response.status_code,
               process_time=process_time)
    
    response.headers["X-Request-ID"] = request_id
    return response

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = await auth_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        return user
    except Exception as e:
        logger.error("Authentication failed", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Permission dependency
def require_permission(resource: str, action: str):
    """Require specific permission for endpoint access"""
    async def permission_dependency(
        current_user = Depends(get_current_user)
    ):
        if not auth_service.has_permission(current_user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {resource}:{action}"
            )
        return current_user
    return permission_dependency

# Health check
@app.get("/health")
async def health_check():
    """System health check"""
    try:
        # Check database connectivity
        async with get_db() as db:
            await db.execute("SELECT 1")
        
        # Check Asimov engine
        asimov_status = asimov_engine.get_status()
        
        # Check cognitive engine
        cognitive_status = cognitive_engine.get_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0",
            "components": {
                "database": "healthy",
                "asimov_engine": asimov_status,
                "cognitive_engine": cognitive_status
            }
        }
    except Exception as e:
        logger.error("Health check failed", exc_info=e)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow(),
                "error": str(e)
            }
        )

# Authentication endpoints
@app.post("/api/auth/login")
async def login(
    credentials: schemas.LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """User authentication with MFA support"""
    try:
        result = await auth_service.authenticate_user(
            db, 
            credentials.username, 
            credentials.password,
            credentials.mfa_code
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
        
        # Check Asimov rules for login
        safety_check = await asimov_engine.validate_action(
            "user_login",
            {"user_id": result["user"].id, "timestamp": datetime.utcnow()}
        )
        
        if not safety_check.approved:
            logger.warning("Login blocked by Asimov rules",
                         user_id=result["user"].id,
                         reason=safety_check.reason)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied by security protocol"
            )
        
        logger.info("User login successful", user_id=result["user"].id)
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@app.post("/api/auth/logout")
async def logout(
    token_data: schemas.TokenData,
    current_user = Depends(get_current_user)
):
    """User logout and token invalidation"""
    try:
        await auth_service.invalidate_token(token_data.token)
        logger.info("User logout successful", user_id=current_user.id)
        return {
            "success": True,
            "message": "Logged out successfully",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error("Logout error", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout service error"
        )

# Mission Control endpoints
@app.get("/api/missions")
async def get_missions(
    page: int = 1,
    limit: int = 20,
    current_user = Depends(require_permission("missions", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all missions with pagination"""
    try:
        missions = await mission_service.get_missions(db, page, limit)
        return {
            "success": True,
            "data": missions,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error("Get missions error", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mission service error"
        )

@app.post("/api/missions")
async def create_mission(
    mission_data: schemas.MissionCreate,
    current_user = Depends(require_permission("missions", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create new mission with Asimov safety validation"""
    try:
        # Asimov safety check
        safety_check = await asimov_engine.validate_mission(mission_data.dict())
        if not safety_check.approved:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Mission violates safety protocols: {safety_check.reason}"
            )
        
        mission = await mission_service.create_mission(db, mission_data, current_user.id)
        
        logger.info("Mission created", 
                   mission_id=mission.id, 
                   created_by=current_user.id)
        
        return {
            "success": True,
            "data": mission,
            "timestamp": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Create mission error", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mission creation error"
        )

@app.post("/api/missions/{mission_id}/start")
async def start_mission(
    mission_id: str,
    current_user = Depends(require_permission("missions", "execute")),
    db: AsyncSession = Depends(get_db)
):
    """Start mission execution with cognitive engine"""
    try:
        mission = await mission_service.get_mission_by_id(db, mission_id)
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mission not found"
            )
        
        # Final Asimov safety check before execution
        safety_check = await asimov_engine.validate_mission_execution(mission)
        if not safety_check.approved:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Mission execution blocked: {safety_check.reason}"
            )
        
        # Start mission with cognitive engine
        result = await mission_service.start_mission(db, mission_id, current_user.id)
        
        # Delegate to cognitive engine for autonomous execution
        asyncio.create_task(
            cognitive_engine.execute_mission(mission_id, mission.objectives)
        )
        
        logger.info("Mission started", 
                   mission_id=mission_id, 
                   started_by=current_user.id)
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Start mission error", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mission start error"
        )

@app.post("/api/missions/emergency-stop")
async def emergency_stop(
    current_user = Depends(require_permission("missions", "emergency_stop")),
    db: AsyncSession = Depends(get_db)
):
    """Emergency stop all missions - Asimov Rule 1 implementation"""
    try:
        # Immediate stop all missions
        stopped_missions = await mission_service.emergency_stop_all(db, current_user.id)
        
        # Stop cognitive engine processes
        await cognitive_engine.emergency_stop()
        
        # Log critical event
        logger.critical("Emergency stop activated", 
                       stopped_missions=len(stopped_missions),
                       activated_by=current_user.id)
        
        return {
            "success": True,
            "message": f"Emergency stop completed. {len(stopped_missions)} missions stopped.",
            "stopped_missions": stopped_missions,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.critical("Emergency stop failed", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Emergency stop failed"
        )

# Background tasks
async def background_health_monitor():
    """Background task for system health monitoring"""
    while True:
        try:
            # Monitor system health
            await monitoring_service.collect_system_metrics()
            
            # Check for anomalies
            anomalies = await monitoring_service.detect_anomalies()
            if anomalies:
                logger.warning("System anomalies detected", anomalies=anomalies)
            
            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logger.error("Health monitoring error", exc_info=e)
            await asyncio.sleep(60)

async def background_threat_intelligence_sync():
    """Background task for threat intelligence synchronization"""
    while True:
        try:
            # Sync threat intelligence feeds
            await threat_service.sync_threat_feeds()
            
            # Process new indicators
            await threat_service.process_new_indicators()
            
            await asyncio.sleep(3600)  # Sync every hour
        except Exception as e:
            logger.error("Threat intelligence sync error", exc_info=e)
            await asyncio.sleep(3600)

# Additional endpoints for threat intelligence, incidents, compliance, etc.
# would be included here following the same pattern...

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )