export type VideoTag = "clutch" | "funny" | "fail";

export interface Video {
  id: number;
  title: string;
  file: string;
  uploader: string;
  average_rating: number;
  views: number;
  tag: VideoTag;
  duration: number;
  contest: number | null;
  created_at: string;
  updated_at: string;
}

export interface VideoUploadData {
  title: string;
  file: File;
  tag: VideoTag;
}

export type TopRatedRange = "day" | "week" | "month" | "year" | "all";
