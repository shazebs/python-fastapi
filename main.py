from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ariadne import QueryType, make_executable_schema, graphql_sync
from ariadne.asgi import GraphQL


companies = [
    {"name": "SpaceX", "ceo": "Elon Musk"},
    {"name": "Microsoft", "ceo": "Bill Gates"},
    {"name": "Microsoft", "ceo": "Shazebs"},
]

# Define GraphQL Schema
type_defs = """
    type Company {
        name: String!
        ceo: String!
    }

    type Query {
        companies(name: String, ceo: String): [Company]!
    }
"""

# Define Query Resolver
query = QueryType()

@query.field("companies")
def resolve_companies(_, info, name=None, ceo=None):
    filtered_companies = companies
    if name:
        filtered_companies = [company for company in filtered_companies if company["name"].lower() == name.lower()]
    if ceo:
        filtered_companies = [company for company in filtered_companies if company["ceo"].lower() == ceo.lower()]
    return filtered_companies

# Create Executable Schema
schema = make_executable_schema(type_defs, query)

# FastAPI App
app = FastAPI()

# Add CORS middleware allowing any origin
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=["http://localhost:5173", 
                   "https://sapherons.netlify.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add GraphQL Route
app.add_route("/graphql", GraphQL(schema, debug=True))

class Item(BaseModel):
    firstName: str = None
    lastName: str = None

items = []

def helloServer():
    a = 1
    b = 2 
    if (a > b):
        print(f"{a} is larger than {b}")
    else:
        print(f"{a} is smaller than {b}")


@app.get("/")
def root():
    helloServer()
    return {"Hello": "World"}


@app.get("/items", response_model=list[Item])
def list_items(limit: int = 10):
    return items[0:limit]


@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return items


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")
    

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)

# http://127.0.0.1:8000/docs for SwaggerUI 
# http://127.0.0.1:8000/openapi.json