from fastapi import FastAPI, Header, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Todo(BaseModel):
    item: str

# Temporary storage for todos (in-memory)
todos: List[Dict[str, str]] = []

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})

@app.post("/todos")
def create_todo(todo: Todo, x_user: str = Header()):
    todos.append({"item": todo.item, "owner": x_user})
    return {"message": "Todo created", "todo": {"item": todo.item, "owner": x_user}}

@app.post("/create-todo")
def create_todo_form(item: str = Form(...), x_user: str = Form(...)):
    todos.append({"item": item, "owner": x_user})
    return RedirectResponse("/", status_code=303)

@app.get("/todos")
def get_all_todos():
    return {"todos": todos}

@app.post("/delete-todo")
def delete_todo_form(item: str = Form(...), x_user: str = Form(...)):
    todos[:] = [todo for todo in todos if not (todo["item"] == item and todo["owner"] == x_user)]
    return RedirectResponse("/", status_code=303)

@app.delete("/todos/{item}")
def delete_todo(item: str, x_user: str = Header()):
    original_count = len(todos)
    todos[:] = [todo for todo in todos if not (todo["item"] == item and todo["owner"] == x_user)]
    if len(todos) == original_count:
        raise HTTPException(status_code=404, detail="Todo not found or not owned by user")
    return {"message": "Todo deleted"}