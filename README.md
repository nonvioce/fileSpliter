# fileSpliter
## 文件分割工具  
1. 可实现将大文件分割成数个小文件。  
2. 合并时随意选取小文件中的一个即可。
3. 修改小文件夹名会导致合并后大文件名不对，重命名即可。
4. 小文件名不能修改，合并前请把小文件放在同一文件夹里。  

原理来自于https://www.cnblogs.com/shenghl/p/3946656.html  
用Pyqt5加了GUI  

## 2.0
加入了加密功能  
参考https://www.cjavapy.com/article/243/  

### 关于密码
1. 密码为16位，AES加密
2. 不足十六位用乘法补足16位
3. 超过16位取前16位
4. 留空为默认密码
5. 填中文闪退（小bug暂时不改了）

## 源码
Python3  
库:PyCryptodome,PyQt5
