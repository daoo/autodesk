import yaml

from autodesk import main, read_yaml


def test_read_yaml(tmp_path):
    cfg = {
        "hardware": "noop",
        "button_pin": 1,
        "delay": 0.1,
        "limits": {"down": 10, "up": 30},
        "motor_pins": {"down": 2, "up": 3},
        "light_pins": {"desk": 4, "session": 5},
    }
    file = tmp_path / "config.yml"
    file.write_text(yaml.dump(cfg))

    loaded = read_yaml(str(file))

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


def test_main(monkeypatch, mocker, tmp_path):
    cfg = {
        "hardware": "noop",
        "button_pin": 1,
        "delay": 0.1,
        "limits": {"down": 10, "up": 30},
        "motor_pins": {"down": 2, "up": 3},
        "light_pins": {"desk": 4, "session": 5},
    }
    file = tmp_path / "config.yml"
    file.write_text(yaml.dump(cfg))

    monkeypatch.setenv("AUTODESK_CONFIG", str(file))
    monkeypatch.setenv("AUTODESK_DATABASE", ":memory:")
    monkeypatch.setenv("AUTODESK_ADDRESS", "127.0.0.1")
    monkeypatch.setenv("AUTODESK_PORT", "7381")

    dummy_factory = DummyPinFactory()
    mocker.patch("autodesk.create_pin_factory", return_value=dummy_factory)

    setup_app = mocker.patch("autodesk.setup_app", return_value={"service": "stub"})
    run_app = mocker.patch("aiohttp.web.run_app")

    main()

    setup_app.assert_called_once()
    run_app.assert_called_once()
