isort --skip venv . &&
  autoflake -r --in-place --remove-all-unused-imports --remove-unused-variables --exclude venv . &&
  black . --exclude venv
