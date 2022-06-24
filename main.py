import model
import random


from flask import Flask, request, jsonify, session

# The following lines defines the application gateway
app = Flask(__name__)
app.secret_key = "flaskkey"


# Following method is used for logging in
@app.route('/login', methods=['GET'])
def login():
    """ used for loggin in .
        if the session is not active and Checks if given username and password is correct then logs in and creates token
        otherwise gives appropriate error response
    """
    payload = request.get_json()
    username = payload["username"]
    password = payload["password"]
    if 'username' in session and username == session['username']:
            response = "user already logged in "
            statusCode = 400

    else:
        (response, statusCode) = model.validate_customer(username, password)
        if statusCode == 200:
            customerDetails = response['response']['customerDetails']
            session['userId'] = customerDetails['customer_id']
            session['username']=username
            session['customerName'] = customerDetails['customer_name']
            session['level'] = customerDetails['level']
            customerDetails['token']=random.random()
            session['token'] = customerDetails['token']

    return formatResponse(response,statusCode), statusCode


@app.route('/logout', methods=['GET'])
def logout():
    """ Used for logging out . checks if given token in valid or not  and if session is active or not"""
    token = float(request.headers.get('token'))
    if 'token' in session :
        if session['token'] == token:
            session.pop('userid', None)
            session.pop('customerName', None)
            session.pop('username',None)
            session.pop('level', None)
            session.pop('token',None)
            response = "Logged out successfully"
            statusCode = 200
        else:
            response = "Invalid token. Please provide a valid token"
            statusCode = 403
    else:
        response = "No active session"
        statusCode = "400"
    return formatResponse(response,statusCode), statusCode


@app.route('/customer', methods=['POST'])
def add_customer():
    """ user for adding customer .The request should contains valid levels: 1 for vendor ,
    0 for customer and 2 for admin """
    data = request.get_json()
    name = data["name"]
    username = data["username"]
    password = data["password"]
    level1 = data["level"]
    if level1 not in ([1,2,3]):
        response= "Invalid level . level should be '0' for customer, '1' for vendor and '2' for admin"
        statusCode= 400
    else:
        (response,statusCode) = model.add_customer(name, username, password, level1)
    return formatResponse(response,statusCode),statusCode


@app.route('/vendor', methods=['POST'])
def add_vendor():
    """user for adding vendor """
    # Extracting JSON from request
    data = request.get_json()
    customerId = data["customerId"]
    storeName = data["storeName"]
    (response,statusCode) = model.add_vendor(customerId, storeName)
    return formatResponse(response,statusCode),statusCode


@app.route('/item', methods=['POST'])
def add_item():
    """ if given logged in user is vendor then adds the requested item"""
    token = request.headers.get('token')
    if 'token' in session :
        if str(session['token'])== token:
            if session['level'] == 1:
                data = request.get_json()
                dish_name = data["dish_name"]
                item_name = data["item_name"]
                vendor_id = data["vendor_id"]
                store_id = data["store_id"]
                available_quantity = data["available_quantity"]
                unit_price = data["unit_price"]
                (response,statusCode) = model.add_item(dish_name, item_name, vendor_id, store_id, available_quantity, unit_price)
            else:
                response = "logged in user is not vendor"
                statusCode = 400
        else:
            response = "invalid token"
            statusCode = 403
    else:
        response= "No Active Session"
        statusCode = 403
    return formatResponse(response,statusCode), statusCode


@app.route('/order', methods=['POST'])
def place_order():
    """if the given logged in user is customer (level=0) then places an order"""
    token = request.headers.get('token')
    if 'token' in session :
        if str(session['token']) == token:
            if session['level'] == 0:
                data = request.get_json()
                item_id = data["item_id"]
                quantity = data["quantity"]
                (response,statusCode) = model.place_order(session['userId'], item_id, quantity)
            else:
                response = "Logged in user not a customer  . Cannot perform this action"
                statusCode = 500
        else:
            response = "invalid token"
            statusCode = 403
    else:
        response = "No Active Session"
        statusCode = 400
    return formatResponse(response,statusCode), statusCode


@app.route('/orders', methods=['GET'])
def get_all_orders():
    """if given logged in user is admin then displays all the orderes placed"""
    token = request.headers.get('token')
    if 'token' in session:
        if str(session['token']) == token:
            if session['level'] == 2:
                (response,statusCode) = model.get_all_orders()
            else:
                response = "Logged in user not a admin  . Cannot perform this action"
                statusCode = 500
        else:
            response = "invalid token"
            statusCode = 403
    else:
        response = "No Active Session"
        statusCode = 400

    return formatResponse(response,statusCode), statusCode


@app.route('/customer/orders', methods=['GET'])
def get_all_orders_by_customers():
    """retrieves details of orders placed by given customer Takes header token and customerId as query parameter"""
    token = request.headers.get('token')
    if 'token' in session :
        if str(session['token']) == token:
                customerId=request.args.get('customerId')
                (response,statusCode) = model.get_orders_by_customer(customerId)

        else:
            response = "invalid token"
            statusCode = 403

    else:
        response = "No Active Session"
        statusCode = 400
    return formatResponse(response,statusCode), statusCode


@app.route('/vendor', methods=['GET'])
def get_all_vendors():
    """returns list of vendors and items they provide"""
    token = request.headers.get('token')
    if 'token' in session:
        if str(session['token']) == token:
            (response,statusCode) = model.get_all_vendors()
        else:
            response = "invalid token"
            statusCode = 403
    else:
        response = "No Active Session"
        statusCode = 400
    return formatResponse(response,statusCode), statusCode


@app.route('/item/<itemName>', methods=['GET'])
def get_item(itemName):
    """used for getting details of given item. itemName is expected as URI parameter"""
    token = request.headers.get('token')
    if 'token' in session :
        if str(session['token']) == token:
            if session['level'] == 1 or session['level'] == 0:
                (response,statusCode) = model.search_item_by_name(itemName)
            else:
                response = "Logged in user not a customer or vendor . Cannot perform this action"
                statusCode = 500
        else:
            response = "invalid token"
            statusCode = 403
    else:
        response = "No Active Session"
        statusCode = 400
    return formatResponse(response,statusCode), statusCode

def formatResponse(message,statusCode):
    """used for forming response"""
    if statusCode == 200:
        if 'response' in message:
            message['response']['statusCode'] = statusCode
            return jsonify(message['response'])
        else:
            return jsonify({'message':message,'statusCode':statusCode})
    else:
        return jsonify({"errMessage":message,"statusCode": statusCode})


if __name__ == '__main__':
    app.run(debug=True)
