# # socket

# import socket
#
# sock = socket.socket()
# sock.bind(('127.0.0.1', 8090))
# sock.listen(5)
#
# while 1:
#     conn, addr = sock.accept()
#     data = conn.recv(1024)
#     print(data)
#     conn.send(b'HTTP/1.1 200 ok\r\nserver: django\r\ncontent-type:text/html\r\n\r\n<h1>hello world</h1>')
#     conn.close()
#


# from functools import wraps
#
# def my_decorator(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         print("Something is happening before the function is called.")
#         result = func(*args, **kwargs)
#         print("Something is happening after the function is called.")
#         return result
#     return wrapper
#
#
# @my_decorator
# def say_hello():
#     """This is the docstring of say_hello function."""
#     print("Hello!")
#
# print(say_hello.__name__)  # 输出: say_hello
# print(say_hello.__doc__)


[
    {
        "model": "notify.notify",
        "pk": 51,
        "fields":
            {
                "user": 1,
                "title": "t4",
                "event_id": 1,
                "expire_days": 7,
                "value_raw": "{""'mail_list': ['user1@test.com', 'user2@test.com', 'user3@test.com', 'user4@test.com']""}",
                "notify_choice": 1,
                "status": 1,
                "create_time": "2024-10-29T13:43:09.300",
                "update_time": "2024-10-29T13:43:09.300",
                "envs": [1]
            }
    }
 ]

