from flask import Flask, render_template, request, url_for, redirect, flash,session
import mysql.connector
from datetime import datetime
import calendar
import decimal

app = Flask(__name__)
app.secret_key = 'your_secret_key'  
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dairybill"
    )

@app.route('/')

@app.route('/home')  # This is the new route you asked for
def sample():
	return render_template('sample.html')

@app.route('/about')  # This is the new route you asked for
def about():
	return render_template('aboutus.html')

@app.route('/contact')  # This is the new route you asked for
def contact():
	return render_template('contact.html')
	



@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()  # Clear any previous session data
    if request.method == 'POST':
        custno = request.form['custno']
        mobileno = request.form['mobileno']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Admin check
        cursor.execute("SELECT * FROM admin WHERE custno = %s AND mobileno = %s", (custno, mobileno))
        admin = cursor.fetchone()
        if admin:
            session['user_type'] = 'admin'
            session['custno'] = custno
            session['login']=True
            session['ip'] = request.remote_addr  # Store IP to identify the session
            session.permanent = True  # Make session permanent (stay across browser restarts)
            return redirect(url_for('select_fats'))

        # Customer check
        cursor.execute("SELECT * FROM customer WHERE custno = %s AND mobileno = %s", (custno, mobileno))
        customer = cursor.fetchone()
        if customer:
            session['user_type'] = 'customer'
            session['custno'] = custno
            session['login']=True
            session['ip'] = request.remote_addr  # Store IP to identify the session
            session.permanent = True  # Make session permanent (stay across browser restarts)
            return redirect(url_for('select_fats'))

        flash("Invalid Customer No or Mobile Number", 'danger')
        return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

#fat table

@app.route('/fselect')  # This is the new route you asked for
def select_fats():
    if session.get('user_type') not in ('admin','customer'):
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fat")
    data = cursor.fetchall()
    conn.close()
    return render_template('fselect1.html', data=data)

@app.route('/finsert', methods=['GET', 'POST'])
def insert_fats():
    if session.get('user_type') != 'admin':
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    if request.method == 'POST':
        fat =float(request.form['fat'])
        price = float(request.form['price'])
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO fat (fat, price) VALUES (%s, %s)", (fat, price))
            conn.commit()
            conn.close()
            flash('Data inserted successfully!', 'success')
        except Exception:
            # Sirf simple error message
            flash('Something went wrong ,fat already exist', 'danger')
        return redirect('/finsert')
    return render_template('finsert1.html')

@app.route('/fupdate', methods=['GET', 'POST'])
def update_fats():
    if session.get('user_type') != 'admin':
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    if request.method == 'POST':
        fat = float(request.form['fat'])
        price = float(request.form['price'])
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM fat WHERE fat = %s", (fat,))
            if cursor.fetchone() is None:
                flash('Fat does not found.', 'danger')
            else:
                cursor.execute("UPDATE fat SET price = %s WHERE fat = %s", (price, fat))
                conn.commit()
                flash('Price updated successfully.', 'success')
            conn.close()
        except Exception as e:
            flash(f'Please, fill correct data', 'danger')
        return redirect('/fupdate')
    return render_template('fupdate1.html')


@app.route('/fdelete', methods=['GET', 'POST'])
def delete_fats():
    if session.get('user_type') != 'admin':
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    if request.method == 'POST':
        fat = float(request.form['fat'])
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM fat WHERE fat = %s", (fat,))
            if cursor.fetchone() is None:
                flash('Fat does not found.', 'danger')
            else:
            	cursor.execute("DELETE FROM fat WHERE fat = %s", (fat,))
            	conn.commit()
            	flash('Fat delete successfully.', 'success')
            conn.close()
        except Exception as e:
            flash(f'Please, fill correct data', 'danger')
        return redirect('/fdelete')
    return render_template('fdelete1.html')

#customer table

@app.route('/cselect', methods=['GET', 'POST'])
def customer_select():
    if session.get('user_type') != 'admin':
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer")
    data = cursor.fetchall()
    conn.close()
    return render_template('cselect.html',data=data)
    
@app.route('/cinsert', methods=['GET', 'POST'])
def customer_insert():
    if session.get('user_type') != 'admin':
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    if request.method == 'POST':
        cname = request.form['cname'].strip().capitalize()
        milk_type = request.form['milk_type'].strip().capitalize()
        address = request.form['address'].strip()
        mobileno = request.form['mobileno'].strip()

        if len(mobileno) == 10 and mobileno.isdigit():
            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                # Check if customer already exists
                cursor.execute("SELECT custno FROM customer WHERE cname = %s AND milk_type = %s AND mobileno = %s", (cname, milk_type, mobileno))
                
                existing = cursor.fetchone()
                if existing is None:
                    # Try inserting new customer
                    try:
                        cursor.execute("INSERT INTO customer (cname, milk_type, mobileno, address) VALUES (%s, %s, %s, %s)", (cname, milk_type, mobileno, address))
                        conn.commit()

                        # Get new customer ID
                        cursor.execute("SELECT custno FROM customer WHERE cname = %s AND mobileno = %s", (cname, mobileno))
                        data = cursor.fetchone()

                        flash(f"Customer successfully added, your number is {data[0]}", "success")
                    except Exception as insert_err:
                        flash("Customer already exists with the same name.", "danger")
                else:
                    flash("Customer already exists with the same name, milk type, and mobile number.", "danger")
            except Exception as e:
                flash("Please fill correct data.", "danger")
            finally:
                conn.close()
        else:
            flash("Invalid mobile number. It must be exactly 10 digits.", "danger")

        return redirect('/cinsert')

    return render_template('cinsert.html')

@app.route('/cupdate', methods=['GET', 'POST'])
def customer_update():
    if session.get('user_type') != 'admin':
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    if request.method == 'POST':
        custno = request.form['custno'].strip()
        cname = request.form['cname'].strip().capitalize()
        milk_type = request.form['milk_type'].strip()
        mobileno = request.form['mobileno'].strip()
        address = request.form['address'].strip()

        if len(mobileno) == 10 and mobileno.isdigit():
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM customer WHERE custno=%s", (custno,))
                if cursor.fetchone() is not None:
                    cursor.execute("UPDATE customer SET cname=%s, milk_type=%s, mobileno=%s, address=%s WHERE custno=%s", (cname, milk_type, mobileno, address, custno))
                    conn.commit()
                    flash("Customer updated successfully", "success")
                else:
                    flash("Customer not found", "danger")
            except Exception as e:
                flash("Mobile number already exist ", "danger")
            finally:
                conn.close()
        else:
            flash("Invalid mobile number. It must be 10 digits.", "danger")

        return redirect('/cupdate')

    return render_template('cupdate.html')

@app.route('/cdelete', methods=['GET', 'POST'])
def customer_delete():
    if session.get('user_type') != 'admin':
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    if request.method == 'POST':
        custno = request.form['custno'].strip()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customer WHERE custno=%s", (custno,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM customer WHERE custno=%s", (custno,))
            conn.commit()
            flash("Customer deleted successfully", "success")
        else:
            flash("Customer not found", "danger")
        conn.close()
        return redirect('/cdelete')
    return render_template('cdelete.html')
@app.route('/mselect', methods=['GET', 'POST'])
def select_milk():
	if session.get('user_type') not in ('admin','customer'):
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login'))
	data=[] # Ensure 'data' is always defined
	if request.method == 'POST':
		try:
			date_input = request.form['date'].strip()  # Format: YYYY-MM-DD
			date_obj = datetime.strptime(date_input, '%Y-%m-%d').date()
			conn = get_db_connection()
			cursor = conn.cursor()
			cursor.execute("SELECT m.custno, c.cname, c.milk_type, m.date, m.am_pm, m.milk, m.fat, m.price FROM milk m, customer c WHERE date=%s and c.custno=m.custno", (date_obj,))
			data = cursor.fetchall()
			conn.close()
		except Exception as e:
			flash('Something went wrong', 'danger')
	return render_template('mselect.html', data=data)

@app.route('/mcselect', methods=['GET', 'POST'])
def select_milk_customer():
    if session.get('user_type') not in ('admin','customer'):
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    data=[]
    if request.method == 'POST':
    	try:
    		custno = request.form['custno']# Format: YYYY-MM-DD
    		conn = get_db_connection()
    		cursor = conn.cursor()
    		cursor.execute("SELECT m.custno, c.cname, c.milk_type, m.date, m.am_pm, m.milk, m.fat, m.price , m.status FROM milk m, customer c WHERE m.custno=%s and c.custno=m.custno order by m.date desc limit 20", (custno,))
    		data = cursor.fetchall()
    		conn.close()
    	except Exception as e:
    		flash('Something went wrong', 'danger')
    return render_template('mcselect.html', data=data)

@app.route('/minsert', methods=['GET', 'POST'])
def insert_milk():
    if session.get('user_type') != 'admin':
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login'))
    if request.method == 'POST':
        custno = request.form['custno'].strip()
        milkt = float(request.form['milk'].strip())
        fat = float(request.form['fat'].strip()) if request.form['status'] == 'buy' else 0  # Set fat to 0 if status is 'sell'
        status = request.form['status'].strip()  # Get the status value from the form

        # Get current date and time information
        now = datetime.now()
        date_today = now.date()
        am_pm = 'AM' if now.hour < 12 else 'PM'

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 1. Check if customer exists
            cursor.execute("SELECT * FROM customer WHERE custno = %s", (custno,))
            customer = cursor.fetchone()
            if not customer:
                flash('Customer not found', 'danger')
                return redirect('/minsert')

            # 2. For "buy" status, get fat price
            if status == 'buy':
                cursor.execute("SELECT price FROM fat WHERE fat = %s", (fat,))
                fat_row = cursor.fetchone()
                if not fat_row:
                    flash('Fat not found', 'danger')
                    return redirect('/minsert')

                price = milkt * fat_row[0]  # Price based on fat price
            elif status == 'sell':
                price = milkt * 70  # Price based on milk * 70 for sell
            else:
                flash('Invalid status', 'danger')
                return redirect('/minsert')

            # 3. Check if milk data already exists for the same customer, date, AM/PM, and status
            cursor.execute("SELECT * FROM milk WHERE custno = %s AND am_pm = %s AND date = %s AND status = %s", 
                           (custno, am_pm, date_today, status))
            milk = cursor.fetchall()
            if milk:
                flash("Milk data already recorded for this time and status", 'danger')
                return redirect('/minsert')

            # 4. Insert milk data based on status (buy or sell)
            cursor.execute("INSERT INTO milk (date, am_pm, custno, milk, fat, price, status) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                           (date_today, am_pm, custno, milkt, fat, price, status))

            conn.commit()
            conn.close()
            flash('Milk data inserted successfully!', 'success')

        except Exception as e:
            flash('Something went wrong: ' + str(e), 'danger')

        return redirect('/minsert')

    return render_template('minsert.html')

@app.route('/mupdate', methods=['GET', 'POST'])
def update_milk():
    if session.get('user_type') != 'admin':
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            # Retrieve form data
            custno = float(request.form['custno'].strip())
            date_input = request.form['date'].strip()       # format: YYYY-MM-DD
            am_pm = request.form['AM_PM'].strip().upper()   # 'AM' or 'PM'
            milk_str = float(request.form['milk'].strip())        # milk amount
            fat_str = float(request.form['fat'].strip()) if request.form['status']=='buy' else 0      # fat percentage
            status = request.form['status'].strip().lower()  # Get the status (buy/sell)
            # Attempt to convert milk and fat to float
            try:
                milkt = float(milk_str)
                fat = round(float(fat_str), 1)
            except ValueError:
                flash('Please ensure all fields are correctly filled with numeric values.', 'danger')
                return redirect('/mupdate')

            # Validate the date format
            try:
                date_obj = datetime.strptime(date_input, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
                return redirect('/mupdate')

            # Establish DB connection
            conn = get_db_connection()
            cursor = conn.cursor()

            # 1. Check if customer exists
            cursor.execute("SELECT * FROM customer WHERE custno = %s", (custno,))
            customer = cursor.fetchone()
            if not customer:
                flash('Customer not found', 'danger')
                return redirect('/mupdate')

            # 2. Check if there is already a record with the same custno, date, AM/PM, and status
            cursor.execute("""
                SELECT * FROM milk 
                WHERE custno = %s AND date = %s AND am_pm = %s AND status = %s
            """, (custno, date_obj, am_pm, status))
            existing_record = cursor.fetchone()

            if not existing_record:
                flash(f'No Milk record for this customer, date, AM/PM, and {status}', 'danger')
                return redirect('/mupdate')

            # 3. Price Calculation based on Status
            if status == 'buy':
                # Get fat price for the 'buy' status
                cursor.execute("SELECT price FROM fat WHERE ROUND(fat,1) = %s", (fat,))
                fat_row = cursor.fetchone()
                if not fat_row:
                    flash('Fat not found in the database', 'danger')
                    return redirect('/mupdate')

                price = milkt * fat_row[0]  # Price based on fat price
            elif status == 'sell':
                # Fixed price for selling milk
                price = milkt * 70  # Assuming the price is always milk * 70 for selling
            else:
                flash('Invalid status. Status must be either "buy" or "sell".', 'danger')
                return redirect('/mupdate')

            # 4. Update or Insert the milk record
            if existing_record:
                # Record exists, perform an update
                cursor.execute("""
                    UPDATE milk 
                    SET milk = %s, fat = %s, price = %s, status = %s 
                    WHERE custno = %s AND date = %s AND am_pm = %s AND status = %s
                """, (milkt, fat, price, status, custno, date_obj, am_pm, status))

            else:
                # Record doesn't exist, proceed with insert (you can customize this part if needed)
                cursor.execute("""
                    INSERT INTO milk (custno, date, am_pm, milk, fat, price, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (custno, date_obj, am_pm, milkt, fat, price, status))

            # Commit the changes and close connection
            conn.commit()
            conn.close()

            flash('Milk record updated successfully!', 'success')
        except Exception as e:
            # In case of an error, provide a user-friendly message
            flash(f'Error: {str(e)}. Please ensure all fields are correctly filled.', 'danger')

        return redirect('/mupdate')

    return render_template('mupdate.html')

@app.route('/mdelete', methods=['GET', 'POST'])
def delete_milk():
    if session.get('user_type') != 'admin':
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login')) 
    if request.method == 'POST':
        try:
            custno = int(request.form['custno'].strip())
            date_input = request.form['date'].strip()  # Format: YYYY-MM-DD
            am_pm = request.form['AM_PM'].strip().upper()
            status = request.form['status'].strip().lower()
            date_obj = datetime.strptime(date_input, '%Y-%m-%d').date()

            conn = get_db_connection()
            cursor = conn.cursor()

            # 1. Check if milk record exists
            cursor.execute("SELECT * FROM milk WHERE custno = %s AND date = %s AND am_pm = %s and status=%s",(custno, date_obj, am_pm,status))
            record = cursor.fetchall()
            if not record:
                flash('Milk record not found for this customer, date, and AM/PM.', 'danger')
                return redirect('/mdelete')

            # 2. Delete record
            cursor.execute("DELETE FROM milk WHERE custno = %s AND date = %s AND am_pm = %s and status=%s ",(custno, date_obj, am_pm,status))

            conn.commit()
            conn.close()
            flash('Milk record deleted successfully!', 'success')

        except Exception as e:
            flash('Please, fill corect data' , 'danger')

        return redirect('/mdelete')

    return render_template('mdelete.html')


# SELECT page
@app.route('/lselect')
def select_loans():
    if session.get('user_type') not in ('admin','customer'):
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    #cursor.execute('SELECT l.custno, c.cname, l.loanamm, l.comment FROM customer c,loan l where c.custno = l.custno')
    cursor.execute("SELECT c.cname, l.custno, SUM(l.loanamm) AS total_loan, l.startdate, l.comment , l.loan_type FROM loan l, customer c where c.custno=l.custno GROUP BY l.custno, c.cname having total_loan>0 ORDER BY total_loan DESC ")
    data = cursor.fetchall()
    if not data:
    	flash("Loan data not found",'danger')
    conn.commit()
    conn.close()
    return render_template('lselect.html', data=data)

@app.route('/linsert', methods=['GET', 'POST'])
def insert_loan():
    if session.get('user_type') != 'admin':
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login'))
    conn = None
    cursor = None

    if request.method == 'POST':
        try:
            custno = int(request.form['custno'])
            loanamm = float(request.form['loanamm'])
            comment = request.form['comment'].strip()
            loantype = request.form['loantype']
            today = datetime.today()

            conn = get_db_connection()  # Establish connection
            cursor = conn.cursor()

            # Check if customer exists
            cursor.execute("SELECT * FROM customer WHERE custno = %s", (custno,))
            customer = cursor.fetchone()  # Fetch customer details

            if customer is None:
                flash("Customer does not exist", 'danger')
            else:
                if loantype == "take":
                    # Check if the requested loan amount is less than or equal to the total amount taken previously
                    cursor.execute("SELECT SUM(loanamm) FROM loan WHERE custno = %s", (custno,))
                    total_loan_taken = cursor.fetchone()[0] or 0

                    if loanamm <= total_loan_taken:
                        # Insert new loan transaction (negative amount for 'take')
                        cursor.execute("""
                            INSERT INTO loan (custno, loanamm, startdate, comment, loan_type)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (custno, -loanamm, today, comment, loantype))
                        flash("Loan taken recorded successfully", 'success')
                    else:
                        flash("Please check loan ammount ", 'danger')
                        return redirect('/linsert') # Redirect back to the form
                elif loantype == "give":
                    # Insert new loan transaction (positive amount for 'give')
                    cursor.execute("""
                        INSERT INTO loan (custno, loanamm, startdate, comment, loan_type)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (custno, loanamm, today, comment, loantype))
                    flash("Loan given recorded successfully", 'success')
                else:
                    flash("Invalid loan type selected", 'danger')
                    return redirect('/linsert') # Redirect back to the form

            conn.commit()  # Commit transaction

        except Exception as e:
            if conn:
                conn.rollback()  # Rollback on error
            flash(f"An error occurred: {e}", 'danger')

        finally:
            if cursor:
                cursor.close()  # Close cursor
            if conn:
                conn.close()  # Close connection

        return redirect('/linsert')

    return render_template('linsert.html')

@app.route('/ldelete', methods=['GET', 'POST'])
def history_loan():
    if session.get('user_type') not in ('admin','customer'):
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    data = []
    total_loan = 0  # Initialize total loan amount

    if request.method == 'POST':
        try:
            custno = int(request.form['custno'])

            conn = get_db_connection()
            cursor = conn.cursor()

            # Step 1: Check if customer exists
            cursor.execute("SELECT * FROM customer WHERE custno = %s", (custno,))
            c = cursor.fetchone()
            if c:
                # Step 2: Check if loan exists
                cursor.execute("SELECT * FROM loan WHERE custno = %s", (custno,))
                s = cursor.fetchall()  # Fetch all rows to avoid 'unread result'
                if s:
                    # Step 3: Fetch all loan records with customer info
                    cursor.execute("""
                        SELECT c.custno, c.cname, l.loanamm, l.comment, l.startdate, l.loan_type
                        FROM loan l
                        JOIN customer c ON c.custno = l.custno
                        WHERE c.custno = %s
                    """, (custno,))
                    data = cursor.fetchall()

                    # Calculate total loan amount
                    total_loan = sum([row[2] for row in data])  # Assuming loanamm is at index 2
                else:
                    flash("Customer doesn't have any loan.", 'danger')
            else:
                flash("Customer not found.", 'danger')

        except Exception as e:
            flash("Please fill correct data", 'danger')

    return render_template('ldelete.html', data=data, total_loan=total_loan)

@app.route("/billhistory", methods=["GET", "POST"])
def bill_history():
    if session.get('user_type') not in ('admin','customer'):
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    bills_summary = []  # Initialize the variable

    if request.method == "POST":
        try:
            custno = int(request.form['custno'])

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT b.custno, c.cname, b.start_date, b.end_date, b.total_milk, b.total_price 
                FROM bill b , customer c
                WHERE b.custno = %s and c.custno=b.custno order by b.bill_id desc limit 10
            """, (custno,))
            
            bills_summary = cursor.fetchall()  # Get the data

        except Exception as e:
            flash("Error: Invalid input or database issue", "danger")
    
    return render_template("billhistory.html", bills_summary=bills_summary)

def validate_dates(start_date_str, end_date_str):
    # Convert the string dates to datetime objects
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return "Invalid date format. Please use the correct format."

    # Get today's date
    today = datetime.today().date()

    # Check if start date or end date is in the future
    if start_date > today or end_date > today:
        return "Start date or end date cannot be in the future."

    # Check if start date is 1st, 11th, or 21st of the month
    if start_date.day not in [1, 11, 21]:
        return "Start date must be 1st, 11th, or 21st of the month."

    # Check if end date is 10th, 20th, or the last day of the month
    last_day_of_month = calendar.monthrange(end_date.year, end_date.month)[1]
    if end_date.day not in [10, 20] and end_date.day != last_day_of_month:
        return f"End date must be 10th, 20th, or the last day of the month ({last_day_of_month})."

    # Check if date difference is more than 11 days
    date_diff = (end_date - start_date).days
    if date_diff > 11 or date_diff < 1:
        return "Date difference cannot be more than 11 days."

    # If all checks pass
    return "Dates are valid."
#@app.route("/")

@app.route("/bill", methods=["GET", "POST"])
def bill():
    if session.get('user_type') != 'admin':
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login'))
    start_date = request.args.get('start_date') or request.form.get('start_date')
    end_date = request.args.get('end_date') or request.form.get('end_date')

    if request.method == "POST":
        # Validate the date range using the validate_dates function
        validation_message = validate_dates(start_date, end_date)

        if validation_message != "Dates are valid.":
            flash(validation_message, "danger")
            return redirect(url_for("bill"))
            #start_date=start_date, end_date=end_date))

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Fetch customers for the given date range
        cursor.execute("""
            SELECT DISTINCT m.custno, c.cname
            FROM milk m
            JOIN customer c ON c.custno = m.custno
            WHERE m.date BETWEEN %s AND %s and status=%s
        """, (start_date, end_date,"buy"))
        customers = cursor.fetchall()

        bills_summary = []
        for customer in customers:
            custno = customer["custno"]
            cname = customer["cname"]

            # Get milk data for the customer in the given date range
            cursor.execute("""
                SELECT * FROM milk
                WHERE custno = %s AND date BETWEEN %s AND %s
            """, (custno, start_date, end_date,))

            milk_data = cursor.fetchall()
            total_milk = 0.0
            total_price = 0.0

            for entry in milk_data:
                milk = entry["milk"]
                price = entry["price"] if entry["price"] is not None else milk
                total_milk += milk
                total_price += price

            # Check if the customer has any loan balance
            cursor.execute("SELECT SUM(loanamm) AS total_loan FROM loan WHERE custno = %s", (custno,))
            loan = cursor.fetchone()
            total_loan = loan["total_loan"] if loan["total_loan"] is not None else 0

            # Check loan status
            if total_loan > 0:
                cursor.execute("""
                    SELECT * FROM loan WHERE custno = %s and startdate BETWEEN %s and %s AND loan_type=%s
                """, (custno, start_date, end_date, "take"))
                loan_payment_today = cursor.fetchall()
                loan_status = "Paid Loan" if loan_payment_today else "Pay Loan"
            else:
                loan_status = "Print Bill"

            # Prepare the bill data
            bill = {
                "custno": custno,
                "cname": cname,
                "start_date": start_date,
                "end_date": end_date,
                "total_milk": round(total_milk, 2),
                "total_price": round(total_price, 2),
                "loan_status": loan_status
            }
            bills_summary.append(bill)

        db.commit()
        cursor.close()
        db.close()

        # Render the page with the newly generated bills
        return render_template("bill.html", bills_summary=bills_summary, start_date=start_date, end_date=end_date)
    #return render_template("bill11.html")
    return render_template("bill.html", bills=None, start_date=start_date, end_date=end_date)

@app.route("/pay_loan", methods=["POST"])
def pay_loan():
    if session.get('user_type') != 'admin':
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login'))
    custno = request.form["custno"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    loanamm = float(request.form["loan_paid"])
    total_milk = float(request.form['total_milk'])
    total_price = float(request.form['total_price'])

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    today = datetime.today()

    # Get total loan remaining
    cursor.execute("SELECT SUM(loanamm) AS total_loan FROM loan WHERE custno=%s", (custno,))
    loan = cursor.fetchone()
    total_loan = loan["total_loan"] if loan["total_loan"] else 0

    # Check if payment is less than or equal to total loan
    if loanamm > total_loan:
        flash(f"Loan payment ({loanamm}) cannot exceed remaining loan ({total_loan})", "danger")
        cursor.close()
        db.close()
        return redirect(url_for("bill", start_date=start_date, end_date=end_date))

    # Proceed to insert negative loan amount (payment)
    cursor.execute("""
        INSERT INTO loan (custno, loanamm, startdate, comment, loan_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (custno, -loanamm, end_date, 'Loan_paid', 'take'))


    cursor.execute("""
        INSERT INTO bill (custno, start_date, end_date, total_milk, total_price, status, loan)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_milk = VALUES(total_milk),
            total_price = VALUES(total_price),
            status = VALUES(status),
            loan = VALUES(loan),
            created_at = CURRENT_TIMESTAMP
    """, (custno, start_date, end_date, round(total_milk, 2), round(total_price, 2), "Print", loanamm))

    db.commit()
    cursor.close()
    db.close()

    flash("Loan paid successfully!", "success")
    return redirect(url_for("bill", start_date=start_date, end_date=end_date))


@app.route("/generate_bill/<int:custno>/<string:start_date>/<string:end_date>")
def generate_individual_bill(custno, start_date, end_date):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Fetch individual milk entries
    cursor.execute("""
        SELECT
            DATE_FORMAT(m.date, '%d-%m-%Y') AS date,
            m.milk,
            m.fat,
            f.price AS fat_rate,
            m.am_pm
        FROM
            milk m
        JOIN
            fat f ON m.fat = f.fat
        WHERE
            m.custno = %s AND m.date BETWEEN %s AND %s AND m.status = 'buy'
        ORDER BY
            m.date,
            CASE m.am_pm
                WHEN 'AM' THEN 1
                WHEN 'PM' THEN 2
                ELSE 3
            END;
    """, (custno, start_date, end_date))
    milk_data = cursor.fetchall()

    milk_entries = []
    daily_data = {}
    for row in milk_data:
        date = row['date']
        am_pm = row['am_pm']
        fat_rate = row['fat_rate']  # Get the price from the fat table

        if date not in daily_data:
            daily_data[date] = {'AM': {'milk': 0, 'fat': 0, 'rate': 0, 'price': 0}, 'PM': {'milk': 0, 'fat': 0, 'rate': 0, 'price': 0}}

        daily_data[date][am_pm]['milk'] = row['milk']
        daily_data[date][am_pm]['fat'] = row['fat']
        daily_data[date][am_pm]['rate'] = fat_rate  # Store the rate
        daily_data[date][am_pm]['price'] = round(row['milk'] * fat_rate, 2) # Calculate price

    for date, data in daily_data.items():
        milk_entries.append([
            date,
            data['AM']['milk'],
            data['AM']['fat'],
            data['AM']['rate'],  # Append the rate
            data['AM']['price'],
            data['PM']['milk'],
            data['PM']['fat'],
            data['PM']['rate'],  # Append the rate
            data['PM']['price']
        ])



    # Calculate total milk and price
    total_morning_milk = sum(data['AM']['milk'] for data in daily_data.values()) or 0
    total_evening_milk = sum(data['PM']['milk'] for data in daily_data.values()) or 0
    total_am = sum(data['AM']['price'] for data in daily_data.values()) or 0
    total_pm = sum(data['PM']['price'] for data in daily_data.values()) or 0
    total_price = sum(data['AM']['price'] + data['PM']['price'] for data in daily_data.values()) or 0
    total_milk = round(total_morning_milk + total_evening_milk, 2)

    total_milk_data = [
        round(total_morning_milk, 2),
        round(total_am, 2),
        round(total_evening_milk, 2),
        round(total_pm, 2),
        total_milk
    ]

    cursor.execute("""
        INSERT INTO bill (custno, start_date, end_date, total_milk, total_price, status, loan)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_milk = VALUES(total_milk),
            total_price = VALUES(total_price),
            status = VALUES(status),
            created_at = CURRENT_TIMESTAMP
    """, (custno, start_date, end_date, round(total_milk, 2), round(total_price, 2), "Print", 0))
    db.commit()


    # Fetch bill details with LEFT JOIN to handle cases where no loan exists
    cursor.execute("""
        SELECT
            SUM(l.loanamm) AS loanamm,
            b.bill_id,
            b.start_date,
            b.end_date,
            b.total_milk,
            b.total_price,
            b.loan,
            c.cname,
            c.custno,
            c.milk_type
        FROM
            bill b
        JOIN
            customer c ON b.custno = c.custno
        LEFT JOIN
            loan l ON c.custno = l.custno AND l.startdate <= %s
        WHERE
            b.custno = %s AND b.start_date = %s AND b.end_date = %s
        GROUP BY
            b.bill_id, b.start_date, b.end_date, b.total_milk, b.total_price, b.loan, c.cname, c.custno, c.milk_type
    """, (end_date, custno, start_date, end_date))
    bill_info = cursor.fetchone()

    if bill_info:
        # If loan is None, treat it as 0.00 for the calculation
        loan_amount = decimal.Decimal(bill_info['loan']) if bill_info['loan'] is not None else decimal.Decimal(0.00)
        total_price = decimal.Decimal(bill_info['total_price']) if bill_info['total_price'] is not None else decimal.Decimal(0.00)

        # Calculate net bill
        net_bill = total_price - loan_amount

        # Creating the bill dictionary
        bill = {
            "rloanamm": bill_info['loanamm'],  # Sum of loanamm
            "billno": bill_info['bill_id'],
            "start_date": bill_info['start_date'],  # .strftime('%d-%m-%Y'),
            "end_date": bill_info['end_date'],      # .strftime('%d-%m-%Y'),
            "custno": bill_info['custno'],
            "cname": bill_info['cname'],
            "milk_type": bill_info['milk_type'],
            "total_bill": round(total_price, 2),
            "loanamm": round(loan_amount, 2),
            "comment": "loan paid" if loan_amount > 0 else " ",
            "net_bill": round(net_bill, 2)  # Rounded for consistency
        }
        cursor.close()
        db.close()

        return render_template("bill_receipt.html",  bill=bill,milk=milk_entries, total_milk_data=total_milk_data)
    else:
        flash("No bill information found for the selected")




def validate_date(start_date_str, end_date_str):
    # Convert the string dates to datetime objects
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return "Invalid date format. Please use the correct format."

    # Get today's date
    today = datetime.today().date()

    # Check if start date or end date is in the future
    if start_date > today or end_date > today:
        return "Start date or end date cannot be in the future."


    # Check if date difference is more than 11 days
    date_diff = (end_date - start_date).days
    if date_diff < 1:
        return "Date difference cannot be less than 1 days."

    # If all checks pass
    return "Dates are valid."
    


@app.route("/bonushistory", methods=["GET", "POST"])
def bonus_history():
    if session.get('user_type') not in ('admin','customer'):
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    bills_summary = []  # Initialize the variable

    if request.method == "POST":
        try:
            custno = int(request.form['custno'])

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT b.custno, b.cname, b.start_date, b.end_date, b.total_milk, b.total_price ,b.percentile, b.bonus
                FROM bonus b, customer c
                WHERE b.custno = %s and c.custno=b.custno order by b.bid desc limit 5
            """, (custno,))
            
            bills_summary = cursor.fetchall()  # Get the data

        except Exception as e:
            flash("Error: Invalid input or database issue", "danger")
    
    return render_template("bonushistory.html", bills_summary=bills_summary)

  
@app.route("/bonus", methods=["GET", "POST"])
def bonus():
    if session.get('user_type') != 'admin':
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login'))
    start_date = request.args.get('start_date') or request.form.get('start_date')
    end_date = request.args.get('end_date') or request.form.get('end_date')

    # Retrieve the percentile value
    percentile_str =request.args.get('percentage') or request.form.get('percentage')
    #percentile = None # Initialize percentile

    if request.method == "POST":
        # Validate the date range using the validate_dates function
        validation_message = validate_date(start_date, end_date)

        if validation_message != "Dates are valid.":
            flash("Dates are not valid", "danger")
            return redirect(url_for("bonus")) # Redirecting to 'bonus' route

        # Validate percentile: Only checking if it's a number and present
        if percentile_str:
            try:
                percentile = float(percentile_str)
                # Removed: if not (0 <= percentile <= 100): as per your request.
                # WARNING: This makes your server-side less robust.
            except ValueError:
                flash("Invalid Bonus Percentage. Please enter a number.", "danger")
                return render_template("bonus.html", start_date=start_date, end_date=end_date, percentile=percentile_str)
        else:
            flash("Bonus Percentage is required.", "danger")
            return render_template("bonus.html", start_date=start_date, end_date=end_date, percentage=percentile_str)

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("select * from bonus where start_date=%s",(start_date,))
        bonus=cursor.fetchone()
        
        if bonus:
        	flash("Records already exist","danger")
        	return redirect("bonus")
        # Fetch customers and their aggregated bill data for the given date range
        cursor.execute("""
            SELECT
                b.custno,
                c.cname,
                SUM(b.total_milk) AS total_milk_period,
                SUM(b.total_price) AS total_price_period
            FROM bill b
            JOIN customer c ON c.custno = b.custno
            WHERE b.start_date >= %s AND b.end_date <= %s
            GROUP BY b.custno, c.cname
        """, (start_date, end_date,))
        customers_bill_data = cursor.fetchall()
        if not customers_bill_data:
        	flash("No data found please check dates","danger")
        	return redirect("bonus")
        bills_summary = []
        for customer_bill in customers_bill_data:
            custno = customer_bill["custno"]
            cname = customer_bill["cname"]
            total_milk = customer_bill["total_milk_period"]
            total_price = customer_bill["total_price_period"]

            # Calculate Bonus
            bonus = 0.0
            if total_price is not None and percentile is not None:
                bonus = (float(total_price) * (percentile / 100.0))
                bonus = round(bonus, 2) # Round bonus to 2 decimal places


            # Prepare the bill data
            bill = {
                "custno": custno,
                "cname": cname,
                "start_date": start_date,
                "end_date": end_date,
                "total_milk": round(total_milk, 2),
                "total_price": round(total_price, 2),
                "percentage":percentile_str,
                "bonus": bonus, # Add bonus to the bill dictionary
                #"loan_status": loan_status
            }
            bills_summary.append(bill)
            
        db.commit()
        cursor.close()
        db.close()

        # Render the page with the newly generated bills, passing the percentile
        return render_template("bonus.html", bills_summary=bills_summary,start_date=start_date, end_date=end_date,percentage=percentile_str)

    # For GET requests or initial load, or if validation fails and redirect is not used
    return render_template("bonus.html", bills_summary=None,start_date=start_date, end_date=end_date,percentage=percentile_str)

@app.route("/generate_bonus/<int:custno>/<string:cname>/<string:start_date>/<string:end_date>/<float:total_milk>/<float:total_price>/<float:percentile>/<float:bonus>")
def generate_individual_bonus(custno,cname,start_date, end_date,total_milk,total_price,percentile,bonus):
    if session.get('user_type') not in ('admin','customer'):
    	flash("Only admin can be access",'danger')
    	return redirect(url_for('login'))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""INSERT INTO bonus(custno, cname, start_date, end_date, total_milk, total_price, percentile, bonus)    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",(custno,cname,start_date,end_date,total_milk,total_price,percentile,bonus))
    db.commit()
    cursor.execute("select milk_type from customer where custno=%s",(custno,))
    milktype=cursor.fetchone()
    
    bill={"custno":custno,
        "cname":cname,
        "start_date":start_date,
        "end_date":end_date,
        "milk_type":milktype["milk_type"],
        "total_milk":total_milk,
        "total_price":total_price,
        "percentile":percentile,
        "bonus":bonus }
    
    return render_template("bonus_receipt.html",  bill=bill)


@app.route("/bodelete")
def delete_bonus():
    if session.get('user_type') != 'admin':
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bid, custno, cname, start_date, end_date, total_milk, total_price, percentile, bonus FROM bonus ORDER BY bid DESC limit 20")
    bill = cursor.fetchall()
    conn.close()  # Always close the connection
    return render_template("bodelete.html", bill=bill)

@app.route("/delete_bonus/<int:bid>", methods=["GET", "POST"])
def delete(bid):
    if session.get('user_type') != 'admin':
	   	flash("Only admin can be access",'danger')
	   	return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bonus WHERE bid = %s", (bid,))
    conn.commit()  # Commit the changes
    conn.close()
    
    flash(f"Bonus with ID {bid} has been deleted!", 'success')
    return redirect(url_for('delete_bonus'))

if __name__ == '__main__':
    app.run(debug=True)