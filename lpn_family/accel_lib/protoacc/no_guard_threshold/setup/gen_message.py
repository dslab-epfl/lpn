import random

def generate_scalar_field(repeated=False):
    if repeated:
        return generate_repeated_field(scalar=True)
    else:
        return [1] #[random.randint(1, 63)]
        # return [random.randint(1, 63)]

def generate_non_scalar_field(repeated=False):
    if repeated:
        return generate_repeated_field(scalar=False)
    else:
        return [random.randint(64, 200)]

def generate_repeated_field(scalar=True):
    length = random.randint(2, 10)  # Adjust the upper limit as needed
    if scalar:
        return [random.randint(1, 63) for _ in range(length)]
    else:
        return [random.randint(64, 200) for _ in range(length)]

def generate_submessage(depth=0):
    if depth > 10:  # Limiting the depth of recursion
        return None
    
    message = {}
    num_fields = 64 #random.randint(1, 5)  # Number of fields in the submessage
    for i in range(num_fields):
        field_type = random.choice(['scalar'])
        # field_type = random.choice(['scalar', 'non-scalar', 'submessage'])
        is_repeated = random.choice([False])  # Decide if the field is repeated

        field_info = {
            "type": field_type,
            "is_repeated": False if field_type == 'submessage' else is_repeated 
        }
        
        if field_type == 'scalar':
            field_info["data"] = generate_scalar_field(repeated=is_repeated)
        elif field_type == 'non-scalar':
            field_info["data"] = generate_non_scalar_field(repeated=is_repeated)
        else:
            field_info["data"] = generate_submessage(depth + 1)
        
        message[f"field_{i}"] = field_info
    
    return message


