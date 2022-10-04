from decimal import Decimal

from pydantic import condecimal, constr

DecimalPercent = condecimal(ge=Decimal("0"), le=Decimal("1.0"))
NonEmptyStr = constr(min_length=1)
