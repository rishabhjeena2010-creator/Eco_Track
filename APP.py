
from flask import Flask, render_template, request, redirect
from database import get_connection
from analysis import analyze_waste

app = Flask(__name__)


@app.route('/')
def home():

    # Get filter values from the website
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    waste_type = request.args.get('waste_type', '')
    period = request.args.get('period', '')

    connection = get_connection()
    cursor = connection.cursor()

    # Build the record filter query
    query = "SELECT * FROM waste_records WHERE 1=1"
    values = []

    # Filter by waste category
    if category != '':
        query += " AND waste_category = %s"
        values.append(category)

    # Filter by location
    if location != '':
        query += " AND location LIKE %s"
        values.append('%' + location + '%')

    # Filter by waste type
    if waste_type != '':
        query += " AND waste_type LIKE %s"
        values.append('%' + waste_type + '%')

    # Filter by time period
    if period == '10days':
        query += " AND record_date >= DATE_SUB(CURDATE(), INTERVAL 10 DAY)"
    elif period == '1month':
        query += " AND record_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
    elif period == '6months':
        query += " AND record_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)"
    elif period == '1year':
        query += " AND record_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"

    # Sort records by newest date first
    query += " ORDER BY record_date DESC, record_id DESC"

    # Show only 5 records when no filters are selected
    if category == '' and location == '' and waste_type == '' and period == '':
        query += " LIMIT 5"

    # Execute the record query
    cursor.execute(query, values)
    records = cursor.fetchall()

    # Calculate total waste recorded
    cursor.execute("SELECT SUM(quantity_kg) FROM waste_records")
    total_waste = cursor.fetchone()[0]

    if total_waste is None:
        total_waste = 0

    # Count all records
    cursor.execute("SELECT COUNT(*) FROM waste_records")
    total_records = cursor.fetchone()[0]

    # Count distinct collection locations
    cursor.execute(
        "SELECT COUNT(DISTINCT location) FROM waste_records"
    )
    total_locations = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    # Generate analysis and charts using Pandas, NumPy and Matplotlib
    analysis = analyze_waste()

    return render_template(
        'index.html',
        records=records,
        total_waste=total_waste,
        total_records=total_records,
        total_locations=total_locations,
        category=category,
        location=location,
        waste_type=waste_type,
        period=period,
        analysis=analysis
    )


@app.route('/add', methods=['POST'])
def add_record():

    # Get the new record details from the form
    record_date = request.form['record_date']
    location = request.form['location']
    category = request.form['category']
    waste_type = request.form['waste_type']
    quantity = request.form['quantity']
    notes = request.form.get('notes', '')

    connection = get_connection()
    cursor = connection.cursor()

    # Insert the new waste record into MySQL
    query = """
    INSERT INTO waste_records
    (record_date, location, waste_category, waste_type,
     quantity_kg, notes)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        record_date,
        location,
        category,
        waste_type,
        quantity,
        notes
    )

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
