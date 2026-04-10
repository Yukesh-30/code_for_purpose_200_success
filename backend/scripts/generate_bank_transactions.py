import pandas as pd
import random
from faker import Faker
from datetime import timedelta, datetime

fake = Faker('en_IN')

def generate_bank_transactions(num_rows=10000):
    # Pre-generate 50 businesses with traits
    businesses = []
    cities = ['Chennai', 'Bengaluru', 'Mumbai', 'Hyderabad', 'Delhi', 'Coimbatore']
    
    for i in range(1, 51):
        is_risky = random.choice([True, False, False, False]) # 25% risky
        city = random.choice(cities)
        businesses.append({
            'business_id': i,
            'account_id': f"ACC-{1000 + i}",
            'city': city,
            'branch': f"{city} {fake.city()} Branch",
            'is_risky': is_risky,
            'balance': random.uniform(100000, 500000) # Initial Balance
        })

    categories = {
        'credit': ['sales', 'refund'],
        'debit': ['rent', 'utilities', 'salary', 'inventory purchase', 'vendor payment', 'loan EMI', 'tax payment', 'fuel', 'internet', 'maintenance']
    }
    
    payment_modes = ['UPI', 'NEFT', 'RTGS', 'cash', 'cheque', 'card']
    
    data = []
    start_date = datetime.now() - timedelta(days=730) # 2 years
    
    # Sort businesses to ensure contiguous transactions if needed, but we'll just distribute
    # To maintain balance integrity, we'll generate transactions sequentially for each business
    # and then sort the final list by date.
    
    rows_per_business = num_rows // 50
    
    for bus in businesses:
        current_balance = bus['balance']
        current_date = start_date
        
        for j in range(rows_per_business):
            # Advance date (roughly daily)
            current_date += timedelta(days=random.randint(1, 3))
            if current_date > datetime.now(): break
            
            # Season detection
            month = current_date.month
            is_festival = month in [10, 11, 3, 4] # Diwali/Festival spikes
            quarter = f"Q{(month-1)//3 + 1}"
            season_label = f"{quarter} - {'Festival' if is_festival else 'Normal'}"
            
            # Transaction logic
            if bus['is_risky']:
                # Risky: more debits, smaller credits
                trans_type = random.choices(['credit', 'debit'], weights=[0.4, 0.6])[0]
            else:
                # Healthy: more credits or balanced
                trans_type = random.choices(['credit', 'debit'], weights=[0.55, 0.45])[0]
            
            category = random.choice(categories[trans_type])
            
            # Amount logic
            if category == 'sales':
                base_amount = random.uniform(20000, 150000)
                if is_festival: base_amount *= random.uniform(1.5, 3.0) # Spike
                amount = round(base_amount, 2)
            elif category == 'rent':
                amount = round(random.uniform(20000, 50000), 2)
            elif category == 'salary':
                amount = round(random.uniform(50000, 200000), 2)
            else:
                amount = round(random.uniform(500, 30000), 2)
            
            # Update balance
            if trans_type == 'credit':
                current_balance += amount
            else:
                # If balance is too low, risky businesses might still spend (simulating overdraft)
                if current_balance < amount and not bus['is_risky']:
                     amount = round(current_balance * 0.1, 2) # Limit spending for healthy
                current_balance -= amount
            
            data.append({
                'transaction_id': f"TXN-{100000 + len(data)}",
                'business_id': bus['business_id'],
                'account_id': bus['account_id'],
                'transaction_date': current_date.date(),
                'amount': amount,
                'transaction_type': trans_type,
                'category': category,
                'merchant_name': fake.company() if trans_type == 'debit' else 'Customer Receipt',
                'payment_mode': random.choice(payment_modes),
                'balance_after_transaction': round(current_balance, 2),
                'city': bus['city'],
                'branch': bus['branch'],
                'season': season_label,
                'description': f"{category.capitalize()} transaction via {random.choice(payment_modes)}"
            })

    # Sort by date for chronological realism
    df = pd.DataFrame(data)
    df = df.sort_values(by='transaction_date')
    
    # Trim to exactly num_rows if needed
    df = df.head(num_rows)
    
    output_path = 'datasets/bank_transactions_10k.csv'
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} rows in {output_path}")

if __name__ == "__main__":
    generate_bank_transactions()
