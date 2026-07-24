/**
 * 浏览器/Node WebCrypto 凭据加密原语（M2 过渡实现）。
 * SPEC 目标为 Argon2id + XChaCha20-Poly1305（Tauri/libsodium）；
 * 此处用 PBKDF2 + AES-256-GCM，保证无明文落盘与可测往返，后续可迁移。
 */

const textEncoder = new TextEncoder();
const textDecoder = new TextDecoder();

export const VAULT_KDF_ITERATIONS = 310_000;

/** 拷贝为独立 ArrayBuffer，满足 DOM BufferSource 类型约束。 */
function toBuf(bytes: Uint8Array): Uint8Array<ArrayBuffer> {
  const out = new Uint8Array(bytes.byteLength);
  out.set(bytes);
  return out;
}

function b64(buf: ArrayBuffer | Uint8Array): string {
  const bytes = buf instanceof Uint8Array ? buf : new Uint8Array(buf);
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s);
}

function fromB64(s: string): Uint8Array<ArrayBuffer> {
  const bin = atob(s);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function getSubtle(): SubtleCrypto {
  const c = globalThis.crypto?.subtle;
  if (!c) throw new Error('WebCrypto SubtleCrypto 不可用');
  return c;
}

/** 主密码 → KEK（PBKDF2-SHA-256）。 */
export async function deriveKek(
  password: string,
  salt: Uint8Array,
  iterations = VAULT_KDF_ITERATIONS,
): Promise<CryptoKey> {
  const subtle = getSubtle();
  const base = await subtle.importKey('raw', textEncoder.encode(password), 'PBKDF2', false, [
    'deriveKey',
  ]);
  return subtle.deriveKey(
    { name: 'PBKDF2', salt: toBuf(salt), iterations, hash: 'SHA-256' },
    base,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt', 'wrapKey', 'unwrapKey'],
  );
}

export async function generateDek(): Promise<CryptoKey> {
  return getSubtle().generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']);
}

export async function wrapDek(
  dek: CryptoKey,
  kek: CryptoKey,
): Promise<{ iv: string; wrapped: string }> {
  const iv = toBuf(globalThis.crypto.getRandomValues(new Uint8Array(12)));
  const wrapped = await getSubtle().wrapKey('raw', dek, kek, { name: 'AES-GCM', iv });
  return { iv: b64(iv), wrapped: b64(wrapped) };
}

export async function unwrapDek(
  wrappedB64: string,
  ivB64: string,
  kek: CryptoKey,
): Promise<CryptoKey> {
  return getSubtle().unwrapKey(
    'raw',
    fromB64(wrappedB64),
    kek,
    { name: 'AES-GCM', iv: fromB64(ivB64) },
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt'],
  );
}

export async function encryptJson(
  dek: CryptoKey,
  value: unknown,
): Promise<{ iv: string; ciphertext: string }> {
  const iv = toBuf(globalThis.crypto.getRandomValues(new Uint8Array(12)));
  const pt = textEncoder.encode(JSON.stringify(value));
  const ct = await getSubtle().encrypt({ name: 'AES-GCM', iv }, dek, pt);
  return { iv: b64(iv), ciphertext: b64(ct) };
}

export async function decryptJson<T>(
  dek: CryptoKey,
  ivB64: string,
  ciphertextB64: string,
): Promise<T> {
  const pt = await getSubtle().decrypt(
    { name: 'AES-GCM', iv: fromB64(ivB64) },
    dek,
    fromB64(ciphertextB64),
  );
  return JSON.parse(textDecoder.decode(pt)) as T;
}

export function randomSalt(bytes = 16): Uint8Array<ArrayBuffer> {
  return toBuf(globalThis.crypto.getRandomValues(new Uint8Array(bytes)));
}

export function saltToB64(salt: Uint8Array): string {
  return b64(salt);
}

export function saltFromB64(s: string): Uint8Array<ArrayBuffer> {
  return fromB64(s);
}

export { b64, fromB64 };
