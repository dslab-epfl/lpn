python3 -m pip install --upgrade build
python3 -m pip uninstall lpnlang -y
cd language
python3 -m build
python3 -m pip install dist/lpnlang-0.0.1-py3-none-any.whl --user
cd ../
