import React, {useEffect, useState} from "react";
import { useLocation, useNavigate } from "react-router-dom";
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
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            console.log("fetch user data is running");
            try{
                const user = await userAPI.getUser();
                setCurrentUser(user.data);
                console.log(user.data);
                const todos = await userAPI.getUsersTodo(user.data.id);
                console.log(todos);
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
    
    const handleEditTodo = (todo) => {
        setChosenTodo(todo);
        setTodoDesc(() => (!todo.description ? "" : todo.description));
        setTodoTitle(todo.title);
        setTodoStatus(() => (todo.status == null ? "" : todo.status));
        setTodoDue(() => (todo.due_date == null ? "" : todo.due_date));
        setShowPopUp(true);
    }

    const handleCreatingTodo = async (e) => {
        e.preventDefault();
        try{
            const todoData = {
                title: todoTitle,
                description: todoDesc,
                status: todoStatus,
                due_date: todoDue
            }
            console.log("Sending todoData:", todoData);
            const newTodo = await userAPI.createTodo(currentUser.id, todoData);
            setLoading(true);
            console.log("New todo: ", newTodo);

            setTodos(prevTodos => [...prevTodos, newTodo.data]); // append new todo to list of todos

            setTodoDesc("");
            setTodoTitle("");
            setTodoStatus("");
            setTodoDue("");
            setShowPopUp(false);
            setError("");
            setLoading(false);
        }
        catch (err){
            console.log(err.message);
            setError(err.message);
        }
    }

    const updateTodo = async (e) => {
        e.preventDefault();
        // get choosen Todo and show the data in popUp window, probaly get it from some event
        try{
        updateData = {
            title: todoTitle,
            description: todoDesc,
            status: todoStatus,
            due_date: todoDue
        }
        const updatedTodo = await userAPI.updateTodo(currentUser.id, chosenTodo.id, updateData);
        
        setTodos(prevTodos =>
            prevTodos.map(todo =>
                todo.id == chosenTodo.id ? updatedTodo.data : todo
            )
        );

        setTodoDesc("");
        setTodoTitle("");
        setTodoStatus("");
        setTodoDue("");
        setShowPopUp(false);
        setError("");
        setLoading(false);
        }
        catch (err){
            console.log(err.message);
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
                    <button type="button" onClick={handleLogout} className="logout-button">
                        Logout
                    </button>
                    <button type="button" onClick={() => setShowPopUp(true)} className="add-todo-button">
                        Create New Todo
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
                            <button type="submit" onClick={handleCreatingTodo}>{loading ? "Creating Todo..." : "Save"}</button>
                            <button type="button" onClick={() => {setShowPopUp(false); setTodoTitle("");setTodoDesc("")}}>Cancel</button>
                          </form>
                        </div>
                      </div>
                    )}

                    <div className="todos-section">
                        <h2>Hi {currentUser.name}, here are your Todos</h2>


                        {todos.length === 0 ? (
                            <p className="no-todos">No todos yet. Start by adding one!</p>
                        ) : (
                            <ul className="todos-list">
                                {todos.map((todo) => (
                                    <li key={todo.id} className={`todo-item ${todo.status ? 'completed' : ''}`}>
                                        <div className="todo-content">
                                            <h3 className="todo-title">{todo.title}</h3>
                                
                                            {todo.description && (
                                                <p className="todo-description">{todo.description}</p>
                                            )}
                                            <div className="todo-meta">
                                                <span className={`todo-status ${todo.status ? todo.status: 'completed' }`}>
                                                    {todo.status ? todo.status: 'completed' }
                                                </span>
                                                {todo.created_at && (
                                                <span className="todo-date">
                                                    Created: {new Date(todo.created_at).toLocaleDateString()}
                                                    </span>
                                                )}
                                            </div>
                                            <div className="todo-actions">
                                                <button onClick={() => handleEditTodo(todo)} className="edit-button">
                                                    Edit
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
