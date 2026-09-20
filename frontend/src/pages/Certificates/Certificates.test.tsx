import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { certificateService } from '../../services/certificateService';
import Certificates from './Certificates';

vi.mock('../../services/certificateService', () => ({
    certificateService: {
        getCertificates: vi.fn(),
        downloadCertificate: vi.fn(),
    },
}));

const certificate = {
    id: 7,
    course: 3,
    course_title: 'Django для начинающих',
    certificate_number: 'CERT-007',
    issued_at: '2026-09-20T12:00:00Z',
    download_url: 'https://example.test/api/v1/certificates/7/download/',
};

describe('Certificates', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.mocked(certificateService.getCertificates).mockResolvedValue([certificate]);
    });

    it('downloads a protected PDF through the authenticated API service', async () => {
        const blob = new Blob(['%PDF-1.4'], { type: 'application/pdf' });
        vi.mocked(certificateService.downloadCertificate).mockResolvedValue(blob);
        const createObjectURL = vi.fn(() => 'blob:certificate');
        const revokeObjectURL = vi.fn();
        Object.defineProperty(URL, 'createObjectURL', { value: createObjectURL, configurable: true });
        Object.defineProperty(URL, 'revokeObjectURL', { value: revokeObjectURL, configurable: true });
        const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);

        render(<Certificates />);
        fireEvent.click(await screen.findByRole('button', { name: 'Скачать PDF' }));

        await waitFor(() => {
            expect(certificateService.downloadCertificate).toHaveBeenCalledWith(7);
            expect(createObjectURL).toHaveBeenCalledWith(blob);
            expect(click).toHaveBeenCalledOnce();
            expect(revokeObjectURL).toHaveBeenCalledWith('blob:certificate');
        });
    });

    it('shows a localized error when download fails', async () => {
        vi.mocked(certificateService.downloadCertificate).mockRejectedValue(new Error('failed'));

        render(<Certificates />);
        fireEvent.click(await screen.findByRole('button', { name: 'Скачать PDF' }));

        expect(await screen.findByRole('alert')).toHaveTextContent(
            'Произошла непредвиденная ошибка. Попробуйте позже.',
        );
    });
});
