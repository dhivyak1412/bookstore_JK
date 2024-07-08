import pytest
from sqlalchemy.exc import IntegrityError
import database,pytest,httpx
from fastapi.testclient import TestClient
from main import app
from database import get_db,UserCredentials,Book
from bookmgmt import create_book



def test_user_valid(mock_db_session,valid_user):
    mock_db_session.add(valid_user)
    # db_session.add(valid_user)
    mock_db_session.commit()
    test=mock_db_session.query(database.UserCredentials).filter_by(email="testabc@gmail.com",password="").first()
    print(test)
    assert test.email =="testabc@gmail.com"

@pytest.mark.xfail(raises=IntegrityError)
def test_user_no_email(mock_db_session):
    user = UserCredentials(firstname="john",lastname="clear")
    mock_db_session.add(user)
    try:
        mock_db_session.commit()
    except IntegrityError:
        mock_db_session.reset_mock()

def test_book_valid(mock_db_session):
    test_book = Book(name="test_book",author="test_author",published_year=1991,book_summary="Title of the Testing")
    mock_db_session.add(test_book)
    mock_db_session.commit()
    actual_book=mock_db_session.query(Book).filter_by(name="test_book").first()
    print(actual_book)
    assert actual_book.name=="test_book"

@pytest.mark.asyncio
async def test_login(test_app,book_payload,book_update_payload):
    async with httpx.AsyncClient(app=test_app,base_url="http://test") as client:
        # get the access token
        login_url="/login"
        login_data={"email":"dviji15@gmail.com",
                    "password":"passkey"}
        response = await client.post(login_url, json=login_data)
        assert response.status_code == 200
        token_response = response.json()
        access_token = token_response.get('access_token')
        assert access_token is not None

        # With access token check the Book APi
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        #  To Check the API Health status
        response =await  client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status":"up"}

        #  Create the new book
        response = await client.post("/books",json=book_payload,headers=headers)
        assert response.status_code == 200
        new_book = response.json()
        print(response.json)
        assert new_book['name'] == "python world"
        assert new_book['author'] == "Joe"

        #  Get or retrieve all the books
        response = await test_app.get(f"/books/",headers=headers)
        assert response.status_code == 200
        all_books = response.json()
        #  Assuming at least one book is present in API
        assert len(all_books)>0 

        #  Get the book by its id(book_id)
        book_id= new_book['id']
        response = await client.get(f"/books/{book_id}",headers=headers)
        assert response.status_code == 200
        book_retrieved = response.json()
        assert book_retrieved['id'] == new_book['id']

        #  Update the book details
        response = await client.put(f"/books/{book_id}",json=book_update_payload,headers=headers)
        response_json = response.json()
        assert response.status_code == 202
        assert response_json['book_id'] == "2000"
        assert response_json['title'] == "Python"

        #  Delete the Book
        response = await client.delete(f"/books/{book_id}",headers=headers)
        assert response.status_code == 202
        assert response_json() == {"message": "Book deleted successfully"}

@pytest.mark.asyncio
async def test_book_api_error_handling(test_app):
    async with httpx.AsyncClient(app=test_app, base_url="http://test") as client:
        # Step 1: Simulate login to obtain access token
        login_url = "/login"
        login_data = {
            "email": "dviji15@gmail.com",
            "password": "passkey"
        }

        response = await client.post(login_url, json=login_data)
        assert response.status_code == 200
        token_response = response.json()
        access_token = token_response.get('access_token')
        assert access_token is not None

        # Step 2: Use the obtained access token to access book-related APIs
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # Get the book details which doesn't exist
        response = await client.get("/books/1000" , headers=headers)
        assert response.status_code == 404  # Not Found

        # updating book with invalid book id
        invalid_update_data = {
            "name": "name updating.."
        }
        response = await client.put("/books/1000", json=invalid_update_data, headers=headers)
        assert response.status_code == 404  # Not Found

        # Deleting the book details with invalid book id
        response = await client.delete("/books/1000", headers=headers)
        assert response.status_code == 404  # Not Found    



    
    

