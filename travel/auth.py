from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from .forms import LoginForm, RegisterForm
from .models import User
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

from . import db

# a blueprint to manage authentication
authbp = Blueprint('auth',__name__)


@authbp.route('/register', methods = ['GET', 'POST'])  
def register():  
  #create the form
    form = RegisterForm()

    if '_flashes' in session:
      session['_flashes'].clear()

    #this line is called when the form - POST
    if form.validate_on_submit():
      print('Register form submitted')
       
      #get username, password and email from the form
      fname =form.first_name.data
      sname = form.surname.data
      email=form.email.data
      phone = form.phone.data
      address = form.address.data
      pwd = form.password.data
      confirm = form.confirm.data

      

      existing_user = User.query.filter(User.emailid == email).first()
      if existing_user:
          if existing_user.emailid == email:
              flash('Email already registered. Please use a different email.', 'danger')
          return redirect(url_for('auth.register', emailid=email))

      if pwd != confirm:
        flash('Re-entered password is not the same. Please put in the same password', 'danger')
        return redirect(url_for('auth.register', pwd=confirm))
      
      password_hash = generate_password_hash(pwd)
      
      #create a new user model object
      new_user = User(first_name=fname, surname=sname, phone=phone, address=address, password_hash=password_hash, emailid=email)


      db.session.add(new_user)
      db.session.commit()
      flash("Successfully Registered!", 'success')
      return redirect(url_for('auth.register'))
       
    return render_template('register.html', form=form, heading='Register')



@authbp.route('/login', methods = ['GET', 'POST'])
def login():
  print(session)
  session.pop('_flashes', None)

  form = LoginForm()
  error=None
  if(form.validate_on_submit()):
    user_email = form.email.data
    password = form.password.data
    u1 = User.query.filter_by(emailid=user_email).first()

        #if there is no user with that name
    if u1 is None:
      error='Email does not exist'

    #check the password - notice password hash function
    elif not check_password_hash(u1.password_hash, password): # takes the hash and password
      error='Incorrect password'
    if error is None:
    #all good, set the login_user
      login_user(u1)
      return redirect(url_for('main.index'))
    else:
      print(error)
    #it comes here when it is a get method
    flash(error)
  return render_template('Log_In.html', form=form, heading='Login')


@authbp.route('/logout')
def logout():
  logout_user()
  return render_template('index.html')