from fastapi import FastAPI
from apis import users, products, goose_dataset

app = FastAPI()

# Register routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(goose_dataset.router)

@app.get("/")
def root():
    return {"message": "Welcome to my API server!"}