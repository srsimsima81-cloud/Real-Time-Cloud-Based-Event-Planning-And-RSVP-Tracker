import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { CalendarDays } from 'lucide-react';

export default function Login() {
  const { login, register } = useAuth();

  const [mode, setMode] = useState('login');

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'ATTENDEE',
  });

  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (mode === 'login') {
        await login(form.email, form.password);
      } else {
        await register(form);
      }
    } catch (err) {
      const detail = err.response?.data?.detail;

      if (Array.isArray(detail)) {
        setError(
          detail
            .map((item) => item.msg || JSON.stringify(item))
            .join(', ')
        );
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError('Request failed. Please try again.');
      }
    }
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError('');

    setForm({
      name: '',
      email: '',
      password: '',
      role: 'ATTENDEE',
    });
  };

  return (
    <main className="auth">
      <div className="auth-card">

        <div className="logo">
          <CalendarDays />
          CloudEvents
        </div>

        <h1>
          {mode === 'login' ? 'Welcome back' : 'Create account'}
        </h1>

        <p className="muted">
          Real-time cloud event planning and RSVP tracking.
        </p>

        <form onSubmit={submit}>

          {mode === 'register' && (
            <input
              type="text"
              placeholder="Full name"
              value={form.name}
              onChange={(e) =>
                setForm({
                  ...form,
                  name: e.target.value,
                })
              }
              required
            />
          )}

          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) =>
              setForm({
                ...form,
                email: e.target.value,
              })
            }
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) =>
              setForm({
                ...form,
                password: e.target.value,
              })
            }
            required
          />

          {mode === 'register' && (
            <select
              value={form.role}
              onChange={(e) =>
                setForm({
                  ...form,
                  role: e.target.value,
                })
              }
            >
              <option value="ATTENDEE">Attendee</option>
              <option value="ORGANIZER">Organizer</option>
            </select>
          )}

          <button className="primary" type="submit">
            {mode === 'login' ? 'Login' : 'Register'}
          </button>

          {error && (
            <div className="error">
              {error}
            </div>
          )}

        </form>

        <div className="switch">
          {mode === 'login'
            ? 'Need an account?'
            : 'Already registered?'}{' '}

          <button type="button" onClick={switchMode}>
            {mode === 'login' ? 'Register' : 'Login'}
          </button>
        </div>

      </div>
    </main>
  );
}