import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { errorMessage } from "../lib/api";
import { AuthLayout } from "../components/AuthLayout";
import { Button, Field, Input } from "../components/ui";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(form.email.trim(), form.password);
      navigate(location.state?.from || "/app", { replace: true });
    } catch (err) {
      setError(err?.response?.status === 401 ? "That email and password don't match." : errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back."
      subtitle="Sign in to see what you've missed."
      footer={<>New here? <Link to="/register" className="font-semibold text-moss underline-offset-4 hover:underline">Create an account</Link></>}
    >
      <form onSubmit={submit} className="space-y-5">
        <Field label="Email">
          <Input type="email" required autoComplete="email" placeholder="you@school.edu" value={form.email} onChange={set("email")} />
        </Field>
        <Field label="Password">
          <div className="relative">
            <Input
              type={show ? "text" : "password"}
              required
              autoComplete="current-password"
              placeholder="Your password"
              value={form.password}
              onChange={set("password")}
              className="pr-12"
            />
            <button type="button" onClick={() => setShow((s) => !s)} aria-label={show ? "Hide password" : "Show password"} className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer text-ink-3 hover:text-ink">
              {show ? <EyeOff className="size-5" /> : <Eye className="size-5" />}
            </button>
          </div>
        </Field>

        {error && <p role="alert" className="rounded-xl bg-clay/10 px-4 py-3 text-sm text-clay">{error}</p>}

        <Button type="submit" size="lg" loading={busy} className="w-full">Sign in</Button>
      </form>
    </AuthLayout>
  );
}
