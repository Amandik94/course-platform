import { api } from './api';
import type { PaginatedResponse } from '../types/common';
import type { Certificate } from '../types/certificate';

export const certificateService = {
    getCertificates: () =>
        api.get<PaginatedResponse<Certificate>>('certificates/').then((res) => res.data.results),
    downloadCertificate: (certificateId: number) =>
        api
            .get<Blob>(`certificates/${certificateId}/download/`, { responseType: 'blob' })
            .then((res) => res.data),
};
