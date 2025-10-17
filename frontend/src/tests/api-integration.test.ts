import { apiRequest, client } from '@/lib/api';

describe('apiRequest', () => {
  it('returns data on success', async () => {
    const spy = jest.spyOn(client, 'request').mockResolvedValueOnce({ data: { ok: true } } as never);

    const result = await apiRequest<{ ok: boolean }>('/health');
    expect(result).toEqual({ ok: true });
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({ url: '/health' }));
    spy.mockRestore();
  });

  it('throws ApiError on failure', async () => {
    const spy = jest.spyOn(client, 'request').mockRejectedValueOnce({
      response: { status: 500, data: { detail: 'Server error' } }
    } as never);

    await expect(apiRequest('/health')).rejects.toMatchObject({ message: 'Server error', status: 500 });
    spy.mockRestore();
  });
});
