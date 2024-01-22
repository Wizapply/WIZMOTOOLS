WIZMO C++ with CMAKE
==================
Windows、Linux(+Raspberry Pi)に対応。

## 使い方
### 実行・セットアップ

PC  
```
sudo apt install cmake
cd ./build_c++/build/build_cmake
cmake -DUSE_32BITOS=0 -DUSE_RPI=0 .
```

Raspberry Pi  
```
sudo apt install cmake
cd ./build_c++/build/build_cmake
cmake -DUSE_32BITOS=0 -DUSE_RPI=1 .
```

x86系の場合は「-DUSE_32BITOS=1」としてください。