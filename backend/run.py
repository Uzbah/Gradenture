"""Development entry point.

Run from the repository root, because `backend` is the importable package:

    python -m backend.run

In production, point a process manager at `backend.main:app` instead.
"""

import uvicorn

from backend.core.conf import settings


def main() -> None:
    uvicorn.run(
        'backend.main:app',
        host='0.0.0.0',
        port=settings.PORT,
        reload=settings.ENVIRONMENT == 'dev',
    )


if __name__ == '__main__':
    main()
