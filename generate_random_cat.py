import random

def generate_random_cat():
    names = ["Барсік", "Мурка", "Пушок", "Сімба", "Луна", "Том", "Белла", "Оскар", "Міло", "Хлоя"]
    features_pool = [
        "любить спати",
        "ловить мух",
        "боїться пилососа",
        "голосно муркоче",
        "грається з шкарпетками",
        "їсть кімнатні рослини",
        "лазить по шторах",
        "бігає вночі",
        "дряпає диван",
        "любить коробки"
    ]

    name = random.choice(names)
    age = random.randint(1, 15)
    features = random.sample(features_pool, random.randint(2, 4))

    return {
        "name": name.lower(),
        "age": age,
        "features": features
    }
