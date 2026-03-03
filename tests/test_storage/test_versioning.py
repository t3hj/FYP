import pytest
from src.storage.versioning import Versioning

@pytest.fixture
def versioning():
    return Versioning()

def test_initial_version(versioning):
    assert versioning.get_current_version() == 1

def test_increment_version(versioning):
    versioning.increment_version()
    assert versioning.get_current_version() == 2

def test_version_history(versioning):
    versioning.increment_version()
    versioning.increment_version()
    history = versioning.get_version_history()
    assert len(history) == 3  # Initial version + 2 increments
    assert history == [1, 2, 3]

def test_reset_version(versioning):
    versioning.increment_version()
    versioning.reset_version()
    assert versioning.get_current_version() == 1

def test_versioning_with_invalid_data(versioning):
    with pytest.raises(ValueError):
        versioning.set_version(-1)  # Invalid version should raise an error

def test_versioning_persistence(versioning):
    versioning.increment_version()
    versioning.save_version()
    new_versioning = Versioning()
    new_versioning.load_version()
    assert new_versioning.get_current_version() == versioning.get_current_version()