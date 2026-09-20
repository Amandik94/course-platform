import { useEffect, useState } from 'react';
import { isAxiosError } from 'axios';
import Button from '../../components/Button/Button';
import Loader from '../../components/Loader/Loader';
import EmptyState from '../../components/EmptyState/EmptyState';
import { certificateService } from '../../services/certificateService';
import type { Certificate } from '../../types/certificate';
import styles from './Certificates.module.css';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';

const getDownloadErrorMessage = async (error: unknown) => {
    if (isAxiosError(error) && error.response?.data instanceof Blob) {
        try {
            const payload = JSON.parse(await error.response.data.text()) as { detail?: unknown };
            if (typeof payload.detail === 'string') return payload.detail;
        } catch {
            // The regular API error mapper provides a safe localized fallback below.
        }
    }
    return getApiErrorMessage(error);
};

const Certificates = () => {
    const [certificates, setCertificates] = useState<Certificate[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [downloadError, setDownloadError] = useState<string | null>(null);
    const [downloadingId, setDownloadingId] = useState<number | null>(null);

    useEffect(() => {
        certificateService
            .getCertificates()
            .then(setCertificates)
            .catch((err) => setError(getApiErrorMessage(err)))
            .finally(() => setIsLoading(false));
    }, []);

    const handleDownload = async (certificate: Certificate) => {
        setDownloadingId(certificate.id);
        setDownloadError(null);
        try {
            const blob = await certificateService.downloadCertificate(certificate.id);
            const objectUrl = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = objectUrl;
            link.download = `${certificate.certificate_number}.pdf`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(objectUrl);
        } catch (err) {
            setDownloadError(await getDownloadErrorMessage(err));
        } finally {
            setDownloadingId(null);
        }
    };

    if (isLoading) return <Loader text="Загрузка сертификатов..." />;
    if (error) return <EmptyState variant="error" title="Ошибка" description={error} />;
    if (certificates.length === 0) {
        return (
            <EmptyState
                variant="empty"
                title="У вас пока нет сертификатов"
                description="Завершите курс полностью, чтобы получить сертификат"
            />
        );
    }

    return (
        <div className={`${styles.page} container`}>
            <h1>Мои сертификаты</h1>
            {downloadError && <p className={styles.downloadError} role="alert">{downloadError}</p>}
            <div className={styles.grid}>
                {certificates.map((cert) => (
                    <div key={cert.id} className={styles.card}>
                        <h3>{cert.course_title}</h3>
                        <span className={styles.number}>№ {cert.certificate_number}</span>
                        <span className={styles.number}>
                            Выдан: {new Date(cert.issued_at).toLocaleDateString('ru-RU')}
                        </span>
                        {cert.download_url && (
                            <Button
                                type="button"
                                variant="secondary"
                                fullWidth
                                isLoading={downloadingId === cert.id}
                                disabled={downloadingId !== null}
                                onClick={() => void handleDownload(cert)}
                            >
                                Скачать PDF
                            </Button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Certificates;
