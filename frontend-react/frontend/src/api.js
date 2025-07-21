import axios from 'axios';

const api = axios.create({
    baseURL: "http://localhost:8000",
    headers: {
        "Content-Type": "application/json"
    }
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("access_token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);
    
export const authAPI = {
    login: (credentials) => api.post("/login", credentials),
    register: (userData) => api.post("/register/", userData),
};

export const userAPI = {
    getUser: () => api.get("/users/me"),
    getUsersTodo: (user_id) => api.get(`/users/${user_id}/todos/`),
    createTodo: (user_id, todoData) => api.post(`/users/${user_id}/add-todo`,todoData),
    updateTodo: (user_id, todo_id, updateData) => api.put(`/users/${user_id}/todos/${todo_id}`, updateData),
    deleteTodo: (user_id, todo_id, successMessage) => api.delete(`/users/${user_id}/todos/${todo_id}`,successMessage),
};