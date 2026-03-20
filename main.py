from fastapi import FastAPI,Query,Response, status
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI()


#-----=MODELS------------
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    item_id:int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)
    order_type: Literal["delivery", "pickup"] = "delivery"
class NewMenuItem(BaseModel):
    name:     str  = Field(..., min_length=2, max_length=100)
    price:    int  = Field(..., gt=0)
    category: str  = Field(..., min_length=2)
    is_available: bool = True
class CheckoutRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


#6------------ TEMPORARY DATA ------------
menu_items = [
    {'id': 1, 'name': 'Margherita Pizza',      'price': 299, 'category': 'Pizza',       'is_available': True},
    {'id': 2, 'name': 'Pepperoni Pizza',       'price': 399, 'category': 'Pizza',       'is_available': True},
    {'id': 3, 'name': 'Veggie Burger',         'price': 199, 'category': 'Burger',      'is_available': True},
    {'id': 4, 'name': 'Cheeseburger',          'price': 249, 'category': 'Burger',      'is_available': False},
    {'id': 5, 'name': 'French Fries',          'price': 79,  'category': 'Sides',       'is_available': True},
    {'id': 6, 'name': 'Chicken Nuggets',       'price': 149, 'category': 'Sides',       'is_available': True},
    {'id': 7, 'name': 'Coca Cola',             'price': 49,  'category': 'Beverage',    'is_available': True},
]

orders        = []
order_counter = 1
cart          = []

#(9 ordertype)7------------ HELPER-------------
def find_menu_item(item_id: int):
    for p in menu_items:
        if p['id'] == item_id:
            return p
    return None
def calculate_bill(item, quantity, order_type):
    total = item["price"] * quantity

    if order_type == "delivery":
        total += 30  # delivery charge

    return total
def filter_menu_logic(category=None, min_price=None,
                          max_price=None, is_available=None):
    result = menu_items
    if category  is not None:
        result = [p for p in result if p['category'] == category]
    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]
    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]
    if is_available  is not None:
        result = [p for p in result if p['is_available'] == is_available]
    return result


#----------endpoints--------

#1.HOME ROUTE
@app.get("/")
def home():
    return {'message': 'Welcome to QuickBite Food Delivery'}

#2.List all records
@app.get("/menu")
def get_menu():
    return {"menu_items": menu_items, "total_items": len(menu_items)}

#11.Add new product with validation
@app.post('/menu')
def add_menu_item(new_menu_item: NewMenuItem, response: Response):
    existing_names = [p['name'].lower() for p in menu_items]
    if new_menu_item.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Product with this name already exists'}
    next_id = max(p['id'] for p in menu_items) + 1
    menu = {
        'id':       next_id,
        'name':     new_menu_item.name,
        'price':    new_menu_item.price,
        'category': new_menu_item.category,
        'is_available': new_menu_item.is_available,
    }
    menu_items.append(menu)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'menu added', 'menu_item': menu}

#10.Filter menu items based on query parameters
@app.get('/menu/filter')
def filter_menu(
    category:  str  = Query(None),
    min_price: int  = Query(None),
    max_price: int  = Query(None),
    is_available:  bool = Query(None),
):
    result = filter_menu_logic(category, min_price, max_price, is_available)
    return {'filtered_menu': result, 'count': len(result)}


#5.Summary/count endpoint
@app.get('/menu/summary')
def menu_summary():
    total_items = len(menu_items)
    is_available_items = sum(1 for p in menu_items if p['is_available'])
    is_not_available_items = total_items - is_available_items
    return {
        'total_items': total_items,
        'is_available_items': is_available_items,
        'is_not_available_items': is_not_available_items
    }

#16 Search menu items by keyword in name
@app.get('/menu/search')
def search_products(
    keyword: str = Query(..., description='Word to search for'),
):
    results = [
        p for p in menu_items
        if keyword.lower() in p['name'].lower()
    ]
    if not results:
        return {'message': f'No menu items found for: {keyword}', 'results': []}
    return {
        'keyword':     keyword,
        'total_found': len(results),
        'results':     results,
    }

#17.Sort menu items by price or name
@app.get('/menu/sort')
def sort_menu(
    sort_by: str = Query('price', description='price or name or category'),
    order:   str = Query('asc',   description='asc or desc'),
):
    if sort_by not in ['price', 'name', 'category']:
        return {'error': "sort_by must be 'price' or 'name' or 'category'"}
    if order not in ['asc', 'desc']:
        return {'error': "order must be 'asc' or 'desc'"}
    reverse         = (order == 'desc')
    sorted_menu = sorted(menu_items, key=lambda p: p[sort_by], reverse=reverse)
    return {
        'sort_by':  sort_by,
        'order':    order,
        'products': sorted_menu,
    }

#18.Pagination for menu items
@app.get('/menu/page')
def get_menu_paged(
    page:  int = Query(1, ge=1,  description='Page number'),
    limit: int = Query(2, ge=1, le=20, description='Items per page'),
):
    start = (page - 1) * limit
    end   = start + limit
    paged = menu_items[start:end]
    return {
        'page':        page,
        'limit':       limit,
        'total':       len(menu_items),
        'total_pages': -(-len(menu_items) // limit),   # ceiling division
        'products':    paged,
    }

#20.Combined search, sort, and pagination
@app.get('/menu/browse')
def browse_menu(
    keyword: str = Query(None),
    sort_by: str = Query('price'),
    order: str = Query('asc'),
    page: int = Query(1),
    limit: int = Query(10)
):
    # Step 1: Search
    result = menu_items

    if keyword:
        result = [p for p in menu_items if keyword.lower() in p['name'].lower()]

    # Step 2: Sort
    if sort_by in ['price', 'name']:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order == 'desc'))

    # Step 3: Paginate
    total = len(result)
    start = (page - 1) * limit
    paged = result[start: start + limit]

    return {
        'keyword': keyword,
        'sort_by': sort_by,
        'order': order,
        'page': page,
        'limit': limit,
        'total': total,
        'data': paged
    }

#12.Update menu item availability and price
@app.put('/menu/{item_id}')
def update_menu_item(
    item_id: int,
    response:   Response,
    is_available:   bool = Query(None),
    price:      int  = Query(None),
):
    menu_item = find_menu_item(item_id)
    if not menu_item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Menu item not found'}
    if is_available is not None:
        menu_item['is_available'] = is_available
    if price is not None:
        menu_item['price'] = price
    return {'message': 'Menu item updated', 'menu_item': menu_item}

#13.Delete menu item by ID
@app.delete('/menu/{item_id}')
def delete_menu_item(item_id: int, response: Response):
    menu_item = find_menu_item(item_id)
    if not menu_item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Menu item not found'}
    menu_items.remove(menu_item)
    return {'message': f"Menu item '{menu_item['name']}' deleted"}

#3.Get record by ID
@app.get('/menu/{item_id}')
def get_menu_item(item_id: int):
    menu_item = find_menu_item(item_id)
    if not menu_item:
        return {'error': 'Menu item not found'}
    return {'menu_item': menu_item}


#7,8 ,9 place order and get orders,order_type
@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    menu_item = find_menu_item(order_data.item_id)
    if not menu_item:
        return {'error': 'Menu item not found'}
    if not menu_item['is_available']:
        return {'error': f"{menu_item['name']} is not available"}
    total= calculate_bill(menu_item, order_data.quantity, order_data.order_type)
    order = {
        'order_id':         order_counter,
        'customer_name':    order_data.customer_name,
        'menu_item':        menu_item['name'],
        'quantity': order_data.quantity,
        'order_type': order_data.order_type,
        'delivery_address': order_data.delivery_address,
        'total_price':      total,
        'status':           'confirmed',
    }
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}

#4.get orders
@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}


#19.Search orders by customer name or order type
@app.get("/orders/search")
def search_orders(
    customer_name: str = Query(None),
    order_type: str = Query(None),
):
    filtered_orders = orders
    if customer_name:
        filtered_orders = [order for order in filtered_orders if order['customer_name'] == customer_name]
    if order_type:
        filtered_orders = [order for order in filtered_orders if order['order_type'] == order_type]
    return {'orders': filtered_orders, 'total_orders': len(filtered_orders)}

#19.Sort orders by total price or customer name
@app.get("/orders/sort")
def sort_orders(
    sort_by: str = Query('total_price', description='Field to sort by'),
    order: str = Query('asc', description='Sort order')
):
    if sort_by not in ['order_id', 'customer_name', 'total_price']:
        return {'error': "sort_by must be 'order_id', 'customer_name', or 'total_price'"}
    if order not in ['asc', 'desc']:
        return {'error': "order must be 'asc' or 'desc'"}
    sorted_orders = sorted(orders, key=lambda x: x[sort_by], reverse=(order == 'desc'))
    return {'orders': sorted_orders, 'total_orders': len(sorted_orders)}



#14.View cart items and grand total
@app.get('/cart')
def get_cart():
    return {'cart': cart, 'grand_total': len(cart)}
 
#14.Add item to cart with quantity and calculate subtotal
@app.post('/cart/add')
def add_to_cart(
    item_id: int = Query(...),
    quantity:   int = Query(1),
):
    menu_item = find_menu_item(item_id)
    if not menu_item:
        return {'error': 'Menu item not found'}
    if not menu_item['is_available']:
        return {'error': f"{menu_item['name']} is not available"}
    for item in cart:
        if item['item_id'] == item_id:
            item['quantity'] += quantity
            item['subtotal']  = calculate_bill(menu_item, item['quantity'], item['order_type'])
            return {'message': 'Cart updated', 'cart_item': item}
    cart_item = {
        'item_id':   item_id,
        'menu_item_name': menu_item['name'],
        'quantity':     quantity,
        'unit_price':   menu_item['price'],
        'subtotal':     calculate_bill(menu_item, quantity, order_type=None),
    }
    cart.append(cart_item)
    return {'message': 'Added to cart', 'cart_item': cart_item}

#15.Checkout cart items and place orders
@app.post('/cart/checkout')
def checkout(checkout_data: CheckoutRequest, response: Response):
    global order_counter
    if not cart:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Cart is empty'}
    placed_orders = []
    grand_total   = 0
    for item in cart:
        order = {
            'order_id':         order_counter,
            'customer_name':    checkout_data.customer_name,
            'menu_item':          item['menu_item_name'],
            'quantity':         item['quantity'],
            'delivery_address': checkout_data.delivery_address,
            'total_price':      item['subtotal'],
            'status':           'confirmed',
        }
        orders.append(order)
        placed_orders.append(order)
        grand_total   += item['subtotal']
        order_counter += 1
    cart.clear()
    response.status_code = status.HTTP_201_CREATED
    return {
        'message':       'Checkout successful',
        'orders_placed': placed_orders,
        'grand_total':   grand_total,
    }

#15.Remove item from cart
@app.delete('/cart/{item_id}')
def remove_from_cart(item_id: int, response: Response):
    for item in cart:
        if item['item_id'] == item_id:
            cart.remove(item)
            return {'message': f"{item['menu_item_name']} removed from cart"}
    response.status_code = status.HTTP_404_NOT_FOUND
    return {'error': 'Item not in cart'}