import pytest, requests

from utils import MongoDb


@pytest.fixture
def get_connection():
    col = MongoDb(host='localhost')
    col.create_connection()
    return col


users_host = 'http://localhost:81'


# create a using using the db
# call users service and get the data
# check that the data is as espected
# delete the user using the database
def test_get_user(get_connection):
    get_connection.upsert('users', 100,
                          {'name': 'John', 'email': 'test@email.eu'})
    response = requests.get(url='{0}/users/100'.format(users_host)).json()
    assert response['_id'] == 100
    assert response['email'] == 'test@email.eu'
    assert response['name'] == 'John'
    get_connection.delete('users', 100)


# create a using using the users service
# check that the data in the db is as espected
# delete the user using the database
def test_create_user(get_connection):
    get_connection.delete('users', 101)
    requests.put(url='{0}/users/101'.format(users_host),
                 data={'name': 'John Doe', 'email': 'johny@email.eu'}).json()
    response = get_connection.get('users', {'_id': 101})
    assert len(response) == 1
    assert response[0]['_id'] == 101
    assert response[0]['email'] == 'johny@email.eu'
    assert response[0]['name'] == 'John Doe'
    get_connection.delete('users', 101)
