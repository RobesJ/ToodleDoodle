import React, {useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";
import { userAPI} from "../api";
import "./user_page.css"

const UserPage = () => {

    const [todos, setTodos] = useState([]);
    const [currentUser, setCurrentUser] = useState(null);
    const [chosenTodo, setChosenTodo] = useState(null)
    const [todoTitle, setTodoTitle] = useState("");
    const [todoDesc, setTodoDesc] = useState("");
    const [todoStatus, setTodoStatus] = useState("");
    const [todoDue, setTodoDue] = useState("");
    const [showPopUp, setShowPopUp] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState ('');
    const [editMode, setEditMode] = useState(false);
    const navigate = useNavigate();

    const updateUrlForTodo = (userId, todoId) => {
        // Update URL to show todo context without navigating away from UserPage
        const newUrl = `/users/${userId}todos/${todoId}`;
        window.history.replaceState({ userId, todoId }, '', newUrl);
    };

    useEffect(() => {
        const fetchUserData = async () => {
            //console.log("fetch user data is running");
            try{
                const user = await userAPI.getUser();
                setCurrentUser(user.data);
                //console.log(user.data);
                const todos = await userAPI.getUsersTodo(user.data.id);
                //console.log(todos);
                setTodos(todos.data);
            }
            catch (err){
                setError (err.message);
                console.log(error);
                const status = err.response?.status;
                if(status == 403 || status == 401){
                    navigate("/login");
                };
            }
        };
        fetchUserData();
        setTimeout(() => {
            setLoading(false);
        }, 1500); // need enough time to read the loading mess

    }, []);
    
    const handleLogout = () => {
        localStorage.removeItem("access_token");
        setCurrentUser(null); 
        navigate("/login");
    }

    const handleCancelFunction = () => {
        setChosenTodo(null);
        setTodoDesc("");
        setTodoTitle("");
        setTodoStatus("");
        setTodoDue("");
        setShowPopUp(false);
        setEditMode(false);
        setLoading(false);
        setError("");
        window.history.replaceState({ userId: currentUser.id }, '', '/user_page');
    }

    const handleEditTodo = (todo) => {
        setChosenTodo(todo);
        setTodoDesc(todo.description || "");
        setTodoTitle(todo.title);
        setTodoStatus(todo.status || "");
        setTodoDue(todo.due_date || "");
        setShowPopUp(true);
        setEditMode(true);
        updateUrlForTodo(currentUser.id,todo.id);
    }

    const handleCreatingTodo = async (e) => {
        e.preventDefault();
        try{
            const todoData = {};
            if (todoTitle.trim() == ""){
                console.error("Title is required field");
                setError("Title is required field");
                return;
            }
            else{
                todoData.title = todoTitle;
            };
            todoDesc.trim()   == "" ? todoData.description = null : todoData.description = todoDesc;
            todoStatus.trim() == "" ? todoData.status      = null : todoData.status = todoStatus;
            todoDue.trim()    == "" ? todoData.due_date    = null : todoData.due_date = todoDue;

            console.log("Sending todoData:", todoData);
            const newTodo = await userAPI.createTodo(currentUser.id, todoData);
            setLoading(true);
            console.log("New todo: ", newTodo);

            setTodos(prevTodos => [...prevTodos, newTodo.data]); // append new todo to list of todos

            handleCancelFunction();
        }
        catch (err){
            console.log(err.message);
            setError(err.message);
        }
    }

    const handleDeleteTodo = async (todo) => {
        try{
            const message = await userAPI.deleteTodo(currentUser.id, todo.id);
            setSuccess(message);
            // Filter out the deleted todo from the list
            setTodos(prevTodos => prevTodos.filter(t => t.id !== todo.id));
        }    
        catch (err){
            console.error("Update error:", err);
            console.error("Error response:", err.response);
            setError(err.message);
        }
    }

    const handleUpdateTodo = async (e) => {
        e.preventDefault();
        
        if (!chosenTodo) {
            console.error("No todo selected for update");
            setError("No todo selected for update");
            return;
        }

        try{
            const updateData = {};

            if (todoTitle.trim() == ""){
                console.error("Title is required field");
                setError("Title is required field");
                return;
            }
            else{
                updateData.title = todoTitle;
            };
            todoDesc.trim()   == "" ? updateData.description = null : updateData.description = todoDesc;
            todoStatus.trim() == "" ? updateData.status      = null : updateData.status = todoStatus;
            todoDue.trim()    == "" ? updateData.due_date    = null : updateData.due_date = todoDue;
        
            console.log("Update Data:", updateData);

            const updatedTodo = await userAPI.updateTodo(currentUser.id, chosenTodo.id, updateData);
           
            //update todo in the UI
            setTodos(prevTodos =>
                prevTodos.map(todo =>
                    todo.id == chosenTodo.id ? updatedTodo.data : todo
                )
            );

            handleCancelFunction();
        }
        catch (err){
            console.error("Update error:", err);
            console.error("Error response:", err.response);
            setError(err.message);
        }
    }

    // show message while fetching user data
    if (loading || !currentUser){
        return (
            <div className="user-page">
            <h2>Wait a sec, I am loading your data </h2>
            </div>
        )
    }
    else {
        return (
                <div className="user-page">

                    <div className="header">
                    <h1 className="brand-name">CreaDo</h1>
                    <button type="button" onClick={handleLogout} className="logout-button">
                        Logout
                    </button>
                    </div>

                    {showPopUp && (
                      <div className="modal-overlay">
                        <div className="modal-content">
                          <h3>Add New Todo</h3>
                          <form>
                            <input type="text" placeholder="Todo title" value={todoTitle} onChange={(e) => setTodoTitle(e.target.value)} required/>
                            <textarea placeholder="Todo description" value={todoDesc} onChange={(e) => setTodoDesc(e.target.value)}></textarea>
                            <input type="text" placeholder="Status" value={todoStatus} onChange={(e) => setTodoStatus(e.target.value)}/>
                            <input type="date" value={todoDue} onChange={(e) => setTodoDue(e.target.value)}/>
                            <button type="submit" onClick={editMode ? handleUpdateTodo : handleCreatingTodo}>{loading ? "Creating Todo..." : "Save"}</button>
                            <button type="button" onClick={handleCancelFunction}>Cancel</button>
                          </form>
                        </div>
                      </div>
                    )}

                    <div className="todos-section">
                        <div className="todos-section-header">
                        <h2>Hi {currentUser.name}, here are your Todos</h2>
                        <button type="button" onClick={() => {setShowPopUp(true); setEditMode(false);}} className="add-todo-button">
                            Create Todo
                        </button>
                        </div>

                        {todos.length === 0 ? (
                            <p className="no-todos">No todos yet. Start by adding one!</p>
                        ) : (
                            <ul className="todos-list">
                                {todos.map((todo) => (
                                    <li key={todo.id} className={`todo-item ${todo.status ? 'completed' : ''}`}>
                                        <div className="todo-content">
                                            <div className="todo-left-section">
                                                <h3 className="todo-title">{todo.title}</h3>
                                                <div className="todo-meta">
                                                    <span className={`todo-status ${todo.status ? todo.status: 'completed' }`}>
                                                        {todo.status ? todo.status: 'completed' }
                                                    </span>
                                                    {todo.created_at && (
                                                        <span className="todo-date">
                                                            Due: {todo.due_date}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="todo-actions">
                                                <button onClick={() => handleEditTodo(todo)} className="edit-button">
                                                   [ Edit ]
                                                </button>
                                                <button onClick={() => handleDeleteTodo(todo)} className="delete-button">
                                                   [ Delete ]
                                                </button>
                                            </div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>
            );
        };
}   
export default UserPage;
