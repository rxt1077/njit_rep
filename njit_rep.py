import random, string
from bottle import get, post, run, request, template, response, HTTPResponse
from bottle import abort, redirect, error

# Codes waiting to be validated to register users
validation_codes = {}

# All our reputation data
reputations = {}

def create_code(size=16):
    """
    Generates a NOT CRYPTOGRAPHICALLY SECURE code of a sepcified size
    """
    characters = string.ascii_uppercase + string.digits
    code = ""
    while len(code) < size:
        code += random.choice(characters)
    return code

@error(401)
def error401(error):
    """
    Display a nice 401 page telling people to register
    """
    return '''
        <div>Access denied</div>
        <div><a href="/register">Please click here to register</a></div>
    '''

def get_email():
    """
    Gets a users email from a cookie or tells them they are unauthorized
    """
    email = request.get_cookie("account")
    if not email:
        abort(401)
    return email

@get('/')
def index():
    """
    Shows the main index
    """
    email = get_email()
    return template('''
        % for email, reputation in reputations.items():
            <div>{{email}}: Good - {{reputation["good"]}}, Bad - {{reputation["bad"]}}</div>
        % end
    ''', reputations=reputations)

@get('/register')
def register():
    """
    Display the registration form
    """
    return '''
        <form action="/register" method="post">
            NJIT Email Address: <input name="email" type="text" />
            <input value="Register" type="submit" />
        </form>
    '''

@post('/register')
def do_register():
    """
    Take the steps necessary to register a user
    """
    email = request.forms.get('email')
    if not email.endswith('@njit.edu'):
        return "Email addresses must be from njit.edu"

    code = create_code()
    validation_codes[code] = email
    return template('''
        <div>A verification link has been sent to {{email}}.<div>
        <div>(For now, click <a href="validate/{{code}}">this</a> link)</div>
        ''', email=email, code=code)

@get('/validate/<code>')
def validate(code):
    """
    If the code is valid, give the users an authentication cookie
    """
    if code in validation_codes:
        email = validation_codes[code]
        response.set_cookie("account", email, path='/')
        del validation_codes[code]
        reputations[email] = {'good': 0, 'bad': 0}
        redirect('/')
    else:
        abort(403, "Invalid code!")

run(host='localhost', port=8080, debug=True)
