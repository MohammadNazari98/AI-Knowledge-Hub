import pytest




@pytest.fixture(autouse=True)
def use_test_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"