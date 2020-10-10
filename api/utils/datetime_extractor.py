from datetime import datetime, timedelta
import re

import datefinder
from pytz import timezone, utc
from word2number import w2n


KST = timezone('Asia/Seoul')

# process single date entity text
def parse_date(date_str):
    output = None
    
    # first check for explicit dates
    matches = datefinder.find_dates(date_str)
    for match in matches:
        output = match
    if output:
        return output
    
    # match the following
    # tomorrow, tonight, today, day after tomorrow
    # next M-S/week/month/year,  this M-S/weekend, \d day[s]/week[s] later/after
    # \d days from now, \d days from today, in \d weeks, in \d days
    re_rel_date = re.compile('tomorrow|tonight|today|day after tomorrow')
    re_dmy = re.compile('day|week|month')
    re_numbers = re.compile('(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty) (days?|weeks?)')
    re_from = re.compile('(from|after) (today|tomorrow)')
    re_day = re.compile('monday|tuesday|wednesday|thursday|friday|saturday|sunday')
    re_exp1 = re.compile('this|upcoming|next')
    re_exp2 = re.compile('')

    day_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2,
                   'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}

    # match by \d day[s] and \d weeks
    # need to check for 'from' today/tomorrow
    res = re_numbers.search(date_str)
    if res:
        n, unit = res.group().split()
        n = w2n.word_to_num(n)

        start_point = 'today'
        res_from = re_from.search(date_str)
        if res_from:
            start_point = res_from.group().split()[-1]
        
        output = utc.localize(datetime.utcnow()).astimezone(KST)
        if unit in ('day', 'days'):
            output += timedelta(days=n)
        elif unit in ('week', 'weeks'):
            output += timedelta(weeks=n)
        if start_point == 'tomorrow':
            output += timedelta(days=1)
        return output

    # match relative date
    res = re_rel_date.search(date_str)
    if res:
        if res.group() == 'today' or res.group() == 'tonight':
            output = utc.localize(datetime.utcnow()).astimezone(KST)
        elif res.group() == 'tomorrow':
            output = utc.localize(datetime.utcnow()).astimezone(KST) + timedelta(days=1)
        elif res.group() == 'day after tomorrow':
            output = utc.localize(datetime.utcnow()).astimezone(KST) + timedelta(days=2)
        return output

    # match by day
    res_day = re_day.search(date_str)
    if res_day:
        day = res_day.group()
        output = utc.localize(datetime.utcnow()).astimezone(KST)
        res_exp1 = re_exp1.search(date_str)
        exp1 = None
        if res_exp1:
            exp1 = res_exp1.group()
        # if exp1 == 'this' or None: closest day from now
        # else, if the day has passed, closet, and next week otherwise
        if exp1 is None or exp1 in ('this', 'upcoming') or day_map[day] < output.weekday():
            output += timedelta(days=(day_map[day] - output.weekday()) % 7)
        else:
            output += timedelta(days=(day_map[day] - output.weekday()) % 7 + 7)
        return output

    return None



# return [(hour, minute), (hour, minute)]
def parse_time(date_str):
    re_exp1 = re.compile('(from)? (?P<start_time>.*) (until|to) (?P<end_time>.*)')
    re_exp2 = re.compile('(at|on|from) (?P<target_time>.*)')
    re_exp3 = re.compile('(by|until) (?P<target_time>.*)')
    
    res = re_exp1.search(date_str)
    if res:
        start_time = parse_time_str(res.group('start_time'))
        end_time = parse_time_str(res.group('end_time'))
        if start_time and end_time:
            return [start_time, end_time]
        else:
            return None

    res = re_exp2.search(date_str)
    if res:
        target_time = parse_time_str(res.group('target_time'))
        return [target_time, (target_time[0] + 1, target_time[1])]
    
    res = re_exp3.search(date_str)
    if res:
        target_time = parse_time_str(res.group('target_time'))
        if target_time:
            return [target_time, target_time]
        return None

    target_time = parse_time_str(date_str)
    if target_time:
        return [target_time, (target_time[0] + 1, target_time[1])]

    return None


# return (hour, minute, type)
# type: default 0 (starts at the given time)
# default 1 (ends at the given time)
def parse_time_str(date_str):
    # end of \d, by \d, at \d, \d+:\d+
    # \d\w?(am|a\.m|pm|p\.m)) 
    # \d+\w(one|two|...|)
    # from \time to|until \time
    
    re_formal = re.compile('(?P<hour>\d{1,2}):(?P<minute>\d{1,2})')
    re_formal2 = re.compile('(?P<hour>\d{2})(?P<minute>\d{2})')
    re_number = re.compile('(?P<hour>one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)(?P<minute> \d{1,2})?')

    res = re_formal.search(date_str)
    if res:
        return (int(res.group("hour")), int(res.group("minute")))

    res = re_formal2.search(date_str)
    if res:
        return (int(res.group("hour")), int(res.group("minute")))

    res = re_number.search(date_str)
    if res:
        hour = res.group("hour")
        minute = res.group("minute")
        if minute:
            minute = int(minute)
        else:
            minute = 0
        return (w2n.word_to_num(hour), minute)

    return None


# return (start_datetime, end_datetime)
def process_datetime_str(date_str):
    date_str = date_str.lower()
    parsed_date = parse_date(date_str)
    parsed_time = parse_time(date_str)
    if parsed_date is None and parsed_time is None:
        return None
    if parsed_time is None:
        return (parsed_date, parsed_date)
    if parsed_date is None:
        parsed_date = utc.localize(datetime.utcnow()).astimezone(KST)
    start_time, end_time = parse_time(date_str)
    if start_time[0] <= 7:
        start_time = (start_time[0] + 12, start_time[1])
        end_time = (end_time[0] + 12, end_time[1])
    start_datetime  = parsed_date.replace(hour=start_time[0]).replace(minute=start_time[1])
    end_datetime = parsed_date.replace(hour=end_time[0]).replace(minute=end_time[1])
    return (start_datetime, end_datetime)

