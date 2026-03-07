from fastapi import Depends, HTTPException, status


async def get_current_user():
    # TODO: Implement Auth0 token verification
    # 1. Extract Bearer token from Authorization header
    # 2. Verify JWT with Auth0 JWKS endpoint
    # 3. Return decoded user payload
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Auth0 not configured yet",
    )
