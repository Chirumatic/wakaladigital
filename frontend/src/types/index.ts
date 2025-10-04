export interface User {
  id: number;
  username: string;
  email: string;
  profile: UserProfile;
}

export interface UserProfile {
  id: number;
  user: number;
  phone_number: string;
  id_number: string;
  is_verified: boolean;
  risk_appetite: 'LOW' | 'MEDIUM' | 'HIGH';
  profile_picture?: string;
}

export interface SavingsGroup {
  id: number;
  name: string;
  description?: string;
  risk_tolerance: 'LOW' | 'MEDIUM' | 'HIGH';
  tier_level: number;
  total_balance: number;
  created_at: string;
  members: GroupMembership[];
}

export interface GroupMembership {
  id: number;
  user: number;
  group: number;
  role: 'ADMIN' | 'MEMBER';
  contribution_limit: number;
  joined_at: string;
}

export interface Contribution {
  id: number;
  member: number;
  amount: number;
  transaction_type: 'DEPOSIT' | 'WITHDRAWAL';
  timestamp: string;
}

export interface Loan {
  id: number;
  borrower: number;
  amount: number;
  interest_rate: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'PAID';
  due_date: string;
  created_at: string;
}

export interface Investment {
  id: number;
  group: number;
  investment_type: 'UNIT_TRUST' | 'STOCKS' | 'BONDS' | 'REAL_ESTATE';
  amount: number;
  current_value: number;
  provider: string;
  annual_return_rate: number;
  start_date: string;
}
