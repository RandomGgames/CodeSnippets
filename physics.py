"""
Functions for working with physics units and measurements
"""

import logging
import math

logger = logging.getLogger(__name__)


class Unit:
    """Lightweight unit descriptor with conversion support"""

    def __init__(self, name: str, dimension: str, factor_to_base: float = 1.0):
        self.name = name
        self.dimension = dimension
        self.factor_to_base = factor_to_base  # scale to base unit (g, mm, s)

    def __str__(self):
        return self.name if self.name else ""

    def __mul__(self, other):
        if not isinstance(other, Unit):
            return NotImplemented
        if self.is_dimensionless():
            return other
        if other.is_dimensionless():
            return self
        return Unit(
            f"{self.name}·{other.name}" if self.name and other.name else self.name or other.name,
            f"{self.dimension}·{other.dimension}" if self.dimension and other.dimension else self.dimension or other.dimension,
            self.factor_to_base * other.factor_to_base
        )

    def __truediv__(self, other):
        if not isinstance(other, Unit):
            return NotImplemented
        if self.factor_to_base == other.factor_to_base and self.dimension == other.dimension:
            return Unit.dimensionless()
        if other.is_dimensionless():
            return self
        if self.is_dimensionless():
            return Unit(f"1/{other.name}", f"1/{other.dimension}", 1 / other.factor_to_base)
        return Unit(
            f"{self.name}/{other.name}" if self.name and other.name else self.name or other.name,
            f"{self.dimension}/{other.dimension}" if self.dimension and other.dimension else self.dimension or other.dimension,
            self.factor_to_base / other.factor_to_base
        )

    def __eq__(self, other):
        if not isinstance(other, Unit):
            return False
        return self.name == other.name and self.dimension == other.dimension

    def is_dimensionless(self):
        return self.name == "" or self.dimension == "dimensionless"

    # ---------------- Unit constructors ----------------
    @classmethod
    def dimensionless(cls):
        return cls("", "dimensionless", 1.0)

    # Mass
    @classmethod
    def kilogram(cls):
        return cls("kg", "mass", 1000.0)

    @classmethod
    def gram(cls):
        return cls("g", "mass", 1.0)

    @classmethod
    def milligram(cls):
        return cls("mg", "mass", 0.001)

    # Length
    @classmethod
    def meter(cls):
        return cls("m", "length", 1000.0)

    @classmethod
    def millimeter(cls):
        return cls("mm", "length", 1.0)

    @classmethod
    def kilometer(cls):
        return cls("km", "length", 1_000_000.0)

    @classmethod
    def centimeter(cls):
        return cls("cm", "length", 10.0)

    @classmethod
    def inch(cls):
        return cls("in", "length", 25.4)

    @classmethod
    def foot(cls):
        return cls("ft", "length", 304.8)

    @classmethod
    def mile(cls):
        return cls("mi", "length", 1_609_344.0)

    # Time
    @classmethod
    def second(cls):
        return cls("s", "time", 1.0)

    @classmethod
    def millisecond(cls):
        return cls("ms", "time", 0.001)

    # Temperature
    @classmethod
    def celsius(cls):
        return cls("°C", "temperature", 1.0)

    @classmethod
    def fahrenheit(cls):
        return cls("°F", "temperature", 1.0)

    @classmethod
    def kelvin(cls):
        return cls("K", "temperature", 1.0)

    # ---------------- Conversion ----------------
    def convert_value_to(self, value: float, target_unit: "Unit", scale_only=False) -> float:
        """Convert a numeric value from this unit to another unit."""
        if self.dimension != target_unit.dimension:
            raise ValueError(f"Cannot convert {self.dimension} to {target_unit.dimension}")

        # Temperature special case
        if self.dimension == "temperature":
            # Convert self -> Kelvin
            match self.name:
                case "°C": val_in_base = value + 273.15
                case "°F": val_in_base = (value - 32) * 5 / 9 + 273.15
                case "K": val_in_base = value
                case _: val_in_base = value

            # Convert Kelvin -> target
            match target_unit.name:
                case "°C": result = val_in_base - 273.15
                case "°F": result = (val_in_base - 273.15) * 9 / 5 + 32
                case "K": result = val_in_base
                case _: result = val_in_base

            if scale_only:
                # Only scale uncertainty linearly
                if self.name == "°C" and target_unit.name == "°F":
                    return value * 9 / 5
                if self.name == "°F" and target_unit.name == "°C":
                    return value * 5 / 9
                return value
            return result

        # Linear conversion
        return value * (self.factor_to_base / target_unit.factor_to_base)


# ---------------- Measurement ----------------
class Measurement:
    """Number with uncertainty, units, and decimals."""

    def __init__(self, value: float, decimals=None, uncertainty: float = 0.0, units: Unit = Unit.dimensionless()):
        if units is None:
            units = Unit.dimensionless()
        self.value = value
        self.uncertainty = uncertainty
        self.units = units
        self.decimals = decimals
        self._round()

    def _round(self):
        if self.decimals is not None:
            self.value = round(self.value, self.decimals)
            self.uncertainty = round(self.uncertainty, self.decimals)

    # ---------------- Arithmetic ----------------
    def _as_measurement(self, other) -> "Measurement":
        if isinstance(other, Measurement):
            return other
        if isinstance(other, (int, float)):
            return Measurement(float(other), decimals=None, uncertainty=0.0, units=self.units)
        raise TypeError(f"Cannot convert {other} to Measurement")

    def _decimals_for(self, other: "Measurement"):
        if self.decimals is None and other.decimals is None:
            return None
        if self.decimals is None:
            return other.decimals
        if other.decimals is None:
            return self.decimals
        return min(self.decimals, other.decimals)

    def __add__(self, other):
        other = self._as_measurement(other)
        if self.units != other.units and not other.units.is_dimensionless():
            raise ValueError(f"Unit mismatch: {self.units} vs {other.units}")
        value = self.value + other.value
        uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
        return Measurement(value, decimals=self._decimals_for(other), uncertainty=uncertainty, units=self.units)

    __radd__ = __add__

    def __sub__(self, other):
        other = self._as_measurement(other)
        if self.units != other.units and not other.units.is_dimensionless():
            raise ValueError(f"Unit mismatch: {self.units} vs {other.units}")
        value = self.value - other.value
        uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
        return Measurement(value, decimals=self._decimals_for(other), uncertainty=uncertainty, units=self.units)

    def __rsub__(self, other):
        return self._as_measurement(other) - self

    def __mul__(self, other):
        other = self._as_measurement(other)
        value = self.value * other.value
        rel_unc = math.sqrt(
            (self.uncertainty / self.value if self.value != 0 else 0)**2 +
            (other.uncertainty / other.value if other.value != 0 else 0)**2
        )
        uncertainty = abs(value) * rel_unc
        units = self.units * other.units
        return Measurement(value, decimals=self._decimals_for(other), uncertainty=uncertainty, units=units)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self._as_measurement(other)
        value = self.value / other.value
        rel_unc = math.sqrt(
            (self.uncertainty / self.value if self.value != 0 else 0)**2 +
            (other.uncertainty / other.value if other.value != 0 else 0)**2
        )
        uncertainty = abs(value) * rel_unc
        units = self.units / other.units
        return Measurement(value, decimals=self._decimals_for(other), uncertainty=uncertainty, units=units)

    def __rtruediv__(self, other):
        return self._as_measurement(other) / self

    def __pow__(self, exponent):
        value = self.value ** exponent
        rel_unc = abs(exponent) * (self.uncertainty / self.value if self.value != 0 else 0)
        uncertainty = abs(value) * rel_unc
        return Measurement(value, decimals=self.decimals, uncertainty=uncertainty, units=self.units)

    # ---------------- Conversions ----------------
    def convert_to(self, target_unit: Unit) -> "Measurement":
        """Convert value and uncertainty using Unit class."""
        new_value = self.units.convert_value_to(self.value, target_unit)
        new_uncertainty = self.units.convert_value_to(self.uncertainty, target_unit, scale_only=True)
        return Measurement(new_value, self.decimals, new_uncertainty, target_unit)

    # ---------------- Representation ----------------
    def __str__(self):
        dec = self.decimals if self.decimals is not None else max(len(str(self.value).rsplit('.', 1)[-1]), 6)
        val_str = f"{self.value:.{dec}f}"
        unc_str = f" ± {self.uncertainty:.{dec}f}" if self.uncertainty != 0 else ""
        units = str(self.units)
        if units == "":
            return f"{val_str}{unc_str}"
        return f"{val_str}{unc_str} {units}"


# ---------------- PhysicsTools ----------------
class PhysicsTools:
    @staticmethod
    def average(measurements: list[Measurement]) -> Measurement:
        if not measurements:
            raise ValueError("No measurements provided")

        # Check if we have valid uncertainties to use for weighting
        # If all uncertainties are 0, we must use a simple arithmetic mean
        has_uncertainty = any(m.uncertainty > 0 for m in measurements)

        values = [m.value for m in measurements]

        if not has_uncertainty:
            # Scenario: Raw data points like [0.585, 0.297, ...]
            # Calculate simple mean
            mean = sum(values) / len(values)
            # For the uncertainty of the mean of raw data,
            # we usually use the Standard Error: std_dev / sqrt(n)
            if len(values) > 1:
                variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
                total_unc = math.sqrt(variance) / math.sqrt(len(values))
            else:
                total_unc = 0.0
        else:
            # Scenario: Combining previous averages like [value1, value2]
            # Calculate Weighted Mean
            weights = [1.0 / (m.uncertainty**2) if m.uncertainty > 0 else 0 for m in measurements]
            # Handle the case where some are 0 and some are not (assign high weight to 0-error)
            # For simplicity, if we have mix, you might need more complex logic.
            # But for your code:
            sum_weights = sum(weights)
            mean = sum(w * v for w, v in zip(weights, values)) / sum_weights
            total_unc = math.sqrt(1.0 / sum_weights)

        decimals = min((m.decimals for m in measurements if m.decimals is not None), default=None)
        units = measurements[0].units
        return Measurement(mean, decimals=decimals, uncertainty=total_unc, units=units)

    @staticmethod
    def average_with_std_dev(measurements: list[Measurement]) -> Measurement:
        """
        Returns a Measurement where:
        - value: The arithmetic mean of the inputs.
        - uncertainty: The sample standard deviation (spread) of the inputs.
        """
        if not measurements:
            raise ValueError("No measurements provided")
        if len(measurements) < 2:
            mean = measurements[0].value
            return Measurement(mean, decimals=measurements[0].decimals, uncertainty=0.0, units=measurements[0].units)
        values = [m.value for m in measurements]
        n = len(values)
        mean = sum(values) / n
        sum_sq_diff = sum((x - mean) ** 2 for x in values)
        std_dev = math.sqrt(sum_sq_diff / (n - 1))
        decimals = min((m.decimals for m in measurements if m.decimals is not None), default=None)
        units = measurements[0].units
        return Measurement(
            value=mean,
            decimals=decimals,
            uncertainty=std_dev,
            units=units
        )


# Example usage
measurements1 = [
    Measurement(0.585, 3, 0, Unit.gram()),
    Measurement(0.297, 3, 0, Unit.gram()),
    Measurement(0.392, 3, 0, Unit.gram()),
    Measurement(0.443, 3, 0, Unit.gram()),
    Measurement(0.564, 3, 0, Unit.gram()),
]
print(f"Measurements list 1: {[str(m) for m in measurements1]}")
average1 = PhysicsTools.average(measurements1)
print(f"average = {average1}")
standarddeviation1 = PhysicsTools.average_with_std_dev(measurements1)
print(f"standard deviation = {standarddeviation1}")
summed1 = sum(m for m in measurements1)
print("Summed values:", summed1)
print()

measurements2 = [
    Measurement(0.982, 3, 0, Unit.gram()),
    Measurement(0.873, 3, 0, Unit.gram()),
    Measurement(0.822, 3, 0, Unit.gram()),
    Measurement(0.700, 3, 0, Unit.gram()),
    Measurement(0.805, 3, 0, Unit.gram()),
]
print(f"Measurements list 2: {[str(m) for m in measurements2]}")
average2 = PhysicsTools.average(measurements2)
print(f"average = {average2}")
standarddeviation2 = PhysicsTools.average_with_std_dev(measurements2)
print(f"standard deviation = {standarddeviation2}")
summed2 = sum(m for m in measurements2)
print("Summed values:", summed2)
print()

value1 = average1
print("value1 =", value1)
value2 = average2
print("value2 =", value2)
average_of_2 = PhysicsTools.average([value1, value2])
print("average_of_2 =", average_of_2)
standard_deviation_of_2 = PhysicsTools.average_with_std_dev([value1, value2])
print("standard_deviation_of_2 =", standard_deviation_of_2)
print()

# --- Scenario: Measuring Material in Cups ---

# 1. Measure 5 empty cups (slight variations in manufacturing)
empty_cups = [
    Measurement(20.105, 3, 0.001, Unit.gram()),
    Measurement(20.102, 3, 0.001, Unit.gram()),
    Measurement(20.108, 3, 0.001, Unit.gram()),
    Measurement(20.104, 3, 0.001, Unit.gram()),
    Measurement(20.106, 3, 0.001, Unit.gram()),
]
print(f"Empty cups: {[str(m) for m in measurements1]}")

# 2. Measure 5 cups filled with material
full_cups = [
    Measurement(55.420, 3, 0.001, Unit.gram()),
    Measurement(55.395, 3, 0.001, Unit.gram()),
    Measurement(55.450, 3, 0.001, Unit.gram()),
    Measurement(55.410, 3, 0.001, Unit.gram()),
    Measurement(55.435, 3, 0.001, Unit.gram()),
]
print(f"Full cups: {[str(m) for m in measurements1]}")

# Calculate averages and their "spread" (Standard Deviation)
avg_empty = PhysicsTools.average_with_std_dev(empty_cups)
print(f"Average Empty Cup: {avg_empty}")
avg_full = PhysicsTools.average_with_std_dev(full_cups)
print(f"Average Full Cup:  {avg_full}")

# Calculate the material mass
# This uses your __sub__ method logic: sqrt(unc1^2 + unc2^2)
material_mass = avg_full - avg_empty
print(f"Material Mass: {material_mass}")
