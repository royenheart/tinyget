# HOW TO

```bash
apt install gettext
xgettext --language=Python --output=_apt.pot _apt.py
msginit --locale=zh_CN.UTF-8 --input=_apt.pot --output=_apt.po # move to zh_CN
msginit --locale=en_US.UTF-8 --input=_apt.pot --output=_apt.po # move to en_US
# in each language folder edit translates and generate output
msgfmt --output-file=_apt.mo _apt.po
```

Put every .po file in git repo, should compile when installing.

You can use `./generate.sh` to re-generate mo file. `./generate.sh verify` to check the sha256