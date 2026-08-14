import { User } from '../../types/auth';
import { ENV } from '../../config/env';

const DEMO_USER: User = {
  id: 'usr_payer_001',
  name: 'Divya K',
  email: 'analyst@demo.com',
  organization: 'Aetna Medicare Value-Based Division',
  role: 'Payer Analyst',
  avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=150',
};

export async function loginUser(email: string, password: string): Promise<User> {
  if (ENV.dataSource === 'api') {
    const response = await fetch(`${ENV.apiBaseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error('Invalid credentials or unauthorized login request.');
    }
    return response.json();
  }

  // Phase 1 Mock Auth simulation delay
  await new Promise((res) => setTimeout(res, 400));

  // Accept ANY email and password combination in Phase 1 mock mode
  if (email && email.trim() && password && password.trim()) {
    const isDefaultDemo = email.toLowerCase() === 'analyst@demo.com';

    // Format custom name from email prefix (e.g., alex.smith@health.com -> Alex Smith)
    const emailPrefix = email.split('@')[0];
    const formattedName = emailPrefix
      .split(/[._-]/)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(' ');

    return {
      id: `usr_${Date.now()}`,
      name: isDefaultDemo ? DEMO_USER.name : formattedName || 'Payer Analyst',
      email: email,
      organization: isDefaultDemo ? DEMO_USER.organization : 'Payer Health Plan Network',
      role: 'Payer Analyst',
      avatar: DEMO_USER.avatar,
    };
  }

  throw new Error('Please enter a valid email and password.');
}

export async function registerUser(data: {
  name: string;
  email: string;
  organization: string;
  password: string;
}): Promise<User> {
  if (ENV.dataSource === 'api') {
    const response = await fetch(`${ENV.apiBaseUrl}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to create account.');
    }
    return response.json();
  }

  // Phase 1 Mock Signup simulation delay
  await new Promise((res) => setTimeout(res, 400));

  return {
    id: `usr_${Date.now()}`,
    name: data.name,
    email: data.email,
    organization: data.organization || 'Payer Healthcare Network',
    role: 'Payer Analyst',
  };
}
