export interface User {
  id: number;
  username: string;
  email?: string;
  bio: string;
  created_at: string;
  updated_at: string;
  followers: number[];
  following: number[];
  followers_count: number;
  following_count: number;
  is_followed_by_me: boolean;
}

export interface UserRegistration {
  username: string;
  email: string;
  password: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface TokenPair {
  access: string;
  refresh: string;
}
