from __future__ import annotations

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "ior_mvp.app:app",
        host=os.getenv("IOR_HOST", "127.0.0.1"),
        port=int(os.getenv("IOR_PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
