"""
Comprehensive Health Monitoring and Alerting System
Monitors crawler performance, success rates, and system health
"""
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
from loguru import logger
import json
from pathlib import Path


class MetricsCollector:
    """
    Collects and aggregates crawler metrics
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize metrics collector

        Args:
            window_size: Number of recent requests to track
        """
        self.window_size = window_size

        # Request tracking
        self.requests = deque(maxlen=window_size)
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

        # Timing metrics
        self.total_duration = 0.0
        self.min_duration = float('inf')
        self.max_duration = 0.0

        # CAPTCHA metrics
        self.captchas_detected = 0
        self.captchas_solved = 0
        self.captchas_failed = 0
        self.captcha_types_seen = {}

        # Proxy metrics
        self.proxy_switches = 0
        self.proxy_failures = 0

        # Error tracking
        self.errors_by_type = {}
        self.errors_by_url = {}

        # Start time
        self.start_time = time.time()

    def record_request(
        self,
        url: str,
        success: bool,
        duration: float,
        status_code: Optional[int] = None,
        captcha_detected: bool = False,
        captcha_solved: bool = False,
        captcha_type: Optional[str] = None,
        error: Optional[str] = None,
        proxy_used: Optional[str] = None
    ):
        """
        Record a request and its metrics

        Args:
            url: The requested URL
            success: Whether request was successful
            duration: Request duration in seconds
            status_code: HTTP status code
            captcha_detected: Whether CAPTCHA was detected
            captcha_solved: Whether CAPTCHA was solved
            captcha_type: Type of CAPTCHA
            error: Error message if failed
            proxy_used: Proxy that was used
        """
        request_data = {
            "url": url,
            "success": success,
            "duration": duration,
            "status_code": status_code,
            "captcha_detected": captcha_detected,
            "captcha_solved": captcha_solved,
            "captcha_type": captcha_type,
            "error": error,
            "proxy_used": proxy_used,
            "timestamp": time.time()
        }

        self.requests.append(request_data)
        self.total_requests += 1

        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

            # Track error types
            if error:
                self.errors_by_type[error] = self.errors_by_type.get(error, 0) + 1
                if url not in self.errors_by_url:
                    self.errors_by_url[url] = []
                self.errors_by_url[url].append(error)

        # Duration stats
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)

        # CAPTCHA stats
        if captcha_detected:
            self.captchas_detected += 1

            if captcha_type:
                self.captcha_types_seen[captcha_type] = \
                    self.captcha_types_seen.get(captcha_type, 0) + 1

            if captcha_solved:
                self.captchas_solved += 1
            else:
                self.captchas_failed += 1

    def get_success_rate(self, window: Optional[int] = None) -> float:
        """
        Get success rate

        Args:
            window: Number of recent requests to consider (None = all)

        Returns:
            Success rate as percentage
        """
        if window:
            recent_requests = list(self.requests)[-window:]
            if not recent_requests:
                return 0.0
            successes = sum(1 for r in recent_requests if r["success"])
            return (successes / len(recent_requests)) * 100
        else:
            if self.total_requests == 0:
                return 0.0
            return (self.successful_requests / self.total_requests) * 100

    def get_avg_duration(self, window: Optional[int] = None) -> float:
        """
        Get average request duration

        Args:
            window: Number of recent requests to consider

        Returns:
            Average duration in seconds
        """
        if window:
            recent_requests = list(self.requests)[-window:]
            if not recent_requests:
                return 0.0
            return sum(r["duration"] for r in recent_requests) / len(recent_requests)
        else:
            if self.total_requests == 0:
                return 0.0
            return self.total_duration / self.total_requests

    def get_captcha_solve_rate(self) -> float:
        """Get CAPTCHA solve rate as percentage"""
        if self.captchas_detected == 0:
            return 0.0
        return (self.captchas_solved / self.captchas_detected) * 100

    def get_requests_per_minute(self) -> float:
        """Get current requests per minute rate"""
        uptime = time.time() - self.start_time
        if uptime == 0:
            return 0.0
        return (self.total_requests / uptime) * 60

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        uptime = time.time() - self.start_time

        return {
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(self.get_success_rate(), 2),
            "recent_success_rate": round(self.get_success_rate(window=20), 2),
            "avg_duration": round(self.get_avg_duration(), 2),
            "recent_avg_duration": round(self.get_avg_duration(window=20), 2),
            "min_duration": round(self.min_duration, 2) if self.min_duration != float('inf') else 0,
            "max_duration": round(self.max_duration, 2),
            "requests_per_minute": round(self.get_requests_per_minute(), 2),
            "captchas_detected": self.captchas_detected,
            "captchas_solved": self.captchas_solved,
            "captchas_failed": self.captchas_failed,
            "captcha_solve_rate": round(self.get_captcha_solve_rate(), 2),
            "captcha_types": self.captcha_types_seen,
            "top_errors": dict(sorted(
                self.errors_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "proxy_switches": self.proxy_switches,
            "proxy_failures": self.proxy_failures
        }


class HealthMonitor:
    """
    System health monitoring with alerting
    """

    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics
        self.alerts: List[Dict[str, Any]] = []
        self.alert_history: List[Dict[str, Any]] = []

        # Thresholds
        self.min_success_rate = 50.0  # %
        self.max_avg_duration = 60.0  # seconds
        self.max_captcha_rate = 80.0  # %
        self.min_captcha_solve_rate = 70.0  # %

    def check_health(self) -> Dict[str, Any]:
        """
        Check system health and generate alerts

        Returns:
            Health status dict
        """
        self.alerts = []
        issues = []

        summary = self.metrics.get_summary()

        # Check success rate
        if summary["success_rate"] < self.min_success_rate:
            alert = {
                "severity": "critical" if summary["success_rate"] < 30 else "warning",
                "type": "low_success_rate",
                "message": f"Success rate is {summary['success_rate']}% (threshold: {self.min_success_rate}%)",
                "value": summary["success_rate"],
                "threshold": self.min_success_rate,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.alerts.append(alert)
            issues.append("Low success rate")

        # Check average duration
        if summary["avg_duration"] > self.max_avg_duration:
            alert = {
                "severity": "warning",
                "type": "high_duration",
                "message": f"Average duration is {summary['avg_duration']}s (threshold: {self.max_avg_duration}s)",
                "value": summary["avg_duration"],
                "threshold": self.max_avg_duration,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.alerts.append(alert)
            issues.append("High response time")

        # Check CAPTCHA solve rate
        if summary["captchas_detected"] > 0:
            if summary["captcha_solve_rate"] < self.min_captcha_solve_rate:
                alert = {
                    "severity": "warning",
                    "type": "low_captcha_solve_rate",
                    "message": f"CAPTCHA solve rate is {summary['captcha_solve_rate']}% (threshold: {self.min_captcha_solve_rate}%)",
                    "value": summary["captcha_solve_rate"],
                    "threshold": self.min_captcha_solve_rate,
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.alerts.append(alert)
                issues.append("Low CAPTCHA solve rate")

        # Check if too many CAPTCHAs
        if summary["total_requests"] > 0:
            captcha_rate = (summary["captchas_detected"] / summary["total_requests"]) * 100
            if captcha_rate > self.max_captcha_rate:
                alert = {
                    "severity": "warning",
                    "type": "high_captcha_rate",
                    "message": f"CAPTCHA rate is {captcha_rate:.1f}% (threshold: {self.max_captcha_rate}%)",
                    "value": captcha_rate,
                    "threshold": self.max_captcha_rate,
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.alerts.append(alert)
                issues.append("High CAPTCHA encounter rate")

        # Determine overall health status
        if any(a["severity"] == "critical" for a in self.alerts):
            health_status = "critical"
        elif any(a["severity"] == "warning" for a in self.alerts):
            health_status = "degraded"
        else:
            health_status = "healthy"

        # Add to history
        for alert in self.alerts:
            self.alert_history.append(alert)

        # Keep only recent alerts (last 100)
        self.alert_history = self.alert_history[-100:]

        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": self.alerts,
            "issues": issues,
            "metrics": summary
        }

    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return self.alert_history[-limit:]


class StatusReporter:
    """
    Generate status reports and save to files
    """

    def __init__(self, metrics: MetricsCollector, health: HealthMonitor, output_dir: str = "reports"):
        self.metrics = metrics
        self.health = health
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_report(self, include_history: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive status report

        Args:
            include_history: Whether to include request history

        Returns:
            Report dict
        """
        health_status = self.health.check_health()

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "health": health_status,
            "metrics": self.metrics.get_summary()
        }

        if include_history:
            report["recent_requests"] = list(self.metrics.requests)[-20:]
            report["alert_history"] = self.health.get_alert_history(20)

        return report

    def save_report(self, report: Optional[Dict[str, Any]] = None) -> str:
        """
        Save report to file

        Args:
            report: Report dict (generates new one if None)

        Returns:
            Path to saved report
        """
        if report is None:
            report = self.generate_report()

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"crawler_report_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved to: {filename}")
        return str(filename)

    def print_status(self):
        """Print current status to console"""
        health_status = self.health.check_health()
        metrics = health_status["metrics"]

        print("\n" + "=" * 80)
        print("CRAWLER STATUS REPORT")
        print("=" * 80)

        # Health status
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️",
            "critical": "❌"
        }

        print(f"\nHealth: {status_emoji.get(health_status['status'], '❓')} {health_status['status'].upper()}")

        # Metrics
        print(f"\n📊 Metrics:")
        print(f"  Uptime: {metrics['uptime_formatted']}")
        print(f"  Total Requests: {metrics['total_requests']}")
        print(f"  Success Rate: {metrics['success_rate']}%")
        print(f"  Recent Success Rate: {metrics['recent_success_rate']}%")
        print(f"  Avg Duration: {metrics['avg_duration']}s")
        print(f"  Requests/Min: {metrics['requests_per_minute']}")

        # CAPTCHA stats
        if metrics['captchas_detected'] > 0:
            print(f"\n🔒 CAPTCHA Stats:")
            print(f"  Detected: {metrics['captchas_detected']}")
            print(f"  Solved: {metrics['captchas_solved']}")
            print(f"  Failed: {metrics['captchas_failed']}")
            print(f"  Solve Rate: {metrics['captcha_solve_rate']}%")

        # Alerts
        if health_status['alerts']:
            print(f"\n⚠️  Active Alerts ({len(health_status['alerts'])}):")
            for alert in health_status['alerts']:
                severity_emoji = "🔴" if alert['severity'] == "critical" else "🟡"
                print(f"  {severity_emoji} {alert['message']}")

        # Top errors
        if metrics['top_errors']:
            print(f"\n❌ Top Errors:")
            for error, count in list(metrics['top_errors'].items())[:3]:
                print(f"  • {error}: {count} occurrences")

        print("\n" + "=" * 80)


# Global instances
metrics_collector = MetricsCollector()
health_monitor = HealthMonitor(metrics_collector)
status_reporter = StatusReporter(metrics_collector, health_monitor)

logger.info("Monitoring system initialized")
