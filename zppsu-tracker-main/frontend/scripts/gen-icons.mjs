import sharp from 'sharp'
import { mkdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const outDir = path.join(root, 'public', 'icons')
mkdirSync(outDir, { recursive: true })

const mark = path.join(root, 'src', 'assets', 'logo-mark.svg')
const maskable = path.join(root, 'src', 'assets', 'logo-maskable.svg')

const jobs = [
  [mark, 'icon-192.png', 192],
  [mark, 'icon-512.png', 512],
  [mark, 'apple-touch-icon.png', 180],
  [maskable, 'icon-maskable-192.png', 192],
  [maskable, 'icon-maskable-512.png', 512],
]

for (const [src, name, size] of jobs) {
  await sharp(src).resize(size, size).png().toFile(path.join(outDir, name))
  console.log('generated', name)
}
