import { type FormEvent, useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import Input from '../../components/Input/Input';
import { useAuth } from '../../features/auth/useAuth';
import styles from './Register.module.css';

const Register = () => {
    const { register, isLoading, error } = useAuth();
    const [form, setForm] = useState({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        password_confirm: '',
    });

    const handleChange = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) => {
        setForm((prev) => ({ ...prev, [field]: e.target.value }));
    };

    const handleSubmit = (event: FormEvent) => {
        event.preventDefault();
        register(form);
    };

    return (
        <div className={styles.page}>
            <div className={styles.card}>
                <h1 className={styles.title}>Регистрация</h1>

                <form className={styles.form} onSubmit={handleSubmit}>
                    {error && <div className={styles.errorBanner}>{error}</div>}

                    <Input
                        label="Имя"
                        name="first_name"
                        value={form.first_name}
                        onChange={handleChange('first_name')}
                        required
                    />
                    <Input
                        label="Фамилия"
                        name="last_name"
                        value={form.last_name}
                        onChange={handleChange('last_name')}
                        required
                    />
                    <Input
                        label="Email"
                        type="email"
                        name="email"
                        value={form.email}
                        onChange={handleChange('email')}
                        required
                        autoComplete="email"
                    />
                    <Input
                        label="Пароль"
                        type="password"
                        name="password"
                        value={form.password}
                        onChange={handleChange('password')}
                        required
                        minLength={8}
                        autoComplete="new-password"
                    />
                    <Input
                        label="Подтверждение пароля"
                        type="password"
                        name="password_confirm"
                        value={form.password_confirm}
                        onChange={handleChange('password_confirm')}
                        required
                        minLength={8}
                        autoComplete="new-password"
                    />

                    <Button type="submit" fullWidth isLoading={isLoading}>
                        Зарегистрироваться
                    </Button>
                </form>

                <p className={styles.footer}>
                    Уже есть аккаунт? <Link to="/login">Войти</Link>
                </p>
            </div>
        </div>
    );
};

export default Register;