"""
NOF1 API Proxy Service
FastAPI service để gọi API NOF1 sử dụng curl_cffi
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from curl_cffi import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="NOF1 API Proxy",
    description="Proxy service cho NOF1 API sử dụng curl_cffi",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
NOF1_BASE_URL = os.getenv("NOF1_BASE_URL", "https://nof1.ai")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Response models
class ApiResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = datetime.now().isoformat()

class HealthResponse(BaseModel):
    status: str
    timestamp: str = datetime.now().isoformat()
    service: str = "nof1-proxy"

# Global session
session = requests.Session()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy")

@app.get("/api/account-totals", response_model=ApiResponse)
async def get_account_totals(marker: Optional[int] = Query(None, description="Marker for pagination")):
    """
    Proxy endpoint cho NOF1 account totals API
    """
    try:
        # Build URL
        url = f"{NOF1_BASE_URL}/api/account-totals"
        if marker is not None:
            url += f"?marker={marker}"
        
        # Headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': f"{NOF1_BASE_URL}/",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Make request using curl_cffi with browser impersonation
        response = session.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            impersonate="chrome120"  # Impersonate Chrome 120
        )
        
        # Check if response is successful
        response.raise_for_status()
        
        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            # If not JSON, return text content
            data = {"content": response.text}
        
        return ApiResponse(
            success=True,
            data=data
        )
        
    except requests.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" (Status: {e.response.status_code})"
        
        return ApiResponse(
            success=False,
            error=error_msg
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@app.get("/api/proxy", response_model=ApiResponse)
async def proxy_request(
    url: str = Query(..., description="URL to proxy to"),
    method: str = Query("GET", description="HTTP method"),
):
    """
    Generic proxy endpoint cho bất kỳ NOF1 API nào
    """
    try:
        # Validate URL starts with NOF1_BASE_URL for security
        if not url.startswith(NOF1_BASE_URL):
            raise HTTPException(
                status_code=400, 
                detail=f"URL must start with {NOF1_BASE_URL}"
            )
        
        # Headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': f"{NOF1_BASE_URL}/",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        # Make request
        response = session.request(
            method.upper(),
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            impersonate="chrome120"
        )
        
        response.raise_for_status()
        
        # Parse response
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"content": response.text}
        
        return ApiResponse(
            success=True,
            data=data
        )
        
    except requests.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" (Status: {e.response.status_code})"
        
        return ApiResponse(
            success=False,
            error=error_msg
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    print("🚀 NOF1 API Proxy started")
    print(f"📡 Proxying to: {NOF1_BASE_URL}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    session.close()
    print("🛑 NOF1 API Proxy stopped")