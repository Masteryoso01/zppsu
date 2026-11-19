// Device biometric verification via WebAuthn (platform authenticator).
// Android -> fingerprint / face unlock, iOS -> Face ID / Touch ID. The biometric
// itself never leaves the phone; we only get a signed assertion back.
//
// NOTE: without a backend the challenge is generated locally, so this proves the
// user unlocked the device but is not tamper-proof. For production, fetch the
// challenge from the server and verify the attestation/assertion there.

const storageKey = (internId) => `geotrack.credential.${internId}`

const toB64 = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf)))
const fromB64 = (str) => Uint8Array.from(atob(str), (c) => c.charCodeAt(0))
const challenge = () => crypto.getRandomValues(new Uint8Array(32))

export function biometricLabel() {
  const ua = navigator.userAgent
  if (/iPhone|iPad|iPod/i.test(ua)) return 'Face ID'
  if (/Android/i.test(ua)) return 'Fingerprint'
  return 'Device biometrics'
}

export async function isBiometricSupported() {
  if (!window.PublicKeyCredential || !window.isSecureContext) return false
  try {
    return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
  } catch {
    return false
  }
}

export function hasCredential(internId) {
  try {
    return !!localStorage.getItem(storageKey(internId))
  } catch {
    return false
  }
}

export function clearCredential(internId) {
  try { localStorage.removeItem(storageKey(internId)) } catch { /* ignore */ }
}

/** Re-key a stored credential (used once the server has assigned the account its final id). */
export function moveCredential(fromId, toId) {
  try {
    const value = localStorage.getItem(storageKey(fromId))
    if (!value) return
    localStorage.setItem(storageKey(toId), value)
    localStorage.removeItem(storageKey(fromId))
  } catch { /* ignore */ }
}

export async function registerBiometric(intern) {
  const cred = await navigator.credentials.create({
    publicKey: {
      challenge: challenge(),
      rp: { name: 'GeoTrack', id: location.hostname },
      user: {
        id: new TextEncoder().encode(String(intern.id)),
        name: intern.email || String(intern.id),
        displayName: intern.name,
      },
      pubKeyCredParams: [{ type: 'public-key', alg: -7 }, { type: 'public-key', alg: -257 }],
      authenticatorSelection: {
        authenticatorAttachment: 'platform',
        userVerification: 'required',
        residentKey: 'preferred',
      },
      timeout: 60000,
    },
  })
  localStorage.setItem(storageKey(intern.id), toB64(cred.rawId))
}

export async function verifyBiometric(internId) {
  const id = localStorage.getItem(storageKey(internId))
  if (!id) throw new Error('No biometric registered on this device.')
  const assertion = await navigator.credentials.get({
    publicKey: {
      challenge: challenge(),
      rpId: location.hostname,
      allowCredentials: [{ type: 'public-key', id: fromB64(id), transports: ['internal'] }],
      userVerification: 'required',
      timeout: 60000,
    },
  })
  return !!assertion
}
