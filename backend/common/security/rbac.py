#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Depends, Request

from backend.common.enums import MethodType, StatusType
from backend.common.exception import errors
from backend.common.log import log
from backend.common.security.jwt import DependsJwtAuth
from backend.core.conf import settings
from backend.utils.import_parse import import_module_cached


async def rbac_verify(request: Request, _token: str = DependsJwtAuth) -> None:
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
    if not user_roles or all(status == 0 for status in user_roles):
        raise errors.AuthorizationError(msg='User has not assigned a role, please contact the system administrator')

    # Detect the roles of the user
    if not any(len(role.menus) > 0 for role in user_roles):
        raise errors.AuthorizationError(msg='User has not assigned a menu, please contact the system administrator')

    # Detect background management operation permissions
    method = request.method
    if method != MethodType.GET or method != MethodType.OPTIONS:
        if not request.user.is_staff:
            raise errors.AuthorizationError(msg='The user has been banned from background management operations, please contact the system administrator')

    # RBAC Authentication
    if settings.RBAC_ROLE_MENU_MODE:
        path_auth_perm = getattr(request.state, 'permission', None)

        # No menu operation permissions identification is not verified
        if not path_auth_perm:
            return

        # Menu authentication whitelist
        if path_auth_perm in settings.RBAC_ROLE_MENU_EXCLUDE:
            return

        # Menu re-removal
        unique_menus = {}
        for role in user_roles:
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
        try:
            casbin_rbac = import_module_cached('backend.plugin.casbin_rbac.rbac')
            casbin_verify = getattr(casbin_rbac, 'casbin_verify')
        except (ImportError, AttributeError) as e:
            log.error(f' is performing RBAC permission verification through casbin, but this plugin does not exist: {e}')
            raise errors.ServerError(msg='Permission verification failed, please contact the system administrator')

        await casbin_verify(request)


# RBAC Authorization Dependency Injection
DependsRBAC = Depends(rbac_verify)
