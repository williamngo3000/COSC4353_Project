import { useForm } from "react-hook-form";
import { useAuth } from "../store.js";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const { register, handleSubmit } = useForm();

  const onSubmit = (d) => {
    try { login(d.email, d.password); nav("/"); }
    catch(e){ alert(e.message); }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} style={{maxWidth:420}}>
      <h2>Login</h2>
      <label>Email</label>
      <input {...register("email")} required />
      <label>Password</label>
      <input type="password" {...register("password")} required />
      <button type="submit">Login</button>
      <p>New here? <Link to="/register">Register</Link></p>
    </form>
  );
}

