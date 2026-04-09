import type { WebhookHeader } from '../store/canvasStore';

export type ParsedWebhookBody =
  | { ok: true; value: unknown }
  | { ok: false; error: string };

export function parseWebhookJsonBody(rawBody: string): ParsedWebhookBody {
  try {
    return { ok: true, value: JSON.parse(rawBody) };
  } catch (error) {
    return {
      ok: false,
      error: (error as Error).message || 'Invalid JSON payload.',
    };
  }
}

export function normalizeWebhookHeaders(headers: WebhookHeader[]): WebhookHeader[] {
  const normalized = headers
    .map((item) => ({ key: item.key.trim(), value: item.value.trim() }))
    .filter((item) => item.key || item.value);

  if (!normalized.some((item) => item.key.toLowerCase() === 'content-type')) {
    return [{ key: 'Content-Type', value: 'application/json' }, ...normalized];
  }

  return normalized;
}

export function webhookHeadersToRecord(headers: WebhookHeader[]): Record<string, string> {
  const record: Record<string, string> = {};
  for (const header of normalizeWebhookHeaders(headers)) {
    if (!header.key) continue;
    record[header.key] = header.value;
  }
  return record;
}
