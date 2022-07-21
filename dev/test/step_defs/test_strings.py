def test_valid_size(image_size):
    print('The user sent input value:')
    p = image_size / 100
    print(p)
    return p


def test_get_image_details(get_image_details):
    a, b = get_image_details
    print('got values')
    print(a)
    print(b)
    return a, b
