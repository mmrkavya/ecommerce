
# Ecommerce Backend

Implemented the backend for an e-commerce website in Flask with SQLite database.

Its a complete backend system which allows  to signup customers and vendors, login them using their credentials, as a vendor add items in the database, as a customer place an order, and as an admin, I should be able to see all the orders placed etc.

## Details 
Attached the postman collection for reference of request-response
/customer:
Post:
    This is a signup API. This should take, “name, username, password, level” as parameters. Here level is 0 for the customer, 1 for vendor and 2 for Admin
/vendor:
post:    Only added customers can be made vendors. This API should take “customer_id, store_name” as parameters.

/login: Get:
    This API should take the username and password of signed up users and successfully logs them in.
    Returns details for the user logged in and token for calling other functions


## IMP: for all the endpoints after this it is madotory to user header :
##-> token: <token returned during login>


/item
->post : Only logged in vendors can add items. This API should take, “dish_name, item_name, vendor_id, store_id, available_quantity, unit_price”
->get:  item/<itemName> Any logged-in customer or vendor can call this API. This API should take, “customer_id, item_name” as parameters.

/order
  post: Only logged in customers can place orders. This API should take, “customer_id, item_id, quantity” as parameters.

/customer/orders
   get: Only logged in user can call this API. This returns all the orders placed by that customer. This should take, “customer_id” as a parameter.

/orders
   get: Only the admin can call this API. This API returns all the orders in the orders table.

/vendor:
  get:Only logged in users can call this API. This should return all the vendor details with their store and item offerings.

/logout:
   get: This API should log out the customer.
