from autodesk import main, read_config


def _dump_toml(cfg: dict) -> str:
    return "\n".join(
        [
            f'hardware = "{cfg["hardware"]}"',
            f"button_pin = {cfg['button_pin']}",
            f"delay = {cfg['delay']}",
            "",
            "[limits]",
            f"down = {cfg['limits']['down']}",
            f"up = {cfg['limits']['up']}",
            "",
            "[motor_pins]",
            f"down = {cfg['motor_pins']['down']}",
            f"up = {cfg['motor_pins']['up']}",
            "",
            "[light_pins]",
            f"desk = {cfg['light_pins']['desk']}",
            f"session = {cfg['light_pins']['session']}",
            "",
        ],
    )


def test_read_config(tmp_path):
    cfg = {
        "hardware": "noop",
        "button_pin": 1,
        "delay": 0.1,
        "limits": {"down": 10, "up": 30},
        "motor_pins": {"down": 2, "up": 3},
        "light_pins": {"desk": 4, "session": 5},
    }
    file = tmp_path / "config.toml"
    file.write_text(_dump_toml(cfg))

    loaded = read_config(str(file))

    assert loaded == cfg


class DummyPinFactory:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True

    def create_input(self, pin: int):
        return object()

    def create_output(self, pin: int):
        return object()


def test_main(mocker, tmp_path):
    cfg = {
        "hardware": "noop",
        "button_pin": 1,
        "delay": 0.1,
        "limits": {"down": 10, "up": 30},
        "motor_pins": {"down": 2, "up": 3},
        "light_pins": {"desk": 4, "session": 5},
    }
    file = tmp_path / "config.toml"
    file.write_text(_dump_toml(cfg))

    dummy_factory = DummyPinFactory()
    mocker.patch("autodesk.create_pin_factory", return_value=dummy_factory)

    setup_app = mocker.patch("autodesk.setup_app", return_value={"service": "stub"})
    run_app = mocker.patch("aiohttp.web.run_app")

    main(
        [
            "--config",
            str(file),
            "--database",
            ":memory:",
            "--address",
            "127.0.0.1",
            "--port",
            "7381",
        ],
    )

    setup_app.assert_called_once()
    run_app.assert_called_once()
