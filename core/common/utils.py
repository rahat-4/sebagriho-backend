import random

def unique_number_generator(instance)->int:
    model = instance.__class__
    unique_number = random.randint(111111, 999999)

    while model.objects.filter(serial_number=unique_number).exists():
        unique_number_generator(instance)

    return unique_number