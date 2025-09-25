import { useForm } from "react-hook-form";
import { useAuth } from "../store.js";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const { register: signup } = useAuth();
  const nav = useNavigate();
  const { register, handleSubmit } = useForm();

  const onSubmit = (d) => {
    try { signup(d.email, d.password); nav("/profile"); } 
    catch(e){ alert(e.message); } B
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} style={{ maxWidth: 420 }}>
      <h2>User Registration</h2>
      <label>Email</label>
      <input {...register("email")} required />
      <label>Password</label>
      <input type="password" {...register("password")} required minLength={6}/>
      <button type="submit">Create Account</button>
    </form>
  );
}

