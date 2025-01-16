from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates
from sqlalchemy.exc import IntegrityError
from concurrent.futures import ThreadPoolExecutor

Base = declarative_base()

# Definire il modello di Film, Room e Reservation
class Film(Base):
    __tablename__ = 'films'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    showtime = Column(String, nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)

class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    total_seats = Column(Integer, nullable=False)

class Reservation(Base):
    __tablename__ = 'reservations'
    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey('films.id'), nullable=False)
    seat_number = Column(Integer, nullable=False)
    is_booked = Column(Boolean, default=False, nullable=False)

    # Validazione per evitare di prenotare lo stesso posto due volte
    @validates('is_booked')
    def validate_is_booked(self, key, value):
        if value is True:
            raise Exception(f"Seat {self.seat_number} is already booked!")
        return value

# Configurazione del database
engine = create_engine('sqlite:///cinema.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

# Funzione per prenotare un posto
def book_seat(film_id, seat_number):
    session = Session()
    try:
        # Verifica se il posto è già stato prenotato
        reservation = session.query(Reservation).filter_by(film_id=film_id, seat_number=seat_number).first()
        if reservation and reservation.is_booked:
            print(f"Error: Seat {seat_number} for film {film_id} is already booked.")
            return False
        
        # Prenotazione del posto
        new_reservation = Reservation(film_id=film_id, seat_number=seat_number, is_booked=True)
        session.add(new_reservation)
        session.commit()
        print(f"Seat {seat_number} successfully booked for film {film_id}")
        return True

    except IntegrityError:
        print(f"Error: Integrity error for seat {seat_number} on film {film_id}.")
        session.rollback()
        return False

    except Exception as e:
        print(f"Error: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

# Funzione per eseguire il test di concorrenza
def run_concurrency_test(film_id, seat_number, num_requests):
    def attempt_booking():
        result = book_seat(film_id, seat_number)
        return result

    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        results = list(executor.map(attempt_booking, range(num_requests)))

    success_count = results.count(True)
    failure_count = results.count(False)
    print(f"Results for seat {seat_number}: {success_count} booked, {failure_count} failed.")

# Funzione per inizializzare i dati di test
def setup_test_data():
    session = Session()
    session.query(Reservation).delete()
    session.query(Film).delete()
    session.query(Room).delete()
    session.commit()

    room = Room(id=1, total_seats=10)
    film1 = Film(id=1, title="Test Movie", showtime="2025-01-16 20:00", room_id=1)

    session.add(room)
    session.add(film1)
    session.commit()
    session.close()

# Funzione di interfaccia utente
def run_app():
    setup_test_data()

    while True:
        print("\nOptions:")
        print("1. Book a seat")
        print("2. Run concurrency test")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            film_id = int(input("Enter film ID (1): "))  # ID del film
            seat_number = int(input("Enter seat number (1-10): "))  # Numero del posto
            book_seat(film_id, seat_number)

        elif choice == '2':
            num_requests = int(input("Enter number of concurrent requests: "))
            seat_number = int(input("Enter seat number for concurrency test (1-10): "))
            film_id = int(input("Enter film ID (1): "))
            run_concurrency_test(film_id, seat_number, num_requests)

        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


run_app()
