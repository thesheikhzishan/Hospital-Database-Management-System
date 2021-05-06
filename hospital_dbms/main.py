from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL

app = Flask(__name__)

# Database confirgurations
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "hospital_admin"
# create username = hospital_admin
# password = "cse2018"
# Add your root password below
app.config['MYSQL_PASSWORD'] = "cse2018"
app.config['MYSQL_DB'] = "hospital"

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employees')
def employees():
    cur = mysql.connection.cursor()
    employees = cur.execute("SELECT * from Employees")

    if employees > 0:
        employee_info = cur.fetchall()
        return render_template('employee.html', employee_info=employee_info)

    return ("<h2>No employee entry in the database</h2>")

@app.route('/patients')
def patients():
    cur = mysql.connection.cursor()
    patients = cur.execute("SELECT * from Patients where discharged = '0'")

    if patients > 0:
        patients_info = cur.fetchall()
        return render_template('patients.html', patients_info=patients_info)

    return ("<h2>No patient entry in the database</h2>")

@app.route('/patient_reg_main')
def patient_reg_main():
	return render_template('patient_main_reg.html')

@app.route('/already_reg', methods = ['GET', 'POST'])
def already_registered():
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		pids = cur.execute("SELECT patient_ID FROM patients")
		pids = cur.fetchall()
		id = request.form['id']
		p_id = (id, )
		if p_id not in pids:
			return ('<h2>patient with this ID doesnot exists. Please enter valid patient ID.</h2>')
		else:
			cur.execute("UPDATE patients set discharged = '0', doctors = NULL, room = NULL, medicine = NULL where patient_ID = \'%s\'"%(id))
			mysql.connection.commit()
			cur.close()
			return redirect(url_for('patient_success'))
	return render_template('already_registered.html')

@app.route('/patient_reg', methods = ['GET', 'POST'])
def patient_registration():
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		pids = cur.execute("SELECT patient_ID FROM patients")
		pids = cur.fetchall()
		id = request.form['id']
		p_id = (id, )
		name = request.form['name']
		contact = request.form['contact']
		dob =  request.form['dob']
		address = request.form['address']
		if p_id in pids:
			return render_template("patient_already_exists.html", id = id)
		else:
			cur.execute("call new_patient(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')" % (id, name, dob, contact, address))
			mysql.connection.commit()
			cur.close()
			return redirect(url_for('patient_success'))

	return render_template("patient_registration.html")

@app.route('/delete', methods=['GET', 'POST'])
def employee_deletion():
	if request.method == 'POST':
		info = request.form['info']
		eid = info.split(' ')[0]
		designation = info.split(' ')[-1]
		print(eid)
		cur = mysql.connection.cursor()
		eids = cur.execute("SELECT id FROM employees")
		eids = cur.fetchall()
		# checking for invalid deletion
		eid = (eid,)
		if eid not in eids:
			return ('<h2>Employee with this ID doesnot exists. Please enter valid ID.</h2>')
		else:
			if designation == "[Doctor]":
				cur.execute("DELETE FROM doctors WHERE id = \'{}\'".format(eid[0]))
			elif designation == "[Nurses]":
				cur.execute("DELETE FROM nurses WHERE id = \'{}\'".format(eid[0]))
			else:
				cur.execute("DELETE FROM management_staff WHERE id = \'{}\'".format(eid[0]))

			cur.execute("DELETE FROM employees WHERE id = \'{}\'".format(eid[0]))
			mysql.connection.commit()
			cur.close()
			return render_template('deleted_successfully.html', info = info)

	cur = mysql.connection.cursor()
	cur.execute("SELECT id, name, designation FROM employees")
	employees_info = cur.fetchall()
	return render_template('employee_deletion.html', employees_info=employees_info)


@app.route('/register', methods=['GET', 'POST'])
def employee_reg():
	if request.method == 'POST':
		id = request.form['id']
		name = request.form['name']
		contact = request.form['contact']
		designation = request.form['designation']
		email = request.form['email']
		address = request.form['address']
		salary = request.form['salary']

		cur = mysql.connection.cursor()

		ids = cur.execute("SELECT id FROM employees")
		ids = cur.fetchall()

		# checking for duplicate entry
		eid = (id,)
		if eid in ids:
		    return render_template("already_exists.html", id = id)
		else:
			if designation == "Doctor":
				cur.execute("call hire_doctor(\'%s\',\'%s\', \'%s\', NULL,\'%s\', \'%s\', %.2f)" % (id, name, contact, email, address, float(salary)))
			elif designation == "Nurse":
				cur.execute("call hire_nurse(\'%s\',\'%s\', \'%s\', \'%s\', \'%s\', %.2f)" % (id, name, contact, email, address, float(salary)))
			else:
				curr.execute("call hire_management(\'%s\',\'%s\', \'%s\', \'%s\', \'%s\', %.2f)" % (id, name, contact, email, address, float(salary)))


		mysql.connection.commit()
		cur.close()
		return redirect(url_for('success'))

	return render_template('employee_registration.html')

@app.route('/success', methods=['GET', 'POST'])
def success():
	return render_template("employee_registered.html")

@app.route('/patient_success', methods = ['GET', 'POST'])
def patient_success():
	return render_template("patient_registered.html")

@app.route('/patient-index')
def patient_index():
	return render_template('patient_index.html')

@app.route('/admin-index')
def admin_index():
	return render_template('admin_index.html')

@app.route('/staff-index')
def staff_index():
	return render_template('staff_index.html')


if __name__ == '__main__':
    app.run(debug=True)
