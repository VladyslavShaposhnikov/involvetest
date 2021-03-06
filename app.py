import datetime
import os

from flask import Flask, render_template, request, redirect
from piastrixlib import PiastrixClient
import logging
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    dev_db = os.environ["dev_db"]
    app.config['SQLALCHEMY_DATABASE_URI'] = dev_db
else:
    app.debug = False
    prod_db = os.environ["prod_db"]
    app.config['SQLALCHEMY_DATABASE_URI'] = prod_db

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class PayInfo(db.Model):
    __tablename__ = 'payinfo'
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(3))
    amount = db.Column(db.Float())
    time = db.Column(db.DateTime, default=datetime.datetime.now())
    description = db.Column(db.Text(), default='')

    def __init__(self, currency, amount, time, description):
        self.currency = currency
        self.amount = amount
        self.time = time
        self.description = description

handler = logging.FileHandler("logging.log") 
app.logger.addHandler(handler)             
app.logger.setLevel(logging.DEBUG)        

@app.route('/', methods=['GET', 'POST'])
def index():
    secret_key = os.environ["secret_key"]
    shop_id = os.environ["shop_id"]
    piastrix = PiastrixClient(shop_id, secret_key)
    if request.method == "POST" and request.form.get('currency') == "978":
        amount = request.form.get('amount')
        currency = '978'
        db_currency = 'EUR'
        shop_order_id = '101'
        extra_fields = {
            'description' : request.form.get('description')
        }
        try:
            response = piastrix.pay(amount, currency, shop_order_id, extra_fields)
            print(response)
            app.logger.info("---\nRedirect to Piastrix servis.\nCurrency: EUR. Amount: {}\nTime: {}".format(amount, datetime.datetime.now()))
            data = PayInfo(currency=db_currency, amount=amount,time=datetime.datetime.now() , description=extra_fields['description'])
            db.session.add(data)
            db.session.commit()
            return render_template("eur.html", response=response)
        except:
            app.logger.error("---\nSomething has gone very wrong.\nCurrency: EUR. Amount: {}\nTime: {}".format(amount ,datetime.datetime.now()))
            return render_template("error.html")
    elif request.method == "POST" and request.form.get('currency') == "840":
        payer_currency = '840'
        db_currency = 'USD'
        shop_amount = request.form.get('amount')
        if shop_amount < '1':
            app.logger.error("---\nYou enter less than 1 USD.\nCurrency: USD. Amount: {}\nTime: {}".format(shop_amount, datetime.datetime.now()))
            return render_template("index.html", massage='You cant pay less than 1 USD') 
        shop_currency = '840'
        shop_order_id = '4239'
        extra_fields = {
            'description' : request.form.get('description')
        }
        try:
            response = piastrix.bill(payer_currency, shop_amount, shop_currency, shop_order_id, extra_fields)
            app.logger.info("---\nRedirect to Piastrix servis.\nCurrency: USD. Amount: {}\nTime: {}".format(shop_amount ,datetime.datetime.now()))
            data = PayInfo(currency=db_currency, amount=shop_amount,time=datetime.datetime.now() , description=extra_fields['description'])
            db.session.add(data)
            db.session.commit()
            return redirect(response['url'], code=302)
        except:
            app.logger.error("---\nSomething has gone very wrong.\nCurrency: USD. Amount: {}\nTime: {}".format(shop_amount, datetime.datetime.now()))
            return render_template("error.html")
    elif request.method == "POST" and request.form.get('currency') == "643":
        amount = request.form.get('amount')
        if amount < '1':
            app.logger.error("---\nYou enter less than 1 USD.\nCurrency: RUB. Amount: {}\nTime: {}".format(amount, datetime.datetime.now()))
            return render_template("index.html", massage='You cant pay less than 1 RUB') 
        currency = '643'
        db_currency = 'RUB'
        shop_order_id = '4126'
        payway = 'advcash_rub'
        extra_fields = {
            'description' : request.form.get('description')
        }
        try:
            response = piastrix.invoice(amount, currency, shop_order_id, payway, extra_fields)
            print(response)
            app.logger.info("---\nRedirect to Piastrix servis.\nCurrency: RUB. Amount: {}\nTime: {}".format(amount, datetime.datetime.now()))
            db_data = PayInfo(currency=db_currency, amount=amount,time=datetime.datetime.now(), description=extra_fields['description'])
            db.session.add(db_data)
            db.session.commit()
            return render_template("rub.html", response=response)
        except:
            app.logger.error("---\nSomething has gone very wrong.\nCurrency: RUB. Amount: {}\nTime: {}".format(amount, datetime.datetime.now()))
            return render_template("error.html")
    elif request.form.get('currency') == "0":
        app.logger.error("---\nField currency is empty.\nTime: {}".format(datetime.datetime.now()))
        return render_template("index.html", massage='Please choise currency') 
    return render_template("index.html") 


if __name__ == "__main__":
    app.run()
