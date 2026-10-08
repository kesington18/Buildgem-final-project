import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { errorMessage } from "../lib/api";
import { AuthLayout } from "../components/AuthLayout";
import { Button, Field, Input } from "../components/ui";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (form.password.length < 8) {
      setError("Use at least 8 characters for your password.");
      return;
    }
    setBusy(true);
    try {
      await register(form.name.trim(), form.email.trim(), form.password);
      navigate("/app", { replace: true });
    } catch (err) {
      setError(errorMessage(err, "We couldn't create your account."));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout
      title="Join your class."
      subtitle="Free for students. Takes under a minute."
      footer={<>Already registered? <Link to="/login" className="font-semibold text-moss underline-offset-4 hover:underline">Sign in</Link></>}
    >
      <form onSubmit={submit} className="space-y-5">
        <Field label="Full name">
          <Input required autoComplete="name" placeholder="Ada Lovelace" value={form.name} onChange={set("name")} />
        </Field>
        <Field label="Email">
          <Input type="email" required autoComplete="email" placeholder="you@school.edu" value={form.email} onChange={set("email")} />
        </Field>
        <Field label="Password" hint="At least 8 characters.">
          <div className="relative">
            <Input
              type={show ? "text" : "password"}
              required
              autoComplete="new-password"
              placeholder="Choose a password"
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

        <Button type="submit" size="lg" loading={busy} className="w-full">Create account</Button>
        <p className="text-center text-sm text-ink-3">
          Class governor? Register as a student first, then claim your group from inside the app.
        </p>
      </form>
    </AuthLayout>
  );
}
