import React, {useEffect, useState} from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { userAPI} from "../api";
import "./user_page.css"

const UserPage = () => {

    const [todos, setTodos] = useState([]);
    const [error, setError] = useState('');

    const [loading, setLoading] = useState(true);
    const [success, setSuccess] = useState('');
    const [currentUser, setCurrentUser] = useState(null);

    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            console.log("fetch user data is running")
            try{
                const user = await userAPI.getUser();
                setCurrentUser(user.data);
                console.log(user.data);
                const todos = await userAPI.getUsersTodo();
                console.log(todos);
                setTodos(todos.data);
            }
            catch (err){
                setError (err.message);
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
    
    const handleAddingTodo = () => {
        userAPI.createTodo(currentUser.name);
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
                    <button
                        type="button" 
                        onClick={handleLogout}
                        className="logout-button"
                    >
                        Logout
                    </button>
                    <button
                        type="button" 
                        onClick={handleAddingTodo}
                        className="add-todo-button"
                    >
                        Create New Todo
                    </button>
                    </div>
                    <div className="todos-section">
                        <h2>Hi {currentUser.name}, here are your Todos</h2>


                        {todos.length === 0 ? (
                            <p className="no-todos">No todos yet. Start by adding one!</p>
                        ) : (
                            <ul className="todos-list">
                                {todos.map((todo) => (
                                    <li key={todo.id} className={`todo-item ${todo.completed ? 'completed' : ''}`}>
                                        <div className="todo-content">
                                            <h3 className="todo-title">{todo.title}</h3>
                                
                                            {todo.description && (
                                                <p className="todo-description">{todo.description}</p>
                                            )}
                                            <div className="todo-meta">
                                                <span className={`todo-status ${todo.completed ? 'completed' : 'pending'}`}>
                                                    {todo.completed ? 'Completed' : 'Pending'}
                                                </span>
                                                {todo.created_at && (
                                                    <span className="todo-date">
                                                        Created: {new Date(todo.created_at).toLocaleDateString()}
                                                    </span>
                                                )}
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
