
def roundToMultiple(value:int, multiple:int):
    '''
    Rounds the `value` to the nearest multiple of `multiple`.
    Returns the result.
    '''

    # Find the division remainder
    mod = value % multiple

    # If the value is closer to the lower multiple,
    # round down. Otherwise, round up.
    if mod < multiple/2:
        return value - mod
    else:
        return value + (multiple - mod)

if __name__ == '__main__':
    print(f'10, 2: {roundToMultiple(10,2)}')
    print(f' 5, 2: {roundToMultiple(5,2)}')
    print(f' 0, 2: {roundToMultiple(0,2)}')

    print(f'500, 25: {roundToMultiple(500,25)}')
    print(f'427, 25: {roundToMultiple(427,25)}')
    print(f'534, 25: {roundToMultiple(534,25)}')

    print(f'-245, 25: {roundToMultiple(-245,25)}')
