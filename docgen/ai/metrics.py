# docgen/ai/metrics.py

import time
from collections import defaultdict


class ProviderMetrics:
    def __init__(self):
        self.stats = defaultdict(lambda: {
            "total_calls": 0,
            "successes": 0,
            "failures": 0,
            "total_latency": 0.0,
        })

    def record_success(self, provider: str, latency: float):
        data = self.stats[provider]
        data["total_calls"] += 1
        data["successes"] += 1
        data["total_latency"] += latency

    def record_failure(self, provider: str):
        data = self.stats[provider]
        data["total_calls"] += 1
        data["failures"] += 1

    def get_stats(self):
        result = {}

        for provider, data in self.stats.items():
            total = data["total_calls"]
            success = data["successes"]
            failures = data["failures"]

            avg_latency = (
                data["total_latency"] / success
                if success > 0 else float("inf")
            )

            success_rate = success / total if total > 0 else 0

            result[provider] = {
                "success_rate": success_rate,
                "avg_latency": avg_latency,
                "failures": failures,
                "total_calls": total,
            }

        return result

    def score_provider(self, provider: str):
        """
        Higher score = better provider
        Score formula:
        success_rate * 2  - avg_latency  - (failures * 0.5)
        """

        stats = self.get_stats().get(provider)

        if not stats:
            return 0

        return (
            stats["success_rate"] * 2
            - stats["avg_latency"]
            - (stats["failures"] * 0.5)
        )


# Global metrics instance
metrics = ProviderMetrics()