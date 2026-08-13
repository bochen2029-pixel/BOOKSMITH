# BOOKSMITH engine container — P0: the public kit, cold, on Linux.
#
# Build context = the PUBLIC tracked tree (git archive HEAD), i.e. exactly what a
# stranger clones. No kit_env.json, no private workspaces, no model weights.
# Proof gates (run inside):
#   python _tools/engine_smoketest.py   -> A..L PASS (engine drive/resume/gates, no Word, no network)
#   python _tools/selfcheck.py          -> kit meta-gate PASS (WARNs allowed: machine-tier probes)
#
# Tier coverage in this image: Tier 2 (kindle DOCX, EPUB, cover compositing/verify glue,
# course domain). Tier 1 print (Word COM) NEVER runs in Linux — it routes to the queued
# Windows print worker (docs/CLOUD_HORIZON_v6.md Part XII §52.1). LibreOffice for the
# Tier-2.5 print experiment ships as a separate layer later, not in the P0 image.
#
# Build (from a staged git-archive tree; see cloud/README.md):
#   docker build -t booksmith-p0 -f cloud/Dockerfile <staged-tree>
# Smoke:
#   docker run --rm booksmith-p0                          # runs the engine smoketest
#   docker run --rm booksmith-p0 python _tools/selfcheck.py

FROM python:3.11-slim-bookworm

# The standing UTF-8 rule (CJK glyphs must never crash a stage) + quiet pip.
ENV PYTHONUTF8=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    BOOKSMITH_CONTAINER=1

# node (interior DOCX generators + selfcheck's JS parse gate). bookworm ships node 18.
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
       libreoffice-writer fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /kit

# Python deps first (stable layer). requirements.txt already carries the
# sys_platform=="win32" marker on pywin32, so it installs clean on Linux.
COPY requirements.txt requirements-studio.txt ./
RUN pip install -r requirements.txt -r requirements-studio.txt

# Vendored-node reproduction: the repo gitignores _tools/node_modules; a cold
# clone reinstalls from the committed manifest+lock (the INSTALL.md story).
COPY _tools/package.json _tools/package-lock.json _tools/
RUN npm ci --prefix _tools --no-audit --no-fund

# The kit itself (docker merge-copies; node_modules from the layer above survives).
COPY . .

# Default command = the graduation exam.
CMD ["python", "_tools/engine_smoketest.py"]
