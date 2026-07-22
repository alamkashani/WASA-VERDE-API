"""
===============================================================================

WASA VERDE Simulation Engine

validator.py

Validation utilities for comparing the Python implementation against
the original MATLAB implementation.

Author:
    Elham Kashani
Company:
    Aqua Solar Aria B.V.

===============================================================================
"""



from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


# =============================================================================
# Validation Result
# =============================================================================

@dataclass(slots=True)
class ValidationResult:

    name: str

    matlab: float

    python: float

    absolute_error: float

    relative_error: float

    tolerance: float

    passed: bool


# =============================================================================
# Validator
# =============================================================================

class SimulationValidator:

    def __init__(

        self,

        tolerance: float = 1e-3

    ):

        self.tolerance = tolerance

        self.results: list[ValidationResult] = []

    # -------------------------------------------------------------------------

    def compare_scalar(

        self,

        name: str,

        matlab: float,

        python: float,

    ) -> ValidationResult:

        error = abs(matlab - python)

        if abs(matlab) < 1e-12:

            relative = 0.0

        else:

            relative = error / abs(matlab)

        passed = error <= self.tolerance

        result = ValidationResult(

            name=name,

            matlab=matlab,

            python=python,

            absolute_error=error,

            relative_error=relative,

            tolerance=self.tolerance,

            passed=passed,

        )

        self.results.append(result)

        return result

    # -------------------------------------------------------------------------

    def compare_vector(

        self,

        name: str,

        matlab: Iterable[float],

        python: Iterable[float],

    ) -> ValidationResult:

        matlab = np.asarray(matlab)

        python = np.asarray(python)

        rmse = np.sqrt(

            np.mean(

                (matlab - python) ** 2

            )

        )

        relative = rmse / np.mean(np.abs(matlab))

        passed = rmse <= self.tolerance

        result = ValidationResult(

            name=name,

            matlab=float(np.mean(matlab)),

            python=float(np.mean(python)),

            absolute_error=float(rmse),

            relative_error=float(relative),

            tolerance=self.tolerance,

            passed=passed,

        )

        self.results.append(result)

        return result

    # -------------------------------------------------------------------------

    @property
    def passed(self) -> bool:

        return all(r.passed for r in self.results)

    # -------------------------------------------------------------------------

    @property
    def failed(self) -> int:

        return sum(

            not r.passed

            for r in self.results

        )

    # -------------------------------------------------------------------------

    def print_report(self) -> None:

        print()

        print("=" * 70)

        print("WASA VERDE VALIDATION REPORT")

        print("=" * 70)

        print()

        for r in self.results:

            status = "PASS" if r.passed else "FAIL"

            print(

                f"{status:5}"

                f" {r.name:30}"

                f" Error={r.absolute_error:.6f}"

            )

        print()

        print(f"Tests : {len(self.results)}")

        print(f"Failed: {self.failed}")

        print(f"Passed: {self.passed}")

        print()

    # -------------------------------------------------------------------------

    def save_report(

        self,

        filename: str = "validation_report.txt",

    ) -> None:

        path = Path(filename)

        with path.open("w") as f:

            f.write("WASA VERDE Validation Report\n")

            f.write("=" * 60)

            f.write("\n\n")

            for r in self.results:

                status = "PASS" if r.passed else "FAIL"

                f.write(

                    f"{status:5} "

                    f"{r.name:30}"

                    f"{r.absolute_error:.8f}\n"

                )

            f.write("\n")

            f.write(

                f"Tests : {len(self.results)}\n"

            )

            f.write(

                f"Failed: {self.failed}\n"

            )

            f.write(

                f"Passed: {self.passed}\n"

            )


# =============================================================================
# End of File
# =============================================================================
