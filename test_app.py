import pytest
from flask import Flask, session
from main import app
import sqlite3
import os
@pytest.fixture
def mock_user():
    # Simulate a user object, you can expand this based on your database schema
    return {
        'email': 'testuser@example.com',
        'password': 'securepassword',
        'firstName': 'John',
        'lastName': 'Doe'
    }
@pytest.fixture
def client():
    # Create a test client for our Flask app
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'  # Use a test database
    client = app.test_client()

    # Set up a clean database before running tests
    with app.app_context():
        # Manually create the schema for the test database
        conn = sqlite3.connect('test_database.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            userId INTEGER PRIMARY KEY, 
            password TEXT,
            email TEXT,
            firstName TEXT,
            lastName TEXT,
            address1 TEXT,
            address2 TEXT,
            zipcode TEXT,
            city TEXT,
            state TEXT,
            country TEXT, 
            phone TEXT
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS products (
            productId INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            description TEXT,
            image TEXT,
            stock INTEGER,
            categoryId INTEGER,
            FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS kart (
            userId INTEGER,
            productId INTEGER,
            FOREIGN KEY(userId) REFERENCES users(userId),
            FOREIGN KEY(productId) REFERENCES products(productId)
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS categories (
            categoryId INTEGER PRIMARY KEY,
            name TEXT
        )''')

        conn.commit()
        conn.close()
        
    yield client

    # Clean up after test: remove the test database file
    os.remove('test_database.db')

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Check for a generic welcome message
    assert b"Shop by Category" in response.data  # Make sure categories section is present

def test_login_page(client):
    # Access the login page
    response = client.get('/loginForm')
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the form and error messages are rendered
    assert b'Email:' in response.data
    assert b'Password:' in response.data
    assert b'Register here' in response.data


def test_login(client):
    """Test the login route"""
    # Set up test data
    test_email = 'test@example.com'
    test_password = 'password123'

    # Try logging in with correct credentials
    response = client.post('/login', data={
        'email': test_email,
        'password': test_password
    }, follow_redirects=True)
    
    assert response.status_code == 200
    #assert b"Welcome" in response.data  # Check that the login was successful (you can adjust this based on your response)

def test_login_invalid_credentials(client):
    # Send POST request with invalid credentials
    response = client.post('/login', data={
        'email': 'invalid@example.com',
        'password': 'wrongpassword'
    })
    
    # Check if the error message is displayed
    assert response.status_code == 200
    assert b'Invalid UserId / Password' in response.data  # Ensure error message appears

def test_login_successful(client):
    with client.session_transaction() as sess:
        sess['loggedIn'] = True
        sess['firstName'] = 'John'
    
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Check for a generic welcome message

def test_login_valid_credentials(client, mock_user):
    # Use the mock_user fixture to send valid credentials
    response = client.post('/login', data={
        'email': mock_user['email'],
        'password': mock_user['password']
    })
    
    # Check if the user is redirected to the homepage (or another page based on your app's logic)
    assert response.status_code == 200  # Redirect status code

def test_register(client):
    """Test the registration route"""
    response = client.post('/register', data={
        'email': 'newuser@example.com',
        'password': 'newpassword',
        'firstName': 'John',
        'lastName': 'Doe',
        'address1': '1234 Main St',
        'address2': '',
        'zipcode': '12345',
        'city': 'Test City',
        'state': 'TS',
        'country': 'Testland',
        'phone': '1234567890'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registered Successfully" in response.data




def test_remove_item_from_cart(client):
    """Test the 'remove from cart' functionality"""
    # Log in and add a product to the cart
    response = client.post('/login', data={'email': 'test@example.com', 'password': 'hashedpassword'})
    response = client.get('/addToCart?productId=1', follow_redirects=True)

    # Now remove the product from the cart
    response = client.get('/removeFromCart?productId=1', follow_redirects=True)

    assert response.status_code == 200


def test_logout(client):
    """Test the logout functionality"""
    # First, log in
    response = client.post('/login', data={'email': 'test@example.com', 'password': 'hashedpassword'})
    
    # Now log out
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome" in response.data  # Adjust according to your homepage response when logged out
