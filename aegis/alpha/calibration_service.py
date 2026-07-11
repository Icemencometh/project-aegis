from __future__ import annotations


class CalibrationService:
    def calibrate(self, probability: float) -> float:
        return max(0.0, min(1.0, float(probability)))