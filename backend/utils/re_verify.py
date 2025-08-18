#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re


def search_string(pattern: str, text: str) -> re.Match[str] | None:
    """
    Regular match for all fields

    :param pattern: regular expression pattern
    :param text: text to be matched
    :return:
    """
    if not pattern or not text:
        return None

    result = re.search(pattern, text)
    return result


def match_string(pattern: str, text: str) -> re.Match[str] | None:
    """
    Regular match from the beginning of the field

    :param pattern: regular expression pattern
    :param text: text to be matched
    :return:
    """
    if not pattern or not text:
        return None

    result = re.match(pattern, text)
    return result


def is_phone(number: str) -> re.Match[str] | None:
    """
    Check mobile phone number format

    :param number: mobile phone number to be checked
    :return:
    """
    if not number:
        return None

    phone_pattern = r'^1[3-9]\d{9}$'
    return match_string(phone_pattern, number)


def is_git_url(url: str) -> re.Match[str] | None:
    """
    Check the git URL format

    :param url: URL to be checked
    :return:
    """
    if not url:
        return None

    git_pattern = r'^(?!(git\+ssh|ssh)://|git@)(?P<scheme>git|https?|file)://(?P<host>[^/]*)(?P<path>(?:/[^/]*)*/)(?P<repo>[^/]+?)(?:\.git)?$'
    return match_string(git_pattern, url)
