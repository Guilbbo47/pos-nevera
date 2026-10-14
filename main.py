from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from datetime import datetime
import os

app = FastAPI(title="POS Nevera Asociación")

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pos_nevera.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    barcode = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Static y templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.post("/api/products")
def create_product(name: str, barcode: str, price: float, stock: int = 0, db: Session = Depends(get_db)):
    if db.query(Product).filter(Product.barcode == barcode).first():
        raise HTTPException(400, "Código de barras ya existe")
    product = Product(name=name, barcode=barcode, price=price, stock=stock)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.get("/api/products/barcode/{barcode}")
def get_by_barcode(barcode: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.barcode == barcode).first()
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    return product

@app.post("/api/sales")
def create_sale(items: list[dict], db: Session = Depends(get_db)):
    if not items:
        raise HTTPException(400, "Venta vacía")
    total = 0
    sale = Sale(total=0)
    db.add(sale)
    db.flush()
    for item in items:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product or product.stock < item["quantity"]:
            raise HTTPException(400, f"Stock insuficiente para {product.name if product else 'producto'}")
        product.stock -= item["quantity"]
        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            quantity=item["quantity"],
            unit_price=product.price
        )
        db.add(sale_item)
        total += product.price * item["quantity"]
    sale.total = total
    db.commit()
    db.refresh(sale)
    return {"sale_id": sale.id, "total": total}

@app.get("/api/sales")
def list_sales(db: Session = Depends(get_db)):
    sales = db.query(Sale).order_by(Sale.created_at.desc()).limit(50).all()
    result = []
    for s in sales:
        result.append({
            "id": s.id,
            "total": s.total,
            "created_at": s.created_at.isoformat(),
            "items": [{"name": i.product.name, "quantity": i.quantity, "unit_price": i.unit_price} for i in s.items]
        })
    return result

@app.put("/api/products/{product_id}/stock")
def update_stock(product_id: int, stock: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    product.stock = stock
    db.commit()
    return product
