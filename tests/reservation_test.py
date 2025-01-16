import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Film, Room, Reservation, Base, book_seat

@pytest.fixture
def setup_database():
    # Impostazione del database in memoria per i test
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Creazione di un film e una sala
    room = Room(id=1, total_seats=10)
    film = Film(id=1, title="Test Movie", showtime="2025-01-16 20:00", room_id=1)

    session.add(room)
    session.add(film)
    session.commit()
    return session, film.id

def test_book_seat(setup_database):
    session, film_id = setup_database

    # Prenotazione di un posto
    result = book_seat(film_id, 5)
    assert result == True  # Il posto dovrebbe essere prenotato con successo

    # Verifica che il posto sia stato prenotato
    reservation = session.query(Reservation).filter_by(film_id=film_id, seat_number=5).first()
    assert reservation is not None
    assert reservation.is_booked == True

