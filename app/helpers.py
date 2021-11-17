
def make_equipment(items, equipment_type):
    aux = []
    for item in items:
        if isinstance(item, equipment_type) and item.is_equipped == True:
            aux.append(item)
            items.remove(item)
    return aux and aux[0]

