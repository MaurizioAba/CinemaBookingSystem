import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import Film, Room, Reservation, Base, book_seat

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

def test_overbooking(setup_database):
    session, film_id = setup_database

    # Prenotazione di un posto
    book_seat(film_id, 5)

    # Tentativo di prenotazione dello stesso posto
    result = book_seat(film_id, 5)
    assert result == False  # La prenotazione dovrebbe fallire, perché il posto è già prenotato

    # Verifica che il posto non sia stato prenotato di nuovo
    reservation = session.query(Reservation).filter_by(film_id=film_id, seat_number=5).first()
    assert reservation is not None
    assert reservation.is_booked == True

from concurrent.futures import ThreadPoolExecutor

def test_concurrency(setup_database):
    session, film_id = setup_database

    # Funzione di prova per prenotare il posto
    def attempt_booking():
        return book_seat(film_id, 5)

    # Esegui 10 richieste concorrenti per prenotare lo stesso posto
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(attempt_booking, range(10)))

    # Verifica che solo una prenotazione sia riuscita
    success_count = results.count(True)
    failure_count = results.count(False)

    assert success_count == 1  # Solo 1 prenotazione dovrebbe essere riuscita
    assert failure_count == 9  # Le altre dovrebbero fallire

    # Verifica che il posto 5 sia effettivamente prenotato
    reservation = session.query(Reservation).filter_by(film_id=film_id, seat_number=5).first()
    assert reservation is not None
    assert reservation.is_booked == True
