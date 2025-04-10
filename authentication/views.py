import psycopg2
from utils.db_utils import get_db_connection
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET'])
def home(request):
    # if request.session.get('phone') is not None:
    #     return redirect('authentication:home')
    return render(request, 'home.html')

@require_http_methods(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        role = request.POST['role']
    
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            # patient
            if role == 'patient':
                cursor.execute("SELECT * FROM patient WHERE phone = %s AND password = %s", (phone, password))
            elif role == 'doctor':
                cursor.execute("SELECT * FROM doctor WHERE phone = %s AND password = %s", (phone, password))
            elif role == 'admin':
                cursor.execute("SELECT * FROM admin WHERE phone = %s AND password = %s", (phone, password))
            else:
                messages.error(request, 'Invalid role')
                return redirect('authentication:login')

            user = cursor.fetchone()

            if user is not None:
                request.session['phone'] = user[0]
                return redirect('authentication:home')
            else:
                messages.error(request, 'phone or password is incorrect')
                return redirect('authentication:login')

        except psycopg2.Error as e:
            print(e)
            return HttpResponse("Error occurred while connecting to the database")

        finally:
            if connection:
                cursor.close()
                connection.close()

    else:
        return render(request, 'login.html')


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        role = request.POST['role']

        try:
            connection = get_db_connection()

            cursor = connection.cursor()
            if role == 'patient':
                cursor.execute("INSERT INTO patient (phone, password) VALUES (%s, %s, %s)", (phone, password))
            elif role == 'doctor': 
                cursor.execute("INSERT INTO doctor (phone, password) VALUES (%s, %s, %s)", (phone, password))
            elif role == 'admin':
                cursor.execute("INSERT INTO admin (phone, password) VALUES (%s, %s, %s)", (phone, password))
                
            connection.commit()

            messages.success(request, 'Registration successful. Please login.')
            return redirect('authentication:login')

        except psycopg2.Error as e:
            if e.pgcode == 'P0001':
                messages.error(request, e.diag.message_primary)
                return redirect('register')
            else:
                print(e)
                return HttpResponse("Error occurred while connecting to the database")

        finally:
            if connection:
                cursor.close()
                connection.close()

    else:
        return render(request, 'register.html')


@require_http_methods(['GET'])
def logout(request):
    request.session.flush()
    return redirect('home')