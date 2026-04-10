import pandas as pd
import random
from faker import Faker
from datetime import timedelta, datetime

fake = Faker('en_IN') # Using Indian locale for realistic names

def generate_invoice_dataset(num_rows=10000):
    data = []
    
    # Pre-generate some customers to ensure behavioral consistency
    customers = []
    for i in range(1, 501):
        behavior = random.choice(['prompt', 'late', 'variable'])
        risk = 'low' if behavior == 'prompt' else ('high' if behavior == 'late' else 'medium')
        customers.append({
            'customer_id': i,
            'name': fake.company(),
            'location': fake.city(),
            'type': random.choice(['retailer', 'wholesaler', 'distributor', 'corporate', 'local shop']),
            'behavior': behavior,
            'risk_score': risk
        })

    for i in range(1, num_rows + 1):
        customer = random.choice(customers)
        business_id = random.randint(1, 50)
        
        # Dates
        invoice_date = fake.date_between(start_date='-1y', end_date='today')
        payment_terms_val = random.choice([15, 30, 45, 60])
        payment_terms = f"Net {payment_terms_val}"
        due_date = invoice_date + timedelta(days=payment_terms_val)
        
        # Amount
        amount = round(random.uniform(1000, 1000000), 2)
        
        # Logic for status and actual payment date based on behavior
        status = random.choice(['paid', 'pending', 'overdue'])
        
        actual_payment_date = None
        delay_days = 0
        
        if status == 'paid':
            if customer['behavior'] == 'prompt':
                # Paid on or before due date
                actual_payment_date = invoice_date + timedelta(days=random.randint(0, payment_terms_val))
                delay_days = 0
            elif customer['behavior'] == 'late':
                # Always late
                delay_days = random.randint(1, 90)
                actual_payment_date = due_date + timedelta(days=delay_days)
            else:
                # Variable
                is_late = random.choice([True, False])
                if is_late:
                    delay_days = random.randint(1, 45)
                    actual_payment_date = due_date + timedelta(days=delay_days)
                else:
                    actual_payment_date = invoice_date + timedelta(days=random.randint(0, payment_terms_val))
                    delay_days = 0
        elif status == 'overdue':
            # Not paid yet, and due date has passed
            delay_days = (datetime.now().date() - due_date).days
            if delay_days < 0: delay_days = random.randint(1, 30) # Force some delay for testing
        else: # pending
            delay_days = 0

        data.append({
            'invoice_id': i,
            'business_id': business_id,
            'customer_id': customer['customer_id'],
            'invoice_number': f"INV-{10000 + i}",
            'customer_name': customer['name'],
            'invoice_amount': amount,
            'invoice_date': invoice_date,
            'due_date': due_date,
            'actual_payment_date': actual_payment_date,
            'delay_days': max(0, delay_days),
            'invoice_status': status,
            'customer_location': customer['location'],
            'customer_type': customer['type'],
            'payment_terms': payment_terms,
            'customer_risk_score': customer['risk_score'],
            'invoice_category': random.choice(['raw materials', 'wholesale order', 'retail order', 'export order'])
        })

    df = pd.DataFrame(data)
    df.to_csv('datasets/invoices_10k.csv', index=False)
    print(f"Successfully generated {num_rows} rows in datasets/invoices_10k.csv")

if __name__ == "__main__":
    generate_invoice_dataset()
