export type VideoTag = "clutch" | "funny" | "fail";

export interface Video {
  id: number;
  title: string;
  file: string;
  file_url: string;
  uploader: string;
  average_rating: number;
  views: number;
  tag: VideoTag;
  duration: number;
  thumbnail_url: string | null;
  allow_download: boolean;
  my_rating_id: number | null;
  my_rating_value: number | null;
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

export interface DownloadResponse {
  download_url: string;
}
