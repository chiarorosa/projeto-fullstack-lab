import { describe, expect, it } from 'vitest';
import {
  normalizeWebhookHeaders,
  parseWebhookJsonBody,
  webhookHeadersToRecord,
} from './webhookTestUtils';

describe('webhook test utils', () => {
  it('parses valid JSON body', () => {
    const parsed = parseWebhookJsonBody('{"task":"hello"}');
    expect(parsed.ok).toBe(true);
    if (parsed.ok) {
      expect(parsed.value).toEqual({ task: 'hello' });
    }
  });

  it('returns validation error for malformed JSON body', () => {
    const parsed = parseWebhookJsonBody('{"task":');
    expect(parsed.ok).toBe(false);
    if (!parsed.ok) {
      expect(parsed.error.length).toBeGreaterThan(0);
    }
  });

  it('injects content-type header when missing', () => {
    const headers = normalizeWebhookHeaders([{ key: 'x-custom', value: 'yes' }]);
    expect(headers[0]).toEqual({ key: 'Content-Type', value: 'application/json' });
  });

  it('keeps user content-type header and maps record', () => {
    const headers = normalizeWebhookHeaders([
      { key: 'Content-Type', value: 'application/json' },
      { key: 'X-Test-Origin', value: 'console' },
    ]);
    const record = webhookHeadersToRecord(headers);
    expect(record['Content-Type']).toBe('application/json');
    expect(record['X-Test-Origin']).toBe('console');
  });
});
