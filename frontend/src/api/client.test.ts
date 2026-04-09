import { afterEach, describe, expect, it, vi } from 'vitest';
import { triggerWebhookTest } from './client';

describe('triggerWebhookTest', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('returns structured diagnostics for accepted webhook calls', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          ok: true,
          execution_id: 'exec-123',
          correlation_id: 'corr-456',
          trigger_id: 'wh-789',
          accepted_at: '2026-04-09T12:00:00Z',
          message: 'Webhook execution accepted',
        }),
        {
          status: 202,
          headers: {
            'content-type': 'application/json',
            'x-trace-id': 'trace-1',
          },
        }
      )
    );

    vi.stubGlobal('fetch', fetchMock);
    vi.spyOn(performance, 'now').mockReturnValueOnce(100).mockReturnValueOnce(160);

    const response = await triggerWebhookTest({
      webhookId: 'wh-789',
      body: '{"task":"hello"}',
      headers: { 'X-Custom': 'yes' },
      correlationId: 'corr-456',
    });

    expect(response.ok).toBe(true);
    expect(response.status).toBe(202);
    expect(response.latencyMs).toBe(60);
    expect(response.executionId).toBe('exec-123');
    expect(response.correlationId).toBe('corr-456');
    expect(response.triggerId).toBe('wh-789');
    expect(response.acceptedAt).toBe('2026-04-09T12:00:00Z');
    expect(response.responseHeaders['x-trace-id']).toBe('trace-1');
  });

  it('returns error diagnostics for failed webhook calls', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Webhook trigger not found' }), {
        status: 404,
        headers: {
          'content-type': 'application/json',
        },
      })
    );

    vi.stubGlobal('fetch', fetchMock);
    vi.spyOn(performance, 'now').mockReturnValueOnce(10).mockReturnValueOnce(35);

    const response = await triggerWebhookTest({
      webhookId: 'missing',
      body: '{"task":"hello"}',
    });

    expect(response.ok).toBe(false);
    expect(response.status).toBe(404);
    expect(response.latencyMs).toBe(25);
    expect(response.responseBody).toEqual({ detail: 'Webhook trigger not found' });
  });
});
