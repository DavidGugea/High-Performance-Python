from functools import partial
from some_database_library import save_results_to_db


def save_value(value, callback):
    print(f"Saving {value} to database")
    save_results_to_db(result, callback)


def print_response(db_response):
    print(f"Response from database: {db_response}")


if __name__ == '__main__':
    eventloop.put(partial(save_value, "Hello World", print_response))
