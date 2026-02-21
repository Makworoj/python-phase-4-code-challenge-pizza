#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI",
    f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# ===============================
# GET /restaurants
# ===============================
class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [
            r.to_dict(rules=("-restaurant_pizzas",))
            for r in restaurants
        ], 200


# ===============================
# GET & DELETE /restaurants/<int:id>
# ===============================
class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)

        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        return restaurant.to_dict(), 200

    def delete(self, id):
        restaurant = Restaurant.query.get(id)

        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()

        return {}, 204


# ===============================
# GET /pizzas
# ===============================
class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [
            p.to_dict(rules=("-restaurant_pizzas",))
            for p in pizzas
        ], 200


# ===============================
# POST /restaurant_pizzas
# ===============================
class RestaurantPizzaList(Resource):
    def post(self):
        data = request.get_json()

        try:
            new_rp = RestaurantPizza(
                price=data["price"],
                restaurant_id=data["restaurant_id"],
                pizza_id=data["pizza_id"],
            )

            db.session.add(new_rp)
            db.session.commit()

            return new_rp.to_dict(), 201

        except ValueError:
            # IMPORTANT: must match test expectation exactly
            return {"errors": ["validation errors"]}, 400


# ===============================
# Register Resources
# ===============================
api.add_resource(RestaurantList, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")
api.add_resource(PizzaList, "/pizzas")
api.add_resource(RestaurantPizzaList, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)

