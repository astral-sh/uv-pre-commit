# uv-pre-commit

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![image](https://img.shields.io/pypi/v/uv.svg)](https://pypi.python.org/pypi/uv)
[![image](https://img.shields.io/pypi/l/uv.svg)](https://pypi.python.org/pypi/uv)
[![image](https://img.shields.io/pypi/pyversions/uv.svg)](https://pypi.python.org/pypi/uv)
[![Actions status](https://github.com/astral-sh/uv-pre-commit/workflows/main/badge.svg)](https://github.com/astral-sh/uv-pre-commit/actions)
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?logo=discord&logoColor=white)](https://discord.gg/astral-sh)

A [pre-commit](https://pre-commit.com/) hook for [uv](https://github.com/astral-sh/uv).

Distributed as a standalone repository to enable installing Ruff via prebuilt wheels from
[PyPI](https://pypi.org/project/uv/).

### Using uv with pre-commit

To run uv's compile via pre-commit, add the following to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/astral-sh/uv-pre-commit
  # uv version.
  rev: v0.1.23
  hooks:
    # Run the pip compile
    - id: pip-compile
      args: [requirements.in, -o, requirements.txt]
```

To compile alternative files, modify the `args` and `files`:

```yaml
- repo: https://github.com/astral-sh/uv-pre-commit
  # uv version.
  rev: v0.1.23
  hooks:
    # Run the pip compile
    - id: pip-compile
      args: [requirements-dev.in, -o, requirements-dev.txt]
      files: ^requirements-dev\.(in|txt)$
```

To run the hook over multiple files at the same time:

```yaml
- repo: https://github.com/astral-sh/uv-pre-commit
  # uv version.
  rev: v0.1.23
  hooks:
    # Run the pip compile
    - id: pip-compile
      name: pip-compile requirements.in
      args: [requirements.in, -o, requirements.txt]
    - id: pip-compile
      name: pip-compile requirements-dev.in
      args: [requirements-dev.in, -o, requirements-dev.txt]
      files: ^requirements-dev\.(in|txt)$
```

## License

MIT

<div align="center">
  <a target="_blank" href="https://astral.sh" style="background:none">
    <img src="https://raw.githubusercontent.com/astral-sh/ruff/main/assets/svg/Astral.svg">
  </a>
</div>
