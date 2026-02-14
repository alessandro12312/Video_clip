export interface Comment {
  id: number;
  user: string;
  video: number;
  content: string;
  timestamp_second: number;
  created_at: string;
  updated_at: string;
}

export interface CreateCommentData {
  video: number;
  content: string;
  timestamp_second: number;
}
