from flask import Flask
import MySQLdb
from flask.ext.mysqldb import MySQL
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)

app.config.from_object(__name__)

#app.secret_key = 'd4rthV4d3rIsYourF4th3r'

mysql = MySQL(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '42926238'
app.config['MYSQL_DB'] = 'nelisa_spaza_shop'



@app.route('/')
def main():
    return render_template('main.html')

@app.route('/products')
def show_products():
	db = mysql.connection.cursor()
	db.execute('SELECT stock_item, SUM(no_sold) AS no_sold FROM sales_history GROUP BY stock_item ORDER BY no_sold DESC')
	entries = [dict(stock_item=row[0], no_sold=row[1]) for row in db.fetchall()]
	return render_template('popular_products.html',entries=entries,msg = "field cannot be blank")

@app.route('/category')
def show_categories():
	db = mysql.connection.cursor()
	db.execute('SELECT cat_name, SUM(no_sold) AS no_sold FROM sales_history INNER JOIN categories ON category_name=categories.cat_name GROUP BY cat_name ORDER BY no_sold DESC')
	entries = [dict(cat_name=row[0], no_sold=row[1]) for row in db.fetchall()]
	return render_template('category.html',entries=entries,msg = "field cannot be blank")

@app.route('/category_earnings')
def show_category_earnings():
	db = mysql.connection.cursor()
	db.execute('SELECT cat_name, SUM(earnings) AS earnings FROM (SELECT cat_name, no_sold*ROUND(AVG(price), 2) AS earnings FROM (SELECT cat_name, stock_item, price, SUM(no_sold) AS no_sold  FROM (SELECT category_name, stock_item, CAST(SUBSTRING(sales_price,2) AS DECIMAL(53,2)) AS price, no_sold FROM sales_history) AS prod_price INNER JOIN categories ON category_name=categories.cat_name GROUP BY stock_item, price) AS product_price GROUP BY stock_item, price) AS cat_earnings GROUP BY cat_name ORDER BY earnings DESC')
	entries = [dict(cat_name=row[0], earnings=row[1]) for row in db.fetchall()]
	return render_template('category_earnings.html',entries=entries,msg = "field cannot be blank")

@app.route('/entire_stock')
def show_entire_stock():
	db = mysql.connection.cursor()
	db.execute('SELECT item, SUM(quantity) as quantity FROM purchase_history GROUP BY item ORDER BY quantity DESC')
	entries = [dict(item=row[0], quantity=row[1]) for row in db.fetchall()]
	return render_template('entire_stock.html',entries=entries,msg = "field cannot be blank")

@app.route('/regular_sales')
def show_regular_sales():
	db = mysql.connection.cursor()
	db.execute('SELECT stock_item, SUM(CASE WHEN no_sold > 0 THEN 1 ELSE 0 END) AS frequency FROM sales_history GROUP BY stock_item ORDER by frequency DESC')
	entries = [dict(stock_item=row[0], frequency=row[1]) for row in db.fetchall()]
	return render_template('regular_sales.html',entries=entries,msg = "field cannot be blank")

@app.route('/all_suppliers', methods=['GET', 'POST'])
def show_all_suppliers():
	if request.method == 'POST' and (request.form['shop'] != ""):
    	#if(request.form['shop'] != ""):
    		db = mysql.connection.cursor()
    		db.execute('INSERT INTO suppliers SET shop = \"%s\" ' %(request.form['shop']))
    		mysql.connection.commit()
    		return redirect(url_for('show_all_suppliers'))
    	
	else:
    		db = mysql.connection.cursor()
        	db.execute('''SELECT * FROM suppliers''')
        	entries = [dict(shop=row[1]) for row in db.fetchall()]
        	return render_template('all_suppliers.html', entries=entries)


if __name__ == "__main__":
    app.run(debug=True,
	host="127.0.0.1",
    port=int("4000"))