import pytest
from sqlite3 import Connection
from .participants_repository import ParticipantsRepository

@pytest.fixture
def db_connection():
    conn = Connection(':memory:')
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE participants (
            id TEXT PRIMARY KEY,
            trip_id TEXT,
            emails_to_invite_id TEXT,
            name TEXT,
            is_confirmed INTEGER DEFAULT 0
        );
        
        CREATE TABLE emails_to_invite (
            id TEXT PRIMARY KEY,
            email TEXT
        );
    ''')
    
    return conn

@pytest.fixture
def participants_repo(db_connection):
    return ParticipantsRepository(db_connection)

def test_registry_participant(participants_repo, db_connection):
    participant_info = {
        "id": "1",
        "trip_id": "trip1",
        "emails_to_invite_id": "email1",
        "name": "André"
    }
    
    participants_repo.registry_participant(participant_info)
    
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM participants WHERE id = ?", ("1",))
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] == "1"
    assert result[1] == "trip1"
    assert result[2] == "email1"
    assert result[3] == "André"
    assert result[4] == 0 

def test_find_participants_from_trip(participants_repo, db_connection):
    cursor = db_connection.cursor()
    cursor.executescript('''
        INSERT INTO emails_to_invite (id, email) VALUES
            ('email1', 'andre@example.com'),
            ('email2', 'gabi@example.com');
        
        INSERT INTO participants (id, trip_id, emails_to_invite_id, name, is_confirmed) VALUES
            ('1', 'trip1', 'email1', 'André', 0),
            ('2', 'trip1', 'email2', 'Gabi', 1),
            ('3', 'trip2', 'email1', 'Lud', 0);
    ''')
    
    participants = participants_repo.find_participants_from_trip('trip1')
    
    assert len(participants) == 2
    assert participants[0] == ('1', 'André', 0, 'andre@example.com')
    assert participants[1] == ('2', 'Gabi', 1, 'gabi@example.com')

def test_update_participant_status(participants_repo, db_connection):
    cursor = db_connection.cursor()
    cursor.execute('''
        INSERT INTO participants (id, trip_id, emails_to_invite_id, name, is_confirmed)
        VALUES ('1', 'trip1', 'email1', 'André', 0)
    ''')
    
    participants_repo.update_participant_status('1')
    
    cursor.execute("SELECT is_confirmed FROM participants WHERE id = ?", ('1',))
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] == 1