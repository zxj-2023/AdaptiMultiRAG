from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.param.auth import LoginRequest, RegisterRequest
from backend.param.common import Response
from backend.service import auth
from backend.config.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["AUTH"]
)


@router.post("/login", response_model=Response)
async def login(login_request: LoginRequest):
    """用户登录"""
    return await auth.login(login_request)


@router.post("/register", response_model=Response)
async def register(register_request: RegisterRequest):
    """用户注册"""
    return await auth.register(register_request)
    # return Response.error("注册功能已禁用，请联系管理员")


@router.get("/me", response_model=Response)
async def get_current_user_info(current_user: int = Depends(get_current_user)):
    """获取当前用户信息"""
    from backend.service.auth import get_user_by_id
    
    user = await get_user_by_id(current_user)
    if not user:
        return Response.error("用户不存在")
    
    return Response.success({
        "username": user.username,
        "email": user.email
    })


@router.get("/protected", response_model=Response)
async def protected(current_user: int = Depends(get_current_user)):
    """受保护的路由示例"""
    return Response.success({"message": "访问成功", "user": current_user})