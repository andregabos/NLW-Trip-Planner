
import pytest
import sqlite3
from .activities_repository import ActivitiesRepository

@pytest.fixture
def connection():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE activities (
            id TEXT PRIMARY KEY,
            trip_id TEXT,
            title TEXT,
            occurs_at TEXT
        )
    ''')
    conn.commit()
    yield conn
    conn.close()

@pytest.fixture
def repository(connection):
    return ActivitiesRepository(connection)

def test_registry_activity(repository, connection):
    activity_infos = {
        "id": "1",
        "trip_id": "100",
        "title": "Caminhada",
        "occurs_at": "2024-07-10T10:00:00"
    }
    repository.registry_activity(activity_infos)

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM activities WHERE id = ?', (activity_infos["id"],))
    activity = cursor.fetchone()
    assert activity == ("1", "100", "Caminhada", "2024-07-10T10:00:00")

def test_find_activities_from_trip(repository):
    activity_infos1 = {
        "id": "1",
        "trip_id": "100",
        "title": "Caminhada",
        "occurs_at": "2024-07-10T10:00:00"
    }
    activity_infos2 = {
        "id": "2",
        "trip_id": "100",
        "title": "Nadar",
        "occurs_at": "2024-07-10T14:00:00"
    }
    repository.registry_activity(activity_infos1)
    repository.registry_activity(activity_infos2)

    activities = repository.find_activities_from_trip("100")
    assert len(activities) == 2
    assert activities == [
        ("1", "100", "Caminhada", "2024-07-10T10:00:00"),
        ("2", "100", "Nadar", "2024-07-10T14:00:00")
    ]
