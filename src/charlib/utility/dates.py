import re
import QuantLib as ql


CONTRACT_MONTH_CODES_MAP: dict[str, int] = {
    "f": ql.January,
    "g": ql.February,
    "h": ql.March,
    "j": ql.April,
    "k": ql.May,
    "m": ql.June,
    "n": ql.July,
    "q": ql.August,
    "u": ql.September,
    "v": ql.October,
    "x": ql.November,
    "z": ql.December,
}


IMM_MONTH_CODES_MAP: dict[str, int] = {
    "h": ql.March,
    "m": ql.June,
    "u": ql.September,
    "z": ql.December,
}


FUTURES_RULES_MAP = {
    'imm': '3Wed',
    'sfe': '2Fri-1b',
    'nsx': '9d+1Wed',
}


TENOR_UNITS: dict[str, int] = {
    "d": ql.Days,
    "w": ql.Weeks,
    "m": ql.Months,
    "y": ql.Years,
}


WEEKDAY_MAP: dict[str, int] = {
    "mon": ql.Monday,
    "tue": ql.Tuesday,
    "wed": ql.Wednesday,
    "thu": ql.Thursday,
    "fri": ql.Friday,
    "sat": ql.Saturday,
    "sun": ql.Sunday,
}


# 1. Import dates from bloomberg -> ECO_FUTURE_RELEASE_DATE_LIST
# 2. Convert to double and round down -> =LET(date,ROUNDDOWN(AD265,0),IF(date>ValueDate,date,NA()))
# 3. Get month -> =IF(ISNUMBER(AD265),INDEX(Misc!$H$19:$H$30,MATCH(MONTH(AD265),Misc!$G$19:$G$30,0)),0) (map of months defined somewhere)
# 4. Calculate the rule: =INT((DAY(AD265)-1)/7)+1&IF(AD265<>0,TEXT(AD265,"Ddd"),"")
MEETING_DATES_RULES_MAP = {
    'boc': {'F': '4Wed', 'G': None, 'H': '3Wed', 'J': '5Wed', 'K': None, 'M': '2Wed', 'N': '3Wed', 'Q': None, 'U': '1Wed', 'V': '4Wed', 'X': None, 'Z': '2Wed'},        # Bank of Canada
    'boe': {'F': None, 'G': '1Thu', 'H': '3Thu', 'J': '5Thu', 'K': None, 'M': '3Thu', 'N': '5Thu', 'Q': None, 'U': '3Thu', 'V': None, 'X': '1Thu', 'Z': '3Thu'},        # Bank of England
    'boj': {'F': '4Fri',  'G': None, 'H': '3Thu', 'J': '4Tue', 'K': None, 'M': '3Tue', 'N': '5Fri', 'Q': None, 'U': '3Fri', 'V': '5Fri', 'X': None, 'Z': '3Fri'},       # Bank of Japan
    'ecb': {'F': None, 'G': '1Thu', 'H': '3Thu', 'J': '5Thu', 'K': None, 'M': '2Thu', 'N': '4Thu', 'Q': None, 'U': '2Thu', 'V': '5Thu', 'X': None, 'Z': '3Thu'},        # European Central Bank
    'fed': {'F': '4Wed', 'G': None, 'H': '3Wed', 'J': '4Wed', 'K': None, 'M': '2Wed', 'N': '4Wed', 'Q': None, 'U': '3Wed', 'V': '4Wed', 'X': None, 'Z': '2Wed'},        # Federal Fund
    'rba': {'F': None, 'G': '1Tue', 'H': '3Tue', 'J': None, 'K': '1Tue', 'M': '3Tue', 'N': None, 'Q': '2Tue', 'U': '4Tue', 'V': None, 'X': '1Tue', 'Z': '2Tue'},        # Reserve Bank of Australia
    'rbnz': {'F': None, 'G': '3Wed', 'H': None, 'J': '2Wed', 'K': '4Wed', 'M': None, 'N': '2Wed', 'Q': '3Wed', 'U': '1Wed', 'V': '2Wed', 'X': '4Wed', 'Z': '2Wed'},     # Reserve Bank of New Zealand
    'snb': {'F': None, 'G': '1Thu', 'H': '3Thu', 'J': '5Thu', 'K': None, 'M': '2Thu', 'N': '4Thu', 'Q': None, 'U': '2Thu', 'V': '5Thu', 'X': None, 'Z': '3Thu'},        # Swiss National Bank
}


MEETING_DATES_SETTLEMENT_MAP = {
    'boc': '1b',
    'boe': '2b',
    'boj': '2b',
    'ecb': '5b',
    'fed': '2b',
    'rba': '1b',
    'rbnz': '2b',
    'snb': '2b',
}


def today() -> ql.Date:
    return ql.Date.todaysDate()


def _parse_rule(rule: str) -> dict:
    rule = rule.strip()
    m = re.fullmatch(r"(\d+)(Mon|Tue|Wed|Thu|Fri|Sat|Sun)([+-]\d+[db])?", rule, re.IGNORECASE)
    if m:
        n_str, weekday_str, suffix = m.groups()
        n = int(n_str)
        weekday = WEEKDAY_MAP[weekday_str.lower()]
        offset, offset_type = 0, None
        if suffix:
            sign = 1 if suffix[0] == "+" else -1
            offset = sign * int(suffix[1:-1])
            offset_type = suffix[-1].lower()
        return {"kind": "nth_weekday", "n": n, "weekday": weekday,
                "offset": offset, "offset_type": offset_type}

    m = re.fullmatch(r"(\d+)d\+(\d+)(Mon|Tue|Wed|Thu|Fri|Sat|Sun)", rule, re.IGNORECASE)
    if m:
        anchor_day_str, n_str, weekday_str = m.groups()
        return {"kind": "after_day", "anchor_day": int(anchor_day_str),
                "n": int(n_str), "weekday": WEEKDAY_MAP[weekday_str.lower()]}

    raise ValueError(f"Cannot parse rule '{rule}'.")


def _apply_rule(rule_info: dict, month: int, year: int, calendar: ql.Calendar, bdc: int) -> ql.Date:
    kind = rule_info["kind"]

    if kind == "nth_weekday":
        n, weekday = rule_info["n"], rule_info["weekday"]
        offset, offset_type = rule_info["offset"], rule_info["offset_type"]
        base = ql.Date.nthWeekday(n, weekday, month, year)

        if offset != 0:
            if offset_type == "b":
                result = calendar.advance(base, offset, ql.Days, bdc)
            else:
                result = base + offset
        else:
            result = base if bdc == ql.Unadjusted else calendar.adjust(base, bdc)
        return result

    elif kind == "after_day":
        anchor    = ql.Date(rule_info["anchor_day"], month, year)
        n         = rule_info["n"]
        weekday   = rule_info["weekday"]
        current   = anchor
        found     = 0
        while True:
            current = current + 1
            if current.month() != month:
                raise ValueError(
                    f"Cannot find {n}-th weekday after day "
                    f"{rule_info['anchor_day']} in month {month} {year}."
                )
            if current.weekday() == weekday:
                found += 1
                if found == n:
                    break
        return calendar.adjust(current, bdc)

    raise RuntimeError(f"Unknown rule kind '{kind}'.")


def compute_rule_date(month_code: str, rule: str, origin_date: ql.Date | None = None, serial: int = 0, calendar: ql.Calendar | None = None, bdc: int = ql.Unadjusted) -> ql.Date:
    if origin_date is None:
        origin_date = today()
    if calendar is None:
        calendar = ql.NullCalendar()

    mcode = month_code.strip().lower()
    if mcode not in CONTRACT_MONTH_CODES_MAP:
        raise ValueError(f"Unknown futures month code '{month_code}'.")

    month = CONTRACT_MONTH_CODES_MAP[mcode.lower()]
    rule_info = _parse_rule(rule)
    year = origin_date.year()
    count = -1

    while True:
        d = _apply_rule(rule_info, month, year, calendar, bdc)
        if d > origin_date:
            count += 1
            if count == serial:
                return d
        year += 1


def nth_weekday(rule: str, month_code: str, calendar: ql.Calendar | None = None, bdc: int = ql.Unadjusted) -> ql.Date:
    rule = rule.strip()
    mc = month_code.strip().lower()
    m = re.fullmatch(r"([fghjkmnquvxz])(\d{2})?", mc)
    if not m:
        raise ValueError(f"Cannot parse month code '{month_code}'. ")
    month = CONTRACT_MONTH_CODES_MAP[m.group(1)]
    year_given = m.group(2) is not None

    if year_given:
        year = 2000 + int(m.group(2))
        cal = calendar or ql.NullCalendar()
        rule_info = _parse_rule(rule)
        result = _apply_rule(rule_info, month, year, cal, bdc)
        if result < today():
            raise ValueError(f"nth_weekday('{rule}', '{month_code}'): resulting date {result} is in the past.")
        return result
    else:
        t = today()
        origin = ql.Date(1, month, t.year()) - 1
        return compute_rule_date(mc[0], rule, origin_date=origin, serial=0, calendar=calendar, bdc=bdc)


def generate_meeting_dates(central_bank: str, n: int, origin_date: ql.Date | None = None, calendar: ql.Calendar | None = None, bdc: int = ql.Unadjusted) -> list[ql.Date]:
    if origin_date is None:
        origin_date = today()

    code = central_bank.strip().lower()
    if code not in MEETING_DATES_RULES_MAP:
        raise ValueError(f"Unknown central bank..")

    cal = calendar or ql.NullCalendar()
    bank_rules = MEETING_DATES_RULES_MAP[code]
    results = []
    current_origin = origin_date

    while len(results) < n:
        candidates = []
        for mcode, rule in bank_rules.items():
            if rule is None:
                continue
            d = compute_rule_date(mcode, rule, origin_date=current_origin, calendar=cal, bdc=bdc)
            candidates.append(d)

        if not candidates:
            raise RuntimeError(f"No valid meeting rules for '{central_bank}'.")

        decision_date = min(candidates)
        lag = MEETING_DATES_SETTLEMENT_MAP.get(code, 0)
        settlement_date = _parse_tenor(lag, decision_date)
        results.append(settlement_date)
        current_origin = decision_date  # advance from decision date, not settlement

    return results


def get_imm_date(code: str, mkt: str = "imm", calendar: ql.Calendar | None = None, bdc: int = ql.Unadjusted) -> ql.Date:
    rule = FUTURES_RULES_MAP.get(mkt.strip().lower())
    if rule is None:
        raise ValueError(f"Unknown market '{mkt}'.")
    month_code = code.strip()[0].lower()
    origin_year = 2000 + int(code.strip()[1:])
    origin_date = ql.Date(1, ql.January, origin_year) - 1
    return compute_rule_date(month_code, rule, origin_date=origin_date, calendar=calendar or ql.NullCalendar(), bdc=bdc)


def generate_imm_dates(n: int, mkt: str = "imm", origin_date: ql.Date | None = None, calendar: ql.Calendar | None = None, bdc: int = ql.Unadjusted, skip_first: bool = False) -> list[ql.Date]:
    if origin_date is None:
        origin_date = today()

    rule = FUTURES_RULES_MAP.get(mkt.strip().lower())
    if rule is None:
        raise ValueError(f"Unknown market '{mkt}'. ")

    cal = calendar or ql.NullCalendar()

    def _next_imm(anchor: ql.Date) -> ql.Date:
        candidates = [compute_rule_date(mc, rule, origin_date=anchor, calendar=cal, bdc=bdc) for mc in IMM_MONTH_CODES_MAP]
        return min(candidates)

    current = origin_date
    if skip_first:
        current = _next_imm(current)

    results = []
    while len(results) < n:
        d = _next_imm(current)
        results.append(d)
        current = d

    return results


def _parse_iso(s: str) -> ql.Date:
    y, m, d = s.split("-")
    return ql.Date(int(d), int(m), int(y))


def _parse_tenor(s: str, anchor: ql.Date, calendar: ql.Calendar | None = None) -> ql.Date:
    m = re.fullmatch(r"(\d+)([dbwmy])", s)
    if not m:
        raise ValueError(f"Cannot parse '{s}' as a tenor.")
    n         = int(m.group(1))
    unit_char = m.group(2).lower()

    if unit_char == "b":
        cal = calendar if calendar is not None else ql.WeekendsOnly()
        d, steps = anchor, 0
        while steps < n:
            d = d + 1
            if cal.isBusinessDay(d):
                steps += 1
        return d
    else:
        unit = TENOR_UNITS.get(unit_char, ql.Days)
        if calendar is not None:
            return calendar.advance(anchor, n, unit, ql.Following)
        return anchor + ql.Period(n, unit)


def _parse_bom_eom(s: str, calendar: ql.Calendar | None = None) -> ql.Date:
    s = s.strip().lower()
    m = re.fullmatch(r"(bom|eom)(\d+)", s)
    if not m:
        raise ValueError(f"Cannot parse '{s}' as a BOM/EOM keyword.")
    prefix = m.group(1)
    n = int(m.group(2))
    t = today()
    bom_this = ql.Date(1, t.month(), t.year())
    target_bom = bom_this + ql.Period(n, ql.Months)
    if prefix == "bom":
        result = target_bom
        return calendar.adjust(result, ql.Following) if calendar is not None else result
    else:
        result = ql.Date.endOfMonth(target_bom)
        return calendar.adjust(result, ql.Preceding) if calendar is not None else result


def _parse_imm(s: str, convention: str = "imm", calendar: ql.Calendar | None = None, bdc: int = ql.Unadjusted) -> ql.Date:
    m = re.fullmatch(r"([fghjkmnquvxz])(\d{2})?", s, re.IGNORECASE)
    rule = FUTURES_RULES_MAP.get(convention.lower())
    if not m:
        raise ValueError(f"Cannot parse '{s}' as an IMM keyword.")
    if rule is None:
        raise ValueError(f"Unknown IMM convention '{convention}'.")
    return nth_weekday(rule, s)


def _parse_meeting_date(s: str, calendar: ql.Calendar | None = None, bdc: int = ql.Unadjusted) -> ql.Date:
    s = s.strip().lower()
    m = re.fullmatch(r"([a-z_]+)(\d+)", s)
    if not m:
        raise ValueError(f"Cannot parse '{s}' as a keyword.")
    code = m.group(1)
    code = code.lower()
    n    = int(m.group(2))

    if n < 1:
        raise ValueError(f"Index must be >= 1 (e.g. '{code}1').")

    # --- futures market: imm1, sfe_au2, nz3, etc. ---
    if code in FUTURES_RULES_MAP:
        dates = generate_imm_dates(n, mkt=code, calendar=calendar, bdc=bdc)
        return dates[-1]

    # --- central bank: rba1, fed2, boe1, ecb3, etc. ---
    if code in MEETING_DATES_RULES_MAP:
        dates = generate_meeting_dates(code, n, calendar=calendar, bdc=bdc)
        return dates[-1]

    raise ValueError(
        f"Unknown code '{code}'. "
        f"Futures markets: {list(FUTURES_RULES_MAP.keys())}. "
        f"Central banks: {[k.lower() for k in MEETING_DATES_RULES_MAP.keys()]}."
    )


def _resolve_anchor(anchor: ql.Date | str | None, calendar: ql.Calendar | None) -> ql.Date:
    if anchor is None:
        return today()
    if isinstance(anchor, ql.Date):
        return anchor
    if isinstance(anchor, str):
        s = anchor.strip().lower()
        if re.fullmatch(r"\d+[dbwmy]", s, re.IGNORECASE):
            return _parse_tenor(s, today(), calendar)
        raise ValueError(
            f"anchor='{s}' is not a recognised tenor string. ")
    raise TypeError(
        f"anchor must be a ql.Date, tenor string, or None — got {type(anchor).__name__}.")


def parse_date(value: ql.Date | str, anchor: ql.Date | str | None = None, calendar: ql.Calendar | None = None, imm_convention: str = "imm", bdc: int = ql.Unadjusted) -> ql.Date:
    if isinstance(value, ql.Date):
        return value
    if not isinstance(value, str):
        raise TypeError(f"parse_date() expects a ql.Date or str, got {type(value).__name__}.")

    s = value.strip().lower()

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return _parse_iso(s)

    # -- composite: e.g. "sfe1+3m", "rba2+1b" --------------------------------
    m = re.fullmatch(r"([a-z0-9]+)([+-]\d+[dbwmy])", s)
    if m:
        base_date  = parse_date(m.group(1), anchor, calendar, imm_convention, bdc)
        sign       = 1 if m.group(2)[0] == "+" else -1
        tenor_str  = m.group(2)[1:]
        unit_char  = tenor_str[-1]
        n          = sign * int(tenor_str[:-1])
        if unit_char == "b":
            cal       = calendar if calendar is not None else ql.WeekendsOnly()
            d, steps  = base_date, 0
            direction = 1 if n > 0 else -1
            while steps < abs(n):
                d = d + direction
                if cal.isBusinessDay(d):
                    steps += 1
            return d
        else:
            unit = TENOR_UNITS.get(unit_char, ql.Days)
            if calendar is not None:
                return calendar.advance(base_date, n, unit, ql.Following)
            return base_date + ql.Period(n, unit)

    if re.fullmatch(r"(bom|eom)\d+", s):
        return _parse_bom_eom(s, calendar)

    # IMM must precede central bank: "h26" matches both patterns
    if re.fullmatch(r"[fghjkmnquvxz]\d{2}", s):
        return _parse_imm(s, imm_convention, calendar, bdc)

    if re.fullmatch(r"[a-z_]+\d+", s):
        return _parse_meeting_date(s, calendar, bdc)

    if re.fullmatch(r"\d+[dbwmy]", s):
        return _parse_tenor(s, _resolve_anchor(anchor, calendar), calendar)

    raise ValueError(f"parse_date() could not recognise '{s}'.")




#pillars_aonia = ['rba1', 'rba2', 'rba3', 'rba4', 'rba5', 'rba6', 'rba7', 'rba8', 'rba9', '18m', '2y', '3y']
#pillars_bbsw3m = ['sfe1', 'sfe2', 'sfe3', 'sfe4', 'sfe5', 'sfe6', 'sfe7', 'sfe8', 'sfe9', '3y']

#spot_date = _parse_tenor('1b', today())
#pillars_aonia_dt = [parse_date(t, spot_date, calendar=ql.Australia()) for t in pillars_aonia]
#pillars_bbsw3m_dt = [parse_date(t, spot_date, calendar=ql.Australia()) for t in pillars_bbsw3m]
#print(pillars_aonia_dt)
#print(pillars_bbsw3m_dt)