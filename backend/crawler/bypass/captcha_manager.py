"""
Advanced CAPTCHA Manager with Multi-Provider Fallback
Manages multiple CAPTCHA solving services with intelligent fallback
"""
from typing import Optional, Dict, Any, List
from loguru import logger
import time
from enum import Enum


class CaptchaProvider(Enum):
    """Available CAPTCHA solving providers"""
    TWOCAPTCHA = "2captcha"
    ANTICAPTCHA = "anticaptcha"
    CAPSOLVER = "capsolver"
    DEATHBYCAPTCHA = "deathbycaptcha"


class CaptchaType(Enum):
    """Types of CAPTCHAs"""
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    CLOUDFLARE_TURNSTILE = "cloudflare_turnstile"
    IMAGE = "image"


class ProviderConfig:
    """Configuration for a CAPTCHA provider"""

    def __init__(
        self,
        provider: CaptchaProvider,
        api_key: str,
        enabled: bool = True,
        priority: int = 1,
        max_solve_time: int = 120,
        cost_per_solve: float = 0.0
    ):
        self.provider = provider
        self.api_key = api_key
        self.enabled = enabled
        self.priority = priority
        self.max_solve_time = max_solve_time
        self.cost_per_solve = cost_per_solve

        # Statistics
        self.total_attempts = 0
        self.successful_solves = 0
        self.failed_solves = 0
        self.total_solve_time = 0.0
        self.last_balance_check = None
        self.current_balance = None


class AdvancedCaptchaManager:
    """
    Advanced CAPTCHA manager with intelligent provider selection and fallback
    """

    def __init__(self):
        self.providers: List[ProviderConfig] = []
        self.solver = None

    def add_provider(self, config: ProviderConfig):
        """Add a CAPTCHA provider"""
        self.providers.append(config)
        self.providers.sort(key=lambda p: p.priority)
        logger.info(f"Added CAPTCHA provider: {config.provider.value} (priority: {config.priority})")

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers"""
        stats = {}

        for provider in self.providers:
            success_rate = 0
            if provider.total_attempts > 0:
                success_rate = (provider.successful_solves / provider.total_attempts) * 100

            avg_solve_time = 0
            if provider.successful_solves > 0:
                avg_solve_time = provider.total_solve_time / provider.successful_solves

            stats[provider.provider.value] = {
                "enabled": provider.enabled,
                "priority": provider.priority,
                "total_attempts": provider.total_attempts,
                "successful_solves": provider.successful_solves,
                "failed_solves": provider.failed_solves,
                "success_rate": round(success_rate, 2),
                "avg_solve_time": round(avg_solve_time, 2),
                "total_cost": round(provider.successful_solves * provider.cost_per_solve, 4),
                "balance": provider.current_balance
            }

        return stats

    def _get_available_providers(self) -> List[ProviderConfig]:
        """Get list of enabled providers sorted by priority"""
        return [p for p in self.providers if p.enabled]

    def solve_captcha(
        self,
        captcha_type: CaptchaType,
        solver,
        **kwargs
    ) -> Optional[str]:
        """
        Solve a CAPTCHA with automatic fallback to other providers

        Args:
            captcha_type: Type of CAPTCHA
            solver: CaptchaSolver instance
            **kwargs: CAPTCHA-specific parameters

        Returns:
            Solution token or None
        """
        available_providers = self._get_available_providers()

        if not available_providers:
            logger.error("No CAPTCHA providers available!")
            return None

        last_error = None

        # Try each provider in order of priority
        for provider_config in available_providers:
            provider = provider_config.provider
            provider_config.total_attempts += 1

            logger.info(f"Attempting to solve {captcha_type.value} with {provider.value}...")

            start_time = time.time()

            try:
                solution = None

                # Route to appropriate solver method
                if captcha_type == CaptchaType.RECAPTCHA_V2:
                    if provider == CaptchaProvider.TWOCAPTCHA:
                        solution = solver.solve_recaptcha_v2(
                            sitekey=kwargs.get('sitekey'),
                            url=kwargs.get('url'),
                            invisible=kwargs.get('invisible', False)
                        )

                elif captcha_type == CaptchaType.RECAPTCHA_V3:
                    if provider == CaptchaProvider.TWOCAPTCHA:
                        solution = solver.solve_recaptcha_v3(
                            sitekey=kwargs.get('sitekey'),
                            url=kwargs.get('url'),
                            action=kwargs.get('action', 'verify'),
                            min_score=kwargs.get('min_score', 0.3)
                        )

                elif captcha_type == CaptchaType.HCAPTCHA:
                    if provider == CaptchaProvider.TWOCAPTCHA:
                        solution = solver.solve_hcaptcha(
                            sitekey=kwargs.get('sitekey'),
                            url=kwargs.get('url')
                        )

                elif captcha_type == CaptchaType.CLOUDFLARE_TURNSTILE:
                    if provider == CaptchaProvider.TWOCAPTCHA:
                        solution = solver.solve_cloudflare_turnstile(
                            sitekey=kwargs.get('sitekey'),
                            url=kwargs.get('url'),
                            action=kwargs.get('action'),
                            data=kwargs.get('data')
                        )

                elif captcha_type == CaptchaType.IMAGE:
                    if provider == CaptchaProvider.TWOCAPTCHA:
                        solution = solver.solve_image_captcha(
                            image_path=kwargs.get('image_path')
                        )

                solve_time = time.time() - start_time

                if solution:
                    # Success!
                    provider_config.successful_solves += 1
                    provider_config.total_solve_time += solve_time

                    logger.success(
                        f"{provider.value} solved {captcha_type.value} in {solve_time:.2f}s"
                    )

                    return solution
                else:
                    # Solver returned None (failed)
                    provider_config.failed_solves += 1
                    last_error = f"{provider.value} returned no solution"
                    logger.warning(last_error)

            except Exception as e:
                # Exception during solving
                provider_config.failed_solves += 1
                last_error = f"{provider.value} error: {str(e)}"
                logger.error(last_error)

            # If we get here, this provider failed - try next one
            logger.warning(f"{provider.value} failed, trying next provider...")

        # All providers failed
        logger.error(f"All CAPTCHA providers failed for {captcha_type.value}")
        logger.error(f"Last error: {last_error}")

        return None

    async def check_balances(self, solver):
        """
        Check account balances for all providers

        Args:
            solver: CaptchaSolver instance
        """
        logger.info("Checking CAPTCHA provider balances...")

        for provider_config in self.providers:
            try:
                balance = solver.get_balance(provider_config.provider.value)

                if balance is not None:
                    provider_config.current_balance = balance
                    provider_config.last_balance_check = time.time()

                    if balance < 1.0:
                        logger.warning(
                            f"{provider_config.provider.value} balance is low: ${balance:.2f}"
                        )
                    else:
                        logger.info(
                            f"{provider_config.provider.value} balance: ${balance:.2f}"
                        )

            except Exception as e:
                logger.error(
                    f"Failed to check balance for {provider_config.provider.value}: {str(e)}"
                )

    def disable_provider(self, provider: CaptchaProvider):
        """Temporarily disable a provider"""
        for p in self.providers:
            if p.provider == provider:
                p.enabled = False
                logger.warning(f"Disabled provider: {provider.value}")
                break

    def enable_provider(self, provider: CaptchaProvider):
        """Re-enable a provider"""
        for p in self.providers:
            if p.provider == provider:
                p.enabled = True
                logger.info(f"Enabled provider: {provider.value}")
                break

    def get_best_provider(self) -> Optional[ProviderConfig]:
        """
        Get the best performing provider based on success rate

        Returns:
            ProviderConfig or None
        """
        available = self._get_available_providers()

        if not available:
            return None

        # Filter providers with at least some attempts
        providers_with_history = [p for p in available if p.total_attempts > 0]

        if not providers_with_history:
            # No history, return highest priority
            return available[0]

        # Sort by success rate
        sorted_providers = sorted(
            providers_with_history,
            key=lambda p: p.successful_solves / max(p.total_attempts, 1),
            reverse=True
        )

        return sorted_providers[0]

    def reset_stats(self):
        """Reset all provider statistics"""
        for provider in self.providers:
            provider.total_attempts = 0
            provider.successful_solves = 0
            provider.failed_solves = 0
            provider.total_solve_time = 0.0

        logger.info("Reset all provider statistics")


logger.info("Advanced CAPTCHA manager module loaded")
