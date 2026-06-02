import psutil
from utils.logger import get_logger

logger = get_logger(__name__)

class SystemMonitor:

    @staticmethod
    def get_system_status() -> str:
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent

            return (
                f"CPU is at {cpu:.0f} percent. "
                f"Memory is at {mem:.0f} percent."
            )

        except Exception as e:
            logger.error(f"System status error: {e}")
            return "Could not retrieve system status."

    @staticmethod
    def get_battery() -> str:
        try:
            battery = psutil.sensors_battery()

            if battery is None:
                return "No battery detected."

            pct = battery.percent
            charging = (
                "charging"
                if battery.power_plugged
                else "on battery"
            )

            return (
                f"Battery is at {pct:.0f} percent "
                f"and {charging}."
            )

        except Exception as e:
            logger.error(f"Battery error: {e}")
            return "Could not read battery status."

    @staticmethod
    def get_memory_usage() -> str:
        try:
            mem = psutil.virtual_memory()

            return (
                f"Memory is at {mem.percent:.0f} percent. "
                f"{mem.available // (1024**2)} MB available."
            )

        except Exception as e:
            logger.error(f"Memory error: {e}")
            return "Could not read memory usage."

    @staticmethod
    def get_cpu_usage() -> str:
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            return f"CPU is at {cpu:.0f} percent."

        except Exception as e:
            logger.error(f"CPU error: {e}")
            return "Could not read CPU usage."
