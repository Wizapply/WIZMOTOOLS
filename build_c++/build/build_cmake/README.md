WIZMO C++ with CMAKE
==================
Windows、Linux(+Raspberry Pi)に対応。

## 使い方
### 実行・セットアップ

・取得セットアップ  
```
sudo apt install cmake git
git clone https://github.com/Wizapply/WIZMOTOOLS.git
cd WIZMOTOOLS
```

・ビルド・実行  

```
cd build_c++/build/build_cmake
cmake .
make

cd ../../bin/＊＊＊/
./wizmo_app
```

cd ../../bin/＊＊＊/の「＊＊＊」部分は生成されたアーキテクチャごとに分かれます。  
x64 or x86 or aarch64 or armv7l等
