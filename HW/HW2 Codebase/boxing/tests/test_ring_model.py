from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of PlaylistModel for each test."""
    return RingModel()

@pytest.fixture
def mock_update_fight_count(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("playlist.models.playlist_model.update_play_count")

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1, 'Boxer 1', 220, 70, 3.8, 23)

@pytest.fixture
def sample_boxer2():
    return Boxer(2, 'Boxer 2', 200, 68, 4.2, 30)

@pytest.fixture
def sample_boxer3():
    return Boxer(3, 'Boxer 3', 190, 65, 3.5, 28)

@pytest.fixture
def sample_ring(sample_boxer1, sample_boxer2):
    return [sample_boxer1,sample_boxer2]


##################################################
# Add / Remove Boxer Management Test Cases
##################################################


def test_enter_ring(ring_model, sample_boxer1):
    """Test adding a song to the playlist.

    """
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == 'Boxer 1'


def test_enter_ring_with_non_boxer(ring_model):
    """Test adding a non boxer to the ring
    
    """

    with pytest.raises(TypeError, f"Invalid type: Expected 'Boxer', got '{type(Boxer).__name__}'"):
        ring_model.enter_ring("Bobby")

def test_add_too_many_boxers_to_ring(ring_model, sample_boxer1, sample_boxer2, sample_boxer3):
    """Test error when adding a duplicate song to the playlist by ID.

    """
    ring_model.enter_ring(sample_boxer2)
    ring_model.enter_ring(sample_boxer2)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(sample_boxer3)

def test_clear_ring(ring_model, sample_boxer2):
    """Test clearing the entire playlist.

    """
    ring_model.enter_ring(sample_boxer2)

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "Ring should be empty after clearing"

##################################################
# Boxer Retrieval Test Cases
##################################################


def test_get_boxers(ring_model):
    """Test successfully retrieving all songs from the playlist.

    """
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    all_boxers = ring_model.get_boxers()
    assert len(all_boxers) == 2
    assert all_boxers[0].id == 1
    assert all_boxers[0].name == "Boxer 1"
    assert all_boxers[0].weight == 220
    assert all_boxers[0].height == 70
    assert all_boxers[0].reach == 3.8
    assert all_boxers[0].age == 23

    assert all_boxers[1].id == 2
    assert all_boxers[1].id == 1
    assert all_boxers[1].name == "Boxer 2"
    assert all_boxers[1].weight == 200
    assert all_boxers[1].height == 68
    assert all_boxers[1].reach == 4.2
    assert all_boxers[1].age == 30

def test_get_boxers_with_empty_ring(ring_model):
    """Tests error when trying to get boxers from an empty ring

    """

    ring_model.clear_ring()
    with pytest.raises(ValueError, match="Ring is empty, cannot retrieve boxers."):
        ring_model.get_boxers()

def test_get_fighting_skill(ring_model, sample_boxer1):
    """Tests successfully retrieving the fighting skill of a boxer
    
    """
    
    skill = ring_model.get_fighting_skill(sample_boxer1)
    age_modifier = -1 if Boxer.age < 25 else (-2 if Boxer.age > 35 else 0)
    assert skill == (sample_boxer1.weight * len(sample_boxer1.name))+(sample_boxer1.reach/10)+ age_modifier

##################################################
# Utility Function Test Cases
##################################################

def test_fight_with_few_boxers(ring_model, sample_boxer1):
    """Tests error when trying to fight with less than 2 boxes in the ring
    
    """

    ring_model.enter_ring(sample_boxer1)
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()
