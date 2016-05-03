from bottle import get, run

@get('/hello')
def hello():
    return "Hello World!"

@get('/users')
def users():
    return "Users List"

@get('/users/<user_id:int>')
def return_user(user_id):
    return "User + " + str(user_id)

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)
