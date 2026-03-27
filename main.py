from fastapi import FastAPI, Query, Response, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

products = [
    {"id": 1, "name": "Classic Oxford Shirt",  "brand": "Arrow",    "category": "Shirt",   "price": 1299, "sizes_available": ["S", "M", "L", "XL"],      "in_stock": True},
    {"id": 2, "name": "Slim Fit Jeans",         "brand": "Levi's",   "category": "Jeans",   "price": 2499, "sizes_available": ["28", "30", "32", "34"],    "in_stock": True},
    {"id": 3, "name": "Running Shoes",          "brand": "Nike",     "category": "Shoes",   "price": 3999, "sizes_available": ["7", "8", "9", "10", "11"], "in_stock": True},
    {"id": 4, "name": "Floral Summer Dress",    "brand": "Zara",     "category": "Dress",   "price": 1899, "sizes_available": ["XS", "S", "M", "L"],       "in_stock": True},
    {"id": 5, "name": "Leather Biker Jacket",   "brand": "Roadster", "category": "Jacket",  "price": 4999, "sizes_available": ["S", "M", "L", "XL"],      "in_stock": False},
    {"id": 6, "name": "Graphic Print T-Shirt",  "brand": "H&M",      "category": "Shirt",   "price": 699,  "sizes_available": ["S", "M", "L", "XL", "XXL"], "in_stock": True},
    {"id": 7, "name": "Straight Cut Chinos",    "brand": "Arrow",    "category": "Jeans",   "price": 1799, "sizes_available": ["30", "32", "34", "36"],    "in_stock": True},
    {"id": 8, "name": "Ankle Boots",            "brand": "Clarks",   "category": "Shoes",   "price": 5499, "sizes_available": ["6", "7", "8", "9"],        "in_stock": True},
]

orders        = []
wishlist      = []
order_counter = 1


class OrderRequest(BaseModel):
    customer_name:    str  = Field(..., min_length=2)
    product_id:       int  = Field(..., gt=0)
    size:             str  = Field(..., min_length=1)
    quantity:         int  = Field(..., gt=0, le=10)
    delivery_address: str  = Field(..., min_length=10)
    gift_wrap:        bool = False
    season_sale:      bool = False

class NewProduct(BaseModel):
    name:             str       = Field(..., min_length=2)
    brand:            str       = Field(..., min_length=2)
    category:         str       = Field(..., min_length=2)
    price:            int       = Field(..., gt=0)
    sizes_available:  List[str] = Field(..., min_items=1)
    in_stock:         bool      = True

class WishlistOrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


def find_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)


def calculate_order_total(price: int, quantity: int, gift_wrap: bool, season_sale: bool):
    base_price       = price * quantity
    season_discount  = 0
    bulk_discount    = 0
    gift_wrap_charge = 0

    after_season = base_price
    if season_sale:
        season_discount = int(base_price * 0.15)
        after_season    = base_price - season_discount

    if quantity >= 5:
        bulk_discount = int(after_season * 0.05)

    after_discounts  = after_season - bulk_discount

    if gift_wrap:
        gift_wrap_charge = 50 * quantity

    total = after_discounts + gift_wrap_charge

    return {
        "base_price":       base_price,
        "season_discount":  season_discount,
        "bulk_discount":    bulk_discount,
        "gift_wrap_charge": gift_wrap_charge,
        "total_cost":       total,
    }


def filter_products_logic(category, brand, max_price, in_stock):
    result = products
    if category is not None:
        result = [p for p in result if p["category"].lower() == category.lower()]
    if brand is not None:
        result = [p for p in result if p["brand"].lower() == brand.lower()]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]
    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]
    return result


@app.get("/")
def home():
    return {"message": "Welcome to TrendZone Fashion Store"}


@app.get("/products")
def get_products():
    in_stock_count = len([p for p in products if p["in_stock"]])
    return {"products": products, "total": len(products), "in_stock_count": in_stock_count}


@app.get("/products/summary")
def product_summary():
    in_stock_count  = len([p for p in products if     p["in_stock"]])
    out_stock_count = len([p for p in products if not p["in_stock"]])
    brands          = list(set(p["brand"] for p in products))
    category_counts = {}
    for p in products:
        category_counts[p["category"]] = category_counts.get(p["category"], 0) + 1
    return {
        "total_products":  len(products),
        "in_stock_count":  in_stock_count,
        "out_stock_count": out_stock_count,
        "brands":          brands,
        "category_counts": category_counts,
    }


@app.get("/products/filter")
def filter_products(
    category:  Optional[str]  = Query(None),
    brand:     Optional[str]  = Query(None),
    max_price: Optional[int]  = Query(None, gt=0),
    in_stock:  Optional[bool] = Query(None),
):
    result = filter_products_logic(category, brand, max_price, in_stock)
    return {"products": result, "count": len(result)}


@app.get("/products/search")
def search_products(keyword: str = Query(..., description="Search keyword")):
    result = [
        p for p in products
        if keyword.lower() in p["name"].lower()
        or keyword.lower() in p["brand"].lower()
        or keyword.lower() in p["category"].lower()
    ]
    if not result:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(result), "products": result}


@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price", description="Sort by: price, name, brand, category"),
    order:   str = Query("asc",   description="asc or desc"),
):
    allowed = ["price", "name", "brand", "category"]
    if sort_by not in allowed:
        return {"error": f"sort_by must be one of: {', '.join(allowed)}"}
    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}
    result = sorted(products, key=lambda p: p[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "products": result}


@app.get("/products/page")
def get_products_paged(
    page:  int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    start       = (page - 1) * limit
    paged       = products[start: start + limit]
    total_pages = -(-len(products) // limit)
    return {
        "page":        page,
        "limit":       limit,
        "total":       len(products),
        "total_pages": total_pages,
        "products":    paged,
    }


@app.get("/products/browse")
def browse_products(
    keyword:   Optional[str]  = Query(None),
    category:  Optional[str]  = Query(None),
    brand:     Optional[str]  = Query(None),
    max_price: Optional[int]  = Query(None, gt=0),
    in_stock:  Optional[bool] = Query(None),
    sort_by:   str            = Query("price"),
    order:     str            = Query("asc"),
    page:      int            = Query(1, ge=1),
    limit:     int            = Query(3, ge=1, le=20),
):
    result = filter_products_logic(category, brand, max_price, in_stock)
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
            or keyword.lower() in p["brand"].lower()
            or keyword.lower() in p["category"].lower()
        ]
    allowed_sort = ["price", "name", "brand", "category"]
    if sort_by in allowed_sort:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order == "desc"))
    total       = len(result)
    start       = (page - 1) * limit
    paged       = result[start: start + limit]
    total_pages = -(-total // limit) if total > 0 else 0
    return {
        "keyword":     keyword,
        "category":    category,
        "brand":       brand,
        "max_price":   max_price,
        "in_stock":    in_stock,
        "sort_by":     sort_by,
        "order":       order,
        "page":        page,
        "limit":       limit,
        "total_found": total,
        "total_pages": total_pages,
        "products":    paged,
    }


@app.get("/products/{product_id}")
def get_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    return {"product": product}


@app.post("/products", status_code=201)
def add_product(data: NewProduct, response: Response):
    if any(p["name"].lower() == data.name.lower() and p["brand"].lower() == data.brand.lower() for p in products):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Product '{data.name}' by '{data.brand}' already exists"}
    next_id = max(p["id"] for p in products) + 1
    new_product = {
        "id":             next_id,
        "name":           data.name,
        "brand":          data.brand,
        "category":       data.category,
        "price":          data.price,
        "sizes_available": data.sizes_available,
        "in_stock":       data.in_stock,
    }
    products.append(new_product)
    return {"message": "Product added", "product": new_product}


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    response:   Response,
    price:      Optional[int]  = Query(None, gt=0),
    in_stock:   Optional[bool] = Query(None),
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    if price is not None:
        product["price"] = price
    if in_stock is not None:
        product["in_stock"] = in_stock
    return {"message": "Product updated", "product": product}


@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    has_orders = any(o["product_name"] == product["name"] for o in orders)
    if has_orders:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Cannot delete '{product['name']}' — it has order history"}
    products.remove(product)
    return {"message": f"Product '{product['name']}' deleted successfully"}


@app.post("/orders")
def place_order(data: OrderRequest):
    global order_counter
    product = find_product(data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"'{product['name']}' is out of stock")
    if data.size not in product["sizes_available"]:
        raise HTTPException(
            status_code=400,
            detail=f"Size '{data.size}' not available. Available sizes: {product['sizes_available']}"
        )
    breakdown = calculate_order_total(product["price"], data.quantity, data.gift_wrap, data.season_sale)
    new_order = {
        "order_id":         order_counter,
        "customer_name":    data.customer_name,
        "product_name":     product["name"],
        "brand":            product["brand"],
        "size":             data.size,
        "quantity":         data.quantity,
        "gift_wrap":        data.gift_wrap,
        "season_sale":      data.season_sale,
        "delivery_address": data.delivery_address,
        "price_breakdown":  breakdown,
        "total_cost":       breakdown["total_cost"],
        "status":           "confirmed",
    }
    orders.append(new_order)
    order_counter += 1
    return {"message": "Order placed successfully", "order": new_order}


@app.get("/orders")
def get_orders():
    total_revenue = sum(o["total_cost"] for o in orders)
    return {"orders": orders, "total": len(orders), "total_revenue": total_revenue}


@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    result = [o for o in orders if customer_name.lower() in o["customer_name"].lower()]
    if not result:
        return {"message": f"No orders found for: {customer_name}"}
    return {"customer_name": customer_name, "total_found": len(result), "orders": result}


@app.get("/orders/sort")
def sort_orders(
    sort_by: str = Query("total_cost", description="Sort by: total_cost or quantity"),
    order:   str = Query("asc"),
):
    allowed = ["total_cost", "quantity"]
    if sort_by not in allowed:
        return {"error": f"sort_by must be one of: {', '.join(allowed)}"}
    result = sorted(orders, key=lambda o: o[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "orders": result}


@app.get("/orders/page")
def get_orders_paged(
    page:  int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    start       = (page - 1) * limit
    total_pages = -(-len(orders) // limit) if orders else 0
    return {
        "page":        page,
        "limit":       limit,
        "total":       len(orders),
        "total_pages": total_pages,
        "orders":      orders[start: start + limit],
    }


@app.get("/orders/{order_id}")
def get_order(order_id: int, response: Response):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": "Order not found"}


@app.post("/wishlist/add")
def add_to_wishlist(
    customer_name: str = Query(..., min_length=2),
    product_id:    int = Query(..., gt=0),
    size:          str = Query(..., min_length=1),
):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if size not in product["sizes_available"]:
        raise HTTPException(
            status_code=400,
            detail=f"Size '{size}' not available. Available sizes: {product['sizes_available']}"
        )
    duplicate = any(
        w["customer_name"].lower() == customer_name.lower()
        and w["product_id"] == product_id
        and w["size"] == size
        for w in wishlist
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="This item is already in your wishlist")
    item = {
        "customer_name": customer_name,
        "product_id":    product_id,
        "product_name":  product["name"],
        "brand":         product["brand"],
        "size":          size,
        "price":         product["price"],
    }
    wishlist.append(item)
    return {"message": "Added to wishlist", "item": item}


@app.get("/wishlist")
def get_wishlist():
    total_value = sum(w["price"] for w in wishlist)
    return {"wishlist": wishlist, "total_items": len(wishlist), "total_wishlist_value": total_value}


@app.delete("/wishlist/remove")
def remove_from_wishlist(
    customer_name: str = Query(...),
    product_id:    int = Query(..., gt=0),
):
    for item in wishlist:
        if item["customer_name"].lower() == customer_name.lower() and item["product_id"] == product_id:
            wishlist.remove(item)
            return {"message": f"'{item['product_name']}' removed from wishlist"}
    raise HTTPException(status_code=404, detail="Item not found in wishlist")


@app.post("/wishlist/order-all", status_code=201)
def order_all_from_wishlist(data: WishlistOrderRequest):
    global order_counter
    customer_items = [w for w in wishlist if w["customer_name"].lower() == data.customer_name.lower()]
    if not customer_items:
        raise HTTPException(status_code=400, detail=f"No wishlist items found for: {data.customer_name}")
    placed_orders = []
    grand_total   = 0
    for item in customer_items:
        product = find_product(item["product_id"])
        if not product or not product["in_stock"]:
            continue
        breakdown = calculate_order_total(product["price"], 1, False, False)
        new_order = {
            "order_id":         order_counter,
            "customer_name":    data.customer_name,
            "product_name":     product["name"],
            "brand":            product["brand"],
            "size":             item["size"],
            "quantity":         1,
            "gift_wrap":        False,
            "season_sale":      False,
            "delivery_address": data.delivery_address,
            "price_breakdown":  breakdown,
            "total_cost":       breakdown["total_cost"],
            "status":           "confirmed",
        }
        orders.append(new_order)
        placed_orders.append(new_order)
        grand_total   += breakdown["total_cost"]
        order_counter += 1
    for item in customer_items:
        if item in wishlist:
            wishlist.remove(item)
    return {
        "message":      f"All wishlist items ordered for {data.customer_name}",
        "orders_placed": placed_orders,
        "grand_total":   grand_total,
    }