export interface Role {
  id: number
  name: string
  description: string | null
}

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  roles: Role[]
  created_at: string
  updated_at: string
}

export interface Profile {
  full_name: string
  avatar: string | null
  bio: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  password2: string
  first_name?: string
  last_name?: string
}

export interface ChangePasswordData {
  current_password: string
  new_password: string
  confirm_password: string
} 