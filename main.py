from fastapi import FastAPI, Header, HTTPException, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Simple user storage
users = {"admin": "password", "monganio": "123", "absalomlor": "1234"}

def get_current_user(session: Optional[str] = Cookie(None)):
    if not session or session not in users:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session

class Todo(BaseModel):
    item: str

# Temporary storage for todos (in-memory)
todos: List[Dict[str, str]] = []

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username in users and users[username] == password:
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("session", username)
        return response
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("session")
    return response

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session: Optional[str] = Cookie(None)):
    if not session or session not in users:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos, "current_user": session})

@app.post("/todos")
def create_todo(todo: Todo, x_user: str = Header()):
    todos.append({"item": todo.item, "owner": x_user})
    return {"message": "Todo created", "todo": {"item": todo.item, "owner": x_user}}

@app.post("/create-todo")
def create_todo_form(item: str = Form(...), current_user: str = Depends(get_current_user)):
    todos.append({"item": item, "owner": current_user})
    return RedirectResponse("/", status_code=303)

@app.get("/todos")
def get_all_todos():
    return {"todos": todos}

@app.post("/delete-todo")
def delete_todo_form(item: str = Form(...), current_user: str = Depends(get_current_user)):
    todos[:] = [todo for todo in todos if not (todo["item"] == item and todo["owner"] == current_user)]
    return RedirectResponse("/", status_code=303)

@app.delete("/todos/{item}")
def delete_todo(item: str, x_user: str = Header()):
    original_count = len(todos)
    todos[:] = [todo for todo in todos if not (todo["item"] == item and todo["owner"] == x_user)]
    if len(todos) == original_count:
        raise HTTPException(status_code=404, detail="Todo not found or not owned by user")
    return {"message": "Todo deleted"}