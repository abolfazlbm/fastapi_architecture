import re


def search_string(pattern: str, text: str) -> re.Match[str]:
    """
    Regular match for all fields

    :param pattern: regular expression pattern
    :param text: text to be matched
    :return:
    """
    return re.search(pattern, text)


def match_string(pattern: str, text: str) -> re.Match[str]:
    """
    Regular match from the beginning of the field

    :param pattern: regular expression pattern
    :param text: text to be matched
    :return:
    """
    return re.match(pattern, text)


def is_phone(number: str) -> re.Match[str]:
    """
    Check mobile phone number format

    :param number: mobile phone number to be checked
    :return:
    """
    phone_pattern = r'^1[3-9]\d{9}$'
    return match_string(phone_pattern, number)


def is_git_url(url: str) -> re.Match[str]:
    """
    Check the git URL format

    :param url: URL to be checked
    :return:
    """
    git_pattern = r'^(?!(git\+ssh|ssh)://|git@)(?P<scheme>git|https?|file)://(?P<host>[^/]*)(?P<path>(?:/[^/]*)*/)(?P<repo>[^/]+?)(?:\.git)?$'
    return match_string(git_pattern, url)


def is_has_number(value: str) -> re.Match[str]:
    """
    检查数字

    :param value: 待检查的值
    :return:
    """
    number_pattern = r'\d'
    return search_string(number_pattern, value)


def is_has_letter(value: str) -> re.Match[str]:
    """
    检查字母

    :param value: 待检查的值
    :return:
    """
    letter_pattern = r'[a-zA-Z]'
    return search_string(letter_pattern, value)


def is_has_special_char(value: str) -> re.Match[str]:
    """
    检查特殊字符

    :param value: 待检查的值
    :return:
    """
    special_char_pattern = r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]'
    return search_string(special_char_pattern, value)
