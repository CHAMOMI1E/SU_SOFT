from soft.soft import main
import asyncio
import os

if __name__ == '__main__':
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(current_script_path)
    session_path = os.path.join(project_root, "soft", "session")
    asyncio.run(main(session_path, '@fdsgfysdu'))