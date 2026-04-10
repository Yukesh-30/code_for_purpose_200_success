import pandas as pd
import random
from faker import Faker
from datetime import timedelta, datetime

fake = Faker('en_IN')

# Shared consistency
business_ids = list(range(1, 51))

def generate_recommendations(num_rows=2000):
    data = []
    products = ['invoice financing', 'overdraft facility', 'supply chain finance', 'machinery loan', 'inventory financing', 'business expansion loan']
    
    for i in range(1, num_rows + 1):
        bus_id = random.choice(business_ids)
        
        # Scenario generation
        delayed_inv = random.choices([0, 1, 3, 7, 12], weights=[40, 30, 15, 10, 5])[0]
        overdraft_prob = random.uniform(0.1, 0.9)
        cash_gap = random.uniform(0, 500000)
        
        # Logical mapping
        if delayed_inv >= 3:
            rec_prod = 'invoice financing'
            conf = random.randint(75, 100)
        elif overdraft_prob > 0.6:
            rec_prod = 'overdraft facility'
            conf = random.randint(70, 95)
        elif cash_gap > 300000:
            rec_prod = 'business expansion loan'
            conf = random.randint(60, 90)
        else:
            rec_prod = random.choice(products)
            conf = random.randint(50, 80)
            
        data.append({
            'business_id': bus_id,
            'cash_gap': round(cash_gap, 2),
            'delayed_invoice_count': delayed_inv,
            'overdraft_probability': round(overdraft_prob, 2),
            'vendor_risk': round(random.uniform(0.1, 0.8), 2),
            'recommended_product': rec_prod,
            'confidence_score': conf
        })
        
    pd.DataFrame(data).to_csv('datasets/recommendations_2k.csv', index=False)
    print("Generated datasets/recommendations_2k.csv")

def generate_risk_scores(num_rows=3000):
    data = []
    bands = ['safe', 'moderate', 'high', 'critical']
    
    for i in range(1, num_rows + 1):
        bus_id = random.choice(business_ids)
        
        # Decide band first for correlation
        band = random.choices(bands, weights=[40, 30, 20, 10])[0]
        
        if band == 'safe':
            liq = random.randint(70, 100)
            ovr = random.randint(0, 30)
            default = random.randint(0, 25)
        elif band == 'moderate':
            liq = random.randint(50, 75)
            ovr = random.randint(30, 60)
            default = random.randint(25, 50)
        elif band == 'high':
            liq = random.randint(20, 50)
            ovr = random.randint(60, 85)
            default = random.randint(50, 80)
        else: # critical
            liq = random.randint(0, 30)
            ovr = random.randint(80, 100)
            default = random.randint(80, 100)
            
        data.append({
            'business_id': bus_id,
            'forecast_date': fake.date_between(start_date='today', end_date='+60d'),
            'liquidity_score': liq,
            'default_risk_score': default,
            'overdraft_risk_score': ovr,
            'working_capital_score': random.randint(10, 90),
            'invoice_risk_score': random.randint(10, 90),
            'vendor_risk_score': random.randint(10, 90),
            'overall_risk_band': band
        })
        
    pd.DataFrame(data).to_csv('datasets/risk_scores_3k.csv', index=False)
    print("Generated datasets/risk_scores_3k.csv")

if __name__ == "__main__":
    generate_recommendations()
    generate_risk_scores()
