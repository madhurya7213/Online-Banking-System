from flask import Flask, render_template, request, flash, redirect, url_for,session

from datetime import datetime
import json
import os.path

app = Flask(__name__)
app.secret_key = '4u8a4ut5au1te51uea6u81e5a1u6d54n65at4y'

acc_num_global = {}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/new-user')
def new_user():
    return render_template('new_user.html')


@app.route('/existing-user')
def existing_user():
    return render_template('existing_user.html')


@app.route('/customer-details', methods=['GET', 'POST'])
def customer_details():
    if request.method == 'POST':
        login = {}
        if os.path.exists('login.json'):
            with open('login.json') as login_file:
                login = json.load(login_file)
        if request.form['type'] == 'new':
            login[request.form['name']] = request.form['password']
            with open('login.json', 'w') as login_file:
                json.dump(login, login_file)
        if request.form['type'] == 'existing':
            if request.form['name'] not in login:
                flash('Access Denied!!')
                flash('Incorrect Username')
                return render_template('existing_user.html')
            if login[request.form['name']] != request.form['password']:
                flash('Access Denied!!')
                flash('Incorrect Password')
                return render_template('existing_user.html')
        return render_template('customer_details.html', name=request.form['name'])
    else:
        return render_template('home.html')


@app.route('/new-customer')
def new_customer():
    return render_template('new_customer.html')



@app.route('/existing-customer')
def existing_customer():
    return render_template('existing_customer.html')





# -------------------------------
# NO CHANGES BELOW THIS COMMENT
# Transaction routes untouched
# -------------------------------

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    global acc_num_global
    if request.method == 'POST':
        customer = {}
        if os.path.exists('customer.json'):
            with open('customer.json') as customer_file:
                customer = json.load(customer_file)
        if request.form['type'] == 'new':
            customer[request.form['acc_num']] = {
                'name': request.form['name'],
                'number': request.form['acc_num'],
                'balance': request.form['balance']
            }
            with open('customer.json', 'w') as customer_file:
                json.dump(customer, customer_file)
        if request.form['type'] == 'existing':
            if request.form['acc_num'] not in customer:
                flash('Access Denied!!')
                flash('Incorrect Account Number')
                return render_template('existing_customer.html')
        acc_num_global = request.form['acc_num']
        return render_template('transaction.html',
                               name=customer[acc_num_global]['name'],
                               number=customer[acc_num_global]['number'],
                               balance=customer[acc_num_global]['balance'])
    else:
        return render_template('home.html')


@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    global acc_num_global
    print(f"[DEBUG] acc_num_global: {acc_num_global}")  # debug print

    if request.method == 'POST':
        customer = {}
        if os.path.exists('customer.json'):
            with open('customer.json', 'r') as customer_file:
                customer = json.load(customer_file)
        else:
            flash("Customer data file missing!")
            return render_template('transaction.html', name="", number="", balance="")

        if acc_num_global == "":
            flash("Account number missing! Please login first.")
            return render_template('transaction.html', name="", number="", balance="")

        if request.form['option'] == 'deposit':
            customer[acc_num_global]['balance'] = str(
                int(customer[acc_num_global]['balance']) + int(request.form['amount']))
            flash('TRANSACTION SUCCESSFUL!!')
            flash('Amount Deposited: Rs. ' + str(request.form['amount']))
        elif request.form['option'] == 'withdraw':
            if (int(customer[acc_num_global]['balance']) - int(request.form['amount'])) >= 0:
                customer[acc_num_global]['balance'] = str(
                    int(customer[acc_num_global]['balance']) - int(request.form['amount']))
                flash('TRANSACTION SUCCESSFUL!!')
                flash('Amount Withdrawn: Rs. ' + str(request.form['amount']))
            else:
                flash('TRANSACTION FAILED!!')
                flash('Insufficient Balance')

        with open('customer.json', 'w') as customer_file:
            json.dump(customer, customer_file)

        return render_template('transaction.html',
                               name=customer[acc_num_global]['name'],
                               number=customer[acc_num_global]['number'],
                               balance=customer[acc_num_global]['balance'])
    else:
        flash("Please use the transaction page to submit the form.")
        return render_template('home.html')


# -------------------------------
# Admin-related changes corrected
# -------------------------------

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid admin credentials')
            return redirect(url_for('admin_login'))
    return render_template('admin.html')


@app.route('/admin-panel')
def admin_panel():
    try:
        with open('customer.json', 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        flash("customer.json file not found.", "error")
        users = {}
    except json.JSONDecodeError:
        flash("Error decoding customer.json.", "error")
        users = {}
    except Exception as e:
        flash(f"Unexpected error: {str(e)}", "error")
        users = {}

    return render_template('admin_panel.html', users=users)




@app.route('/edit-user/<acc_num>', methods=['GET', 'POST'])
def edit_user(acc_num):
    customers = {}
    if os.path.exists('customer.json'):
        with open('customer.json', 'r') as file:
            customers = json.load(file)

    if acc_num not in customers:
        flash("User not found.")
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        name = request.form['name']

        # Update user details
        customers[acc_num]['name'] = name

        # Save updated data
        with open('customer.json', 'w') as file:
            json.dump(customers, file)

        flash("User details updated successfully.")
        return redirect(url_for('edit_user', acc_num=acc_num))

    return render_template('edit_user.html', user=customers[acc_num], acc_num=acc_num)


@app.route('/delete-user/<acc_num>', methods=['POST'])
def delete_user(acc_num):
    try:
        if os.path.exists('customer.json'):
            with open('customer.json', 'r') as file:
                customers = json.load(file)
        else:
            flash("Customer data not found.")
            return redirect(url_for('admin_panel'))

        if acc_num in customers:
            del customers[acc_num]
            with open('customer.json', 'w') as file:
                json.dump(customers, file)
            flash(f"User with account number {acc_num} deleted successfully.")
        else:
            flash("Account number not found.")
    except Exception as e:
        flash(f"An error occurred: {str(e)}")

    return redirect(url_for('admin_panel'))

@app.route('/finance_diary', methods=['GET', 'POST'])
def finance_diary():
    global acc_num_global

    if not acc_num_global:
        flash("Please log in before accessing the finance diary.")
        return redirect(url_for('home'))

    diary = {}
    diary_file = f'diary_{acc_num_global}.json'  # separate file per user

    if os.path.exists(diary_file):
        with open(diary_file) as f:
            diary = json.load(f)

    if request.method == 'POST':
        date = request.form.get('date') or datetime.now().strftime('%Y-%m-%d')
        category = request.form.get('category')
        amount = request.form.get('amount')
        note = request.form.get('note')

        if not category or not amount:
            flash("Both Category and Amount are required!")
            return render_template('finance_diary.html', diary=diary)

        try:
            amount = float(amount)
        except ValueError:
            flash("Amount must be a number!")
            return render_template('finance_diary.html', diary=diary)

        # Add new transaction entry under the date
        diary.setdefault(date, [])
        diary[date].append({
            'category': category,
            'amount': amount,
            'note': note
        })

        with open(diary_file, 'w') as f:
            json.dump(diary, f, indent=4)

        flash("Transaction added successfully!")

    return render_template('finance_diary.html', diary=diary)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.")
    return redirect(url_for('existing_user'))  # Redirect to home page




# -------------------------------
# Main entry point
# -------------------------------

if __name__ == '__main__':
    app.run(port=5055, debug=True)
