# Zero-Emission Bus Tracker

This project was created to track Winnipeg's ZEB rollout, which I have been
closely following since the fall of 2025. At first, I was recording each ZEB run 
in a spreadsheet which automatically aggregated the data by bus and generated
cool statistics and graphs. However, as the rollout gained traction in the spring
of 2026, manually entering each run in a spreadsheet became very time-consuming.

I started building this Python program in order to automate
my bus-tracking habit. It includes a live traker that uses the Winnipeg
Transit API and GTFS archive to find all active ZEB runs, after which they can
all be added to the database in a few clicks. From there, you can view and 
search/filter all runs and buses in the system, and export the run data to
a CSV file.

As for the technical side, the app uses an MCV architecture with listeners in
the domain model, SQLite persistence, and a Custom Tkinter GUI. It also makes
use of concurrency for the location scan (via Python's threading module).

I've always been fascinated by Python's elegance and wanted to get more comfortable
with the language as I rarely encountered it in my coursework. This was the perfect
opportunity to do so, all while building something meaningful and useful for
myself.

---

## Running

With Python installed (version 3.13 or later), navigate to the root directory
(src) from the command line and type the following:

```bash
python Main.py
```

---

## Technologies

- App built with Python 3.13.3 in IntelliJ IDEA
- GUI built with Custom Tkinter library
- SQLite3 2.6.0 database

---

## License

All code is licensed under the MIT license.

---

## Author

Michel Préjet

Computer Science Student, University of Manitoba

*Last updated: June 20, 2026*