# FlipperZero Extras Manager

## install

```bash
git submodule init
git submodule update --init --recursive
git submodule sync --recursive

python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

## execute update

```bash
source ./venv/bin/activate
python3 update.py
```

### example

```
$ python3 update.py                                                        
2023-02-06 22:01:35,428 __main__[10996] INFO	01. updating repos...
2023-02-06 22:01:35,433 __main__[10996] INFO	update_repos/[UberGuidoZ_Flipper]: https://github.com/UberGuidoZ/Flipper.git
2023-02-06 22:01:46,811 __main__[10996] INFO	update_repos/[xMasterX_unleashed-extra-pack]: https://github.com/xMasterX/unleashed-extra-pack.git
2023-02-06 22:01:47,311 __main__[10996] INFO	update_repos/[logickworkshop_Flipper-IRDB]: https://github.com/logickworkshop/Flipper-IRDB.git
2023-02-06 22:01:47,922 __main__[10996] INFO	update_repos/[Gioman101_FlipperAmiibo]: https://github.com/Gioman101/FlipperAmiibo.git
2023-02-06 22:01:48,445 __main__[10996] INFO	02. building new package...
2023-02-06 22:01:48,445 __main__[10996] INFO	build_pkg: 2023-02-06
2023-02-06 22:01:48,445 __main__[10996] WARNING	build_pkg/path: 2023-02-06 already exists, deleting
2023-02-06 22:01:49,400 __main__[10996] INFO	build_pkg/repo([UberGuidoZ]): UberGuidoZ_Flipper
2023-02-06 22:01:51,372 __main__[10996] INFO	build_pkg/repo([xMasterX_u]): xMasterX_unleashed-extra-pack
2023-02-06 22:01:51,400 __main__[10996] INFO	build_pkg/repo([logickwork]): logickworkshop_Flipper-IRDB
2023-02-06 22:01:51,651 __main__[10996] INFO	build_pkg/repo([Gioman101_]): Gioman101_FlipperAmiibo
2023-02-06 22:01:52,027 __main__[10996] INFO	03. installing package...
2023-02-06 22:01:52,027 __main__[10996] INFO	install_pkg: target digest does not match, will update
2023-02-06 22:02:19,781 __main__[10996] INFO	install_pkg/copytree/count: 11243
2023-02-06 22:02:19,782 __main__[10996] INFO	04. installed successfully
$ 
$ python3 update.py                                                        
2023-02-06 22:02:38,353 __main__[11552] INFO	01. updating repos...
2023-02-06 22:02:38,358 __main__[11552] INFO	update_repos/[UberGuidoZ_Flipper]: https://github.com/UberGuidoZ/Flipper.git
2023-02-06 22:02:49,531 __main__[11552] INFO	update_repos/[xMasterX_unleashed-extra-pack]: https://github.com/xMasterX/unleashed-extra-pack.git
2023-02-06 22:02:50,105 __main__[11552] INFO	update_repos/[logickworkshop_Flipper-IRDB]: https://github.com/logickworkshop/Flipper-IRDB.git
2023-02-06 22:02:50,940 __main__[11552] INFO	update_repos/[Gioman101_FlipperAmiibo]: https://github.com/Gioman101/FlipperAmiibo.git
2023-02-06 22:02:51,485 __main__[11552] INFO	02. building new package...
2023-02-06 22:02:51,485 __main__[11552] INFO	build_pkg: 2023-02-06
2023-02-06 22:02:51,485 __main__[11552] WARNING	build_pkg/path: 2023-02-06 already exists, deleting
2023-02-06 22:02:52,525 __main__[11552] INFO	build_pkg/repo([UberGuidoZ]): UberGuidoZ_Flipper
2023-02-06 22:02:54,554 __main__[11552] INFO	build_pkg/repo([xMasterX_u]): xMasterX_unleashed-extra-pack
2023-02-06 22:02:54,583 __main__[11552] INFO	build_pkg/repo([logickwork]): logickworkshop_Flipper-IRDB
2023-02-06 22:02:54,832 __main__[11552] INFO	build_pkg/repo([Gioman101_]): Gioman101_FlipperAmiibo
2023-02-06 22:02:55,184 __main__[11552] INFO	03. installing package...
2023-02-06 22:02:55,185 __main__[11552] INFO	install_pkg: target digest matches - no need to update
2023-02-06 22:02:55,185 __main__[11552] INFO	04. installed successfully
$ 
```

## commit updated repos

```bash
git add repos/ .gitmodules
git status
git commit -m "update source repos"
```