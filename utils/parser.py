def _split(s, delimiter="|", default_value1=None, default_value2=None):
    if delimiter in s:
        value1, value2 = s.split(delimiter, 1)
    else:
        value1, value2 = default_value1, s
    return value1, value2


def parse(file_path):
    result = ''

    with open(file_path, 'rb') as f:
        lines = f.readlines()

        for line in lines:
            if line.strip() == b'':
                continue
            data = line.strip().split(b'\t\t')
            url = data[0]
            username, password = _split(data[1], delimiter=b'|')

            result += f'{url.decode()} --- Username: {username.decode()} --- Password: {password.decode()}\n'

    return result