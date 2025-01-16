# Cinema Reservation System

A simple cinema reservation system using Python, SQLAlchemy, and SQLite.
The system allows users to book seats for films and performs concurrency tests.

## Features
- Book seats for a film
- Run a concurrency test to simulate simultaneous booking attempts
- Handle errors such as overbooking gracefully

## Requirements
- Python 3.x
- SQLAlchemy
- SQLite (embedded database)

## Unit tests to cover the following cases:

Verify that a seat is booked correctly.
Verify that the same seat cannot be booked twice (overbooking management).
Verify that the concurrency system works correctly (concurrency testing).

## Installation
To install the dependencies, run:
```bash

pip install -r requirements.txt
