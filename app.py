from flask import Flask, render_template, request
import psycopg2 # (or sqlite3, pymysql depending on your DB)

app = Flask(__name__)

def get_db_connection():
     #Replace with your actual database connection credentials
    conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="Adhyayan1@")
    return conn
    pass

@app.route('/')
def index():
    """Requirement A: Start page with the search form."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Requirement B: Display available flights based on form submission."""
    origin = request.form['origin']
    dest = request.form['dest']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT f.flight_number, f.departure_date, fs.origin_code, fs.dest_code, fs.departure_time
        FROM Flight f
        JOIN FlightService fs ON f.flight_number = fs.flight_number
        WHERE fs.origin_code = %s 
          AND fs.dest_code = %s 
          AND f.departure_date >= %s 
          AND f.departure_date <= %s
    """
    cur.execute(query, (origin, dest, start_date, end_date))
    flights = cur.fetchall() # Returns a list of tuples
    
    cur.close()
    conn.close()

    return render_template('results.html', flights=flights)

@app.route('/flight/<flight_number>/<departure_date>')
def flight_details(flight_number, departure_date):
    """Requirement C: Display capacity and available seats for a specific flight."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            a.capacity, 
            COUNT(b.seat_number) as booked_seats,
            (a.capacity - COUNT(b.seat_number)) as available_seats
        FROM Flight f
        JOIN Aircraft a ON f.plane_type = a.plane_type
        LEFT JOIN Booking b ON f.flight_number = b.flight_number AND f.departure_date = b.departure_date
        WHERE f.flight_number = %s AND f.departure_date = %s
        GROUP BY a.capacity
    """
    cur.execute(query, (flight_number, departure_date))
    details = cur.fetchone() 
    
    cur.close()
    conn.close()

    return render_template('details.html', 
                           flight_number=flight_number, 
                           departure_date=departure_date, 
                           details=details)

if __name__ == '__main__':
    app.run(debug=True)