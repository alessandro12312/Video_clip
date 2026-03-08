export interface Comment {
  id: number;
  user: string;
  video: number;
  content: string;
  timestamp_second: number;
  like_count: number;
  is_liked_by_me: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCommentData {
  video: number;
  content: string;
  timestamp_second: number;
}
