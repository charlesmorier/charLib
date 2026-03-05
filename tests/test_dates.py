
from charlib.utility import dates

# Rule
d = dates.compute_rule_date('H', '2Wed')
print(d)

# IMM dates
d = dates.get_imm_date("U6")
print(d)

# IMM dates series
d = dates.generate_imm_dates(n=8)
print(d)

# Meeting dates
d = dates.generate_meeting_dates(central_bank='RBA', n=8)
print(d)