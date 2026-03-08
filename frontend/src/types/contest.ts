import type { Video, VideoTag } from "./video";

export interface Contest {
  id: number;
  name: string;
  tag: VideoTag;
  start_date: string;
  end_date: string;
  winner: number | null;
  winner_title: string | null;
  is_closed: boolean;
  closed_at: string | null;
  video_count: number;
  winner_detail?: Video | null;
}
