export interface ReviewAuthor {
    id: number;
    first_name: string;
    last_name: string;
    avatar: string | null;
}

export interface Review {
    id: number;
    student: ReviewAuthor;
    rating: number;
    comment: string;
    created_at: string;
    updated_at: string;
}

export interface ReviewFilters {
    page?: number;
    ordering?: string;
    mine?: boolean;
}

export interface CreateReviewPayload {
    rating: number;
    comment: string;
}

export interface UpdateReviewPayload {
    rating?: number;
    comment?: string;
}
