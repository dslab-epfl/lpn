import random
import time
def generate_scalar_field(repeated, budget):
    cost = 0
    if repeated:
        n = random.randint(1, 10)
        vals = []
        for _ in range(n):
            val = random.randint(1, 64)
            if cost + val > budget:
                if budget - cost > 0:
                    val = budget-cost
                    vals.append(val)
                    cost += val         
                break
            vals.append(val)
            cost += val
    else:
        val = random.randint(1, 64)
        vals = [min(val, budget)]
        cost = vals[0]
    return vals, cost

UPPER = 10
def generate_non_scalar_field(repeated, budget):
    cost = 0
    if repeated:
        n = random.randint(1, 10)
        vals = []
        for _ in range(n):
            val = random.randint(1, UPPER)
            if cost + val > budget:
                if budget - cost > 0:
                    val = budget-cost
                    vals.append(val)
                    cost += val         
                break
            vals.append(val)
            cost += val
    else:
        val = random.randint(1, UPPER)
        vals = [min(val, budget)]
        cost = vals[0]
    return vals, cost

def generate_submessage(budget, max_depth=float('inf')):

    message = {}
    total_cost = 0
    while budget > 0:
        if max_depth == 1:
            field_type = random.choice(['scalar', 'non-scalar'])
        else:
            # field_type = random.choice(['scalar', 'non-scalar', 'submessage', 'submessage', 'submessage','submessage','submessage','submessage','submessage','submessage','submessage'])
            field_type = random.choice(['scalar', 'non-scalar', 'non-scalar', 'submessage','submessage'])

        is_repeated = random.choice([True, False])  
        
        field_info = {
            "type": field_type,
            "is_repeated": False if field_type == 'submessage' else is_repeated 
        }

        if field_type == 'scalar':
            field_data, cost = generate_scalar_field(is_repeated, budget)
        elif field_type == 'non-scalar':
            field_data, cost = generate_non_scalar_field(is_repeated, budget)
        else:  # Submessage
            field_data, cost = generate_submessage(budget, max_depth - 1)

        if cost > 0:
            field_info["data"] = field_data
            message[f"field_{len(message) + 1}"] = field_info
            budget -= cost
            total_cost += cost
    
    return message, total_cost
