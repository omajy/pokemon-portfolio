from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for
from sqlalchemy import func
from collections import defaultdict

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

def calculate_portfolio_stats():
    """Calculate various statistics about the card portfolio"""
    cards = Card.query.all()
    stats = {}
    
    if not cards:
        return {
            'total_value': 0,
            'total_cost': 0,
            'total_roi': 0,
            'total_cards': 0,
            'highest_roi_card': None,
            'highest_value_card': None,
            'top_characters': [],
            'character_stats': {}
        }
    
    # Total statistics
    total_live_value = sum(card.live_price for card in cards)
    total_purchase_cost = sum(card.purchase_price for card in cards)
    # Use the correct ROI formula: ((live_price - purchase_price) / purchase_price) * 100
    overall_roi = ((total_live_value - total_purchase_cost) / total_purchase_cost * 100) if total_purchase_cost > 0 else 0
    
    # Find highest ROI and value cards
    highest_roi_card = max(cards, key=lambda card: card.roi)
    highest_value_card = max(cards, key=lambda card: card.live_price)
    
    # Character statistics
    character_data = defaultdict(lambda: {
        'count': 0, 
        'total_value': 0, 
        'total_cost': 0,
        'roi': 0,
        'avg_grade': 0
    })
    
    for card in cards:
        character_data[card.character]['count'] += 1
        character_data[card.character]['total_value'] += card.live_price
        character_data[card.character]['total_cost'] += card.purchase_price
        character_data[card.character]['avg_grade'] += float(card.grade)
    
    # Calculate averages and ROI for each character
    for character, data in character_data.items():
        data['avg_grade'] = round(data['avg_grade'] / data['count'], 1)
        # Using the correct ROI formula: ((total_value - total_cost) / total_cost) * 100
        data['roi'] = round(((data['total_value'] - data['total_cost']) / data['total_cost'] * 100), 2) if data['total_cost'] > 0 else 0
    
    # Find top 3 characters by ROI with at least 1 card
    top_characters = sorted(
        [(char, data) for char, data in character_data.items()],
        key=lambda x: x[1]['roi'],
        reverse=True
    )[:3]
    
    stats = {
        'total_value': round(total_live_value, 2),
        'total_cost': round(total_purchase_cost, 2),
        'total_roi': round(overall_roi, 2),
        'total_cards': len(cards),
        'highest_roi_card': highest_roi_card,
        'highest_value_card': highest_value_card,
        'top_characters': top_characters,
        'character_stats': character_data
    }
    
    return stats

@app.route('/')
def show_cards():
    cards = Card.query.all()
    stats = calculate_portfolio_stats()
    return render_template('show_cards.html', cards=cards, stats=stats)

@app.route('/add', methods=['GET', 'POST'])
def add_card():
    if request.method == 'POST':
        # Get form data
        character = request.form['character']
        set_number = request.form['set_number']
        set_name = request.form['set_name']
        era = request.form['era']
        grade = request.form['grade']
        purchase_price = float(request.form['purchase_price'])  # Get purchase price from form

        # Calculate live price and ROI (placeholders for now)
        live_price = purchase_price * 1.2  # Placeholder live price calculation
        # Use the correct ROI formula: ((live_price - purchase_price) / purchase_price) * 100
        roi = round(((live_price - purchase_price) / purchase_price) * 100, 2)   # Calculate ROI
        image_url = f"https://img.pokemondb.net/artwork/large/{character.lower()}.jpg"  # Placeholder image URL

        # Add card to the database
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

        return redirect(url_for('show_cards'))
    
    return render_template('add_card.html')

@app.route('/delete/<int:card_id>', methods=['POST'])
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('show_cards'))

if __name__ == '__main__':
    app.run(debug=True)