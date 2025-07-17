import React, {useEffect, useState} from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { userAPI} from "../api";
import "./user_page.css"

const UserPage = () => {

    const [todos, setTodos] = useState([]);
    const [error, setError] = useState('');

    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');

    useEffect(() => {
        const fetchUserData = async () => {
            console.log("fetch user data is running")
            try{
                const todos = await userAPI.getTodos();
                console.log(todos);
                setTodos(todos.data);
            }
            catch (err){
                setError (err.mesage);
            }
        };
        fetchUserData();
    }, []);
    


    return (
        <div className="user-page">
            <div className="todos-section">
                <h2>Your Todos</h2>

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

export default UserPage;