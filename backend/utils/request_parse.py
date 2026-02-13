import httpx

from fastapi import Request
from ip2loc import XdbSearcher
from user_agents import parse

from backend.common.dataclasses import IpInfo, UserAgentInfo
from backend.common.log import log
from backend.core.conf import settings
from backend.core.path_conf import STATIC_DIR
from backend.database.redis import redis_client


def get_request_ip(request: Request) -> str:
    """
    Get the requested IP address

    :param request: FastAPI request object
    :return:
    """
    real = request.headers.get('X-Real-IP')
    if real:
        return real

    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0]

    # ignore pytest
    if request.client.host == 'testclient':
        return '127.0.0.1'

    return request.client.host


async def get_location_online(ip: str) -> dict | None:
    """
    Get the IP address location online, no availability is guaranteed, and the accuracy is high

    :param ip: IP address
    :return:
    """
    async with httpx.AsyncClient(timeout=3) as client:
        try:
            response = await client.get(f'http://ip-api.com/json/{ip}?lang=zh-CN')
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.error(f'Failed to obtain IP address locality online, error message：{e}')
            return None


# Offline IP searcher singleton (data will be cached to memory, cache size depends on IP data file size)
__xdb_searcher = XdbSearcher(contentBuff=XdbSearcher.loadContentFromFile(dbfile=STATIC_DIR / 'ip2region_v4.xdb'))


def get_location_offline(ip: str) -> dict | None:
    """
    Get IP address location offline, no accuracy guaranteed, 100% available

    :param ip: IP address
    :return:
    """
    try:
        data = __xdb_searcher.search(ip)
        data = data.split('|')
        return {
            'country': data[0] if data[0] != '0' else None,
            'regionName': data[1] if data[1] != '0' else None,
            'city': data[2] if data[2] != '0' else None,
        }
    except Exception as e:
        log.error(f'Failed to obtain IP address offline, error message：{e}')
        return None


async def parse_ip_info(request: Request) -> IpInfo:
    """
    Resolve the requested IP information

    :param request: FastAPI request object
    :return:
    """
    country, region, city = None, None, None
    ip = get_request_ip(request)
    location = await redis_client.get(f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}')
    if location:
        country, region, city = location.split('|')
        return IpInfo(ip=ip, country=country, region=region, city=city)

    location_info = None
    if settings.IP_LOCATION_PARSE == 'online':
        location_info = await get_location_online(ip)
    elif settings.IP_LOCATION_PARSE == 'offline':
        location_info = get_location_offline(ip)

    if location_info:
        country = location_info.get('country')
        region = location_info.get('regionName')
        city = location_info.get('city')
        await redis_client.set(
            f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}',
            f'{country}|{region}|{city}',
            ex=settings.IP_LOCATION_EXPIRE_SECONDS,
        )
    return IpInfo(ip=ip, country=country, region=region, city=city)


def parse_user_agent_info(request: Request) -> UserAgentInfo:
    """
    Resolve requested user agent information

    :param request: FastAPI request object
    :return:
    """
    os, browser, device = None, None, None
    user_agent = request.headers.get('User-Agent')
    if user_agent:
        user_agent_ = parse(user_agent)
        os = user_agent_.get_os()
        browser = user_agent_.get_browser()
        device = user_agent_.get_device()
    return UserAgentInfo(user_agent=user_agent, device=device, os=os, browser=browser)
