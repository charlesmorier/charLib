import re
from typing import Optional
from typing import List
import QuantLib as ql

CONTRACT_MONTHS_CODES_MAP = {
    'F': ql.January,
    'G': ql.February,
    'H': ql.March,
    'J': ql.April,
    'K': ql.May,
    'M': ql.June,
    'N': ql.July,
    'Q': ql.August,
    'U': ql.September,
    'V': ql.October,
    'X': ql.November,
    'Z': ql.December,
}

IMM_MONTH_CODES = ["H", "M", "U", "Z"]

WEEKDAY_MAP = {
    "Mon": ql.Monday,
    "Tue": ql.Tuesday,
    "Wed": ql.Wednesday,
    "Thu": ql.Thursday,
    "Fri": ql.Friday,
    "Sat": ql.Saturday,
    "Sun": ql.Sunday,
}

FUTURES_RULES_MAP = {
    'IMM': '3Wed',  # Stop trading at IMM -2b
    'AU': '2Fri-1b',
    'NZ': '9d+1Wed',
}

# 1. Import dates from bloomberg -> ECO_FUTURE_RELEASE_DATE_LIST
# 2. Convert to double and round down -> =LET(date,ROUNDDOWN(AD265,0),IF(date>ValueDate,date,NA()))
# 3. Get month -> =IF(ISNUMBER(AD265),INDEX(Misc!$H$19:$H$30,MATCH(MONTH(AD265),Misc!$G$19:$G$30,0)),0) (map of months defined somewhere)
# 4. Calculate the rule: =INT((DAY(AD265)-1)/7)+1&IF(AD265<>0,TEXT(AD265,"Ddd"),"")
MEETING_DATES_RULES_MAP = {
    'BOC': {'F': '4Wed', 'G': None, 'H': '3Wed', 'J': '5Wed', 'K': None, 'M': '2Wed', 'N': '3Wed', 'Q': None, 'U': '1Wed', 'V': '4Wed', 'X': None, 'Z': '2Wed'},        # Bank of Canada
    'BOE': {'F': None, 'G': '1Thu', 'H': '3Thu', 'J': '5Thu', 'K': None, 'M': '3Thu', 'N': '5Thu', 'Q': None, 'U': '3Thu', 'V': None, 'X': '1Thu', 'Z': '3Thu'},        # Bank of England
    'BOJ': {'F': '4Fri',  'G': None, 'H': '3Thu', 'J': '4Tue', 'K': None, 'M': '3Tue', 'N': '5Fri', 'Q': None, 'U': '3Fri', 'V': '5Fri', 'X': None, 'Z': '3Fri'},       # Bank of Japan
    'ECB': {'F': None, 'G': '1Thu', 'H': '3Thu', 'J': '5Thu', 'K': None, 'M': '2Thu', 'N': '4Thu', 'Q': None, 'U': '2Thu', 'V': '5Thu', 'X': None, 'Z': '3Thu'},        # European Central Bank
    'FED': {'F': '4Wed', 'G': None, 'H': '3Wed', 'J': '4Wed', 'K': None, 'M': '2Wed', 'N': '4Wed', 'Q': None, 'U': '3Wed', 'V': '4Wed', 'X': None, 'Z': '2Wed'},        # Federal Fund
    'RBA': {'F': None, 'G': '1Tue', 'H': '3Tue', 'J': None, 'K': '1Tue', 'M': '3Tue', 'N': None, 'Q': '2Tue', 'U': '4Tue', 'V': None, 'X': '1Tue', 'Z': '2Tue'},        # Reserve Bank of Australia
    'RBNZ': {'F': None, 'G': '3Wed', 'H': None, 'J': '2Wed', 'K': '4Wed', 'M': None, 'N': '2Wed', 'Q': '3Wed', 'U': '1Wed', 'V': '2Wed', 'X': '4Wed', 'Z': '2Wed'},     # Reserve Bank of New Zealand
    'SNB': {'F': None, 'G': '1Thu', 'H': '3Thu', 'J': '5Thu', 'K': None, 'M': '2Thu', 'N': '4Thu', 'Q': None, 'U': '2Thu', 'V': '5Thu', 'X': None, 'Z': '3Thu'},       # Swiss National Bank
}


def json_to_ql_date(json_date):
    y, m, d = map(int, json_date.split("-"))
    return ql.Date(d, m, y)


def get_code_from_month(month: int):
    for k, v in CONTRACT_MONTHS_CODES_MAP.items():
        if v == month:
            return k
    return None


def _parse_rule(rule: str):
    pattern_nth_weekday = r"^(\d+)(Mon|Tue|Wed|Thu|Fri|Sat|Sun)([+-]\d+[db])?$"
    m = re.fullmatch(pattern_nth_weekday, rule)
    if m:
        return _rule_nth_weekday(m)
    pattern_after_day = r"^(\d+)d\+(\d+)(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$"
    m = re.fullmatch(pattern_after_day, rule)
    if m:
        return _rule_after_day(m)
    raise ValueError(f"Invalid rule format: {rule}")


def _rule_nth_weekday(m):
    n_str, weekday_str, suffix = m.groups()
    n = int(n_str)
    weekday = WEEKDAY_MAP[weekday_str]
    offset = 0
    offset_type = None

    if suffix:
        sign = 1 if suffix[0] == "+" else -1
        num = int(suffix[1:-1])
        unit = suffix[-1]
        offset = sign * num
        offset_type = unit

    return {
        "kind": "nth_weekday",
        "n": n,
        "weekday": weekday,
        "offset": offset,
        "offset_type": offset_type,
    }


def _rule_after_day(m):
    anchor_day_str, n_str, weekday_str = m.groups()
    anchor_day = int(anchor_day_str)
    n = int(n_str)
    weekday = WEEKDAY_MAP[weekday_str]

    return {
        "kind": "after_day",
        "anchor_day": anchor_day,
        "n": n,
        "weekday": weekday,
    }


def _compute_rule_date_for_year(month_code: str, rule: str, year: int, calendar: ql.Calendar, bdc: int) -> ql.Date:
    info = _parse_rule(rule)
    mcode = month_code.upper()

    if mcode not in CONTRACT_MONTHS_CODES_MAP:
        raise ValueError(f"Unknown futures month code: {month_code}")
    month = CONTRACT_MONTHS_CODES_MAP[mcode]
    kind = info["kind"]

    if kind == "nth_weekday":
        n = info["n"]
        weekday = info["weekday"]
        offset = info["offset"]
        offset_type = info["offset_type"]

        base = ql.Date.nthWeekday(n, weekday, month, year)
        if base.serialNumber() == 0:
            # fallback to last existing weekday of that type
            for k in range(n - 1, 0, -1):
                candidate = ql.Date.nthWeekday(k, weekday, month, year)
                if candidate.isValid():
                    base = candidate
                    break
        if offset != 0:
            if offset_type == "b":
                shifted = calendar.advance(base, offset, ql.Days)
                result = calendar.adjust(shifted, bdc)
            else:  # offset_type == "d"
                shifted = ql.Date(base.serialNumber() + offset)
                result = shifted  # calendar-day offsets are NOT adjusted
        else:
            result = base
        return result

    elif kind == "after_day":
        anchor_day = info["anchor_day"]
        n = info["n"]
        weekday = info["weekday"]
        anchor = ql.Date(anchor_day, month, year)
        current = ql.Date(anchor.serialNumber())
        found = 0

        while True:
            current = ql.Date(current.serialNumber() + 1)
            if current.month() != month or current.year() != year:
                raise ValueError(
                    f"Cannot find {n}-th {weekday} after day {anchor_day} in {month_code} {year}"
                )
            if current.weekday() == weekday:
                found += 1
                if found == n:
                    break

        result = calendar.adjust(current, bdc)
        return result

    else:
        raise RuntimeError("Unknown rule kind")


def compute_rule_date(
    month_code: str,
    rule: str,
    origin_date: Optional[ql.Date] = None,
    serial: int = 0,
    calendar: Optional[ql.Calendar] = None,
    bdc: int = ql.Unadjusted,
) -> ql.Date:
    if origin_date is None:
        origin_date = ql.Date.todaysDate()
    if calendar is None:
        calendar = ql.NullCalendar()

    mcode = month_code.strip().upper()
    if mcode not in CONTRACT_MONTHS_CODES_MAP:
        raise ValueError(f"Unknown futures month code: {month_code}")

    year = origin_date.year()
    count = -1
    while True:
        d = _compute_rule_date_for_year(mcode, rule, year, calendar, bdc)
        if d > origin_date:
            count += 1
            if count == serial:
                return d
        year += 1


def generate_meeting_dates(central_bank: str, n: int, origin_date: Optional[ql.Date] = None):
    if origin_date is None:
        origin_date = ql.Date.todaysDate()
    bank_rules = MEETING_DATES_RULES_MAP[central_bank.upper()]
    month_order = list(bank_rules.keys())
    results: List[ql.Date] = []
    current_origin = origin_date

    while len(results) < n:
        candidates: List[ql.Date] = []

        for m in month_order:
            rule = bank_rules[m]
            if rule is None:
                continue
            d = compute_rule_date(
                month_code=m,
                rule=rule,
                origin_date=current_origin
            )
            candidates.append(d)

        if not candidates:
            raise RuntimeError(f"No valid meeting rules for bank {central_bank}")

        next_date = min(candidates)
        if next_date <= current_origin:
            raise RuntimeError("contract_date returned non-increasing date; check logic")
        results.append(next_date)
        current_origin = next_date

    return results


def get_imm_date(code: str, mkt: str = "IMM"):
    rule = FUTURES_RULES_MAP[mkt.upper()]
    month_code = code[0].upper()
    origin_year = 2000 + int(code[1:])
    origin_date = ql.Date(1, ql.January, origin_year)
    return compute_rule_date(month_code, rule, origin_date)


def generate_imm_dates(n: int, mkt: str = "IMM", origin_date: Optional[ql.Date] = None, roll: bool = False) -> List[ql.Date]:
    if origin_date is None:
        origin_date = ql.Date.todaysDate()
    rule = FUTURES_RULES_MAP[mkt]

    def next_imm_after(anchor: ql.Date) -> ql.Date:
        candidates: List[ql.Date] = []
        for mcode in IMM_MONTH_CODES:
            d = compute_rule_date(month_code=mcode, rule=rule, origin_date=anchor)
            candidates.append(d)
        next_date = min(candidates)
        if next_date <= anchor:
            raise RuntimeError("compute_rule_date returned non-increasing date")
        return next_date

    current_origin = origin_date

    if roll:
        skipped = next_imm_after(current_origin)
        current_origin = skipped

    results: List[ql.Date] = []
    while len(results) < n:
        d = next_imm_after(current_origin)
        results.append(d)
        current_origin = d

    return results