# Util function to add offset and decimal to obtain real data
def add_offset_and_decimal(raw_value, offset, decimal):
    return int((raw_value + offset) / (10 ** decimal))


# Util function to remove offset and decimal to obtain raw data
def remove_offset_and_decimal(real_value, offset, decimal):
    return int(((10 ** decimal) * real_value) - offset)
