import type { VideoTag } from "./video";

export interface Contest {
  id: number;
  name: string;
  tag: VideoTag;
  start_date: string;
  end_date: string;
  winner: number | null;
  is_closed: boolean;
  closed_at: string | null;
}
