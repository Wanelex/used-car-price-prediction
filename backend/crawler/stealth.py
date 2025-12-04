"""
Advanced Stealth & Anti-Fingerprinting Module
Comprehensive browser fingerprint randomization and evasion techniques
"""
import random
from typing import Dict, Any, List, Optional
from loguru import logger


class StealthScripts:
    """
    Collection of JavaScript stealth scripts to evade detection
    """

    @staticmethod
    def get_canvas_fingerprint_randomizer() -> str:
        """
        Randomize canvas fingerprinting
        This prevents sites from identifying your browser by canvas rendering
        """
        noise_level = random.uniform(0.0001, 0.001)

        return f"""
        (function() {{
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

            const noise = {noise_level};

            // Add noise to canvas operations
            const addNoise = function(data) {{
                for (let i = 0; i < data.length; i += 4) {{
                    data[i] = data[i] + Math.random() * noise - noise / 2;
                    data[i + 1] = data[i + 1] + Math.random() * noise - noise / 2;
                    data[i + 2] = data[i + 2] + Math.random() * noise - noise / 2;
                }}
                return data;
            }};

            // Override toDataURL
            HTMLCanvasElement.prototype.toDataURL = function() {{
                const context = this.getContext('2d');
                if (context) {{
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    addNoise(imageData.data);
                    context.putImageData(imageData, 0, 0);
                }}
                return originalToDataURL.apply(this, arguments);
            }};

            // Override getImageData
            CanvasRenderingContext2D.prototype.getImageData = function() {{
                const imageData = originalGetImageData.apply(this, arguments);
                addNoise(imageData.data);
                return imageData;
            }};

            console.log('Canvas fingerprint randomization active');
        }})();
        """

    @staticmethod
    def get_webgl_fingerprint_randomizer() -> str:
        """
        Randomize WebGL fingerprinting
        Prevents GPU-based fingerprinting
        """
        vendor_options = [
            "Intel Inc.", "NVIDIA Corporation", "ATI Technologies Inc.",
            "AMD", "Google Inc.", "Qualcomm"
        ]
        renderer_options = [
            "Intel Iris OpenGL Engine", "ANGLE (NVIDIA GeForce GTX 1050 Ti Direct3D11)",
            "ANGLE (AMD Radeon RX 580 Direct3D11)", "Mesa DRI Intel(R) HD Graphics"
        ]

        vendor = random.choice(vendor_options)
        renderer = random.choice(renderer_options)

        return f"""
        (function() {{
            const getParameter = WebGLRenderingContext.prototype.getParameter;

            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) {{
                    return '{vendor}';
                }}
                if (parameter === 37446) {{
                    return '{renderer}';
                }}
                return getParameter.call(this, parameter);
            }};

            console.log('WebGL fingerprint randomization active');
        }})();
        """

    @staticmethod
    def get_audio_context_randomizer() -> str:
        """
        Randomize audio context fingerprinting
        """
        noise = random.uniform(0.00001, 0.0001)

        return f"""
        (function() {{
            const audioContext = window.AudioContext || window.webkitAudioContext;

            if (audioContext) {{
                const originalCreateOscillator = audioContext.prototype.createOscillator;

                audioContext.prototype.createOscillator = function() {{
                    const oscillator = originalCreateOscillator.apply(this, arguments);
                    const originalStart = oscillator.start;

                    oscillator.start = function() {{
                        oscillator.frequency.value += Math.random() * {noise} - {noise} / 2;
                        return originalStart.apply(this, arguments);
                    }};

                    return oscillator;
                }};

                console.log('Audio context fingerprint randomization active');
            }}
        }})();
        """

    @staticmethod
    def get_webdriver_evasion() -> str:
        """
        Hide webdriver property and automation indicators
        """
        return """
        (function() {
            // Delete webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        name: 'Chrome PDF Plugin',
                        filename: 'internal-pdf-viewer',
                        description: 'Portable Document Format'
                    },
                    {
                        name: 'Chrome PDF Viewer',
                        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                        description: ''
                    },
                    {
                        name: 'Native Client',
                        filename: 'internal-nacl-plugin',
                        description: ''
                    }
                ]
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // Hide Chrome automation
            window.chrome = {
                runtime: {}
            };

            console.log('WebDriver evasion active');
        })();
        """

    @staticmethod
    def get_screen_randomizer() -> str:
        """
        Randomize screen properties
        """
        widths = [1920, 1366, 1536, 1440, 1280]
        heights = [1080, 768, 864, 900, 720]

        width = random.choice(widths)
        height = random.choice(heights)
        color_depth = random.choice([24, 32])
        pixel_ratio = random.choice([1, 1.5, 2])

        return f"""
        (function() {{
            Object.defineProperty(screen, 'width', {{
                get: () => {width}
            }});

            Object.defineProperty(screen, 'height', {{
                get: () => {height}
            }});

            Object.defineProperty(screen, 'availWidth', {{
                get: () => {width}
            }});

            Object.defineProperty(screen, 'availHeight', {{
                get: () => {height - 40}
            }});

            Object.defineProperty(screen, 'colorDepth', {{
                get: () => {color_depth}
            }});

            Object.defineProperty(screen, 'pixelDepth', {{
                get: () => {color_depth}
            }});

            Object.defineProperty(window, 'devicePixelRatio', {{
                get: () => {pixel_ratio}
            }});

            console.log('Screen properties randomized');
        }})();
        """

    @staticmethod
    def get_timezone_randomizer() -> str:
        """
        Randomize timezone
        """
        timezones = [
            'America/New_York', 'America/Chicago', 'America/Los_Angeles',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Istanbul',
            'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Dubai'
        ]

        timezone = random.choice(timezones)
        offset = random.choice([-8, -7, -6, -5, -4, 0, 1, 2, 3, 8, 9])

        return f"""
        (function() {{
            const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;

            Date.prototype.getTimezoneOffset = function() {{
                return {offset * 60};
            }};

            // Override Intl.DateTimeFormat
            const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
            Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
                const options = originalResolvedOptions.call(this);
                options.timeZone = '{timezone}';
                return options;
            }};

            console.log('Timezone randomized to {timezone}');
        }})();
        """

    @staticmethod
    def get_battery_randomizer() -> str:
        """
        Randomize battery API
        """
        level = random.uniform(0.4, 0.95)
        charging = random.choice([True, False])

        return f"""
        (function() {{
            if (navigator.getBattery) {{
                const originalGetBattery = navigator.getBattery;

                navigator.getBattery = function() {{
                    return Promise.resolve({{
                        charging: {str(charging).lower()},
                        chargingTime: Infinity,
                        dischargingTime: Infinity,
                        level: {level},
                        addEventListener: function() {{}},
                        removeEventListener: function() {{}},
                        dispatchEvent: function() {{}}
                    }});
                }};

                console.log('Battery API randomized');
            }}
        }})();
        """

    @staticmethod
    def get_hardware_concurrency_randomizer() -> str:
        """
        Randomize CPU cores
        """
        cores = random.choice([2, 4, 6, 8, 12, 16])

        return f"""
        (function() {{
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {cores}
            }});

            console.log('Hardware concurrency set to {cores} cores');
        }})();
        """

    @staticmethod
    def get_font_randomizer() -> str:
        """
        Randomize font detection
        """
        return """
        (function() {
            const originalOffsetWidth = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetWidth');
            const originalOffsetHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');

            Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {
                get: function() {
                    const width = originalOffsetWidth.get.call(this);
                    return width + Math.random() * 0.01 - 0.005;
                }
            });

            Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
                get: function() {
                    const height = originalOffsetHeight.get.call(this);
                    return height + Math.random() * 0.01 - 0.005;
                }
            });

            console.log('Font fingerprinting randomized');
        })();
        """

    @staticmethod
    def get_comprehensive_stealth_script() -> str:
        """
        Get all stealth scripts combined
        """
        scripts = [
            StealthScripts.get_webdriver_evasion(),
            StealthScripts.get_canvas_fingerprint_randomizer(),
            StealthScripts.get_webgl_fingerprint_randomizer(),
            StealthScripts.get_audio_context_randomizer(),
            StealthScripts.get_screen_randomizer(),
            StealthScripts.get_timezone_randomizer(),
            StealthScripts.get_battery_randomizer(),
            StealthScripts.get_hardware_concurrency_randomizer(),
            StealthScripts.get_font_randomizer()
        ]

        return "\n\n".join(scripts)


class HumanBehavior:
    """
    Simulate realistic human behavior patterns
    """

    @staticmethod
    def generate_mouse_path(start_x: int, start_y: int, end_x: int, end_y: int, steps: int = 20) -> List[Dict[str, int]]:
        """
        Generate a realistic curved mouse movement path
        Uses Bezier curves for natural motion
        """
        import math

        # Control points for Bezier curve
        control1_x = start_x + (end_x - start_x) * random.uniform(0.2, 0.4)
        control1_y = start_y + (end_y - start_y) * random.uniform(0.2, 0.4)
        control2_x = start_x + (end_x - start_x) * random.uniform(0.6, 0.8)
        control2_y = start_y + (end_y - start_y) * random.uniform(0.6, 0.8)

        path = []
        for i in range(steps + 1):
            t = i / steps

            # Cubic Bezier curve formula
            x = (1-t)**3 * start_x + 3*(1-t)**2*t * control1_x + 3*(1-t)*t**2 * control2_x + t**3 * end_x
            y = (1-t)**3 * start_y + 3*(1-t)**2*t * control1_y + 3*(1-t)*t**2 * control2_y + t**3 * end_y

            # Add slight random jitter
            x += random.uniform(-2, 2)
            y += random.uniform(-2, 2)

            path.append({"x": int(x), "y": int(y)})

        return path

    @staticmethod
    def get_typing_delays() -> List[float]:
        """
        Generate realistic typing delays (milliseconds)
        """
        return [random.uniform(50, 200) for _ in range(10)]

    @staticmethod
    def get_scroll_pattern() -> List[Dict[str, Any]]:
        """
        Generate realistic scroll pattern
        """
        pattern = []
        current_pos = 0

        for _ in range(random.randint(3, 7)):
            # Scroll down with varying speeds
            distance = random.randint(100, 500)
            duration = random.uniform(0.3, 1.2)

            pattern.append({
                "from": current_pos,
                "to": current_pos + distance,
                "duration": duration
            })

            current_pos += distance

            # Random pause
            if random.random() > 0.5:
                pattern.append({
                    "type": "pause",
                    "duration": random.uniform(0.5, 2.0)
                })

        # Scroll back up sometimes
        if random.random() > 0.6:
            pattern.append({
                "from": current_pos,
                "to": random.randint(0, current_pos // 2),
                "duration": random.uniform(0.5, 1.5)
            })

        return pattern

    @staticmethod
    def get_random_pause() -> float:
        """
        Get a random human-like pause duration
        """
        # 70% short pause, 20% medium, 10% long
        rand = random.random()
        if rand < 0.7:
            return random.uniform(0.1, 0.5)
        elif rand < 0.9:
            return random.uniform(0.5, 2.0)
        else:
            return random.uniform(2.0, 5.0)


logger.info("Stealth module loaded with comprehensive anti-fingerprinting")
