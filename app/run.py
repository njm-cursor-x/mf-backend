"""Process entrypoint. Read PORT in Python — never pass shell ${PORT} to uvicorn."""

import os

import uvicorn


def listen_port(raw: str | None = None) -> int:
    value = raw if raw is not None else os.environ.get("PORT", "8080")
    try:
        return int(value)
    except (TypeError, ValueError):
        return 8080


def main() -> None:
    port_i = listen_port()
    print(f"mf-backend run.py listening on 0.0.0.0:{port_i}", flush=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port_i, proxy_headers=True)


if __name__ == "__main__":
    main()
