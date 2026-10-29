"""Package the complete project, excluding runtime state and generated copies."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '.github', '.openai', '__pycache__', 'dist', 'qa'}
OUTPUT = 'Hata_Kamus_Mandailing_Lengkap.zip'
files = []
for path in sorted(ROOT.rglob('*')):
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED for part in relative.parts):
        continue
    if not path.is_file() or path.suffix == '.pyc' or path.name in {OUTPUT, 'SHA256SUMS.txt'}:
        continue
    if relative.parts[0] == 'migration':
        continue
    files.append((relative.as_posix(), path))
checksums = ''.join(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + name + '\n'
                    for name, path in files)
with zipfile.ZipFile(ROOT / OUTPUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name, path in files:
        archive.write(path, name)
    archive.writestr('SHA256SUMS.txt', checksums)
with zipfile.ZipFile(ROOT / OUTPUT) as archive:
    assert archive.testzip() is None
print(f'Packaged {len(files)} files in {OUTPUT}.')
