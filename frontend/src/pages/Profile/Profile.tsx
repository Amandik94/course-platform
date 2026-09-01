import { type FormEvent, useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import { authService } from '../../services/authService';
import Button from '../../components/Button/Button';
import Input from '../../components/Input/Input';
import styles from './Profile.module.css';

const Profile = () => {
    const { user, setUser } = useAuthStore();
    const [firstName, setFirstName] = useState(user?.first_name ?? '');
    const [lastName, setLastName] = useState(user?.last_name ?? '');
    const [isLoading, setIsLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    if (!user) return null; // страница защищена ProtectedRoute, но TypeScript этого не знает

    const initials = `${user.first_name[0] ?? ''}${user.last_name[0] ?? ''}`.toUpperCase();

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();
        setIsLoading(true);
        setSuccessMessage(null);
        try {
            const updated = await authService.updateMe({ first_name: firstName, last_name: lastName });
            setUser(updated);
            setSuccessMessage('Профиль обновлён');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.card}>
                <div className={styles.avatarRow}>
                    <div className={styles.avatar}>
                        {user.avatar ? <img src={user.avatar} alt={user.full_name} /> : initials}
                    </div>
                    <div>
                        <h2>{user.full_name}</h2>
                        <span className={styles.roleTag}>{user.role}</span>
                    </div>
                </div>

                <form className={styles.form} onSubmit={handleSubmit}>
                    {successMessage && <div className={styles.successBanner}>{successMessage}</div>}

                    <Input label="Email" value={user.email} disabled />
                    <Input
                        label="Имя"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        required
                    />
                    <Input
                        label="Фамилия"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        required
                    />

                    <Button type="submit" isLoading={isLoading}>
                        Сохранить
                    </Button>
                </form>
            </div>
        </div>
    );
};

export default Profile;