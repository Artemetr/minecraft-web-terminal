def str_to_camel_case(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def dict_keys_to_camel_case(snake_dict: dict, recursive: bool = True) -> dict:
    return {str_to_camel_case(key): dict_keys_to_camel_case(value, recursive) if recursive and type(
        value) == dict else list_dicts_to_camel_case(value, recursive) if recursive and type(value) == list else value
            for key, value in snake_dict.items()}


def list_dicts_to_camel_case(snake_list: list, recursive: bool = True) -> list:
    return [list_dicts_to_camel_case(i, recursive) if recursive and type(i) == list else dict_keys_to_camel_case(
        i, recursive) if type(i) == dict else i for i in snake_list]


def to_camel_case(snake_subject: str or list or dict, recursive: bool = True) -> str or list or dict:
    return str_to_camel_case(snake_subject) if recursive and type(snake_subject) == str else dict_keys_to_camel_case(
        snake_subject, recursive) if recursive and type(snake_subject) == dict else list_dicts_to_camel_case(
        snake_subject, recursive) if recursive and type(snake_subject) == list else snake_subject
