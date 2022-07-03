from some_async_database_library import save_results_to_db


async def save_value(value):
    print(f"Saving {value} to database")
    db_response = await save_results_to_db(result)
    print(f"Response from database: {db_response}")


if __name__ == '__main__':
    eventloop.put(
        partial(save_value, "Hello World", print)
    )
