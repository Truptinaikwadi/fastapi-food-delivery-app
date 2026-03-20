# Food Delivery API

A backend REST API built using FastAPI that simulates a real-world food delivery system.  
This project includes menu management, order processing, cart functionality, and advanced features like search, filtering, sorting, and pagination.


##  Features

- View full menu
- Add, update, and delete menu items (CRUD)
- Search menu items by keyword
- Filter menu by category, price, availability
- Sort menu by price, name, and category
- Pagination support
- Add to cart and manage cart items
- Checkout system with order creation
- Place orders (delivery & pickup)
- Search and sort orders
- Menu summary (available vs unavailable items)


##  Tech Stack

- FastAPI
- Python
- Pydantic (Data Validation)
- Uvicorn (ASGI Server)


## Project Structure
│── main.py
│── requirements.txt
│── README.md
│── screenshots/
│── home.png
│── menu.png
│── order.png
│── cart.png



##  Installation & Setup

### Steps

1. Open Command Prompt (CMD) and create a project folder:
mkdir fastapi-project
cd fastapi-project


2. Create a virtual environment:


python -m venv venv


3. Activate the virtual environment:


venv\Scripts\activate


4. Install dependencies:


pip install -r requirements.txt


*(or manually install)*


pip install fastapi uvicorn


5. Run the server:

uvicorn main:app --reload


6. Open in browser:

- API Home: http://127.0.0.1:8000  
- Swagger UI: http://127.0.0.1:8000/docs  


## API Endpoints

### Menu

- `GET /menu` → Get all menu items  
- `POST /menu` → Add new item  
- `PUT /menu/{item_id}` → Update item  
- `DELETE /menu/{item_id}` → Delete item  
- `GET /menu/filter` → Filter items  
- `GET /menu/search` → Search items  
- `GET /menu/sort` → Sort items  
- `GET /menu/page` → Pagination  
- `GET /menu/browse` → Combined search + sort + pagination  
- `GET /menu/summary` → Menu statistics  

###  Orders

- `POST /orders` → Place order  
- `GET /orders` → View all orders  
- `GET /orders/search` → Search orders  
- `GET /orders/sort` → Sort orders  

###  Cart

- `POST /cart/add` → Add item to cart  
- `GET /cart` → View cart  
- `DELETE /cart/{item_id}` → Remove item  
- `POST /cart/checkout` → Checkout  



##  Author

Trupti Naikwadi  


##  Internship Project

This project was developed as part of a Data Science internship training program, where I learned backend development using FastAPI.

It demonstrates the practical implementation of concepts such as API development, data validation, and handling structured data through RESTful services.

Through this project, I gained hands-on experience in building APIs, managing application logic, and understanding how backend systems support data-driven applications.
