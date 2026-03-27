# 🛍️ TrendZone Fashion Store API

A fully functional Fashion Store REST API built with **FastAPI** and **Python** as the Final Project for the FastAPI Internship Training at **Innomatics Research Labs**.

---

## 🚀 Quick Start

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the server
```bash
uvicorn main:app --reload
```

### Open Swagger UI
```
http://127.0.0.1:8000/docs
```

> If port 8000 is blocked, use:
> ```bash
> uvicorn main:app --reload --port 8001
> ```

---

## 📦 Tech Stack

| Tool       | Purpose                        |
|------------|-------------------------------|
| Python     | Programming language           |
| FastAPI    | Web framework                  |
| Pydantic   | Request validation             |
| Uvicorn    | ASGI server                    |

---

## 🗂️ Project Structure

```
trendzone/
│
├── main.py            ← All API code
├── requirements.txt   ← Dependencies
└── README.md          ← This file
```

---

## 🛒 Features

- ✅ Browse 8 pre-loaded clothing products
- ✅ Full CRUD — Add, Update, Delete products
- ✅ Place orders with dynamic price breakdown
- ✅ Season sale (15%), bulk discount (5%), gift wrap charges
- ✅ Wishlist with duplicate prevention
- ✅ Convert entire wishlist to orders in one call
- ✅ Search across name, brand, and category
- ✅ Sort by price, name, brand, or category
- ✅ Pagination on products and orders
- ✅ Combined browse endpoint — filter + sort + paginate

---

## 📋 API Endpoints

### Products
| Method   | Endpoint                    | Description                          |
|----------|-----------------------------|--------------------------------------|
| GET      | `/`                         | Welcome message                      |
| GET      | `/products`                 | All products                         |
| GET      | `/products/summary`         | Stock stats and category counts      |
| GET      | `/products/filter`          | Filter by category, brand, price     |
| GET      | `/products/search`          | Search by keyword                    |
| GET      | `/products/sort`            | Sort by price, name, brand, category |
| GET      | `/products/page`            | Paginate products                    |
| GET      | `/products/browse`          | Filter + sort + paginate combined    |
| GET      | `/products/{product_id}`    | Single product by ID                 |
| POST     | `/products`                 | Add new product                      |
| PUT      | `/products/{product_id}`    | Update price or stock status         |
| DELETE   | `/products/{product_id}`    | Delete product                       |

### Orders
| Method   | Endpoint                    | Description                          |
|----------|-----------------------------|--------------------------------------|
| GET      | `/orders`                   | All orders with total revenue        |
| GET      | `/orders/search`            | Search by customer name              |
| GET      | `/orders/sort`              | Sort by total cost or quantity       |
| GET      | `/orders/page`              | Paginate orders                      |
| GET      | `/orders/{order_id}`        | Single order by ID                   |
| POST     | `/orders`                   | Place a new order                    |

### Wishlist
| Method   | Endpoint                    | Description                          |
|----------|-----------------------------|--------------------------------------|
| GET      | `/wishlist`                 | View wishlist and total value        |
| POST     | `/wishlist/add`             | Add item to wishlist                 |
| DELETE   | `/wishlist/remove`          | Remove item from wishlist            |
| POST     | `/wishlist/order-all`       | Convert all wishlist items to orders |

---

## 💰 Price Breakdown Logic

When placing an order, the total is calculated in this order:

```
1. base_price       = price × quantity
2. season_discount  = 15% off base_price     (if season_sale = true)
3. bulk_discount    = 5% off after season    (if quantity >= 5)
4. gift_wrap_charge = ₹50 × quantity         (if gift_wrap = true)
5. total_cost       = base - season_discount - bulk_discount + gift_wrap_charge
```

---

## 🧪 Sample Request — Place an Order

```json
POST /orders

{
  "customer_name":    "Rahul Sharma",
  "product_id":       1,
  "size":             "M",
  "quantity":         2,
  "delivery_address": "123 MG Road, Bangalore 560001",
  "gift_wrap":        false,
  "season_sale":      false
}
```

---

## ⚠️ Error Handling

| Status Code | When it happens                                      |
|-------------|------------------------------------------------------|
| 200         | Successful GET / PUT / DELETE                        |
| 201         | POST /products or POST /wishlist/order-all           |
| 400         | Out of stock, wrong size, product has order history  |
| 404         | Product ID or Order ID does not exist                |
| 422         | Validation failed (e.g. quantity=0)                  |

---

## 👨‍💻 Author

Built as the **Final Project** for FastAPI Internship Training  
**Innomatics Research Labs**  
Project #10 — Fashion Store (TrendZone)

---
