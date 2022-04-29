from flask import Flask, render_template, request, url_for, redirect, abort, session
from flask_session import Session
import sqlite3
import os

app = Flask(__name__)
sess = Session()



def gen_custID():
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    cur.execute("UPDATE metadata SET custnum = custnum + 1")
    conn.commit()
    custnum = str([i for i in cur.execute("SELECT custnum FROM metadata")][0][0])
    conn.close()
    id = "CID"+"0"*(7-len(custnum))+custnum
    return id

def gen_sellID():
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    cur.execute("UPDATE metadata SET sellnum = sellnum + 1")
    conn.commit()
    sellnum = str([i for i in cur.execute("SELECT sellnum FROM metadata")][0][0])
    conn.close()
    id = "SID"+"0"*(7-len(sellnum))+sellnum
    return id

def gen_prodID():
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    cur.execute("UPDATE metadata SET prodnum = prodnum + 1")
    conn.commit()
    prodnum = str([i for i in cur.execute("SELECT prodnum FROM metadata")][0][0])
    conn.close()
    id = "PID"+"0"*(7-len(prodnum))+prodnum
    return id

def gen_orderID():
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    cur.execute("UPDATE metadata SET ordernum = ordernum + 1")
    conn.commit()
    ordernum = str([i for i in cur.execute("SELECT ordernum FROM metadata")][0][0])
    conn.close()
    id = "OID"+"0"*(7-len(ordernum))+ ordernum
    return id

def add_user(data):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    email = data["email"]
    if data['type']=="Customer":
        a = cur.execute("SELECT * FROM customer WHERE email=?", (email,))
    elif data['type']=="Seller":
        a = cur.execute("SELECT * FROM seller WHERE email=?", (email,))
    if len(list(a))!=0:
        return False
    tup = ( data["name"],
            data["email"],
            data["phone"],
            data["area"],
            data["locality"],
            data["city"],
            data["state"],
            data["country"],
            data["zip"],
            data["password"])
    if data['type']=="Customer":
        cur.execute("INSERT INTO customer VALUES (?,?,?,?,?,?,?,?,?,?,?)",(gen_custID(), *tup))
    elif data['type']=="Seller":
        cur.execute("INSERT INTO seller VALUES (?,?,?,?,?,?,?,?,?,?,?)", (gen_sellID(), *tup))
    conn.commit()
    conn.close()
    return True

def auth_user(data):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    type = data["type"]
    email = data["email"]
    password = data["password"]
    if type=="Customer":
        a = cur.execute("SELECT custID, name FROM customer WHERE email=? AND password=?", (email, password))
    elif type=="Seller":
        a = cur.execute("SELECT sellID, name FROM seller WHERE email=? AND password=?", (email, password))
    a = list(a)
    conn.close()
    if len(a)==0:
        return False
    return a[0]

def fetch_details(userid, type):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    if type=="Customer":
        a = cur.execute("SELECT * FROM customer WHERE custID=?", (userid,))
        a = list(a)
        b = []
    elif type=="Seller":
        a = cur.execute("SELECT * FROM seller WHERE sellID=?", (userid,))
        a = list(a)
        b = cur.execute("SELECT DISTINCT(category) from product WHERE sellID=?", (userid,))
        b = [i[0] for i in b ]
    conn.close()
    return a, b

def search_users(search, srch_type):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    search = "%"+search+"%"
    if srch_type=="Customer":
        res = cur.execute("SELECT custID, name, email, phone, area, locality, city, state, country, zipcode FROM customer WHERE LOWER(name) like ?", (search,))
    elif srch_type=="Seller":
        res = cur.execute("SELECT sellID, name, email, phone, area, locality, city, state, country, zipcode FROM seller WHERE LOWER(name) like ?", (search,))
    res = [i for i in res ]
    conn.close()
    return res

def update_details(data, userid, type):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    if type=="Customer":
        cur.execute("UPDATE customer SET phone=?, area=?, locality=?, city=?, state=?, country=?, zipcode=? where custID=?", (data["phone"],
                    data["area"],
                    data["locality"],
                    data["city"],
                    data["state"],
                    data["country"],
                    data["zip"],
                    userid))
    elif type=="Seller":
        cur.execute("UPDATE seller SET phone=?, area=?, locality=?, city=?, state=?, country=?, zipcode=? where sellID=?", (data["phone"],
                    data["area"],
                    data["locality"],
                    data["city"],
                    data["state"],
                    data["country"],
                    data["zip"],
                    userid))
    conn.commit()
    conn.close()

def check_psswd(psswd, userid, type):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    if type=="Customer":
        a = cur.execute("SELECT password FROM customer WHERE custID=?", (userid,))
    elif type=="Seller":
        a = cur.execute("SELECT password FROM seller WHERE sellID=?", (userid,))
    real_psswd = list(a)[0][0]
    conn.close()
    return psswd==real_psswd

def set_psswd(psswd, userid, type):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    if type=="Customer":
        a = cur.execute("UPDATE customer SET password=? WHERE custID=?", (psswd, userid))
    elif type=="Seller":
        a = cur.execute("UPDATE seller SET password=? WHERE sellID=?", (psswd, userid))
    conn.commit()
    conn.close()

def add_prod(sellID, data):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    prodID = gen_prodID()
    tup = (prodID,
           data["name"],
           data["qty"],
           data["category"],
           data["price"],
           data["price"],
           data["desp"],
           sellID)
    cur.execute("INSERT INTO product VALUES (?,?,?,?,?,(SELECT profit_rate from metadata)*?,?,?)", tup)
    conn.commit()
    conn.close()

def get_categories(sellID):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    a = cur.execute("SELECT DISTINCT(category) from product where sellID=?", (sellID,))
    categories = [i[0] for i in a]
    conn.close()
    return categories

def search_myproduct(sellID, srchBy, category, keyword):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    keyword = ['%'+i+'%' for i in keyword.split()]
    if len(keyword)==0: keyword.append('%%')
    if srchBy=="by category":
        a = cur.execute("""SELECT prodID, name, quantity, category, cost_price
                        FROM product WHERE category=? AND sellID=? """,(category, sellID))
        res = [i for i in a]
    elif srchBy=="by keyword":
        res = []
        for word in keyword:
            a = cur.execute("""SELECT prodID, name, quantity, category, cost_price
                            FROM product
                            WHERE (name LIKE ? OR description LIKE ? OR category LIKE ?) AND sellID=? """,
                            (word, word, word, sellID))
            res += list(a)
        res = list(set(res))
    elif srchBy=="both":
        res = []
        for word in keyword:
            a = cur.execute("""SELECT prodID, name, quantity, category, cost_price
                            FROM product
                            WHERE (name LIKE ? OR description LIKE ?) AND sellID=? AND category=? """,
                            (word, word, sellID, category))
            res += list(a)
        res = list(set(res))
    conn.close()
    return res

def get_product_info(id):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    a = cur.execute("""SELECT p.name, p.quantity, p.category, p.cost_price, p.sell_price,
                    p.sellID, p.description, s.name FROM product p JOIN seller s
                    WHERE p.sellID=s.sellID AND p.prodID=? """, (id,))
    res = [i for i in a]
    conn.close()
    if len(res)==0:
        return False, res
    return True, res[0]

def update_product(data, id):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    cur.execute("""UPDATE product
    SET name=?, quantity=?, category=?, cost_price=?,
    sell_price=(SELECT profit_rate from metadata)*?, description=?
    where prodID=?""",( data['name'],
                        data['qty'],
                        data['category'],
                        data['price'],
                        data['price'],
                        data['desp'],
                        id))
    conn.commit()
    conn.close()

def search_products(srchBy, category, keyword):
    conn = sqlite3.connect("OnlineShop/onlineshop.db")
    cur = conn.cursor()
    keyword = ['%'+i+'%' for i in keyword.split()]
    if len(keyword)==0: keyword.append('%%')
    if srchBy=="by category":
        a = cur.execute("""SELECT prodID, name, category, sell_price
                        FROM product WHERE category=? AND quantity!=0 """,(category,))
        res = [i for i in a]
    elif srchBy=="by keyword":
        res = []
        for word in keyword:
            a = cur.execute("""SELECT prodID, name, category, sell_price
                            FROM product
                            WHERE (name LIKE ? OR description LIKE ? OR category LIKE ?) AND quantity!=0 """,
                            (word, word, word))
            res += list(a)
        res = list(set(res))
    elif srchBy=="both":
        res = []
        for word in keyword:
            a = cur.execute("""SELECT prodID, name, category, sell_price
                            FROM product
                            WHERE (name LIKE ? OR description LIKE ?) AND quantity!=0 AND category=? """,
                            (word, word, category))
            res += list(a)
        res = list(set(res))
    conn.close()
    return res

def get_seller_products(sellID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    a = cur.execute("SELECT prodID, name, category, sell_price FROM product WHERE sellID=? AND quantity!=0", (sellID,))
    res = [i for i in a]
    conn.close()
    return res

def place_order(prodID, custID, qty):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    orderID = gen_orderID()
    cur.execute("""INSERT INTO orders
                    SELECT ?,?,?,?,datetime('now'), cost_price*?, sell_price*?, 'PLACED'
                    FROM product WHERE prodID=? """, (orderID, custID, prodID, qty, qty, qty, prodID))
    conn.commit()
    conn.close()

def cust_orders(custID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    a = cur.execute("""SELECT o.orderID, o.prodID, p.name, o.quantity, o.sell_price, o.date, o.status
                       FROM orders o JOIN product p
                       WHERE o.prodID=p.prodID AND o.custID=? AND o.status!='RECIEVED'
                       ORDER BY o.date DESC """, (custID,))
    res = [i for i in a]
    conn.close()
    return res

def sell_orders(sellID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    a = cur.execute(""" SELECT o.orderID, o.prodID, p.name, o.quantity, p.quantity, o.cost_price, o.date, o.status
                        FROM orders o JOIN product p
                        WHERE o.prodID=p.prodID AND p.sellID=? AND o.status!='RECIEVED'
                        ORDER BY o.date DESC """, (sellID,))
    res = [i for i in a]
    conn.close()
    return res

def get_order_details(orderID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    a = cur.execute(""" SELECT o.custID, p.sellID, o.status FROM orders o JOIN product p
                        WHERE o.orderID=? AND o.prodID=p.prodID """, (orderID,))
    res = [i for i in a]
    conn.close()
    return res

def change_order_status(orderID, new_status):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status=? WHERE orderID=? ", (new_status, orderID))
    if new_status=='DISPACHED':
        cur.execute("""UPDATE product SET
                     quantity=quantity-(SELECT quantity FROM orders WHERE orderID=? )
                     WHERE prodID=(SELECT prodID FROM orders WHERE orderID=? )""", (orderID, orderID))
    conn.commit()
    conn.close()

def cust_purchases(custID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    a = cur.execute("""SELECT o.prodID, p.name, o.quantity, o.sell_price, o.date
                       FROM orders o JOIN product p
                       WHERE o.prodID=p.prodID AND o.custID=? AND o.status='RECIEVED'
                       ORDER BY o.date DESC """, (custID,))
    res = [i for i in a]
    conn.close()
    return res

def sell_sales(sellID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    a = cur.execute("""SELECT o.prodID, p.name, o.quantity, o.sell_price, o.date, o.custID, c.name
                       FROM orders o JOIN product p JOIN customer c
                       WHERE o.prodID=p.prodID AND o.custID=c.custID AND p.sellID=? AND o.status='RECIEVED'
                       ORDER BY o.date DESC """, (sellID,))
    res = [i for i in a]
    conn.close()
    return res

def add_product_to_cart(prodID, custID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    cur.execute("""INSERT INTO cart VALUES (?,?,1) """, (custID, prodID))
    conn.commit()
    conn.close()

def get_cart(custID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    a = cur.execute("""SELECT p.prodID, p.name, p.sell_price, c.sum_qty, p.quantity
                       FROM (SELECT custID, prodID, SUM(quantity) AS sum_qty FROM cart
                       GROUP BY custID, prodID) c JOIN product p
                       WHERE p.prodID=c.prodID AND c.custID=?""", (custID,))
    res = [i for i in a]
    conn.close()
    return res

def update_cart(custID, qty):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    for prodID in qty:
        cur.execute("DELETE FROM cart WHERE prodID=? AND custID=?", (prodID, custID))
        cur.execute("INSERT INTO cart VALUES (?,?,?)", (custID, prodID, qty[prodID]))
    conn.commit()
    conn.close()

def cart_purchase(custID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    cart = get_cart(custID)
    for item in cart:
        orderID = gen_orderID()
        prodID = item[0]
        qty = item[3]
        cur.execute("""INSERT INTO orders
                        SELECT ?,?,?,?,datetime('now'), cost_price*?, sell_price*?, 'PLACED'
                        FROM product WHERE prodID=? """, (orderID, custID, prodID, qty, qty, qty, prodID))
        cur.execute("DELETE FROM cart WHERE custID=? AND prodID=?", (custID, prodID))
        conn.commit()
    conn.close()

def empty_cart(custID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE custID=?", (custID,))
    conn.commit()

def remove_from_cart(custID, prodID):
    conn = sqlite3.connect('OnlineShop/onlineshop.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE custID=? AND prodID=?", (custID, prodID))
    conn.commit()
    

@app.route("/")
def home():
    if "userid" in session:
        return render_template("home.html", signedin=True, id=session['userid'], name=session['name'], type=session['type'])
    return render_template("home.html", signedin=False)

@app.route("/signup/", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        data = request.form
        ok = add_user(data)
        if ok:
            return render_template("success_signup.html")
        return render_template("signup.html", ok=ok)
    return render_template("signup.html", ok=True)

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = request.form
        userdat = auth_user(data)
        if userdat:
            session["userid"] = userdat[0]
            session["name"] = userdat[1]
            session["type"] = data["type"]
            return redirect(url_for('home'))
        return render_template("login.html", err=True)
    return render_template("login.html", err=False)

@app.route("/logout/")
def logout():
    session.pop('userid')
    session.pop('name')
    session.pop('type')
    return redirect(url_for('home'))

@app.route("/viewprofile/<id>/")
def view_profile(id):
    if 'userid' not in session:
        return redirect(url_for('home'))
    userid = session["userid"]
    type = session["type"]
    my = True if userid==id else False
    if not my: profile_type = "Customer" if type=="Seller" else "Seller"
    else: profile_type = type

    det, categories = fetch_details(id, profile_type)   #details
    if len(det)==0:
        abort(404)
    det = det[0]
    return render_template("view_profile.html",
                            type=profile_type,
                            name=det[1],
                            email=det[2],
                            phone=det[3],
                            area=det[4],
                            locality=det[5],
                            city=det[6],
                            state=det[7],
                            country=det[8],
                            zip=det[9],
                            category=(None if profile_type=="Customer" else categories),
                            my=my)

@app.route("/viewprofile/", methods=["POST", "GET"])
def profile():
    if 'userid' not in session:
        return redirect(url_for('home'))
    type = "Seller" if session['type']=="Customer" else "Customer"
    if request.method=="POST":
        search = request.form['search']
        results = search_users(search, type)
        found = len(results)
        return render_template('profiles.html', id=session['userid'], type=type, after_srch=True, found=found, results=results)

    return render_template('profiles.html', id=session['userid'], type=type, after_srch=False)

@app.route("/viewprofile/<id>/sellerproducts/")
def seller_products(id):
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session["type"]=="Seller":
        abort(403)
    det, categories = fetch_details(id, "Seller")   #details
    if len(det)==0:
        abort(404)
    det = det[0]
    name=det[1]
    res = get_seller_products(id)
    return render_template('seller_products.html', name=name, id=id, results=res)

@app.route("/editprofile/", methods=["POST", "GET"])
def edit_profile():
    if 'userid' not in session:
        return redirect(url_for('home'))

    if request.method=="POST":
        data = request.form
        update_details(data, session['userid'], session['type'])
        return redirect(url_for('view_profile', id=session['userid']))

    if request.method=="GET":
        userid = session["userid"]
        type = session["type"]
        det, _ = fetch_details(userid, type)
        det = det[0]
        return render_template("edit_profile.html",
                                type=type,
                                name=det[1],
                                email=det[2],
                                phone=det[3],
                                area=det[4],
                                locality=det[5],
                                city=det[6],
                                state=det[7],
                                country=det[8],
                                zip=det[9])

@app.route("/changepassword/", methods=["POST", "GET"])
def change_password():
    if 'userid' not in session:
        return redirect(url_for('home'))
    check = True
    equal = True
    if request.method=="POST":
        userid = session["userid"]
        type = session["type"]
        old_psswd = request.form["old_psswd"]
        new_psswd = request.form["new_psswd"]
        cnfrm_psswd = request.form["cnfrm_psswd"]
        check = check_psswd(old_psswd, userid, type)
        if check:
            equal = (new_psswd == cnfrm_psswd)
            if equal:
                set_psswd(new_psswd, userid, type)
                return redirect(url_for('home'))
    return render_template("change_password.html", check=check, equal=equal)

@app.route("/sell/", methods=["POST", "GET"])
def my_products():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session["type"]=="Customer":
        abort(403)
    categories = get_categories(session["userid"])
    if request.method=="POST":
        data = request.form
        srchBy = data["search method"]
        category = None if srchBy=='by keyword' else data["category"]
        keyword = data["keyword"]
        results = search_myproduct(session['userid'], srchBy, category, keyword)
        return render_template('my_products.html', categories=categories, after_srch=True, results=results)
    return render_template("my_products.html", categories=categories, after_srch=False)

@app.route("/sell/addproducts/", methods=["POST", "GET"])
def add_products():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session["type"]=="Customer":
        abort(403)
    if request.method=="POST":
        data = request.form
        add_prod(session['userid'],data)
        return redirect(url_for('my_products'))
    return render_template("add_products.html")

@app.route("/viewproduct/")
def view_prod():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        return redirect(url_for('my_products'))
    if session['type']=="Customer":
        return redirect(url_for('buy'))

@app.route("/viewproduct/<id>/")
def view_product(id):
    if 'userid' not in session:
        return redirect(url_for('home'))
    type = session["type"]
    ispresent, tup = get_product_info(id)
    if not ispresent:
        abort(404)
    (name, quantity, category, cost_price, sell_price, sellID, desp, sell_name) = tup
    if type=="Seller" and sellID!=session['userid']:
        abort(403)
    return render_template('view_product.html', type=type, name=name, quantity=quantity, category=category, cost_price=cost_price, sell_price=sell_price, sell_id=sellID, sell_name=sell_name, desp=desp, prod_id=id)

@app.route("/viewproduct/<id>/edit/", methods=["POST", "GET"])
def edit_product(id):
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Customer":
        abort(403)
    ispresent, tup = get_product_info(id)
    if not ispresent:
        abort(404)
    (name, quantity, category, cost_price, sell_price, sellID, desp, sell_name) = tup
    if sellID!=session['userid']:
        abort(403)
    if request.method=="POST":
        data = request.form
        update_product(data, id)
        return redirect(url_for('view_product', id=id))
    return render_template('edit_product.html', prodID=id, name=name, qty=quantity, category=category, price=cost_price, desp=desp)

@app.route("/buy/", methods=["POST", "GET"])
def buy():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        abort(403)
    if request.method=="POST":
        data = request.form
        srchBy = data["search method"]
        category = None if srchBy=='by keyword' else data["category"]
        keyword = data["keyword"]
        results = search_products(srchBy, category, keyword)
        return render_template('search_products.html', after_srch=True, results=results)
    return render_template('search_products.html', after_srch=False)

@app.route("/buy/<id>/", methods=['POST', 'GET'])
def buy_product(id):
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        abort(403)
    ispresent, tup = get_product_info(id)
    if not ispresent:
        abort(404)
    (name, quantity, category, cost_price, sell_price, sellID, desp, sell_name) = tup
    if request.method=="POST":
        data = request.form
        total = int(data['qty'])*float(sell_price)
        return redirect(url_for('buy_confirm', total=total, quantity=data['qty'], id=id))
    return render_template('buy_product.html', name=name, category=category, desp=desp, quantity=quantity, price=sell_price)

@app.route("/buy/<id>/confirm/", methods=["POST", "GET"])
def buy_confirm(id):
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        abort(403)
    ispresent, tup = get_product_info(id)
    if not ispresent:
        abort(404)
    (name, quantity, category, cost_price, sell_price, sellID, desp, sell_name) = tup
    if 'total' not in request.args or 'quantity' not in request.args:
        abort(404)
    total = request.args['total']
    qty = request.args['quantity']
    if request.method=="POST":
        choice = request.form['choice']
        if choice=="PLACE ORDER":
            place_order(id, session['userid'], qty)
            return redirect(url_for('my_orders'))
        elif choice=="CANCEL":
            return redirect(url_for('buy_product', id=id))
    items = ((name, qty, total),)
    return render_template('buy_confirm.html', items=items, total=total)

@app.route("/buy/myorders/")
def my_orders():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        abort(403)
    res = cust_orders(session['userid'])
    return render_template('my_orders.html', orders=res)

@app.route("/cancel/<orderID>/")
def cancel_order(orderID):
    if 'userid' not in session:
        return redirect(url_for('home'))
    res = get_order_details(orderID)
    if len(res)==0:
        abort(404)
    custID = res[0][0]
    sellID = res[0][1]
    status = res[0][2]
    if session['type']=="Seller" and sellID!=session['userid']:
        abort(403)
    if session['type']=="Customer" and custID!=session['userid']:
        abort(403)
    if status!="PLACED":
        abort(404)
    change_order_status(orderID, "CANCELLED")
    return redirect(url_for('my_orders')) if session['type']=="Customer" else redirect(url_for('new_orders'))

@app.route("/dispatch/<orderID>/")
def dispatch_order(orderID):
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Customer":
        abort(403)
    res = get_order_details(orderID)
    if len(res)==0:
        abort(404)
    custID = res[0][0]
    sellID = res[0][1]
    status = res[0][2]
    if session['userid']!=sellID:
        abort(403)
    if status!="PLACED":
        abort(404)
    change_order_status(orderID, "DISPACHED")
    return redirect(url_for('new_orders'))

@app.route("/recieve/<orderID>/")
def recieve_order(orderID):
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        abort(403)
    res = get_order_details(orderID)
    if len(res)==0:
        abort(404)
    custID = res[0][0]
    sellID = res[0][1]
    status = res[0][2]
    if session['userid']!=custID:
        abort(403)
    if status!="DISPACHED":
        abort(404)
    change_order_status(orderID, "RECIEVED")
    return redirect(url_for('my_purchases'))

@app.route("/buy/purchases/")
def my_purchases():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        abort(403)
    res = cust_purchases(session['userid'])
    return render_template('my_purchases.html', purchases=res)

@app.route("/sell/neworders/")
def new_orders():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Customer":
        abort(403)
    res = sell_orders(session['userid'])
    return render_template('new_orders.html', orders=res)

@app.route("/sell/sales/")
def my_sales():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Customer":
        abort(403)
    res = sell_sales(session['userid'])
    return render_template('my_sales.html', sales=res)

@app.route("/buy/cart/", methods=["POST", "GET"])
def my_cart():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        abort(403)
    cart = get_cart(session['userid'])
    if request.method=="POST":
        data = request.form
        qty = {}
        for i in data:
            if i.startswith("qty"):
                qty[i[3:]]=data[i]      #qty[prodID]=quantity
        update_cart(session['userid'], qty)
        return redirect("/buy/cart/confirm/")
    return render_template('my_cart.html', cart=cart)

@app.route("/buy/cart/confirm/", methods=["POST", "GET"])
def cart_purchase_confirm():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        abort(403)
    if request.method=="POST":
        choice = request.form['choice']
        if choice=="PLACE ORDER":
            cart_purchase(session['userid'])
            return redirect(url_for('my_orders'))
        elif choice=="CANCEL":
            return redirect(url_for('my_cart'))
    cart = get_cart(session['userid'])
    items = [(i[1], i[3], float(i[2])*float(i[3])) for i in cart]
    total = 0
    for i in cart:
        total += float(i[2])*int(i[3])
    return render_template('buy_confirm.html', items=items, total=total)

@app.route("/buy/cart/<prodID>/")
def add_to_cart(prodID):
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['type']=="Seller":
        abort(403)
    add_product_to_cart(prodID, session['userid'])
    return redirect(url_for('view_product', id=prodID))

@app.route("/buy/cart/delete/")
def delete_cart():
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['userid']=="Seller":
        abort(403)
    empty_cart(session['userid'])
    return redirect(url_for('my_cart'))

@app.route("/buy/cart/delete/<prodID>/")
def delete_prod_cart(prodID):
    if 'userid' not in session:
        return redirect(url_for('home'))
    if session['userid']=="Seller":
        abort(403)
    remove_from_cart(session['userid'], prodID)
    return redirect(url_for('my_cart'))


app.config['SECRET_KEY'] = os.urandom(17)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TEMPLATES_AUTO_RELOAD'] = True
sess.init_app(app)
if __name__=="__main__":
	app.run(debug = True)
