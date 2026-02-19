"""Measurements"""

from decimal import Decimal, ROUND_HALF_UP
from collections import Counter
import re


from decimal import Decimal, ROUND_HALF_UP, Context, setcontext
from collections import Counter
import re

# Set high precision context to prevent InvalidOperation during complex math
setcontext(Context(prec=30))


class Measurement:
    def __init__(self, value, uncertainty, unit=""):
        self.value = Decimal(str(value))
        self.uncertainty = Decimal(str(uncertainty))
        self.unit = self._simplify_units(unit)

    def _simplify_units(self, unit_str: str) -> str:
        if not unit_str or unit_str == "unitless":
            return ""

        # Normalize: Remove parentheses and standardize separators
        unit_str = unit_str.replace('(', '').replace(')', '')
        parts = unit_str.replace('*', ' ').replace('/', ' / ').split()

        counts: dict[str, float] = {}
        multiplier = 1.0

        for p in parts:
            if p == '/':
                multiplier = -1.0
                continue

            # Regex to catch base unit and the entire exponent string (e.g., 'm^2^0.5')
            match = re.match(r"([a-zA-Z]+)\^?([\d\.\-\^]*)", p)
            if match:
                base, exp_logic = match.groups()

                # Handle chained exponents like 2^0.5
                if '^' in exp_logic:
                    sub_parts = exp_logic.split('^')
                    exp = 1.0
                    for val in sub_parts:
                        if val:
                            try:
                                exp *= float(val)
                            except ValueError:
                                continue
                else:
                    exp = float(exp_logic) if exp_logic else 1.0

                counts[base] = counts.get(base, 0.0) + (exp * multiplier)

        num = []
        den = []
        for unit in sorted(counts.keys()):
            power = counts[unit]
            if abs(power) < 1e-9:
                continue

            p_display = int(power) if power % 1 == 0 else round(power, 2)
            p_abs = abs(p_display)
            formatted = f"{unit}^{p_abs}" if p_abs != 1 else unit

            if power > 0:
                num.append(formatted)
            else:
                den.append(formatted)

        if not num and not den:
            return ""
        res = "*".join(num) if num else "1"
        if den:
            res += "/" + "*".join(den)
        return res.replace("1/", "/").lstrip("/") if res != "1" else ""

    def __repr__(self):
        if self.uncertainty <= 0:
            return f"{format(self.value.normalize(), 'f')} {self.unit}".strip()
        try:
            unc_norm = self.uncertainty.normalize()
            display_val = self.value.quantize(unc_norm, rounding=ROUND_HALF_UP)
            v_str = format(display_val.normalize(), 'f')
            u_str = format(unc_norm, 'f')
            return f"{v_str} ± {u_str} {self.unit}".strip()
        except Exception:
            return f"{format(self.value.normalize(), 'f')} ± {format(self.uncertainty.normalize(), 'f')} {self.unit}".strip()

    def __add__(self, other):
        if not isinstance(other, Measurement) or self.unit != other.unit:
            raise ValueError(f"Units must match for addition: {self.unit} != {getattr(other, 'unit', 'scalar')}")
        return Measurement(self.value + other.value, self.uncertainty + other.uncertainty, self.unit)

    def __sub__(self, other):
        if not isinstance(other, Measurement) or self.unit != other.unit:
            raise ValueError(f"Units must match for subtraction: {self.unit} != {getattr(other, 'unit', 'scalar')}")
        return Measurement(self.value - other.value, self.uncertainty + other.uncertainty, self.unit)

    def __mul__(self, other):
        if not isinstance(other, Measurement):
            val = Decimal(str(other))
            return Measurement(self.value * val, self.uncertainty * abs(val), self.unit)
        new_val = self.value * other.value
        rel_error = (self.uncertainty / abs(self.value)) + (other.uncertainty / abs(other.value))
        return Measurement(new_val, rel_error * abs(new_val), f"{self.unit}*{other.unit}")

    def __truediv__(self, other):
        if not isinstance(other, Measurement):
            val = Decimal(str(other))
            return Measurement(self.value / val, self.uncertainty / abs(val), self.unit)
        rel_error = (self.uncertainty / abs(self.value)) + (other.uncertainty / abs(other.value))
        new_val = self.value / other.value
        return Measurement(new_val, rel_error * abs(new_val), f"{self.unit}/{other.unit}")

    def __pow__(self, power):
        p = Decimal(str(power))
        new_val = self.value ** p
        rel_error = abs(p) * (self.uncertainty / abs(self.value))
        return Measurement(new_val, rel_error * abs(new_val), f"{self.unit}^{p}")

    def sqrt(self):
        return self ** "0.5"


if __name__ == "__main__":
    print("--- STARTING MEASUREMENT ENGINE TEST ---\n")

    # 1. Basic Addition & Subtraction
    m1 = Measurement("10.500", "0.005", "g")
    m2 = Measurement("5.250", "0.005", "g")
    print(f"Addition:       {m1} + {m2} = {m1 + m2}")
    print(f"Subtraction:    {m1} - {m2} = {m1 - m2}")

    # 2. Multiplication & Unit Simplification (Dimensional Analysis)
    # 10m * 1000mm/m should = 10000mm
    length = Measurement("10.0", "0.1", "m")
    factor = Measurement("1000", "0", "mm/m")
    print(f"Unit Conversion: {length} * {factor} = {length * factor}")

    # 3. Scalar Math (Multiplying by a plain number)
    print(f"Scalar Scaling: {m1} * 3 = {m1 * 3}")

    # 4. Complex Derived Units (Force = Mass * Acceleration)
    mass = Measurement("2.00", "0.01", "kg")
    accel = Measurement("9.81", "0.01", "m/s^2")
    force = mass * accel
    print(f"Force Calc:     {force}")  # Should be kg*m/s^2

    # 5. Powers & Roots
    side = Measurement("4.00", "0.02", "m")
    area = side ** 2
    print(f"Power (Area):   {area}")  # Should be m^2

    root_side = area.sqrt()
    print(f"Root (Side):    {root_side}")  # Should be back to m

    # 6. Density Calculation (Mass / Volume)
    # Volume = side^3
    vol = side ** 3
    weight = Measurement("500.0", "0.5", "g")
    density = weight / vol
    print(f"Density:        {density}")  # Should be g/m^3

    # 7. Error Handling (Uncomment to test)
    print("\n--- ERROR HANDLING CHECKS ---")
    try:
        # Trying to add grams and meters
        bad_math = m1 + side
    except ValueError as e:
        print(f"Caught Unit Mismatch: {e}")

    print("\n--- TEST COMPLETE ---")
