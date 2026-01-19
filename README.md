# CTFOnlinePlatform-CoinCollector

​	众所周知，NSSCTF，Bugku等很多国内在线CTF靶场需要金币开启题目环境(或者下载附件)，获取金币的方法要么氪金，要么签到，当然对于白嫖怪来说是一分都不可能氪的，因此，本工具就诞生了，可实现自动化挂机签到拿金币

​	小玩具项目，可靠性与稳定性均未知，图一乐就好

​	当前支持在线靶场：

- [NSSCTF](https://www.nssctf.cn/)
- [Bugku](https://ctf.bugku.com/)
- [CTFHub](https://www.ctfhub.com/)
- [攻防世界](https://adworld.xctf.org.cn/)
- [青少年CTF练习平台](https://www.qsnctf.com/)



## 食用方法

### Docker部署

​	拉取项目

```
git clone https://github.com/YZBRH/CTFOnlinePlatform-CoinCollector.git
cd CTFOnlinePlatform-CoinCollector
```

​	配置config.py文件，输入账号密码等信息

​	然后执行

```
cd docker
docker-compose up -d
```



### 本地部署

​	拉取项目

```
git clone https://github.com/YZBRH/CTFOnlinePlatform-CoinCollector.git
cd CTFOnlinePlatform-CoinCollector
```


​	配置config.py文件，输入账号密码等信息

​	然后执行

```
pip install -r requirement.txt
python main.py
```



## 更新日志

### V1.0

### V1.0.1

- fix(NSSCTF): 修复NSSCTF签到失败的问题

### V1.1.0

- feature(Module): 添加[CTFHub](https://www.ctfhub.com/)，[攻防世界](https://adworld.xctf.org.cn/)

### V1.2.0

- feature(Module): 添加[青少年CTF练习平台](https://www.qsnctf.com/)

- perf(main): 优化部分代码逻辑

### V1.2.1

- perf(log): 增加日志轮询，防止日志文件过大

### V1.2.2

- fix(NSSCTF): 更新登录接口以适应平台变化

### V1.2.3

- fix(import): 解决了ddddocr库导入失败的问题