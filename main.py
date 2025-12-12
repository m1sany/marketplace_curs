from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from database import init_db
from routers import auth, products, orders, commissions

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Marketplace API",
    description="API маркетплейса",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(commissions.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    #Главная страница
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    #Страница входа
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    #Страница регистрации
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/products", response_class=HTMLResponse)
async def products_page(request: Request):
    #Страница каталога товаров
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/my-products", response_class=HTMLResponse)
async def my_products_page(request: Request):
    #Страница моих товаров (для продавцов)
    return templates.TemplateResponse("my_products.html", {"request": request})


@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    #Страница заказов
    return templates.TemplateResponse("orders.html", {"request": request})


@app.get("/commissions", response_class=HTMLResponse)
async def commissions_page(request: Request):
    #Страница комиссий (для продавцов)
    return templates.TemplateResponse("commissions.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

