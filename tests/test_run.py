from app.run import listen_port


def test_listen_port_uses_integer() -> None:
    assert listen_port("8080") == 8080


def test_listen_port_rejects_shell_placeholder() -> None:
    assert listen_port("${PORT:-8000}") == 8080


def test_listen_port_defaults_when_empty() -> None:
    assert listen_port("") == 8080
