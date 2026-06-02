import sys
import traceback
from gui.app import RobinApp
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """ROBIN Entry Point."""
    # Professional, quiet terminal header
    print("-" * 30)
    print(" ROBIN AI: System Online")
    print("-" * 30)
    
    try:
        app = RobinApp()
        app.mainloop()
    except KeyboardInterrupt:
        # Silent graceful exit
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical Startup Error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
