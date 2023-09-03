from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace these with your MySQL cluster connection details
DATABASE_URLS = [
    "mysql+mysqlconnector://user1:password1@host1/dbname",
    "mysql+mysqlconnector://user2:password2@host2/dbname",
    "mysql+mysqlconnector://user3:password3@host3/dbname",
]

# Create a list of SQLAlchemy database engines for each host
engines = [create_engine(url) for url in DATABASE_URLS]

# Create a list of SQLAlchemy session factories for each engine
SessionLocals = [sessionmaker(autocommit=False, autoflush=False, bind=engine) for engine in engines]

# Create a FastAPI app
app = FastAPI()

# SQLAlchemy models
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, Sequence("item_id_seq"), primary_key=True, index=True)
    name = Column(String(50), index=True)

# Create the database tables for each engine
for engine in engines:
    Base.metadata.create_all(bind=engine)

def get_session():
    # Round-robin session selection for load balancing between database hosts
    return SessionLocals.pop(0)

def release_session(session):
    SessionLocals.append(session)

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    # Create a new item in the database on the selected host
    db = get_session()
    try:
        db_item = Item(name=item.name)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    finally:
        release_session(db)

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    # Retrieve an item from the database by ID using round-robin session selection
    db = get_session()
    try:
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return db_item
    finally:
        release_session(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
