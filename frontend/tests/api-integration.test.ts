import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8002';

jest.setTimeout(20000);

async function login(email: string, password: string) {
  const response = await axios.post(`${API_URL}/api/auth/login`, { email, password });
  expect(response.status).toBe(200);
  return response.data as { access_token: string; refresh_token: string; user_role: string };
}

describe('API Integration Tests', () => {
  let brandToken: string;
  let adminToken: string;

  beforeAll(async () => {
    const brandLogin = await login('slebronov@mail.ru', '12322828');
    brandToken = brandLogin.access_token;

    const adminLogin = await login('admin@example.com', 'Secret123!');
    adminToken = adminLogin.access_token;
  });

  it('auth login returns tokens', () => {
    expect(brandToken).toBeDefined();
    expect(typeof brandToken).toBe('string');
  });

  it('campaigns endpoint returns list', async () => {
    const response = await axios.get(`${API_URL}/api/campaigns`);
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data.items)).toBe(true);
  });

  it('payments endpoint returns mock data', async () => {
    const response = await axios.get(`${API_URL}/api/payments`);
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data.items)).toBe(true);
  });

  it('notifications endpoint returns data for brand user', async () => {
    const response = await axios.get(`${API_URL}/api/notifications`, {
      headers: {
        Authorization: `Bearer ${brandToken}`
      }
    });
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data.items)).toBe(true);
  });

  it('admin statistics endpoint returns totals', async () => {
    const response = await axios.get(`${API_URL}/api/admin/statistics`, {
      headers: {
        Authorization: `Bearer ${adminToken}`
      }
    });
    expect(response.status).toBe(200);
    expect(typeof response.data.total_users).toBe('number');
  });
});
