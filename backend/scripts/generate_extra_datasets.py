import pandas as pd
import random
from faker import Faker
from datetime import timedelta, datetime

fake = Faker('en_IN')

# Shared consistency
business_ids = list(range(1, 51))
start_date = datetime.now() - timedelta(days=730)

def generate_expenses(num_rows=3000):
    data = []
    categories = ['rent', 'electricity', 'internet', 'fuel', 'maintenance', 'software', 'employee welfare', 'raw materials', 'transportation', 'warehouse', 'tax']
    importance_levels = ['low', 'medium', 'high', 'critical']
    frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
    
    for i in range(1, num_rows + 1):
        bus_id = random.choice(business_ids)
        cat = random.choice(categories)
        is_recurring = random.choice([True, False])
        freq = random.choice(frequencies) if is_recurring else None
        
        # Amount logic
        amount = round(random.uniform(500, 50000), 2)
        if cat in ['rent', 'warehouse', 'raw materials']:
            amount = round(random.uniform(50000, 500000), 2)
        
        date = fake.date_between(start_date='-2y', end_date='today')
        # Simulate high expense months (random spike)
        if date.month in [3, 9]: # March/Sept spikes
             amount *= random.uniform(1.2, 1.8)

        data.append({
            'expense_id': i,
            'business_id': bus_id,
            'expense_name': f"{cat.capitalize()} Payment",
            'expense_category': cat,
            'amount': round(amount, 2),
            'expense_date': date,
            'recurring': is_recurring,
            'frequency': freq,
            'supplier_name': fake.company(),
            'importance': random.choice(importance_levels)
        })
    
    pd.DataFrame(data).to_csv('datasets/expenses_3k.csv', index=False)
    print("Generated datasets/expenses_3k.csv")

def generate_payroll(num_rows=2000):
    data = []
    departments = ['sales', 'HR', 'operations', 'finance', 'warehouse', 'manufacturing', 'support']
    
    # Pre-define business size for consistency
    bus_sizes = {bid: random.randint(5, 500) for bid in business_ids}
    
    for i in range(1, num_rows + 1):
        bus_id = random.choice(business_ids)
        dept = random.choice(departments)
        emp_count = bus_sizes[bus_id]
        
        # Monthly records logic
        date = fake.date_between(start_date='-2y', end_date='today')
        
        base_salary = emp_count * random.uniform(20000, 35000)
        overtime = 0
        if dept in ['manufacturing', 'warehouse', 'operations']:
            overtime = base_salary * random.uniform(0.05, 0.15)
            
        bonus = 0
        if date.month in [10, 11]: # Festival bonus
            bonus = base_salary * random.uniform(0.1, 0.25)
            
        data.append({
            'payroll_id': i,
            'business_id': bus_id,
            'payroll_date': date.replace(day=1), # Start of month
            'employee_count': emp_count,
            'salary_amount': round(base_salary, 2),
            'department': dept,
            'overtime_cost': round(overtime, 2),
            'bonus_amount': round(bonus, 2)
        })
        
    pd.DataFrame(data).to_csv('datasets/payroll_2k.csv', index=False)
    print("Generated datasets/payroll_2k.csv")

def generate_vendor_payments(num_rows=3000):
    data = []
    categories = ['raw materials', 'logistics', 'packaging', 'machinery', 'electricity', 'internet', 'software', 'maintenance']
    
    # Pre-define some late-paying businesses
    late_businesses = random.sample(business_ids, 10)
    
    for i in range(1, num_rows + 1):
        bus_id = random.choice(business_ids)
        due_date = fake.date_between(start_date='-2y', end_date='today')
        status = random.choice(['paid', 'pending', 'overdue'])
        
        delay = 0
        payment_date = None
        
        if status == 'paid':
            if bus_id in late_businesses:
                delay = random.randint(10, 60)
                payment_date = due_date + timedelta(days=delay)
            else:
                is_late = random.choice([True, False, False, False])
                if is_late:
                    delay = random.randint(1, 15)
                    payment_date = due_date + timedelta(days=delay)
                else:
                    payment_date = due_date - timedelta(days=random.randint(0, 5))
                    
        elif status == 'overdue':
            delay = random.randint(1, 60)
            
        data.append({
            'vendor_payment_id': i,
            'business_id': bus_id,
            'vendor_name': fake.company(),
            'payment_amount': round(random.uniform(5000, 1000000), 2),
            'due_date': due_date,
            'payment_date': payment_date,
            'delay_days': delay,
            'criticality_level': random.choice(['low', 'medium', 'high', 'critical']),
            'vendor_category': random.choice(categories),
            'payment_status': status
        })
        
    pd.DataFrame(data).to_csv('datasets/vendor_payments_3k.csv', index=False)
    print("Generated datasets/vendor_payments_3k.csv")

def generate_loans(num_rows=2000):
    data = []
    loan_types = ['working capital loan', 'machinery loan', 'overdraft', 'invoice financing', 'business expansion loan', 'vehicle loan']
    lenders = ['HDFC Bank', 'ICICI Bank', 'Axis Bank', 'SBI', 'Kotak', 'NBFC']
    
    for i in range(1, num_rows + 1):
        bus_id = random.choice(business_ids)
        loan_amount = random.uniform(500000, 10000000)
        interest_rate = round(random.uniform(7, 20), 2)
        
        # Simple EMI logic
        emi = (loan_amount * (interest_rate/100/12)) + (loan_amount / 36) # Approx 36 month term
        
        missed = random.choices([0, 1, 2, 5, 8, 10], weights=[70, 10, 10, 5, 3, 2])[0]
        status = 'overdue' if missed > 2 else 'active'
        
        outstanding = loan_amount * random.uniform(0.1, 0.9)
        
        data.append({
            'loan_id': i,
            'business_id': bus_id,
            'lender_name': random.choice(lenders),
            'loan_type': random.choice(loan_types),
            'loan_amount': round(loan_amount, 2),
            'emi_amount': round(emi, 2),
            'due_date': fake.date_between(start_date='-1y', end_date='+1y'),
            'interest_rate': interest_rate,
            'outstanding_amount': round(outstanding, 2),
            'missed_payment_count': missed,
            'loan_status': status
        })
        
    pd.DataFrame(data).to_csv('datasets/loans_2k.csv', index=False)
    print("Generated datasets/loans_2k.csv")

if __name__ == "__main__":
    generate_expenses()
    generate_payroll()
    generate_vendor_payments()
    generate_loans()
