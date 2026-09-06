import { useEffect, useState } from 'react';
import Button from '../../components/Button/Button';
import Loader from '../../components/Loader/Loader';
import EmptyState from '../../components/EmptyState/EmptyState';
import { certificateService } from '../../services/certificateService';
import type { Certificate } from '../../types/certificate';
import styles from './Certificates.module.css';

const Certificates = () => {
    const [certificates, setCertificates] = useState<Certificate[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        certificateService
            .getCertificates()
            .then(setCertificates)
            .catch(() => setError('Не удалось загрузить сертификаты.'))
            .finally(() => setIsLoading(false));
    }, []);

    if (isLoading) return <Loader text="Загрузка сертификатов..." />;
    if (error) return <EmptyState title="Ошибка" description={error} />;
    if (certificates.length === 0) {
        return (
            <EmptyState
                title="У вас пока нет сертификатов"
                description="Завершите курс полностью, чтобы получить сертификат"
            />
        );
    }

    return (
        <div className={`${styles.page} container`}>
            <h1>Мои сертификаты</h1>
            <div className={styles.grid}>
                {certificates.map((cert) => (
                    <div key={cert.id} className={styles.card}>
                        <h3>{cert.course_title}</h3>
                        <span className={styles.number}>№ {cert.certificate_number}</span>
                        <span className={styles.number}>
                            Выдан: {new Date(cert.issued_at).toLocaleDateString()}
                        </span>
                        {cert.pdf && (
                            <a href={cert.pdf} target="_blank" rel="noopener noreferrer">
                                <Button variant="secondary" fullWidth>Скачать PDF</Button>
                            </a>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Certificates;