from datetime import datetime
from flask import Flask, request, jsonify, session, render_template, redirect
from pymongo import MongoClient
from bson import ObjectId
import requests


app = Flask(__name__)
app.secret_key = '1'

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Gym"]
collection = db["users"]
collection2 = db["announcements"]
collection3 = db["services"]
collection4 = db["trainers"]
collection5 = db["reservations"]


########## -############-##########-############-###############-#############
# HTML endpoint
@app.route('/homeHTML')
def home():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('home.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Register HTML page
@app.route('/registerHTML')
def register_html():
    user_role = session.get('user', {}).get('role')
    try:
        return render_template('register.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 4


# User registration endpoint
@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        # Extracting data from JSON request
        first_name = data["first_name"]
        last_name = data["last_name"]
        country = data["country"]
        city = data["city"]
        address = data["address"]
        email = data["email"]
        username = data["username"]
        password = data["password"]
        # Unique Username,Email
        if collection.count_documents({'username': username}) > 0:
            return jsonify({"message": "Username is already in use. Please choose another."}), 400
        if collection.count_documents({'email': email}) > 0:
            return jsonify({"message": "Email is already in use. Please choose another."}), 400
        # Insert data into db
        user_document = {
            'first_name': first_name,
            'last_name': last_name,
            'country': country,
            'city': city,
            'address': address,
            'email': email,
            'username': username,
            'password': password,
            'role': 'pending',
        }
        insert_result = collection.insert_one(user_document)
        return jsonify({"message": "Registration successful!"}), 200
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Country endpoint
@app.route('/countries', methods=['GET'])
def get_countries():
    try:
        response = requests.get(
            "https://countriesnow.space/api/v0.1/countries")
        countries = response.json()["data"]
        return jsonify(countries), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# City endpoint
@app.route('/cities', methods=['POST'])
def get_cities():
    try:
        country = request.json.get('country')
        response = requests.post(
            "https://countriesnow.space/api/v0.1/countries/cities", json={"country": country})
        cities = response.json()["data"]
        return jsonify(cities), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


########## -############-##########-############-###############-###############

# Login HTML page
@app.route('/loginHTML')
def login_html():
    user_role = session.get('user', {}).get('role')
    try:
        return render_template('login.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data["username"]
        password = data["password"]

        # Check if username and password match
        user = collection.find_one(
            {'username': username, 'password': password})

        if user:
            if user['role'] == 'pending':
                # Forbidden
                return jsonify({"message": "Your account is pending approval"}), 403
            else:
                # User information
                session['user'] = {
                    '_id': str(user['_id']),
                    'role': user['role']
                }

                user_role = session['user']['role']
                return jsonify({"message": "Login successful", "success": True, "userRole": user_role}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Logout endpoint
@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to the home page
    return redirect('/homeHTML')


########## -############-##########-############-###############-###############

# Pending Users HTML page
@app.route('/pendingUsersHTML')
def pending_users_html():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('pendingUsers.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Endpoint to get pending users
@app.route('/pendingUsers', methods=['GET'])
def get_pending_users():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        pending_users = list(collection.find({'role': 'pending'}))
        for user in pending_users:
            user['_id'] = str(user['_id'])
        return jsonify(pending_users), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to approve or reject a user
@app.route('/userRole/<string:user_id>', methods=['PUT', 'DELETE'])
def approve_reject_user(user_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401

        user = collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({"message": "User not found"}), 404

        if request.method == 'PUT':
            data = request.json
            role = data.get('role')
            if not role or role not in ['user', 'admin']:
                return jsonify({"message": "Invalid role"}), 400
            collection.update_one({'_id': ObjectId(user_id)}, {
                                  '$set': {'role': role}})
            return jsonify({"message": "User approved successfully"}), 200
        elif request.method == 'DELETE':
            collection.delete_one({'_id': ObjectId(user_id)})
            return jsonify({"message": "User rejected  successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


########## -############-##########-############-###############-###############

# CRUD Users HTML page
@app.route('/crudUsersHTML')
def crud_users_html():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('crudUsers.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Endpoint to fetch all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        users = list(collection.find())
        for user in users:
            user['_id'] = str(user['_id'])
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to update a user
@app.route('/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.json
        updated_user = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'username': data['username'],
            'password': data['password'],
            'country': data['country'],
            'city': data['city'],
            'address': data['address']
        }
        collection.update_one({'_id': ObjectId(user_id)}, {
                              '$set': updated_user})
        return jsonify({"message": "User updated successfully"}), 200
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to delete a user
@app.route('/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        collection.delete_one({'_id': ObjectId(user_id)})
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to assign or modify a user's role
@app.route('/users/role/<string:user_id>', methods=['PUT'])
def assign_modify_role(user_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.json
        role = data.get('role')
        if not role or role not in ['user', 'admin']:
            return jsonify({"message": "Invalid role"}), 400
        collection.update_one({'_id': ObjectId(user_id)}, {
                              '$set': {'role': role}})
        return jsonify({"message": "User role updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

########## -############-##########-############-###############-###############


# CRUD Services HTML page
@app.route('/crudServicesHTML')
def crud_services_html():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('crudServices.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


@app.route('/createServiceHTML')
def create_services_html():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('createService.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Service endpoint
@app.route('/createServices', methods=['POST'])
def create_service():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.json
        # Extracting data from JSON request
        name = data["name"]
        service_type = data["service_type"]
        date = data["date"]
        time = data["time"]
        trainer_surname = data["trainer_surname"]
        capacity = data["capacity"]

        # Insert data into db
        service_document = {
            'name': name,
            'service_type': service_type,
            'date': date,
            'time': time,
            'trainer_surname': trainer_surname,
            'capacity': capacity
        }
        insert_result = collection3.insert_one(service_document)
        return jsonify({"message": "Service uploaded successfully!"}), 200
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# HTML Services


@app.route('/servicesHTML')
def services_html():
    try:
        user_role = session.get('user', {}).get('role')
        # Fetch services from the database
        services = list(collection3.find())
        # Pass services to the HTML template
        return render_template('services.html', userHTML=user_role, services=services)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Endpoint to fetch all services
@app.route('/services', methods=['GET'])
def get_services():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        services = list(collection3.find())
        for service in services:
            service['_id'] = str(service['_id'])
        return jsonify(services), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to update a service
@app.route('/services/<string:service_id>', methods=['PUT'])
def update_service(service_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.json
        updated_service = {
            'name': data['name'],
            'service_type': data['service_type'],
            'date': data['date'],
            'time': data['time'],
            'trainer_surname': data['trainer_surname'],
            'capacity': data['capacity']
        }
        collection3.update_one({'_id': ObjectId(service_id)}, {
            '$set': updated_service})
        return jsonify({"message": "Service updated successfully"}), 200
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to delete a service
@app.route('/services/<string:service_id>', methods=['DELETE'])
def delete_service(service_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        collection3.delete_one({'_id': ObjectId(service_id)})
        return jsonify({"message": "Service deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


########## -############-##########-############-###############-###############
# Trainers


# Create Trainer Page
@app.route('/createTrainerHTML')
def create_trainer_html():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('createTrainer.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Trainer endpoint
@app.route('/createTrainers', methods=['POST'])
def create_trainer():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.json
        # Extracting data from JSON request
        name = data["name"]
        surname = data["surname"]

        # Insert data into db
        trainer_document = {
            'name': name,
            'surname': surname
        }
        insert_result = collection4.insert_one(trainer_document)
        return jsonify({"message": "Trainer uploaded successfully!"}), 200
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to fetch all trainers
@app.route('/trainers', methods=['GET'])
def get_trainers():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        trainers = list(collection4.find())
        for trainer in trainers:
            trainer['_id'] = str(trainer['_id'])
        return jsonify(trainers), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to update a trainer
@app.route('/trainers/<string:trainer_id>', methods=['PUT'])
def update_trainer(trainer_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.json
        updated_trainer = {
            'name': data['name'],
            'surname': data['surname']
        }
        collection4.update_one({'_id': ObjectId(trainer_id)}, {
            '$set': updated_trainer})
        return jsonify({"message": "Trainer updated successfully"}), 200
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to delete a trainer
@app.route('/trainers/<string:trainer_id>', methods=['DELETE'])
def delete_trainer(trainer_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        collection4.delete_one({'_id': ObjectId(trainer_id)})
        return jsonify({"message": "Trainer deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


########## -############-##########-############-###############-###############
# Announcements
# HTML
@app.route('/announcementsHTML')
def announc_html():
    try:
        user_role = session.get('user', {}).get('role')
        # Fetch announcements from the database
        announcements = list(collection2.find())
        # Pass announcements to the HTML template
        return render_template('announcements.html', userHTML=user_role, announcements=announcements)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# HTML
@app.route('/createAnnouncementHTML')
def create_announc_html():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('createAnnouncement.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# HTML
@app.route('/crudAnnouncementsHTML')
def crud_announc_html():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('crudAnnouncements.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Announcement endpoint
@app.route('/createAnnouncements', methods=['POST'])
def create_announcement():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.json
        # Extracting data from JSON request
        title = data["title"]
        content = data["content"]

        # Insert data into db
        announcement_document = {
            'title': title,
            'content': content
        }
        insert_result = collection2.insert_one(announcement_document)
        return jsonify({"message": "Announcement uploaded successfully!"}), 200
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to fetch all announcements
@app.route('/announcements', methods=['GET'])
def get_announcements():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        announcements = list(collection2.find())
        for announcement in announcements:
            announcement['_id'] = str(announcement['_id'])
        return jsonify(announcements), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to update an announcement
@app.route('/announcements/<string:announcement_id>', methods=['PUT'])
def update_announcement(announcement_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.json
        updated_announcement = {
            'title': data['title'],
            'content': data['content']
        }
        collection2.update_one({'_id': ObjectId(announcement_id)}, {
            '$set': updated_announcement})
        return jsonify({"message": "Announcement updated successfully"}), 200
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to delete an announcement
@app.route('/announcements/<string:announcement_id>', methods=['DELETE'])
def delete_announcement(announcement_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({"message": "Unauthorized access"}), 401
        collection2.delete_one({'_id': ObjectId(announcement_id)})
        return jsonify({"message": "Announcement deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


########## -############-##########-############-###############-###############
# BOOK


# HTML Availability
@app.route('/checkAvailabilityHTML')
def reservation_search_html():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('checkAvailability.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Endpoint for Checking Availability
@app.route('/checkAvailability', methods=['POST'])
def check_availability():
    try:
        if 'user' not in session or session['user']['role'] != 'user':
            return jsonify({"message": "Unauthorized access"}), 401
        data = request.json
        program = data.get('program')
        date = data.get('date')

        all_services = list(collection3.find())

        # Filter services based on program and/or date
        filtered_services = all_services

        if program:
            filtered_services = [
                service for service in filtered_services if service['service_type'] == program]

        if date:
            filtered_services = [
                service for service in filtered_services if service['date'] == date]

        response_data = []
        for service in filtered_services:
            capacity = int(service['capacity']) if isinstance(
                service['capacity'], str) and service['capacity'].isdigit() else service['capacity']
            service_data = {
                '_id': str(service['_id']),
                'name': service['name'],
                'time': service['time'],
                'capacity': capacity,
                'dates': [service['date']],
            }
            response_data.append(service_data)

        return jsonify({"message": "Available time slots", "available_time_slots": response_data}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint for Reserving Service
@app.route('/reserveTimeSlot', methods=['POST'])
def reserve_time_slot():
    try:
        if 'user' not in session or session['user']['role'] != 'user':
            return jsonify({"message": "Unauthorized access"}), 401

        data = request.json
        user_id = session['user']['_id']
        service_id = data.get('service_id')

        if not service_id or not ObjectId.is_valid(service_id):
            return jsonify({"message": "Invalid Service ID provided"}), 400

        service = collection3.find_one({'_id': ObjectId(service_id)})

        if not service:
            return jsonify({"message": "Service not found"}), 404

        capacity = int(service['capacity'])

        if capacity <= 0:
            return jsonify({"message": "No available slots for this service"}), 400

        # Update capacity by -1
        collection3.update_one({'_id': ObjectId(service_id)}, {
                               '$set': {'capacity': capacity - 1}})

        # Get the current date and time in a readable format
        reservation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        reservation_data = {
            'user_id': user_id,
            'service_id': str(service_id),
            'reservation_date': reservation_date,
            'status': 'booked'
        }
        insert_result = collection5.insert_one(reservation_data)

        return jsonify({"message": "Reservation successful!"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# HTML Reservation
@app.route('/userReservationHTML')
def user_resHTML():
    try:
        user_role = session.get('user', {}).get('role')
        return render_template('userReservation.html', userHTML=user_role)
    except FileNotFoundError:
        return jsonify({"message": "HTML file not found"}), 404


# Endpoint to get users' reservations and corresponding service details
@app.route('/userReservations', methods=['GET'])
def get_user_reservations():
    try:
        if 'user' not in session or session['user']['role'] != 'user':
            return jsonify({"message": "Unauthorized access"}), 401

        user_id = session['user']['_id']

        reservations = list(collection5.find({'user_id': user_id}))

        if not reservations:
            return jsonify({"message": "No reservations found"}), 200

        # Retrieve service details for each reservation
        user_reservations = []
        for reservation in reservations:
            service_id = reservation['service_id']
            service_details = collection3.find_one(
                {'_id': ObjectId(service_id)})
            if service_details:
                service_details['_id'] = str(service_details['_id'])
                # Include reservation ID
                reservation['_id'] = str(reservation['_id'])
                # Include service details
                reservation['service_details'] = service_details
                user_reservations.append(reservation)

        return jsonify(user_reservations), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Endpoint to cancel a reservation
@app.route('/cancelReservation/<string:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    try:
        if 'user' not in session or session['user']['role'] != 'user':
            return jsonify({"message": "Unauthorized access"}), 401

        # Check if the reservation exists
        reservation = collection5.find_one({'_id': ObjectId(reservation_id)})
        if not reservation:
            return jsonify({"message": "Reservation not found"}), 404

        # Check if the reservation belongs to the current user
        user_id = session['user']['_id']
        if reservation['user_id'] != user_id:
            return jsonify({"message": "You are not authorized to cancel this reservation"}), 403

        # Update the service's capacity by +1 since the reservation is being canceled
        service_id = reservation['service_id']
        service = collection3.find_one({'_id': ObjectId(service_id)})
        if service:
            capacity = int(service['capacity'])
            collection3.update_one({'_id': ObjectId(service_id)}, {
                                   '$set': {'capacity': capacity + 1}})

        # Delete the reservation
        collection5.delete_one({'_id': ObjectId(reservation_id)})

        return jsonify({"message": "Reservation canceled successfully"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


########## -############-##########-############-###############-###############
# Run flask in debug mode in port 5000
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
