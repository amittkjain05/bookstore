import requests
import pytest


BASE_URL =  "http://127.0.0.1:5000"
HEADERS = {"Content-Type": "application/json"}

def url(path=""):
    return f"{BASE_URL}{path}"


class TestHeathCheck():

    def test_status_200(self):
        r = requests.get(url("/"))
        assert  r.status_code == 200

    def test_content_type_is_json(self):
        r = requests.get(url("/"))
        assert  "application/json" == r.headers["Content-type"]

    def test_body_has_status_running(self):
        r = requests.get(url("/"))
        assert r.json()["status"] == "running"

    def test_body_has_endpoints_key(self):
        r = requests.get(url("/"))
        assert "endpoints" in r.json()

class TestGetAllBooks:
    def test_status_200(self):
        r = requests.get(url("/books"))
        assert r.status_code == 200

    def test_content_type_is_json(self):
        r = requests.get(url("/books"))
        assert "application/json" in r.headers["Content-type"]

    def test_response_has_count_and_books(self):
        r = requests.get(url("/books"))
        counter = 0
        for item in r.json()["books"]:
            counter += 1
        #assert r.json()["count"] == 3
        assert "count" in r.json()
        assert "books" in r.json()

    def test_books_is_a_list(self):
        r = requests.get(url("/books"))
        assert isinstance(r.json()["books"], list)

    def test_count_matches_list_length(self):
        r = requests.get(url("/books"))
        body = r.json()
        assert body["count"] == len(body["books"])

    def test_filter_in_stock_true(self):
        r = requests.get(url("/books?in_stock=true"))
        books = r.json()["books"]
        # counter = 0
        # for item in body:
        #     if item["in_stock"] == True:
        #         counter += 1
        # assert counter > 0
        assert all(b["in_stock"] is True for b in books)

    def test_each_book_has_required_fields(self):
        r = requests.get(url("/books"))
        books = r.json()["books"]
        for b in books:
            assert 'title' in b
            assert 'author' in b
            assert 'price' in b
            assert 'in_stock' in b

class TestGetSingleBook:
    def test_status_200_for_existing_book(self):
        r = requests.get(url("/books/1"))
        assert r.status_code == 200

    def test_returns_correct_book(self):
        r = requests.get(url("/books/1"))
        assert r.json()["id"] == 1

    def test_title_is_string(self):
        r = requests.get(url("/books/1"))
        assert isinstance(r.json()["title"], str)

    def test_price_is_number(self):
        r = requests.get(url("/books/1"))
        assert isinstance(r.json()["price"], (int, float))

    def test_404_for_nonexistent_book(self):
        r = requests.get(url("/books/100"))
        assert r.status_code == 404

    def test_404_body_has_error_key(self):
        r = requests.get(url("/books/100"))
        assert r.json()["error"] == "Book with id 100 not found."


class TestCreateBook:

    NEW_BOOK = {
        "title" : "Refactoring",
        "author" : "Martin Flower",
        "price" :  29.00,
        "in_stock": True
    }

    def test_status_201_on_create(self):
        r = requests.post(url("/books"), json=self.NEW_BOOK, headers=HEADERS)
        assert r.status_code == 201

    def test_response_contains_id(self):
        r = requests.post(url("/books"), json=self.NEW_BOOK, headers=HEADERS)
        assert "id" in r.json()

    def test_response_title_matches_input(self):
        r = requests.post(url("/books"), json=self.NEW_BOOK, headers=HEADERS)
        assert r.json()["title"] == self.NEW_BOOK["title"]

    def test_response_price_matches_input(self):
        r = requests.post(url("/books"), json=self.NEW_BOOK, headers=HEADERS)
        assert r.json()["price"] == self.NEW_BOOK["price"]

    def test_created_book_retrievable(self):
        r = requests.post(url("/books"), json=self.NEW_BOOK, headers=HEADERS)
        book_id = r.json()["id"]
        book = requests.get(url(f"/books/{book_id}"))
        assert book.status_code == 200
        assert book.json()["title"] == self.NEW_BOOK["title"]

    def test_400_missing_title(self):
        r = requests.post(url("/books"), json={"author" : "Martin Flower", "price" :  29.00, "in_stock": True }, headers=HEADERS)
        assert r.status_code == 400

    def test_400_negative_price(self):
        r = requests.post(url("/books"), json={"author": "Martin Flower", "price": -29.00, "in_stock": True},
                          headers=HEADERS)
        assert r.status_code == 400

    def test_400_body_has_error_key(self):
        r = requests.post(url("/books"), json={},  headers=HEADERS)
        assert "error" in r.json()

    @pytest.mark.parametrize("price", [0, 0.01, 99.99, 1000])
    def test_valid_price_boundaries(self, price):
        payload = {"title": "Test", "author": "Author", "price": price}
        r = requests.post(url("/books"), json=payload, headers=HEADERS)
        assert r.status_code == 201

class TestUpdateBook:

    UPDATE_PAYLOAD = {
        "title": "Clean Code (Updated)",
        "author": "Robert C. Martin",
        "price": 39.99,
        "in_stock": False
    }

    def test_status_200_on_update(self):
        r = requests.put(url("/books/2"), json=self.UPDATE_PAYLOAD, headers=HEADERS )
        assert r.status_code == 200

    def test_title_is_updated(self):
        r = requests.put(url("/books/2"), json=self.UPDATE_PAYLOAD, headers=HEADERS)
        request2 = requests.get(url("/books/2"))
        assert self.UPDATE_PAYLOAD["title"] == request2.json()["title"]

    def test_404_on_nonexistent_book(self):
        r = requests.put(url("/books/100"), json=self.UPDATE_PAYLOAD, headers=HEADERS)
        assert r.status_code == 404

    def test_400_when_missing_required_fields(self):
        r = requests.put(url("/books/1"), json={"title": "Clean Code (Updated)", "author": "Robert C. Martin"}, headers=HEADERS)
        assert r.status_code == 400

class TestPatchBook:
    def test_status_200_on_patch(self):
        r = requests.patch(url("/books/2"), json={"price" : 39.00}, headers=HEADERS)
        print(r.json()["price"])
        assert r.status_code == 200

class TestDeleteBook:
    def test_statu_200_on_delete(self):
        r = requests.post(url("/books"), json={"title": "Temp", "author": "Temp", "price": 1.00},
                          headers=HEADERS)
        tmp_id = r.json()["id"]
        r_del = requests.delete(url(f"/books/{tmp_id}"))
        assert r_del.status_code == 200

    def test_response_has_message(self):
        r = requests.post(url("/books"), json={"title": "Temp", "author": "Temp", "price": 1.00},
                          headers=HEADERS)
        tmp_id = r.json()["id"]
        r_del = requests.delete(url(f"/books/{tmp_id}"))
        assert "message" in r_del.json()

BOOKS_DATA = [
    ("Python Crash Course",     "Eric Matthes",      29.99, True),
    ("Fluent Python",           "Luciano Ramalho",   55.00, True),
    ("Learning Python",         "Mark Lutz",         60.00, False),
    ("Automate the Boring Stuff","Al Sweigart",       25.00, True),
    ("Effective Python",        "Brett Slatkin",     42.00, True),
    ("Two Scoops of Django",    "Daniel Greenfeld",  38.50, False),
    ("The Linux Command Line",  "William Shotts",    30.00, True),
    ("Introduction to Algorithms","CLRS",            89.99, False),
    ("Structure & Interpretation","Abelson & Sussman",40.00, True),
    ("Code Complete",           "Steve McConnell",   50.00, True),
]



@pytest.mark.parametrize("title, author, price, in_stock", BOOKS_DATA)
def test_create_various_books(title, author, price, in_stock):
    payload = {
        "title": title,
        "author": author,
        "price": price,
        "in_stock": in_stock
    }

    r = requests.post(url("/books"), json=payload, headers=HEADERS)
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == title
    assert body["author"] == author
    assert body["price"] == price
