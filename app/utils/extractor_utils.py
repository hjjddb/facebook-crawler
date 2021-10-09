from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

from config.config import timezone


def title_extractor(title_div):
    return title_div.string.strip()


def date_extractor(date_div):
    time_re = "\d{1,2}:\d{2}"
    time = re.search(time_re, str(date_div)).group()
    date_re = "\d{1,2}/\d{1,2}/(\d{2}){1,2}"
    date = re.search(date_re, str(date_div)).group()
    return int(datetime.timestamp(datetime.strptime(f"{date} {time}", "%d/%m/%Y %H:%M")))


def time_extractor(time_div):
    """
    convert normal timestamp to integer timestamp
    """
    now = datetime.now(timezone)
    if "giờ" in time_div:
        delta = int(re.search('\d{1,2}').group())
        return int(datetime.timestamp(now - timedelta(hours=delta)))
    if "lúc" in time_div:
        time = re.search("(?<= )\d{1,2}:\d{1,2}", time_div).group()
        if "Hôm qua" in time_div:
            delta = (datetime.strptime(
                f'{now.hour}:{now.minute}', '%H:%M') - datetime.strptime(time, '%H:%M')).total_seconds()
            return int(datetime.timestamp(now - timedelta(days=1))-delta)
        date = re.findall("\d{1,4}", time_div)
        print(date)
        if len(date) < 5:
            date[2] = now.year
        return int(datetime.timestamp(datetime.strptime(f"{date[0]} {date[1]} {date[2]} {time}", "%d %m %Y %H:%M")))
    date = re.findall("\d{1,4}", time_div)
    if len(date) < 3:
        date.append(now.year)
    return int(datetime.timestamp(datetime.strptime(f"{date[0]} {date[1]} {date[2]}", "%d %m %Y")))