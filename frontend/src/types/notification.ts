export interface Notification {
  id: number;
  recipient: number;
  sender: number | null;
  sender_username: string | null;
  type: NotificationType;
  type_display: string;
  is_read: boolean;
  created_at: string; // ISO 8601
  video: number | null;
  video_title: string | null;
  comment: number | null;
  contest: number | null;
}

export type NotificationType =
  | "comment_received"
  | "like_received"
  | "comment_promoted"
  | "contest_opened"
  | "bracket_invite"
  | "bracket_turn"
  | "contest_results";
