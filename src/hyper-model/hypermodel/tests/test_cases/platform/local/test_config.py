from hypermodel.platform.local.config import LocalConfig


def test_str():
    obj=LocalConfig()
    assert str(obj) =="LocalConfig(PlatformConfig)"


