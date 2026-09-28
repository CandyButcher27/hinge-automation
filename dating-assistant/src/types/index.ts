export interface Profile {
  id: number;
  name: string | null;
  age: number | null;
  occupation: string | null;
  location: string | null;
  bio: string | null;
  notes: string | null;
  user_rating: number | null;
  fingerprint: string | null;
  created_at: string;
  updated_at: string;
}

export interface Preference {
  id: number;
  category: string;
  value: string;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: number;
  profile_id: number;
  content: string;
  created_at: string;
}

export interface Draft {
  id: number;
  profile_id: number | null;
  draft: string;
  status: string;
  created_at: string;
}

export interface ProfileAnalysis {
  profile: Profile;
  possible_interests: string[];
  conversation_topics: string[];
  questions_to_consider: string[];
  potential_compatibility: string[];
  uncertainties: string[];
}
