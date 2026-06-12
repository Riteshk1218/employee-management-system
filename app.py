# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)  # initialize MySQL extension

# ─────────────────────────────────────────────
# READ — List all employees
# ─────────────────────────────────────────────
@app.route('/')
def index():
    cur = mysql.connection.cursor()

    # Optional search filter
    search = request.args.get('search', '')
    dept   = request.args.get('department', '')

    query  = "SELECT * FROM employees WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE %s OR email LIKE %s)"
        params += [f'%{search}%', f'%{search}%']

    if dept:
        query += " AND department = %s"
        params.append(dept)

    query += " ORDER BY created_at DESC"
    cur.execute(query, params)
    employees = cur.fetchall()

    # Get unique departments for the filter dropdown
    cur.execute("SELECT DISTINCT department FROM employees")
    departments = [row['department'] for row in cur.fetchall()]
    cur.close()

    return render_template('index.html',
                           employees=employees,
                           departments=departments,
                           search=search,
                           selected_dept=dept)


# ─────────────────────────────────────────────
# READ — View single employee
# ─────────────────────────────────────────────
@app.route('/employee/<int:id>')
def view_employee(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cur.fetchone()
    cur.close()

    if not employee:
        flash('Employee not found!', 'danger')
        return redirect(url_for('index'))

    return render_template('view_employee.html', employee=employee)


# ─────────────────────────────────────────────
# CREATE — Add new employee
# ─────────────────────────────────────────────
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        # Collect form data
        data = {
            'name':       request.form['name'],
            'email':      request.form['email'],
            'phone':      request.form['phone'],
            'department': request.form['department'],
            'position':   request.form['position'],
            'salary':     request.form['salary'],
            'hire_date':  request.form['hire_date'],
            'status':     request.form['status'],
        }

        # Basic validation
        if not data['name'] or not data['email']:
            flash('Name and Email are required!', 'danger')
            return render_template('add_employee.html', data=data)

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO employees
                    (name, email, phone, department, position, salary, hire_date, status)
                VALUES
                    (%(name)s, %(email)s, %(phone)s, %(department)s,
                     %(position)s, %(salary)s, %(hire_date)s, %(status)s)
            """, data)
            mysql.connection.commit()
            cur.close()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('add_employee.html', data={})


# ─────────────────────────────────────────────
# UPDATE — Edit employee
# ─────────────────────────────────────────────
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        data = {
            'id':         id,
            'name':       request.form['name'],
            'email':      request.form['email'],
            'phone':      request.form['phone'],
            'department': request.form['department'],
            'position':   request.form['position'],
            'salary':     request.form['salary'],
            'hire_date':  request.form['hire_date'],
            'status':     request.form['status'],
        }

        try:
            cur.execute("""
                UPDATE employees SET
                    name=%(name)s, email=%(email)s, phone=%(phone)s,
                    department=%(department)s, position=%(position)s,
                    salary=%(salary)s, hire_date=%(hire_date)s, status=%(status)s
                WHERE id=%(id)s
            """, data)
            mysql.connection.commit()
            cur.close()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    # GET — load existing data
    cur.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cur.fetchone()
    cur.close()

    if not employee:
        flash('Employee not found!', 'danger')
        return redirect(url_for('index'))

    return render_template('edit_employee.html', employee=employee)


# ─────────────────────────────────────────────
# DELETE — Remove employee
# ─────────────────────────────────────────────
@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM employees WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)