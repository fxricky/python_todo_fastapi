from atexit import register
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from python_fast_api.models.models import Todo, Todo_Pydantic, TodoIn_Pydantic
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise

app  = FastAPI()

@app.get("/")
async def read_root():
  return {"Hello": "World"}

class Status(BaseModel):
  message: str

@app.post('/todos', response_model=Todo_Pydantic)
async def create_todo(todo: Todo_Pydantic):
  todo_obj = await Todo.create(**todo.dict(exclude_unset=True))
  return await Todo_Pydantic.from_tortoise_orm(todo_obj)

@app.get('/get_todos',response_model=List[Todo_Pydantic])
async def get_todo():
  return await Todo_Pydantic.from_queryset(Todo.all())

@app.get('/get_todo_by_id/{todo_id}', response_model=Todo_Pydantic, responses={404: {"model": HTTPNotFoundError}})
async def get_todo_by_id(todo_id: int):
  return await Todo_Pydantic.from_queryset_single(Todo.get(id=todo_id))

@app.put('/update_todo/{todo_id}', response_model=Todo_Pydantic, responses={404: {"model": HTTPNotFoundError}})
async def update_todo(todo_id: int, todo:TodoIn_Pydantic):
  await Todo.filter(id=todo_id).update(**todo.dict(exclude={'id'}, exclude_unset=True))
  return await Todo_Pydantic.from_queryset_single(Todo.get(id=todo_id))

class DeleteReq(BaseModel):
  todo_id: int

@app.delete('/delete_todo', response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_todo(req: DeleteReq):
  todo_id = req.todo_id
  
  delete_count  = await Todo.filter(id=todo_id).delete()

  if not delete_count:
    raise HTTPException(status_code=404, detail=f'Todo {todo_id} not found')

  return Status(message=f'Deleted todo {todo_id}')


register_tortoise(
  app,
  db_url="postgres://<name>:<password>@localhost:<port>/<database_name>",
  modules={"models": ["python_fast_api.models.models"]},
  generate_schemas=True,
  add_exception_handlers=True
)