# A class representing models.
import sqlite3 as sql
import CustomerException

path="ecommerce.db"
orderId=1
def validate_customer(username, password):
        """
            Checks if given username and password is correct then returns user details
            otherwise gives appropriate error response
        """
        try:
                con = sql.connect(path)
                cur = con.cursor()
                cur.execute("select id,name,level from customer where username= ?  and password= ? ",(username,password))
                row = cur.fetchone();
                if row is not None:
                   response =({'response':{"customerDetails": {"customer_id":row[0],"customer_name":row[1],"level":row[2]}}}
                              ,200)

                else:
                    raise CustomerException.CustomException("login username/ password is incorrect",403)

        except CustomerException.CustomException as e:
            return (e.getMessage(),e.getStatusCode())
        except Exception as e:
            return ("error during login operation"+e,500)
        else:
            return response

        finally:
            con.close()



def add_customer(name, username, password, level1):
    """user for adding customer is no other customer has same username """
    try:
            # Making a connection to SQLite db
            con = sql.connect(path)
            cur = con.cursor()
            # Executing a SQL query
            count=(cur.execute("select count(*) from customer where username=?",(username,)).fetchone())
            if(count[0]>0):
               raise CustomerException.CustomException("User already exists. Please change the username",400)
            cur.execute("INSERT INTO customer (name, username, password, level) VALUES (?,?,?,?)",(name, username, password, level1))
            con.commit()
            response = ("Record successfully added",200)

    except CustomerException.CustomException as e:
            return (e.getMessage(),e.getStatusCode())
    except Exception as e:
            print(e)
            con.rollback()
            return ("error while adding new customer",400)
    else:
        return response
    finally:
            con.close()


def add_vendor(customerId,storeName):
    """adding vendor if given customerID is valid and storename is already present in vendor table"""
    response = None
    try:
        # Making a connection to SQLite db
        con = sql.connect(path)
        cur = con.cursor()
        # Executing a SQL query
        res = (cur.execute("select level from customer where id=? ", (customerId,)).fetchone())
        if (res is None):
            raise CustomerException.CustomException("Invalid customer id. For vendor should be linked with valid customer id", 400)

        count = (cur.execute("select count(*) from vendor where store_name = ?",(storeName,)).fetchone())
        if(count[0] > 0):
            raise CustomerException.CustomException("Store name already existes. Please provide a diff storeName", 400)
        cur.execute("INSERT INTO vendor (customer_id, store_name) VALUES (?,?)",(customerId,storeName))
        if res[0] == 0:
            cur.execute("update customer set level=1 where id=?",(customerId,))
        con.commit()
        response = ("Vendor successfully added",200)

    except CustomerException.CustomException as e:
        print(e)
        con.rollback()
        return (e.getMessage(),e.getStatusCode())


    except Exception as e:
        print(e)
        con.rollback()
        return ("error while adding new Vendor", 400)

    else:
        return response

    finally:
        con.close()


def add_item(dish_name, item_name, vendor_id, store_id, available_quantity, unit_price):
    response = None
    """used for adding item in item table"""
    try:
        # Making a connection to SQLite db
        con = sql.connect(path)
        cur = con.cursor()
        # Executing a SQL query
        cur.execute("INSERT INTO item (dish_name, item_name, vendor_id, store_id, available_quantity, unit_price) VALUES (?,?,?,?,?,?)",
                    (dish_name, item_name, vendor_id, store_id, available_quantity, unit_price))
        con.commit()
        response = ("Item successfully added", 200)


    except Exception as e:
        print(e)
        con.rollback()
        return ("error while adding new item", 400)
    else:
        return response
    finally:
        con.close()


def search_item_by_name(item_name):
    """used for searching item by name"""
    try:
        # Making a connection to SQLite db
        con = sql.connect(path)
        cur = con.cursor()
        # Executing a SQL query
        cur.execute("select item.dish_name, item.item_name, item.vendor_id, item.store_id, item.available_quantity,"+
                    "item.unit_price, vendor.store_name, customer.name, customer.id from vendor vendor,item item, customer customer "+
                    " where item.vendor_id= vendor.id and vendor.customer_id= customer.id  and item.item_name= ?",
                    (item_name,))
        listrow = cur.fetchall();
        itemDetailsList = []
        for row in listrow:
            itemDetails = {}
            itemDetails["dish_name"] = row[0]
            itemDetails["item_name"] = row[1]
            itemDetails["vendor_id"] = row[2]
            itemDetails["store_id"] = row[3]
            itemDetails["available_quantity"] = row[4]
            itemDetails["unit_price"]=row[5]
            itemDetails["store_name"] = row[6]
            itemDetails["customer_name"] = row[7]
            itemDetails["customer_id"] = row[8]
            itemDetailsList.append(itemDetails)
        response = ({'response':{"itemDetails": itemDetailsList}},200)


    except Exception as e:
        print(e)
        return ("error while fetching item", 400)
    else:
        return response
    finally:
        con.close()

    return response

def place_order(customer_id, item_id, quantity):
    """used for placing order"""
    try:
        # Making a connection to SQLite db
        con = sql.connect(path)
        cur = con.cursor()

        # Executing a SQL query
        cur.execute(
            "INSERT INTO orders (customer_id, item_id, quantity) VALUES (?,?,?)",(customer_id, item_id, quantity))
        con.commit()


        response = ({'response':{"orderDetails": {"item_id":item_id,"quantity":quantity}}},200)


    except Exception as e:
        print(e)
        con.rollback()
        return ("error while placing order",400)
    else:
        return response

    finally:
        con.close()



def get_all_orders():
    """used to get list of all orders"""
    response = None
    try:
        # Making a connection to SQLite db
        con = sql.connect(path)
        cur = con.cursor()

        # Executing a SQL query
        cur.execute(" select item.dish_name, item.item_name, item.vendor_id, item.store_id, vendor.store_name, item.unit_price, orders.quantity, orders.quantity * item.unit_price as total_price,orders.customer_id from orders orders, vendor vendor, item item where item.id=orders.item_id and item.vendor_id=vendor.id")
        rows=cur.fetchall();
        orderDetailsList=[]
        for row in rows:
            orderDetails={}
            orderDetails["dish_name"]=row[0]
            orderDetails["item_name"]=row[1]
            orderDetails["vendor_id"]=row[2]
            orderDetails["store_id"]=row[3]
            orderDetails["store_name"]=row[4]
            orderDetails["unit_price"]=row[5]
            orderDetails["quantity"]=row[6]
            orderDetails["total_price"]=row[7]
            orderDetails["customer_id"]=row[8]
            orderDetailsList.append(orderDetails)
        response = ({'response':{"orderDetails": orderDetailsList}},200)

    except Exception as e:
        print(e)
        return ("error while fetching order details",400)
    else:
        return response
    finally:
        con.close()



def get_orders_by_customer(customerId):
    response = None
    """used for getting all the orders placed by given customer"""
    try:
        # Making a connection to SQLite db
        con = sql.connect(path)
        cur = con.cursor()

        # Executing a SQL query
        count =  (cur.execute("select count(*) from customer where id = ? ",(customerId,)).fetchone())
        if count[0]==0:
            raise CustomerException.CustomException("invalid customerId. Please input correct customer ID",400)
        cur.execute(" select item.dish_name, item.item_name, item.vendor_id, item.store_id, vendor.store_name, item.unit_price, orders.quantity, orders.quantity * item.unit_price as total_price,orders.customer_id from orders orders, vendor vendor, item item where item.id=orders.item_id and item.vendor_id=vendor.id and orders.customer_id=?",(customerId,))
        rows = cur.fetchall();
        orderDetailsList = []
        for row in rows:
            orderDetails = {}
            orderDetails["dish_name"] = row[0]
            orderDetails["item_name"] = row[1]
            orderDetails["vendor_id"] = row[2]
            orderDetails["store_id"] = row[3]
            orderDetails["store_name"] = row[4]
            orderDetails["unit_price"] = row[5]
            orderDetails["quantity"] = row[6]
            orderDetails["total_price"] = row[7]
            orderDetails["customer_id"] = row[8]
            orderDetailsList.append(orderDetails)
        response = ({'response':{"orderDetails": orderDetailsList}}, 200)

    except CustomerException.CustomException as e:
        print(e)
        return (e.getMessage(),e.getStatusCode())
    except Exception as e:
        print(e)
        ("error while fetching order details",400)
    else:
        return response

    finally:
        con.close()



def get_all_vendors():
    """used for getting list of all vendors and items they provide"""
    try:
        # Making a connection to SQLite db
        con = sql.connect(path)
        cur = con.cursor()

        # Executing a SQL query
        cur.execute(
            " select item.dish_name, item.item_name, item.vendor_id, item.store_id, vendor.store_name, item.unit_price, item.available_quantity from vendor vendor, item item where item.vendor_id=vendor.id ")
        rows = cur.fetchall();
        vendorDetailsList = []
        for row in rows:
            vendorDetails = {}
            vendorDetails["dish_name"] = row[0]
            vendorDetails["item_name"] = row[1]
            vendorDetails["vendor_id"] = row[2]
            vendorDetails["store_id"] = row[3]
            vendorDetails["store_name"] = row[4]
            vendorDetails["unit_price"] = row[5]
            vendorDetails["available_quantity"] = row[6]
            vendorDetailsList.append(vendorDetails)
        response = ({'response':{"vendorDetails": vendorDetailsList}},200)

    except Exception as e:
        print(e)
        return ("error while fetching vendor details", 400)
    else:
        return response
    finally:
        con.close()

