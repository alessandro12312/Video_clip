export interface ContestEntryNested {
  id: number;
  user_id: number;
  username: string;
  video_id: number;
  video_title: string;
  video_thumbnail_url: string;
}

export interface MatchupOutput {
  id: number;
  round_number: number;
  position: number;
  entry_1: ContestEntryNested | null;
  entry_2: ContestEntryNested | null;
  winner: number | null;
  is_completed: boolean;
  avg_rating_1: number | null;
  avg_rating_2: number | null;
}

export interface BracketListItem {
  id: number;
  name: string;
  description: string;
  status: "registration" | "active" | "completed";
  max_participants: number;
  current_round: number;
  entries_count: number;
  created_by: number;
  created_by_username: string;
  created_at: string;
  prize_description: string;
}

export interface BracketDetail extends BracketListItem {
  matchups_by_round: Record<string, MatchupOutput[]>;
  my_entry: ContestEntryNested | null;
}

export interface EnterBracketInput {
  video_id: number;
}

export interface VoteMatchupInput {
  entry: number;
  value: number;
}
