from flask import Flask,request
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager,jwt_required,create_access_token,get_jwt_identity
from flask_mail import Mail,Message  
import os  

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///planets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
# app.config['FLASK_SECRET KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9."

app.config["JWT_SECRET_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9."
# app.config["MAIL_SERVER"] = 'smtp.mailtrap.io'
# app.config["MAIL_USERNAME"] = os.environ['MAIL_USERNAME']
# app.config["MAIL_PASSWORD"] = os.environ['MAIL_PASSWORD']

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'f3f70804fe1f15'
app.config['MAIL_PASSWORD'] = '843cd5003257fc'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
ma = Marshmallow(db)
jwt = JWTManager(app)
mail = Mail(app)

@app.cli.command("db_create")
def db_create():
    db.create_all()
    print("database created!")

@app.cli.command("db_drop")
def db_drop():
    db.drop_all()
    print("database droped!")

@app.cli.command("db_seed")
def db_seed():
    Mercury=Planet(planet_name='Mercury',
                  planet_type='Class D',
                  home_star='Sun',
                  mass=3.258e23,
                  radius=1516,
                  distance=35.98e6  )
    Venus=Planet( planet_name='Venus',
                  planet_type='Class K',
                  home_star='Sun',
                  mass=4.867e24,
                  radius=3760,
                  distance=66.24e6  )
    Earth=Planet( planet_name='Earth',
                  planet_type='Class M',
                  home_star='Sun',
                  mass=5.972e24,
                  radius=3959,
                  distance=92.96e6  )
    db.session.add(Mercury)
    db.session.add(Venus)
    db.session.add(Earth)

    test_user=User(first_name="Gaurav",
                    last_name="Pingale",
                    email="gp@gmail.com",
                    password="123")
    db.session.add(test_user)
    db.session.commit()
    print("database seeded")

@app.route("/")
def hello():
    return "hello",200

@app.route("/parameters")
def parameters():
    name = request.args.get("name")
    age = int(request.args.get("age"))
    if age < 18:
        return jsonify(message=f"Sorry {name} , You are not allowed"),401
    else:
        return jsonify(message=f"Welcome {name} , You are allowed"),200


@app.route("/url_var/<string:name>/<int:age>")
def url_var(name: str, age: int):
    if age < 18:
        return jsonify(message=f"Sorry {name} , You are not allowed"),401
    else:
        return jsonify(message=f"Welcome {name} , You are allowed"),200


@app.route("/planets",methods=["GET"])
@jwt_required()
def planets():
    logged_user = get_jwt_identity()
    print(logged_user)
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)

@app.route("/planet_details/<int:planet_id>",methods=['GET'])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message="That planet does not exist"), 404


@app.route("/add_planet",methods=['POST'])
@jwt_required()
def add_planet():
    
    planet_name = request.form["planet_name"]
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify(message="There is already a planet by that name"),409
    else:
        planet_type = request.form["planet_type"]
        home_star = request.form["home_star"]
        mass = float(request.form["mass"])
        radius = float(request.form["radius"])
        distance = float(request.form["distance"])
        new_planet = Planet(planet_name=planet_name,planet_type=planet_type,home_star=home_star,mass=mass,radius=radius,distance=distance)
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message="New planet added"),201

@app.route("/update_planet",methods=['PUT'])
@jwt_required()
def update_planet():
    planet_id = request.form["planet_id"]
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet: 
        planet.planet_name = request.form["planet_name"] 
        planet.planet_type = request.form["planet_type"]
        planet.home_star = request.form["home_star"]
        planet.mass = float(request.form["mass"])
        planet.radius = float(request.form["radius"])
        planet.distance = float(request.form["distance"])
        db.session.commit()
        return jsonify(message="Planet Updated"),202
    else:
        return jsonify(message="There is no planet with given id"),404


@app.route("/remove_planet/<int:planet_id>",methods=['DELETE'])
@jwt_required()
def remove_planet(planet_id):
    
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message="Planet removed"),202
    else:
        return jsonify(message="There is no planet with given id"),404

        
@app.route("/register",methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message ="This emial address already exists."),409
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = request.form["password"]
        user = User(first_name=first_name,last_name=last_name,email=email,password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="user created successfully"),201


@app.route("/login",methods=['POST'])
def login():
    
    if request.is_json:
        email=request.json['email']
        password=request.json['password']
    else:
        email = request.form["email"]
        password = request.form["password"]
    
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeeded!",access_token=access_token )
    else:
        return jsonify(message="Login failed!" ),401


@app.route("/retrive_password/<string:email>",methods=['GET'])
def retrive_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("Your Planetary API password is "+user.password,
                sender="admin@planetary-api.com",
                recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to "+email)
    else:
        return jsonify(message="the email doesn't exists"),401


# database model
class User(db.Model):
    __tablename__= 'users'
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(100), nullable=False)
    last_name=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100), nullable=False)

class Planet(db.Model):
    __tablename__= 'planets'
    planet_id=db.Column(db.Integer, primary_key=True)
    planet_name=db.Column(db.String(100), nullable=False)
    planet_type=db.Column(db.String(100), nullable=False)
    home_star=db.Column(db.String(100),nullable=False)
    mass=db.Column(db.Float, nullable=False)
    radius=db.Column(db.Float, nullable=False)
    distance=db.Column(db.Float, nullable=False)

class UserSchema(ma.Schema):
    class Meta:
        fields=("id","first_name","last_name","email","password")
    
class PlanetSchema(ma.Schema):
    class Meta:
        fields=("planet_id","planet_name","planet_type","home_star","mass","radius","distance")
    

user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__== "__main__":
    app.run(debug=True)
