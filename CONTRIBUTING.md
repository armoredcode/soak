Contributing to SOAK First off, thanks for taking the time to contribute! SOAK
thrives on the community's collective knowledge of security tools.

🛠 How to Add a New Tool Adding a tool to SOAK is a three-step process:

1. Update the Dockerfile

The tool must be available inside the openSUSE Tumbleweed environment.

- If it's a Python tool: Use pip install --break-system-packages.
- If it's a Go tool: Use go install.
- If it's a Ruby tool: Use gem install.
- If it's a System package: Use zypper install -y.

```Dockerfile
RUN gem install new-security-tool
```

2. Register the Tool in analyzer.py

Add the tool to the TOOLS_MAPPING dictionary.

- Key: The file extension (e.g., .php, .py) or a global trigger.
- Value: A list of tuples ("tool_name", ["command", "args"]).
- Use the {OUTPUT} placeholder if the tool supports a specific flag for the
  output file. If not, the orchestrator will automatically redirect stdout to
  the report file.

````python
``` py
".php": [
    ("phpstan", ["phpstan", "analyse", ".", "--error-format=json"])
]
````

3. Update the CHANGELOG.md Follow Semantic Versioning.

- Patch (1.1.x): Bug fixes, minor internal changes.
- Minor (1.x.0): New tool added, new language support, new CLI feature.
- Major (x.0.0): Breaking changes in report format or core architecture.

## 🚦 Pull Request Process

1. Fork the repository and create your branch from main.
2. Test your changes locally by running soak against a test codebase containing
   the relevant files for your new tool.
3. Ensure your code follows PEP 8 for Python.
4. Update the documentation if you added new features or changed existing
   behavior.
5. Submit the PR with a clear description of what you added and why.

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the
GNU AGPL 3.0.
