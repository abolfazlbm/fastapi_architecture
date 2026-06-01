from fastapi import Depends, Request

from backend.common.context import ctx
from backend.common.enums import MethodType, StatusType
from backend.common.exception import errors
from backend.common.security.jwt import DependsJwtAuth
from backend.core.conf import settings


async def rbac_verify(request: Request, _token: str = DependsJwtAuth) -> None:  # noqa: C901
    """
    RBAC permission verification (the order of authentication is very important, please modify it with caution)

    :param request: FastAPI request object
    :param _token: JWT token
    :return:
    """
    path = request.url.path

    # API authentication whitelist
    if path in settings.TOKEN_REQUEST_PATH_EXCLUDE:
        return
    for pattern in settings.TOKEN_REQUEST_PATH_EXCLUDE_PATTERN:
        if pattern.match(path):
            return

    # JWT Authorization Status Forced Verification
    if not request.auth.scopes:
        raise errors.TokenError

    # Super administrator without verification
    if request.user.is_superuser:
        return

    # Detect user roles
    user_roles = request.user.roles
    enabled_roles = [role for role in user_roles if role.status == StatusType.enable]
    if not enabled_roles:
        raise errors.AuthorizationError(msg='The role of the user has been locked, please contact the system administrator')

    # Detect the roles of the user
    if not any(len(role.menus) > 0 for role in enabled_roles):
        raise errors.AuthorizationError(msg='User has not assigned a menu, please contact the system administrator')

    # Detect background management operation permissions
    method = request.method
    if method not in {MethodType.GET, MethodType.OPTIONS} and not request.user.is_staff:
        raise errors.AuthorizationError(msg='The user has been banned from background management operations, please contact the system administrator')

    # RBAC Authentication
    if settings.RBAC_ROLE_MENU_MODE:
        path_auth_perm = ctx.permission

        # No menu operation permissions identification is not verified
        if not path_auth_perm:
            return

        # Menu authentication whitelist
        if path_auth_perm in settings.RBAC_ROLE_MENU_EXCLUDE:
            return

        # Menu re-removal
        unique_menus = {}
        for role in enabled_roles:
            for menu in role.menus:
                unique_menus[menu.id] = menu

        # Assigned menu permission verification
        allow_perms = []
        for menu in list(unique_menus.values()):
            if menu.perms and menu.status == StatusType.enable:
                allow_perms.extend(menu.perms.split(','))
        if path_auth_perm not in allow_perms:
            raise errors.AuthorizationError
    else:
        # casbin method
        try:
            from backend.plugin.casbin_rbac.rbac import casbin_verify
        except ImportError:
            raise errors.ServerError(msg='Casbin RBAC Plug-in usage failed to import, please contact the system administrator')

        await casbin_verify(request)


# RBAC Authorization Dependency Injection
DependsRBAC = Depends(rbac_verify)
