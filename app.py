from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Message
from config import Config
from extensions import mail, mongo
from forms import UserForm

app = Flask(__name__)
app.config.from_object(Config)

mail.init_app(app)
mongo.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        # Save user data to MongoDB
        user_data = {
            'name': name,
            'email': email,
            'message': message
        }
        mongo.db.users.insert_one(user_data)

        # Send the email
        msg = Message('Thank you for your submission', recipients=[email])
        # print(msg)
        msg.body = render_template('email_template.txt', name=name, message=message)
        # print(msg.body)
        msg.html = render_template('email_template.html', name=name, message=message)
        # print(msg.html)

        try:
            mail.send(msg)
            flash('Form submitted successfully! An email has been sent.', 'success')
        except Exception as e:
            flash(f'An error occurred while sending the email: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('form.html', form=form)


@app.route('/api/submit', methods=['POST'])
def api_submit():
    data = request.json

    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({'error': 'Missing required fields'}), 400

    # Save user data to MongoDB
    user_data = {
        'name': name,
        'email': email,
        'message': message
    }
    mongo.db.users.insert_one(user_data)

    # Send the email
    msg = Message('Thank you for your submission', recipients=[email])
    msg.body = f"Dear {name},\n\n{message}\n\nThank you!"
    msg.html = render_template('email_template.html', name=name, message=message)

    try:
        mail.send(msg)
        return jsonify({'message': 'Form submitted successfully! An email has been sent.'}), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred while sending the email: {str(e)}'}), 500
    


if __name__ == '__main__':
    app.run(debug=True, port=8000)
