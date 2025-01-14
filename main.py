from flask import Flask, render_template, request, redirect, g
import pymysql
import pymysql.cursors
import flask_login
from dynaconf import Dynaconf 
from argon2 import PasswordHasher


settings = Dynaconf(
    settings_file = ('settings.toml')
)

app = Flask(__name__)
app.secret_key = settings.app_key
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True

    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def get_id(self):
        return str(self.id)

def connect_db():
    return pymysql.connect(
        host="192.168.1.173",
        port = 3417,
        user= settings.db_user,
        password = str(settings.db_pass),
        database=settings.db_name,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def get_db():
    '''Opens a new database connection per request.'''        
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

@app.teardown_appcontext
def close_db(error):
    '''Closes the database connection at the end of request.'''    
    if hasattr(g, 'db'):
        g.db.close()

@login_manager.user_loader
def load_user(user_id):
    cursor = get_db().cursor()
    cursor.execute(f"SELECT * FROM `users` WHERE `id` = {user_id}")
    result = cursor.fetchone()
    cursor.close()
    get_db().commit()

    if result is None:
        return None
    
    return User(result["id"], result["username"], result["email"])

@app.route('/home', methods=['GET', 'POST'])
def restaurant_list():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM `restaurant`")
    restaurant_results = cursor.fetchone()
    cursor.execute("SELECT * FROM `restaurant`")
    results = cursor.fetchall()
    cursor.close()
    return render_template("index.jinja", restaurant_data = restaurant_results, restaurants = results)

@app.route('/')
def landing ():
    return render_template ('landing.jinja')


@app.route('/restaurant/<restaurant_id>', methods=['GET', 'POST'])
def restaurant(restaurant_id):
    cursor = get_db().cursor()
    cursor.execute(f"SELECT * FROM `restaurant` WHERE `restaurant_id` = {restaurant_id}")
    restaurant_results = cursor.fetchone()
    cursor.execute(f"SELECT * FROM `menu_categories` WHERE `restaurant_id` = {restaurant_id}")
    category_results = cursor.fetchall()
    cursor.execute(f"""
        SELECT * FROM `items` 
        INNER JOIN `price` ON `items`.item_id = `price`.item_id
        INNER JOIN `delivery_services` ON `price`.service_id = `delivery_services`.service_id
        INNER JOIN `menu_categories` on `items`.category_id = `menu_categories`.category_id
        WHERE `items`.`restaurant_id` = {restaurant_id}
        ORDER BY `items`.`category_id`
    """)
    
    itemprice_results = cursor.fetchall()

    # return itemprice_results
    return render_template("restaurant.jinja", restaurant_data = restaurant_results, category_data = category_results, itemprice = itemprice_results)

ph = PasswordHasher()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        new_email = request.form['new_email']
        hashed_password = ph.hash(new_password)
        # hashed_email = ph.hash(new_email)
        # hashed_username = ph.hash(new_username)
        conn = connect_db()  # Call the connect_db function here
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO `users` (`username`, `password`, `email`) VALUES (%s, %s, %s)',
        (new_username, hashed_password, new_email))
        cursor.close()
        conn.close()
        get_db().commit()
        return redirect('/login')
    return render_template('signup.jinja')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = get_db().cursor()
        cursor.execute(f'SELECT * FROM `users` WHERE username=%s', (username,))
        result = cursor.fetchone()
        cursor.close()

        try:
            if result and ph.verify(result['password'], password):
                user = load_user(result['id'])
                flask_login.login_user(user)
                return redirect('/home')
            else:
                # Incorrect username or password
                return render_template('login.html', error='Invalid username or password')
        except:
            pass
        # This part only works if no encryption is used. KEEP COMMENTED
        #    if password == result['password']:
        #         user = load_user(result['id'])
        #         flask_login.login_user(user)
        #         return redirect('/home')
    return render_template('login.jinja')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect('/')

@app.route('/cart')
def cart():
    return render_template('cart.jinja')