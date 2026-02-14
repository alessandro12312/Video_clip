export interface Rating {
  id: number;
  user: string;
  video: number;
  value: number;
  created_at: string;
  updated_at: string;
}

export interface CreateRatingData {
  video: number;
  value: number;
}
