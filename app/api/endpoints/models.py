from fastapi import HTTPException, Depends, APIRouter
from app.db.models import Model
from app.db.schemas import ModelSchema
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

model_router = APIRouter(
    prefix='/model',
    tags=['Model']
)


@model_router.post('/create/', response_model=ModelSchema)
async def create_model(model: ModelSchema, db: Session = Depends(get_db)):
    model_db = Model(model_name = model.model_name, brand_id=model.brand_id)
    db.add(model_db)
    db.commit()
    db.refresh(model_db)
    return model_db


@model_router.get('/list/', response_model=List[ModelSchema])
async def last_model(db: Session = Depends(get_db)):
   return db.query(Model).all()


@model_router.get('/{model_id}/')
async def detail_model(model_id: int, db: Session = Depends(get_db)):
   model_db =  db.query(Model).filter(Model.id == model_id).first()
   if model_db is None:
       raise HTTPException(status_code=404, detail='модель жок')
   return model_db


@model_router.put('/{model_id}/', response_model=dict)
async def update_model(model: ModelSchema, model_id: int,
                          db: Session = Depends(get_db)):
   model_db =  db.query(Model).filter(Model.id == model_id).first()
   if model_db is None:
       raise HTTPException(status_code=404, detail='not a data')
   model_db.model_name = model.model_name
   db.add(model_db)
   db.commit()
   db.refresh(model_db)
   return {'message': 'Update'}


@model_router.delete('/{model_id}/')
async def delete_model(model_id: int, db: Session = Depends(get_db)):
   model_db =  db.query(Model).filter(Model.id == model_id).first()
   if model_db is None:
       raise HTTPException(status_code=404, detail='модел жок')
   db.delete(model_db)
   db.commit()
   return {'message': 'Delete'}