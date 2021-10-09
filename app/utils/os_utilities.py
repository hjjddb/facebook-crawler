import platform


def get_current_os():
    """
    get the current OS, i.e. Linux or Windows, or ect.
    :return:
    """
    p = platform.system()
    if p.startswith('Linux'):
        return 'linux'
    elif p.startswith('Windows'):
        return 'windows'
    else:
        return 'unknown'
