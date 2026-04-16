"""
Flask REST API — Book Store
===========================
A simple CRUD API to practice REST testing.

Run : python app.py
Base: http://127.0.0.1:5000
"""

from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# ── In-memory "database" ──────────────────────────────────────
books = {
    1: {"id": 1, "title": "Clean Code",          "author": "Robert C. Martin", "price": 35.99, "in_stock": True},
    2: {"id": 2, "title": "The Pragmatic Programmer", "author": "Andy Hunt",   "price": 42.00, "in_stock": True},
    3: {"id": 3, "title": "Design Patterns",      "author": "Gang of Four",    "price": 54.50, "in_stock": False},
}
next_id = 4   # auto-increment counter


# ── Helpers ───────────────────────────────────────────────────
def book_not_found(book_id):
    return jsonify({"error": f"Book with id {book_id} not found."}), 404


# ══════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════

# ── GET /books  →  list all books ────────────────────────────
@app.route("/books", methods=["GET"])
def get_books():
    in_stock = request.args.get("in_stock")          # optional filter
    result = list(books.values())
    if in_stock is not None:
        flag = in_stock.lower() == "true"
        result = [b for b in result if b["in_stock"] == flag]
    return jsonify({"count": len(result), "books": result}), 200


# ── GET /books/<id>  →  single book ──────────────────────────
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = books.get(book_id)
    if not book:
        return book_not_found(book_id)
    return jsonify(book), 200


# ── POST /books  →  create a book ────────────────────────────
@app.route("/books", methods=["POST"])
def create_book():
    global next_id
    data = request.get_json()

    # Validate required fields
    required = ["title", "author", "price"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    if not isinstance(data["price"], (int, float)) or data["price"] < 0:
        return jsonify({"error": "price must be a non-negative number."}), 400

    book = {
        "id":       next_id,
        "title":    data["title"],
        "author":   data["author"],
        "price":    round(float(data["price"]), 2),
        "in_stock": bool(data.get("in_stock", True)),
    }
    books[next_id] = book
    next_id += 1
    return jsonify(book), 201


# ── PUT /books/<id>  →  full update ──────────────────────────
@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = books.get(book_id)
    if not book:
        return book_not_found(book_id)

    data = request.get_json()
    required = ["title", "author", "price"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    book.update({
        "title":    data["title"],
        "author":   data["author"],
        "price":    round(float(data["price"]), 2),
        "in_stock": bool(data.get("in_stock", book["in_stock"])),
    })
    return jsonify(book), 200


# ── PATCH /books/<id>  →  partial update ─────────────────────
@app.route("/books/<int:book_id>", methods=["PATCH"])
def patch_book(book_id):
    book = books.get(book_id)
    if not book:
        return book_not_found(book_id)

    data = request.get_json()
    allowed = {"title", "author", "price", "in_stock"}
    for key, value in data.items():
        if key in allowed:
            book[key] = value
    return jsonify(book), 200


# ── DELETE /books/<id>  →  remove a book ─────────────────────
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = books.pop(book_id, None)
    if not book:
        return book_not_found(book_id)
    return jsonify({"message": f"Book '{book['title']}' deleted successfully."}), 200


# ── GET /  →  API index / health check ───────────────────────
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "BookStore REST API",
        "status":  "running",
        "endpoints": {
            "GET    /books":          "List all books (optional ?in_stock=true/false)",
            "GET    /books/<id>":     "Get a single book",
            "POST   /books":          "Create a new book",
            "PUT    /books/<id>":     "Full update of a book",
            "PATCH  /books/<id>":     "Partial update of a book",
            "DELETE /books/<id>":     "Delete a book",
        }
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
