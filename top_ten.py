import random, string
from bottle import get, post, run, request, template, response, HTTPResponse
from bottle import abort, redirect, error

validation_codes = {}
entries = []

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
def error404(error):
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
        <div><a href="/create">Create</a></div>
        % for entry in top_ten:
            <div>{{entry['author']}}: {{entry['content']}}</div>
        % end''', top_ten=entries[:10])

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
        redirect('/')
    else:
        return "Invalid code!"

@get('/create')
def create():
    """
    Present the form to create new content
    """
    email = get_email() 
    return '''
        <form action="/create" method="post">
            What do you have to say? 
            <input name="content" type="text" maxlength=80 size=80 />
            <input type="submit" value="Submit" />
        </form>'''

@post('/create')
def do_create():
    """
    Add the entry to our list
    """
    email = get_email()
    entries.append({
        'content': request.forms.get('content'),
        'author': email,
    })
    redirect('/')

run(host='localhost', port=8080, debug=True)
