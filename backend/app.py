from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for

app = Flask(__name__, template_folder='../frontend/templates')

app.config['WTF_CSRF_ENABLED'] = False

# Set up the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define a simple model for the cards table
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character = db.Column(db.String(50), nullable=False)
    set_number = db.Column(db.String(50), nullable=False)
    set_name = db.Column(db.String(50), nullable=False)
    era = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    live_price = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    roi = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<Card {self.character}>"

with app.app_context():
    db.create_all()

@app.route('/show')
def show_cards():
    cards = Card.query.all()
    return render_template('show_cards.html', cards=cards)

@app.route('/add', methods=['GET', 'POST'])
def add_card():
    if request.method == 'POST':
        # Get form data
        character = request.form['character']
        set_number = request.form['set_number']
        set_name = request.form['set_name']
        era = request.form['era']
        grade = request.form['grade']
        live_price = float(request.form['live_price'])
        purchase_price = float(request.form['purchase_price'])
        roi = float(request.form['roi'])
        image_url = request.form['image_url']

        # Add card to database
        new_card = Card(
            character=character, 
            set_number=set_number, 
            set_name=set_name,
            era=era, 
            grade=grade, 
            live_price=live_price, 
            purchase_price=purchase_price,
            roi=roi, 
            image_url=image_url
        )
        db.session.add(new_card)
        db.session.commit()
        
        return "Card added successfully!"
    
    return render_template('add_card.html')


if __name__ == '__main__':
    app.run(debug=True)