export type VideoTag = "clutch" | "funny" | "fail";

export interface Video {
  id: number;
  title: string;
  file: string;
  uploader: string;
  average_rating: number;
  like_count: number;
  views: number;
  tag: VideoTag;
  duration: number;
  allow_download: boolean;
  contest: number | null;
  created_at: string;
  updated_at: string;
}

export interface VideoUploadData {
  title: string;
  file: File;
  tag: VideoTag;
  allow_download?: boolean;
}

export type TopRatedRange = "day" | "week" | "month" | "year" | "all";
